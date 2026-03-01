"""CMC planning utilities for refua-preclinical.

This module covers:
- Formulation and process development plans
- Batch manufacturing records
- Stability study planning and result trending
- Release criteria evaluation
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Any, Mapping


def default_cmc_spec() -> dict[str, Any]:
    """Return a starter CMC configuration."""
    return {
        "product_name": "RX-001 immediate-release tablet",
        "dosage_form": "tablet",
        "strength_mg": 50.0,
        "target_batch_size_units": 100_000,
        "formulation": [
            {
                "component": "RX-001 API",
                "function": "active",
                "amount_per_unit_mg": 50.0,
            },
            {
                "component": "Lactose monohydrate",
                "function": "diluent",
                "amount_per_unit_mg": 120.0,
            },
            {
                "component": "Microcrystalline cellulose",
                "function": "binder",
                "amount_per_unit_mg": 20.0,
            },
            {
                "component": "Croscarmellose sodium",
                "function": "disintegrant",
                "amount_per_unit_mg": 6.0,
            },
            {
                "component": "Magnesium stearate",
                "function": "lubricant",
                "amount_per_unit_mg": 2.0,
            },
            {
                "component": "Hypromellose coat",
                "function": "film_coat",
                "amount_per_unit_mg": 4.0,
            },
        ],
        "process_steps": [
            {
                "step_id": "S01",
                "operation": "dispensing",
                "equipment": "dispensing booth",
                "duration_min": 90,
                "setpoints": {"line_clearance": "verified", "balance_check": "pass"},
                "in_process_checks": ["material identity", "dispense reconciliation"],
            },
            {
                "step_id": "S02",
                "operation": "blending",
                "equipment": "bin blender",
                "duration_min": 45,
                "setpoints": {"blend_rpm": 12, "target_duration_min": 45},
                "in_process_checks": ["blend uniformity"],
            },
            {
                "step_id": "S03",
                "operation": "compression",
                "equipment": "tablet press",
                "duration_min": 180,
                "setpoints": {"target_weight_mg": 202, "hardness_kp": "8-12"},
                "in_process_checks": ["tablet weight", "hardness", "friability"],
            },
            {
                "step_id": "S04",
                "operation": "film_coating",
                "equipment": "coating pan",
                "duration_min": 120,
                "setpoints": {"inlet_temp_c": 55, "spray_rate_g_min": 180},
                "in_process_checks": ["coat appearance", "weight gain"],
            },
            {
                "step_id": "S05",
                "operation": "packaging",
                "equipment": "blister line",
                "duration_min": 150,
                "setpoints": {"leak_test": "pass"},
                "in_process_checks": ["count verification", "seal integrity"],
            },
        ],
        "stability_plan": {
            "start_date": datetime.now(UTC).date().isoformat(),
            "conditions": [
                {
                    "condition_id": "long_term_25c_60rh",
                    "label": "Long-term 25C/60%RH",
                    "temperature_c": 25.0,
                    "rh_percent": 60.0,
                },
                {
                    "condition_id": "accelerated_40c_75rh",
                    "label": "Accelerated 40C/75%RH",
                    "temperature_c": 40.0,
                    "rh_percent": 75.0,
                },
            ],
            "timepoints_months": [0, 1, 3, 6, 9, 12, 18, 24],
            "tests": [
                "assay_percent",
                "total_impurities_percent",
                "dissolution_q30_percent",
                "water_content_percent",
                "appearance_score",
            ],
            "replicates_per_timepoint": 3,
        },
        "release_criteria": {
            "assay_percent": {"min": 95.0, "max": 105.0, "unit": "% label claim"},
            "total_impurities_percent": {"max": 2.0, "unit": "%"},
            "dissolution_q30_percent": {"min": 80.0, "unit": "%"},
            "water_content_percent": {"max": 3.0, "unit": "%"},
            "appearance_score": {"min": 4.0, "max": 5.0, "unit": "score"},
        },
    }


def cmc_spec_from_mapping(data: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate and normalize a CMC config object."""
    default = default_cmc_spec()
    if data is None:
        source: Mapping[str, Any] = default
    else:
        if not isinstance(data, Mapping):
            raise ValueError("CMC config must be a JSON/YAML object.")
        nested = data.get("cmc")
        if isinstance(nested, Mapping):
            source = nested
        else:
            source = data

    product_name = _required_str(
        source.get("product_name", default["product_name"]),
        "product_name",
    )
    dosage_form = _required_str(
        source.get("dosage_form", default["dosage_form"]),
        "dosage_form",
    )
    strength_mg = _required_float(
        source.get("strength_mg", default["strength_mg"]),
        "strength_mg",
        minimum=0.001,
    )
    target_batch_size_units = _required_int(
        source.get("target_batch_size_units", default["target_batch_size_units"]),
        "target_batch_size_units",
        minimum=1,
    )
    formulation = _normalize_formulation(
        source.get("formulation", default["formulation"]),
    )
    process_steps = _normalize_process_steps(
        source.get("process_steps", default["process_steps"]),
    )
    stability_plan = _normalize_stability_plan(
        source.get("stability_plan", default["stability_plan"]),
        default_plan=default["stability_plan"],
    )
    release_criteria = _normalize_release_criteria(
        source.get("release_criteria", default["release_criteria"]),
        default_criteria=default["release_criteria"],
    )

    return {
        "product_name": product_name,
        "dosage_form": dosage_form,
        "strength_mg": strength_mg,
        "target_batch_size_units": target_batch_size_units,
        "formulation": formulation,
        "process_steps": process_steps,
        "stability_plan": stability_plan,
        "release_criteria": release_criteria,
    }


