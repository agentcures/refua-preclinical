from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from refua_preclinical.bioanalytics import run_bioanalytical_pipeline
from refua_preclinical.models import default_study_spec


def test_bioanalysis_pipeline_summarizes_group_and_auc() -> None:
    study = default_study_spec()
    rows = [
        {
            "sample_id": "low-1-0p5",
            "arm_id": "low",
            "animal_id": "low-001",
            "analyte": "parent",
            "matrix": "plasma",
            "day": 1,
            "time_hr": 0.5,
            "concentration_ng_ml": 4.0,
        },
        {
            "sample_id": "low-1-1p0",
            "arm_id": "low",
            "animal_id": "low-001",
            "analyte": "parent",
            "matrix": "plasma",
            "day": 1,
            "time_hr": 1.0,
            "concentration_ng_ml": 6.0,
        },
        {
            "sample_id": "low-1-2p0",
            "arm_id": "low",
            "animal_id": "low-001",
            "analyte": "parent",
            "matrix": "plasma",
            "day": 1,
            "time_hr": 2.0,
            "concentration_ng_ml": 3.5,
        },
    ]

    payload = run_bioanalytical_pipeline(study, rows, lloq_ng_ml=1.0)

    assert payload["parsed_rows"] == 3
    assert payload["flag_count"] == 0
    assert len(payload["grouped_summary"]) == 3
    assert len(payload["nca"]) == 1
    assert payload["nca"][0]["auc_last_ng_h_per_ml"] > 0.0
