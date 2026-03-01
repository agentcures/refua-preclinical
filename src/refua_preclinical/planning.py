"""Study planning workflows for refua-preclinical."""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from random import Random
from typing import Any

from .bioanalytics import run_bioanalytical_pipeline
from .cmc import (
    assess_stability_results,
    build_formulation_process_plan,
    build_stability_study_plan,
    default_cmc_templates,
    evaluate_release_criteria,
    generate_batch_record,
)
from .glp import evaluate_glp_readiness
from .models import PreclinicalStudySpec, default_study_spec, study_spec_to_mapping
from .research import latest_cmc_references
from .scheduler import build_in_vivo_schedule


def build_study_plan(spec: PreclinicalStudySpec, *, seed: int = 7) -> dict[str, Any]:
    glp = evaluate_glp_readiness(spec.glp)
    schedule = build_in_vivo_schedule(spec)
    randomization = _build_randomization(spec, seed=seed)

    total_animals = sum(max(0, int(arm.n_animals)) for arm in spec.arms)
    dose_levels = [float(arm.dose_mg_per_kg) for arm in spec.arms]

    return {
        "study_id": spec.study_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "study": study_spec_to_mapping(spec),
        "summary": {
            "title": spec.title,
            "species": spec.species,
            "strain": spec.strain,
            "study_type": spec.study_type,
            "modality": spec.modality,
            "duration_days": spec.duration_days,
            "arm_count": len(spec.arms),
            "total_animals": total_animals,
            "min_dose_mg_per_kg": min(dose_levels) if dose_levels else None,
            "max_dose_mg_per_kg": max(dose_levels) if dose_levels else None,
            "sampling_day_count": len(set(spec.sampling.days)),
            "sampling_timepoint_count": len(set(spec.sampling.timepoints_hr)),
        },
        "glp_readiness": glp,
        "schedule_summary": {
            "event_count": schedule["event_count"],
            "event_counts": schedule["event_counts"],
            "max_events_single_day": schedule["max_events_single_day"],
        },
        "randomization": randomization,
        "recommendations": _plan_recommendations(glp=glp, schedule=schedule),
    }


def build_workup(
    spec: PreclinicalStudySpec,
    *,
    samples: list[dict[str, Any]] | None = None,
    seed: int = 7,
    lloq_ng_ml: float = 1.0,
    cmc_config: dict[str, Any] | None = None,
    stability_results: list[dict[str, Any]] | None = None,
    batch_results: dict[str, Any] | list[dict[str, Any]] | None = None,
    batch_id: str = "BATCH-001",
) -> dict[str, Any]:
    plan = build_study_plan(spec, seed=seed)
    schedule = build_in_vivo_schedule(spec)

    payload = {
        "study_id": spec.study_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "plan": plan,
        "schedule": schedule,
    }

    if samples is not None:
        payload["bioanalysis"] = run_bioanalytical_pipeline(
            spec,
            samples,
            lloq_ng_ml=lloq_ng_ml,
        )

    if (
        cmc_config is not None
        or stability_results is not None
        or batch_results is not None
    ):
        cmc_payload: dict[str, Any] = {
            "plan": build_formulation_process_plan(cmc_config),
            "batch_record": generate_batch_record(cmc_config, batch_id=batch_id),
            "stability_plan": build_stability_study_plan(
                cmc_config,
                batch_ids=[batch_id],
            ),
        }
        release_criteria = cmc_payload["plan"]["cmc"]["release_criteria"]
        stability_assessment: dict[str, Any] | None = None
        if stability_results is not None:
            stability_assessment = assess_stability_results(
                stability_results,
                release_criteria=release_criteria,
            )
            cmc_payload["stability_assessment"] = stability_assessment
        if batch_results is not None:
            cmc_payload["release_assessment"] = evaluate_release_criteria(
                batch_results=batch_results,
                release_criteria=release_criteria,
                stability_assessment=stability_assessment,
                critical_quality_attributes=cmc_payload["plan"]["cmc"][
                    "critical_quality_attributes"
                ],
            )
        cmc_payload["references"] = latest_cmc_references()
        payload["cmc"] = cmc_payload

    return payload