def build_formulation_process_plan(
    cmc_config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate formulation/process development outputs from CMC config."""
    cmc = cmc_spec_from_mapping(cmc_config)
    formulation = cmc["formulation"]
    process_steps = cmc["process_steps"]

    total_unit_mass_mg = sum(float(item["amount_per_unit_mg"]) for item in formulation)
    api_mass_mg = sum(
        float(item["amount_per_unit_mg"])
        for item in formulation
        if "active" in str(item["function"]).strip().lower()
        or str(item["function"]).strip().lower() in {"api", "drug_substance"}
    )
    api_load_percent = (
        float(api_mass_mg / total_unit_mass_mg * 100.0) if total_unit_mass_mg > 0 else 0.0
    )
    batch_size = int(cmc["target_batch_size_units"])
    theoretical_batch_mass_kg = float(total_unit_mass_mg * batch_size / 1_000_000.0)

    in_process_check_count = sum(
        len(step["in_process_checks"]) for step in process_steps
    )
    setpoint_count = sum(len(step["setpoints"]) for step in process_steps)
    operations = [str(step["operation"]).strip().lower() for step in process_steps]

    recommendations: list[str] = []
    if "blending" not in operations:
        recommendations.append(
            "Add an explicit blending operation with blend-uniformity IPC coverage."
        )
    if "compression" not in operations and cmc["dosage_form"].strip().lower() == "tablet":
        recommendations.append(
            "Tablet dosage form selected without a compression step; verify process design."
        )
    if api_load_percent >= 40.0:
        recommendations.append(
            "API load is high; tighten blend-uniformity and dissolution control strategy."
        )
    if setpoint_count < len(process_steps):
        recommendations.append(
            "At least one process step has no quantitative setpoints; add CPP targets."
        )
    if not recommendations:
        recommendations.append(
            "Formulation and process plan are balanced for process characterization start."
        )

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "cmc": cmc,
        "summary": {
            "product_name": cmc["product_name"],
            "dosage_form": cmc["dosage_form"],
            "strength_mg": cmc["strength_mg"],
            "component_count": len(formulation),
            "process_step_count": len(process_steps),
            "total_unit_mass_mg": round(total_unit_mass_mg, 3),
            "api_load_percent": round(api_load_percent, 3),
            "target_batch_size_units": batch_size,
            "theoretical_batch_mass_kg": round(theoretical_batch_mass_kg, 6),
            "in_process_check_count": in_process_check_count,
            "setpoint_count": setpoint_count,
        },
        "formulation_development": {
            "components": formulation,
            "component_functions": sorted(
                {str(item["function"]).strip().lower() for item in formulation}
            ),
        },
        "process_development": {
            "steps": process_steps,
            "operations": operations,
        },
        "recommendations": recommendations,
    }


def generate_batch_record(
    cmc_config: Mapping[str, Any] | None = None,
    *,
    batch_id: str = "BATCH-001",
    operator: str = "TBD",
    site: str = "TBD",
    manufacture_date: str | None = None,
) -> dict[str, Any]:
    """Generate an electronic batch record template from CMC config."""
    cmc = cmc_spec_from_mapping(cmc_config)
    batch_key = _required_str(batch_id, "batch_id")
    batch_size = int(cmc["target_batch_size_units"])
    manufacture_date_value = (
        str(manufacture_date).strip()
        if manufacture_date is not None and str(manufacture_date).strip()
        else datetime.now(UTC).date().isoformat()
    )

    material_dispense: list[dict[str, Any]] = []
    for item in cmc["formulation"]:
        per_unit_mg = float(item["amount_per_unit_mg"])
        theoretical_qty_kg = float(per_unit_mg * batch_size / 1_000_000.0)
        material_dispense.append(
            {
                "component": item["component"],
                "function": item["function"],
                "amount_per_unit_mg": per_unit_mg,
                "theoretical_qty_kg": round(theoretical_qty_kg, 6),
                "actual_qty_kg": None,
                "dispensed_by": None,
                "verified_by": None,
                "lot_number": None,
            }
        )

    execution_steps: list[dict[str, Any]] = []
    for step in cmc["process_steps"]:
        execution_steps.append(
            {
                "step_id": step["step_id"],
                "operation": step["operation"],
                "equipment": step["equipment"],
                "target_duration_min": step["duration_min"],
                "setpoints": dict(step["setpoints"]),
                "in_process_checks": [
                    {"test": test_name, "observed": None, "pass": None}
                    for test_name in step["in_process_checks"]
                ],
                "actual_start": None,
                "actual_end": None,
                "performed_by": None,
                "verified_by": None,
                "comments": None,
            }
        )

    release_testing: list[dict[str, Any]] = []
    for test_name, criterion in sorted(cmc["release_criteria"].items()):
        release_testing.append(
            {
                "test": test_name,
                "minimum": criterion.get("min"),
                "maximum": criterion.get("max"),
                "target": criterion.get("target"),
                "unit": criterion.get("unit"),
                "observed": None,
                "pass": None,
            }
        )

    theoretical_total_kg = sum(row["theoretical_qty_kg"] for row in material_dispense)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "batch_id": batch_key,
        "header": {
            "product_name": cmc["product_name"],
            "dosage_form": cmc["dosage_form"],
            "strength_mg": cmc["strength_mg"],
            "site": _required_str(site, "site"),
            "operator": _required_str(operator, "operator"),
            "manufacture_date": manufacture_date_value,
            "target_batch_size_units": batch_size,
        },
        "material_dispense": material_dispense,
        "process_execution_record": execution_steps,
        "yield_reconciliation": {
            "theoretical_total_kg": round(theoretical_total_kg, 6),
            "actual_yield_kg": None,
            "yield_percent": None,
        },
        "deviations": [],
        "release_testing": release_testing,
        "release_decision": {
            "status": "pending",
            "approved_by": None,
            "approved_at": None,
        },
    }


def build_stability_study_plan(
    cmc_config: Mapping[str, Any] | None = None,
    *,
    batch_ids: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Build stability sample schedule from CMC config."""
    cmc = cmc_spec_from_mapping(cmc_config)
    stability = cmc["stability_plan"]
    if batch_ids is None:
        resolved_batch_ids = ["BATCH-001"]
    else:
        resolved_batch_ids = [
            str(item).strip() for item in batch_ids if str(item).strip()
        ]
    if not resolved_batch_ids:
        raise ValueError("batch_ids must include at least one non-empty value.")

    start = _parse_date(stability["start_date"])
    conditions = stability["conditions"]
    timepoints = stability["timepoints_months"]
    tests = stability["tests"]
    replicates = int(stability["replicates_per_timepoint"])

    samples: list[dict[str, Any]] = []
    for batch_id in resolved_batch_ids:
        for condition in conditions:
            for month in timepoints:
                due_date = (start + timedelta(days=int(float(month) * 30.4375))).isoformat()
                for replicate in range(1, replicates + 1):
                    sample_id = (
                        f"{batch_id}-{condition['condition_id']}-M{int(month)}-R{replicate}"
                    )
                    samples.append(
                        {
                            "sample_id": sample_id,
                            "batch_id": batch_id,
                            "condition_id": condition["condition_id"],
                            "condition_label": condition["label"],
                            "temperature_c": condition["temperature_c"],
                            "rh_percent": condition["rh_percent"],
                            "timepoint_month": month,
                            "due_date": due_date,
                            "replicate": replicate,
                            "tests": list(tests),
                        }
                    )

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "product_name": cmc["product_name"],
        "batch_ids": resolved_batch_ids,
        "start_date": start.isoformat(),
        "condition_count": len(conditions),
        "timepoint_count": len(timepoints),
        "tests": list(tests),
        "replicates_per_timepoint": replicates,
        "sample_count": len(samples),
        "samples": samples,
    }


