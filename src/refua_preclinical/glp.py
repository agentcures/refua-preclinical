"""GLP readiness checks for preclinical study plans."""

from __future__ import annotations

from typing import Any

from .models import GLPChecklistSpec


def evaluate_glp_readiness(glp: GLPChecklistSpec) -> dict[str, Any]:
    items = [
        _item(
            "statement_of_compliance",
            "GLP statement of compliance",
            glp.statement_of_compliance,
        ),
        _item(
            "quality_assurance_unit",
            "Quality Assurance Unit assigned",
            glp.quality_assurance_unit,
        ),
        _item(
            "protocol_approved", "Protocol approved before start", glp.protocol_approved
        ),
        _item("sop_index", "Current SOP index available", glp.sop_index),
        _item(
            "instrument_calibration_records",
            "Instrument calibration/maintenance records available",
            glp.instrument_calibration_records,
        ),
        _item(
            "computer_system_validation",
            "Computerized systems validation documented",
            glp.computer_system_validation,
        ),
        _item(
            "sample_chain_of_custody",
            "Sample chain-of-custody process documented",
            glp.sample_chain_of_custody,
        ),
        _item(
            "raw_data_archival_plan",
            "Raw data archival and retention plan documented",
            glp.raw_data_archival_plan,
        ),
    ]

    passed = sum(1 for item in items if item["pass"])
    total = len(items)
    score = float(passed / total) if total else 0.0
    failed = [item for item in items if not item["pass"]]

    return {
        "score": score,
        "passed": passed,
        "total": total,
        "ready": len(failed) == 0,
        "failed_items": failed,
        "checklist": items,
    }


def _item(key: str, label: str, condition: bool) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "pass": bool(condition),
        "status": "pass" if bool(condition) else "fail",
    }
