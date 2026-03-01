from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from refua_preclinical.cmc import (
    assess_stability_results,
    build_formulation_process_plan,
    build_stability_study_plan,
    default_cmc_templates,
    evaluate_release_criteria,
    generate_batch_record,
)


def test_cmc_plan_and_batch_record_structure() -> None:
    plan = build_formulation_process_plan()
    assert plan["summary"]["component_count"] > 0
    assert plan["summary"]["process_step_count"] > 0
    assert "release_criteria" in plan["cmc"]

    batch_record = generate_batch_record(batch_id="BATCH-QA-001")
    assert batch_record["batch_id"] == "BATCH-QA-001"
    assert len(batch_record["material_dispense"]) > 0
    assert len(batch_record["process_execution_record"]) > 0
    assert len(batch_record["release_testing"]) > 0


def test_stability_plan_and_assessment() -> None:
    templates = default_cmc_templates()
    cmc = templates["cmc"]
    stability_rows = templates["stability_results_rows"]
    criteria = cmc["release_criteria"]

    stability_plan = build_stability_study_plan(cmc, batch_ids=["BATCH-001", "BATCH-002"])
    assert stability_plan["sample_count"] > 0
    assert len(stability_plan["batch_ids"]) == 2

    assessment = assess_stability_results(stability_rows, release_criteria=criteria)
    assert assessment["parsed_rows"] == len(stability_rows)
    assert assessment["oos_count"] == 0
    assert assessment["passes_release_criteria"] is True


def test_release_eval_detects_out_of_specification() -> None:
    templates = default_cmc_templates()
    cmc = templates["cmc"]
    criteria = cmc["release_criteria"]
    passing_results = templates["batch_results"]
    passing_eval = evaluate_release_criteria(
        batch_results=passing_results,
        release_criteria=criteria,
    )
    assert passing_eval["passed"] is True
    assert passing_eval["decision"] == "release"

    failing_results = dict(passing_results)
    failing_results["assay_percent"] = 108.2
    failing_eval = evaluate_release_criteria(
        batch_results=failing_results,
        release_criteria=criteria,
    )
    assert failing_eval["passed"] is False
    assert failing_eval["decision"] == "hold"
    assert any(item["test"] == "assay_percent" for item in failing_eval["failed_checks"])