def assess_stability_results(
    rows: list[dict[str, Any]],
    *,
    release_criteria: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assess stability results and trend by batch/condition/test."""
    if not isinstance(rows, list):
        raise ValueError("rows must be a list of objects.")
    criteria = _normalize_release_criteria(
        release_criteria,
        default_criteria={},
    )

    parsed_rows: list[dict[str, Any]] = []
    oos_rows: list[dict[str, Any]] = []
    grouped: dict[tuple[str, str, str], list[tuple[float, float]]] = {}

    for idx, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ValueError(f"rows[{idx}] must be an object.")
        batch_id = _required_str(row.get("batch_id"), f"rows[{idx}].batch_id")
        condition_id = _required_str(
            row.get("condition_id"),
            f"rows[{idx}].condition_id",
        )
        test_name = _required_str(row.get("test"), f"rows[{idx}].test")
        value = _required_float(row.get("value"), f"rows[{idx}].value")
        timepoint_month = _required_float(
            row.get("timepoint_month"),
            f"rows[{idx}].timepoint_month",
            minimum=0.0,
        )
        unit = str(row.get("unit", "") or "").strip()

        criterion = criteria.get(test_name)
        passes_criteria: bool | None = None
        if criterion is not None:
            passes_criteria = _passes_limits(
                value,
                minimum=criterion.get("min"),
                maximum=criterion.get("max"),
            )
            if not passes_criteria:
                oos_rows.append(
                    {
                        "row_index": idx,
                        "batch_id": batch_id,
                        "condition_id": condition_id,
                        "test": test_name,
                        "value": value,
                        "minimum": criterion.get("min"),
                        "maximum": criterion.get("max"),
                        "unit": criterion.get("unit") or unit,
                    }
                )

        grouped.setdefault((batch_id, condition_id, test_name), [])
        grouped[(batch_id, condition_id, test_name)].append((timepoint_month, value))
        parsed_rows.append(
            {
                "batch_id": batch_id,
                "condition_id": condition_id,
                "test": test_name,
                "timepoint_month": timepoint_month,
                "value": value,
                "unit": unit,
                "criteria_applied": criterion is not None,
                "passes_criteria": passes_criteria,
            }
        )

    grouped_trends: list[dict[str, Any]] = []
    for key in sorted(grouped.keys()):
        points = sorted(grouped[key], key=lambda item: item[0])
        values = [point[1] for point in points]
        grouped_trends.append(
            {
                "batch_id": key[0],
                "condition_id": key[1],
                "test": key[2],
                "n": len(points),
                "min": min(values),
                "max": max(values),
                "mean": (sum(values) / len(values)),
                "slope_per_month": _linear_slope(points),
            }
        )

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "input_rows": len(rows),
        "parsed_rows": len(parsed_rows),
        "criteria_test_count": len(criteria),
        "oos_count": len(oos_rows),
        "passes_release_criteria": len(oos_rows) == 0,
        "oos_rows": oos_rows,
        "grouped_trends": grouped_trends,
        "rows": parsed_rows,
    }


def evaluate_release_criteria(
    batch_results: Mapping[str, Any] | list[dict[str, Any]],
    release_criteria: Mapping[str, Any],
    *,
    stability_assessment: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate release criteria against observed batch test results."""
    criteria = _normalize_release_criteria(
        release_criteria,
        default_criteria={},
    )
    if not criteria:
        raise ValueError("release_criteria must define at least one test.")

    observed = _normalize_batch_results(batch_results)
    checks: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []

    for test_name, criterion in sorted(criteria.items()):
        value = observed.get(test_name)
        if value is None:
            check = {
                "test": test_name,
                "observed": None,
                "minimum": criterion.get("min"),
                "maximum": criterion.get("max"),
                "unit": criterion.get("unit"),
                "pass": False,
                "reason": "missing_result",
            }
            failed.append(check)
            checks.append(check)
            continue

        passed = _passes_limits(
            float(value),
            minimum=criterion.get("min"),
            maximum=criterion.get("max"),
        )
        check = {
            "test": test_name,
            "observed": float(value),
            "minimum": criterion.get("min"),
            "maximum": criterion.get("max"),
            "unit": criterion.get("unit"),
            "pass": passed,
            "reason": None if passed else "out_of_specification",
        }
        if not passed:
            failed.append(check)
        checks.append(check)

    stability_oos_count = 0
    if isinstance(stability_assessment, Mapping):
        raw_oos = stability_assessment.get("oos_count")
        if isinstance(raw_oos, (int, float, str)):
            try:
                stability_oos_count = int(raw_oos)
            except (TypeError, ValueError):
                stability_oos_count = 0
        if stability_oos_count > 0:
            failed.append(
                {
                    "test": "stability_summary",
                    "observed": stability_oos_count,
                    "minimum": None,
                    "maximum": 0,
                    "unit": "count",
                    "pass": False,
                    "reason": "stability_oos_present",
                }
            )

    passed = len(failed) == 0
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "passed": passed,
        "decision": "release" if passed else "hold",
        "criteria_count": len(criteria),
        "observed_test_count": len(observed),
        "checks": checks,
        "failed_checks": failed,
        "stability_oos_count": stability_oos_count,
    }


