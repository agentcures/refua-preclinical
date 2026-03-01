from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from refua_preclinical.cli import main
from refua_preclinical.cmc import default_cmc_templates, default_cmc_spec
from refua_preclinical.models import default_study_spec, study_spec_to_mapping


def test_cli_plan_and_schedule(tmp_path: Path) -> None:
    config_path = tmp_path / "study.json"
    plan_path = tmp_path / "plan.json"
    schedule_path = tmp_path / "schedule.json"

    config_path.write_text(
        json.dumps(study_spec_to_mapping(default_study_spec()), indent=2),
        encoding="utf-8",
    )

    rc = main(["plan", "--config", str(config_path), "--output", str(plan_path)])
    assert rc == 0
    assert plan_path.exists()

    rc = main(
        ["schedule", "--config", str(config_path), "--output", str(schedule_path)]
    )
    assert rc == 0
    assert schedule_path.exists()

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
    assert plan["summary"]["total_animals"] > 0
    assert schedule["event_count"] > 0


def test_cli_cmc_workflow(tmp_path: Path) -> None:
    cmc_config_path = tmp_path / "cmc.json"
    cmc_plan_path = tmp_path / "cmc_plan.json"
    batch_record_path = tmp_path / "batch_record.json"
    stability_plan_path = tmp_path / "stability_plan.json"
    stability_rows_path = tmp_path / "stability_rows.json"
    batch_results_path = tmp_path / "batch_results.json"
    release_eval_path = tmp_path / "release_eval.json"

    cmc_config_path.write_text(
        json.dumps(default_cmc_spec(), indent=2),
        encoding="utf-8",
    )
    templates = default_cmc_templates()
    stability_rows_path.write_text(
        json.dumps(templates["stability_results_rows"], indent=2),
        encoding="utf-8",
    )
    batch_results_path.write_text(
        json.dumps(templates["batch_results"], indent=2),
        encoding="utf-8",
    )

    rc = main(
        ["cmc-plan", "--config", str(cmc_config_path), "--output", str(cmc_plan_path)]
    )
    assert rc == 0
    assert cmc_plan_path.exists()

    rc = main(
        [
            "batch-record",
            "--config",
            str(cmc_config_path),
            "--batch-id",
            "BATCH-QA-001",
            "--output",
            str(batch_record_path),
        ]
    )
    assert rc == 0
    assert batch_record_path.exists()

    rc = main(
        [
            "stability-plan",
            "--config",
            str(cmc_config_path),
            "--batch-id",
            "BATCH-QA-001",
            "--output",
            str(stability_plan_path),
        ]
    )
    assert rc == 0
    assert stability_plan_path.exists()

    rc = main(
        [
            "release-eval",
            "--config",
            str(cmc_config_path),
            "--batch-results",
            str(batch_results_path),
            "--stability-results",
            str(stability_rows_path),
            "--output",
            str(release_eval_path),
        ]
    )
    assert rc == 0
    assert release_eval_path.exists()

    cmc_plan = json.loads(cmc_plan_path.read_text(encoding="utf-8"))
    batch_record = json.loads(batch_record_path.read_text(encoding="utf-8"))
    stability_plan = json.loads(stability_plan_path.read_text(encoding="utf-8"))
    release_eval = json.loads(release_eval_path.read_text(encoding="utf-8"))
    assert cmc_plan["summary"]["component_count"] > 0
    assert batch_record["batch_id"] == "BATCH-QA-001"
    assert stability_plan["sample_count"] > 0
    assert release_eval["passed"] is True