def render_plan_markdown(plan: dict[str, Any]) -> str:
    summary = _mapping(plan.get("summary"))
    glp = _mapping(plan.get("glp_readiness"))
    schedule_summary = _mapping(plan.get("schedule_summary"))
    recommendations = plan.get("recommendations")
    if not isinstance(recommendations, list):
        recommendations = []

    lines = [
        f"# Preclinical Plan: {plan.get('study_id', 'unknown')}",
        "",
        "## Summary",
        f"- Title: {summary.get('title')}",
        f"- Species/Strain: {summary.get('species')} / {summary.get('strain')}",
        f"- Study Type: {summary.get('study_type')}",
        f"- Arms: {summary.get('arm_count')}",
        f"- Total Animals: {summary.get('total_animals')}",
        "",
        "## GLP Readiness",
        f"- Score: {glp.get('score')}",
        f"- Ready: {glp.get('ready')}",
        f"- Failed Checks: {len(glp.get('failed_items') or [])}",
        "",
        "## Schedule",
        f"- Event Count: {schedule_summary.get('event_count')}",
        f"- Max Events in a Day: {schedule_summary.get('max_events_single_day')}",
        "",
        "## Recommendations",
    ]
    for rec in recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines).strip() + "\n"


def default_templates() -> dict[str, Any]:
    study = default_study_spec()
    cmc_templates = default_cmc_templates()
    sample_rows: list[dict[str, Any]] = []
    for arm in study.arms:
        for time_hr, concentration in (
            (0.5, max(0.0, arm.dose_mg_per_kg * 0.35)),
            (1.0, max(0.0, arm.dose_mg_per_kg * 0.50)),
            (2.0, max(0.0, arm.dose_mg_per_kg * 0.42)),
            (4.0, max(0.0, arm.dose_mg_per_kg * 0.27)),
            (8.0, max(0.0, arm.dose_mg_per_kg * 0.12)),
            (24.0, max(0.0, arm.dose_mg_per_kg * 0.03)),
        ):
            sample_rows.append(
                {
                    "sample_id": f"{arm.arm_id}-D1-{str(time_hr).replace('.', 'p')}",
                    "arm_id": arm.arm_id,
                    "animal_id": f"{arm.arm_id}-001",
                    "analyte": study.sampling.analyte,
                    "matrix": study.sampling.matrix,
                    "day": 1,
                    "time_hr": time_hr,
                    "concentration_ng_ml": round(concentration, 3),
                }
            )
    return {
        "study": study_spec_to_mapping(study),
        "bioanalysis_rows": sample_rows,
        "cmc": cmc_templates["cmc"],
        "cmc_batch_results": cmc_templates["batch_results"],
        "cmc_stability_results_rows": cmc_templates["stability_results_rows"],
        "cmc_references": cmc_templates["cmc_references"],
    }


def _build_randomization(spec: PreclinicalStudySpec, *, seed: int) -> dict[str, Any]:
    rng = Random(seed)
    assignments: list[dict[str, Any]] = []

    for arm in spec.arms:
        female_target = arm.n_animals // 2
        male_target = arm.n_animals - female_target
        sexes = ["F"] * female_target + ["M"] * male_target
        if arm.sex.lower() == "female":
            sexes = ["F"] * arm.n_animals
        elif arm.sex.lower() == "male":
            sexes = ["M"] * arm.n_animals
        rng.shuffle(sexes)

        for idx in range(1, arm.n_animals + 1):
            assignments.append(
                {
                    "animal_id": f"{arm.arm_id}-{idx:03d}",
                    "arm_id": arm.arm_id,
                    "sex": sexes[idx - 1],
                    "dose_mg_per_kg": arm.dose_mg_per_kg,
                    "route": arm.route,
                }
            )

    rng.shuffle(assignments)
    return {
        "seed": seed,
        "assignment_count": len(assignments),
        "assignments": assignments,
    }


def _plan_recommendations(
    *,
    glp: dict[str, Any],
    schedule: dict[str, Any],
) -> list[str]:
    recommendations: list[str] = []

    failed_items = glp.get("failed_items")
    if isinstance(failed_items, list) and failed_items:
        recommendations.append(
            "Resolve all GLP checklist failures before first dosing day."
        )

    max_events_day = schedule.get("max_events_single_day")
    if isinstance(max_events_day, int) and max_events_day > 60:
        recommendations.append(
            "Daily workload is dense; split sampling windows or increase technician coverage."
        )

    event_counts = _mapping(schedule.get("event_counts"))
    sample_events = int(event_counts.get("sample", 0))
    if sample_events > 300:
        recommendations.append(
            "Consider staggered sample processing batches to protect bioanalytical turnaround."
        )

    if not recommendations:
        recommendations.append(
            "Plan is operationally balanced for baseline execution; proceed to site readiness checks."
        )

    return recommendations


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}