def default_cmc_templates() -> dict[str, Any]:
    """Return default CMC config and starter stability/release rows."""
    cmc = default_cmc_spec()
    return {
        "cmc": cmc,
        "batch_results": _default_batch_results(cmc["release_criteria"]),
        "stability_results_rows": _default_stability_rows(cmc),
    }


def _default_batch_results(release_criteria: Mapping[str, Any]) -> dict[str, float]:
    results: dict[str, float] = {}
    for test_name, criterion_raw in release_criteria.items():
        if not isinstance(criterion_raw, Mapping):
            continue
        minimum = _optional_float(criterion_raw.get("min"), allow_none=True)
        maximum = _optional_float(criterion_raw.get("max"), allow_none=True)
        if minimum is not None and maximum is not None:
            results[str(test_name)] = float((minimum + maximum) / 2.0)
            continue
        if maximum is not None:
            results[str(test_name)] = float(maximum * 0.75)
            continue
        if minimum is not None:
            results[str(test_name)] = float(minimum * 1.25)
    return results


def _default_stability_rows(cmc: Mapping[str, Any]) -> list[dict[str, Any]]:
    criteria = _normalize_release_criteria(
        cmc.get("release_criteria"),
        default_criteria={},
    )
    stability = cmc.get("stability_plan")
    if not isinstance(stability, Mapping):
        return []
    conditions_raw = stability.get("conditions")
    if not isinstance(conditions_raw, list) or not conditions_raw:
        return []
    first_condition = conditions_raw[0]
    if not isinstance(first_condition, Mapping):
        return []
    condition_id = str(first_condition.get("condition_id", "long_term_25c_60rh"))
    unit_overrides = {name: str(spec.get("unit", "")) for name, spec in criteria.items()}

    timepoints = [0, 3, 6, 12]
    max_month = max(timepoints)
    rows: list[dict[str, Any]] = []
    for test_name, criterion in sorted(criteria.items()):
        minimum = criterion.get("min")
        maximum = criterion.get("max")
        for month in timepoints:
            fraction = float(month / max_month) if max_month > 0 else 0.0
            if minimum is not None and maximum is not None:
                center = (float(minimum) + float(maximum)) / 2.0
                span = float(maximum) - float(minimum)
                value = center - span * 0.1 * fraction
            elif maximum is not None:
                value = float(maximum) * (0.55 + 0.35 * fraction)
            elif minimum is not None:
                value = float(minimum) * (1.45 - 0.2 * fraction)
            else:
                value = 0.0
            rows.append(
                {
                    "batch_id": "BATCH-001",
                    "condition_id": condition_id,
                    "timepoint_month": month,
                    "test": test_name,
                    "value": round(value, 4),
                    "unit": unit_overrides.get(test_name, ""),
                }
            )
    return rows


