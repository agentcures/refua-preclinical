"""refua-preclinical public API."""

from __future__ import annotations

import tomllib
from importlib.metadata import version as _distribution_version
from pathlib import Path

from .bioanalytics import run_bioanalytical_pipeline
from .cmc import (
    assess_stability_results,
    build_formulation_process_plan,
    build_stability_study_plan,
    cmc_spec_from_mapping,
    default_cmc_spec,
    default_cmc_templates,
    evaluate_release_criteria,
    generate_batch_record,
)
from .glp import evaluate_glp_readiness
from .models import (
    BioanalyticalSample,
    GLPChecklistSpec,
    PreclinicalStudySpec,
    SamplingPlanSpec,
    StudyArmSpec,
    default_study_spec,
    study_spec_from_mapping,
    study_spec_to_mapping,
)
from .planning import build_study_plan, build_workup, default_templates, render_plan_markdown
from .research import latest_preclinical_references
from .scheduler import build_in_vivo_schedule


def _read_version_from_pyproject() -> str | None:
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    if not pyproject_path.exists():
        return None
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = data.get("project", {})
    version = project.get("version")
    if not version:
        return None
    return str(version)


def _resolve_version() -> str:
    local_version = _read_version_from_pyproject()
    if local_version is not None:
        return local_version
    return _distribution_version("refua-preclinical")


__version__ = _resolve_version()

__all__ = [
    "BioanalyticalSample",
    "GLPChecklistSpec",
    "PreclinicalStudySpec",
    "SamplingPlanSpec",
    "StudyArmSpec",
    "assess_stability_results",
    "build_in_vivo_schedule",
    "build_formulation_process_plan",
    "build_stability_study_plan",
    "build_study_plan",
    "build_workup",
    "cmc_spec_from_mapping",
    "default_cmc_spec",
    "default_cmc_templates",
    "default_study_spec",
    "default_templates",
    "evaluate_glp_readiness",
    "evaluate_release_criteria",
    "generate_batch_record",
    "latest_preclinical_references",
    "render_plan_markdown",
    "run_bioanalytical_pipeline",
    "study_spec_from_mapping",
    "study_spec_to_mapping",
    "__version__",
]
