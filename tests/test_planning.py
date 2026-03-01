from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from refua_preclinical.models import default_study_spec
from refua_preclinical.planning import build_study_plan, build_workup


def test_build_study_plan_has_expected_sections() -> None:
    study = default_study_spec()
    payload = build_study_plan(study, seed=13)

    assert payload["study_id"] == study.study_id
    assert payload["summary"]["arm_count"] == len(study.arms)
    assert payload["summary"]["total_animals"] > 0
    assert payload["glp_readiness"]["ready"] is True
    assert payload["schedule_summary"]["event_count"] > 0
    assert payload["randomization"]["assignment_count"] == payload["summary"]["total_animals"]


def test_build_workup_includes_bioanalysis_when_rows_provided() -> None:
    study = default_study_spec()
    rows = [
        {
            "sample_id": "s1",
            "arm_id": "low",
            "animal_id": "low-001",
            "analyte": study.sampling.analyte,
            "matrix": study.sampling.matrix,
            "day": 1,
            "time_hr": 1.0,
            "concentration_ng_ml": 8.5,
        }
    ]

    payload = build_workup(study, samples=rows, lloq_ng_ml=1.0)

    assert "plan" in payload
    assert "schedule" in payload
    assert "bioanalysis" in payload
    assert payload["bioanalysis"]["parsed_rows"] == 1