def _normalize_formulation(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError("formulation must be a non-empty list.")
    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"formulation[{idx}] must be an object.")
        amount = item.get("amount_per_unit_mg", item.get("amount_mg_per_unit"))
        normalized.append(
            {
                "component": _required_str(
                    item.get("component"),
                    f"formulation[{idx}].component",
                ),
                "function": _required_str(
                    item.get("function"),
                    f"formulation[{idx}].function",
                ),
                "amount_per_unit_mg": _required_float(
                    amount,
                    f"formulation[{idx}].amount_per_unit_mg",
                    minimum=0.000001,
                ),
            }
        )
    return normalized


def _normalize_process_steps(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError("process_steps must be a non-empty list.")
    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"process_steps[{idx}] must be an object.")
        step_id = str(item.get("step_id", f"S{idx + 1:02d}") or f"S{idx + 1:02d}").strip()
        operation = _required_str(
            item.get("operation"),
            f"process_steps[{idx}].operation",
        )
        equipment = str(item.get("equipment", "TBD") or "TBD").strip()
        duration_min = _required_int(
            item.get("duration_min", 0),
            f"process_steps[{idx}].duration_min",
            minimum=0,
        )
        setpoints_raw = item.get("setpoints", {})
        if setpoints_raw is None:
            setpoints_raw = {}
        if not isinstance(setpoints_raw, Mapping):
            raise ValueError(f"process_steps[{idx}].setpoints must be an object.")
        in_process_checks = _normalize_string_list(
            item.get("in_process_checks", item.get("ipc_tests", [])),
            field_name=f"process_steps[{idx}].in_process_checks",
        )
        normalized.append(
            {
                "step_id": step_id or f"S{idx + 1:02d}",
                "operation": operation,
                "equipment": equipment or "TBD",
                "duration_min": duration_min,
                "setpoints": {
                    str(key): _jsonable_value(raw_value)
                    for key, raw_value in setpoints_raw.items()
                },
                "in_process_checks": in_process_checks,
            }
        )
    return normalized


def _normalize_stability_plan(
    value: Any,
    *,
    default_plan: Mapping[str, Any],
) -> dict[str, Any]:
    raw = value
    if raw is None:
        raw = default_plan
    if not isinstance(raw, Mapping):
        raise ValueError("stability_plan must be an object.")

    start_date_raw = raw.get("start_date", default_plan.get("start_date"))
    start_date_value = _parse_date(start_date_raw).isoformat()

    conditions_raw = raw.get("conditions", default_plan.get("conditions"))
    if not isinstance(conditions_raw, list) or not conditions_raw:
        raise ValueError("stability_plan.conditions must be a non-empty list.")
    conditions: list[dict[str, Any]] = []
    for idx, condition in enumerate(conditions_raw):
        if not isinstance(condition, Mapping):
            raise ValueError(f"stability_plan.conditions[{idx}] must be an object.")
        condition_id = _required_str(
            condition.get("condition_id", f"cond_{idx + 1}"),
            f"stability_plan.conditions[{idx}].condition_id",
        )
        conditions.append(
            {
                "condition_id": condition_id,
                "label": _required_str(
                    condition.get("label", condition_id),
                    f"stability_plan.conditions[{idx}].label",
                ),
                "temperature_c": _required_float(
                    condition.get("temperature_c"),
                    f"stability_plan.conditions[{idx}].temperature_c",
                ),
                "rh_percent": _required_float(
                    condition.get("rh_percent"),
                    f"stability_plan.conditions[{idx}].rh_percent",
                    minimum=0.0,
                ),
            }
        )

    timepoints_raw = raw.get("timepoints_months", default_plan.get("timepoints_months"))
    if not isinstance(timepoints_raw, list) or not timepoints_raw:
        raise ValueError("stability_plan.timepoints_months must be a non-empty list.")
    timepoints = sorted(
        {
            _required_int(
                month,
                "stability_plan.timepoints_months[]",
                minimum=0,
            )
            for month in timepoints_raw
        }
    )
    if 0 not in timepoints:
        timepoints = [0, *timepoints]

    tests = _normalize_string_list(
        raw.get("tests", default_plan.get("tests", [])),
        field_name="stability_plan.tests",
    )
    replicates = _required_int(
        raw.get(
            "replicates_per_timepoint",
            default_plan.get("replicates_per_timepoint", 1),
        ),
        "stability_plan.replicates_per_timepoint",
        minimum=1,
    )

    return {
        "start_date": start_date_value,
        "conditions": conditions,
        "timepoints_months": timepoints,
        "tests": tests,
        "replicates_per_timepoint": replicates,
    }


def _normalize_release_criteria(
    value: Any,
    *,
    default_criteria: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    raw = value if value is not None else default_criteria
    if not isinstance(raw, Mapping):
        raise ValueError("release_criteria must be an object.")

    normalized: dict[str, dict[str, Any]] = {}
    for test_name, criterion_raw in raw.items():
        if not isinstance(criterion_raw, Mapping):
            raise ValueError(f"release_criteria.{test_name} must be an object.")
        minimum = _optional_float(criterion_raw.get("min"), allow_none=True)
        maximum = _optional_float(criterion_raw.get("max"), allow_none=True)
        target = _optional_float(criterion_raw.get("target"), allow_none=True)
        if minimum is None and maximum is None:
            raise ValueError(
                f"release_criteria.{test_name} must include min and/or max limits."
            )
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError(
                f"release_criteria.{test_name} min cannot be greater than max."
            )
        normalized[str(test_name)] = {
            "min": minimum,
            "max": maximum,
            "target": target,
            "unit": str(criterion_raw.get("unit", "") or ""),
        }
    return normalized


def _normalize_batch_results(
    value: Mapping[str, Any] | list[dict[str, Any]],
) -> dict[str, float]:
    if isinstance(value, Mapping):
        nested = value.get("results")
        if isinstance(nested, list):
            return _normalize_batch_results(nested)
        observed: dict[str, float] = {}
        for test_name, raw_value in value.items():
            if test_name == "results":
                continue
            if isinstance(raw_value, Mapping) and "value" in raw_value:
                observed[str(test_name)] = _required_float(
                    raw_value.get("value"),
                    f"batch_results.{test_name}.value",
                )
                continue
            try:
                observed[str(test_name)] = float(raw_value)
            except (TypeError, ValueError):
                continue
        return observed

    if isinstance(value, list):
        grouped: dict[str, list[float]] = {}
        for idx, row in enumerate(value):
            if not isinstance(row, Mapping):
                raise ValueError(f"batch_results[{idx}] must be an object.")
            test_name = _required_str(row.get("test"), f"batch_results[{idx}].test")
            result_value = _required_float(
                row.get("value", row.get("observed")),
                f"batch_results[{idx}].value",
            )
            grouped.setdefault(test_name, []).append(result_value)
        return {
            test_name: float(sum(values) / len(values))
            for test_name, values in grouped.items()
            if values
        }

    raise ValueError("batch_results must be an object or a list of {test, value} rows.")


def _passes_limits(
    value: float,
    *,
    minimum: float | None,
    maximum: float | None,
) -> bool:
    if minimum is not None and value < float(minimum):
        return False
    if maximum is not None and value > float(maximum):
        return False
    return True


def _linear_slope(points: list[tuple[float, float]]) -> float | None:
    if len(points) < 2:
        return None
    x_mean = sum(item[0] for item in points) / len(points)
    y_mean = sum(item[1] for item in points) / len(points)
    denominator = sum((item[0] - x_mean) ** 2 for item in points)
    if denominator <= 0:
        return None
    numerator = sum((item[0] - x_mean) * (item[1] - y_mean) for item in points)
    return float(numerator / denominator)


def _parse_date(value: Any) -> date:
    text = str(value or "").strip()
    if not text:
        return datetime.now(UTC).date()
    try:
        if len(text) == 10:
            return date.fromisoformat(text)
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return datetime.now(UTC).date()


def _required_str(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} must be non-empty.")
    return text


def _required_int(value: Any, field_name: str, *, minimum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer.") from exc
    if parsed < minimum:
        raise ValueError(f"{field_name} must be >= {minimum}.")
    return parsed


def _required_float(
    value: Any,
    field_name: str,
    *,
    minimum: float | None = None,
) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number.") from exc
    if minimum is not None and parsed < float(minimum):
        raise ValueError(f"{field_name} must be >= {minimum}.")
    return parsed


def _optional_float(value: Any, *, allow_none: bool) -> float | None:
    if value is None:
        if allow_none:
            return None
        raise ValueError("value cannot be None.")
    if value == "":
        if allow_none:
            return None
        raise ValueError("value cannot be blank.")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("value must be numeric.") from exc


def _normalize_string_list(value: Any, *, field_name: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        items = [item.strip() for item in value.split(",") if item.strip()]
        if not items:
            raise ValueError(f"{field_name} must contain at least one value.")
        return items
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list of strings.")
    normalized = [str(item).strip() for item in value if str(item).strip()]
    if not normalized:
        raise ValueError(f"{field_name} must contain at least one value.")
    return normalized


def _jsonable_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_jsonable_value(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonable_value(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _jsonable_value(raw) for key, raw in value.items()}
    return str(value)

