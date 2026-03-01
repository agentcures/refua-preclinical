"""Typed models for refua-preclinical."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class StudyArmSpec:
    arm_id: str
    treatment: str
    dose_mg_per_kg: float
    route: str = "PO"
    frequency_per_day: int = 1
    n_animals: int = 8
    sex: str = "mixed"


@dataclass(slots=True)
class SamplingPlanSpec:
    analyte: str = "parent"
    matrix: str = "plasma"
    timepoints_hr: list[float] = field(
        default_factory=lambda: [0.5, 1.0, 2.0, 4.0, 8.0, 24.0]
    )
    days: list[int] = field(default_factory=lambda: [1, 14])
    stabilization_minutes: int = 30


@dataclass(slots=True)
class GLPChecklistSpec:
    statement_of_compliance: bool = True
    quality_assurance_unit: bool = True
    protocol_approved: bool = True
    sop_index: bool = True
    instrument_calibration_records: bool = True
    computer_system_validation: bool = True
    sample_chain_of_custody: bool = True
    raw_data_archival_plan: bool = True


@dataclass(slots=True)
class PreclinicalStudySpec:
    study_id: str
    title: str
    indication: str
    species: str
    strain: str
    modality: str = "small_molecule"
    study_type: str = "repeat_dose_toxicology"
    start_date: str = field(
        default_factory=lambda: datetime.now(UTC).date().isoformat()
    )
    duration_days: int = 28
    dosing_days: list[int] = field(default_factory=lambda: list(range(1, 15)))
    objectives: list[str] = field(
        default_factory=lambda: [
            "Establish toxicokinetic exposure over multiple dose levels",
            "Characterize dose-limiting toxicity and reversibility",
        ]
    )
    arms: list[StudyArmSpec] = field(default_factory=list)
    sampling: SamplingPlanSpec = field(default_factory=SamplingPlanSpec)
    glp: GLPChecklistSpec = field(default_factory=GLPChecklistSpec)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BioanalyticalSample:
    sample_id: str
    arm_id: str
    animal_id: str
    analyte: str
    matrix: str
    day: int
    time_hr: float
    concentration_ng_ml: float | None


def default_study_spec() -> PreclinicalStudySpec:
    return PreclinicalStudySpec(
        study_id="refua-preclinical-demo",
        title="28-day rat repeat-dose tox + TK",
        indication="Oncology",
        species="Rat",
        strain="Sprague-Dawley",
        modality="small_molecule",
        study_type="repeat_dose_toxicology",
        duration_days=28,
        dosing_days=list(range(1, 15)),
        arms=[
            StudyArmSpec(
                arm_id="vehicle",
                treatment="vehicle_control",
                dose_mg_per_kg=0.0,
                route="PO",
                n_animals=10,
            ),
            StudyArmSpec(
                arm_id="low",
                treatment="rx-001",
                dose_mg_per_kg=10.0,
                route="PO",
                n_animals=10,
            ),
            StudyArmSpec(
                arm_id="mid",
                treatment="rx-001",
                dose_mg_per_kg=30.0,
                route="PO",
                n_animals=10,
            ),
            StudyArmSpec(
                arm_id="high",
                treatment="rx-001",
                dose_mg_per_kg=100.0,
                route="PO",
                n_animals=10,
            ),
        ],
    )


def study_spec_to_mapping(spec: PreclinicalStudySpec) -> dict[str, Any]:
    return asdict(spec)


def study_spec_from_mapping(data: dict[str, Any]) -> PreclinicalStudySpec:
    if not isinstance(data, dict):
        raise ValueError("Study config must be a JSON/YAML object")

    default = default_study_spec()

    study_id = _required_str(data.get("study_id"), "study_id")
    title = _required_str(data.get("title"), "title")
    indication = _required_str(data.get("indication"), "indication")
    species = _required_str(data.get("species"), "species")
    strain = _required_str(data.get("strain"), "strain")

    arms_raw = data.get("arms")
    if not isinstance(arms_raw, list) or not arms_raw:
        raise ValueError("arms must be a non-empty list")
    arms: list[StudyArmSpec] = []
    for index, item in enumerate(arms_raw):
        if not isinstance(item, dict):
            raise ValueError(f"arms[{index}] must be an object")
        arm = StudyArmSpec(
            arm_id=_required_str(item.get("arm_id"), f"arms[{index}].arm_id"),
            treatment=_required_str(item.get("treatment"), f"arms[{index}].treatment"),
            dose_mg_per_kg=_required_float(
                item.get("dose_mg_per_kg"), f"arms[{index}].dose_mg_per_kg"
            ),
            route=str(item.get("route", "PO") or "PO"),
            frequency_per_day=_required_int(
                item.get("frequency_per_day", 1),
                f"arms[{index}].frequency_per_day",
                minimum=1,
            ),
            n_animals=_required_int(
                item.get("n_animals", 8), f"arms[{index}].n_animals", minimum=1
            ),
            sex=str(item.get("sex", "mixed") or "mixed"),
        )
        arms.append(arm)

    dosing_days = _coerce_int_list(
        data.get("dosing_days", default.dosing_days),
        field_name="dosing_days",
        minimum=1,
    )
    if not dosing_days:
        raise ValueError("dosing_days must include at least one day")

    sampling_raw = data.get("sampling", {})
    if sampling_raw is None:
        sampling_raw = {}
    if not isinstance(sampling_raw, dict):
        raise ValueError("sampling must be an object")
    sampling = SamplingPlanSpec(
        analyte=str(
            sampling_raw.get("analyte", default.sampling.analyte)
            or default.sampling.analyte
        ),
        matrix=str(
            sampling_raw.get("matrix", default.sampling.matrix)
            or default.sampling.matrix
        ),
        timepoints_hr=_coerce_float_list(
            sampling_raw.get("timepoints_hr", default.sampling.timepoints_hr),
            field_name="sampling.timepoints_hr",
            minimum=0.0,
        ),
        days=_coerce_int_list(
            sampling_raw.get("days", default.sampling.days),
            field_name="sampling.days",
            minimum=1,
        ),
        stabilization_minutes=_required_int(
            sampling_raw.get(
                "stabilization_minutes", default.sampling.stabilization_minutes
            ),
            "sampling.stabilization_minutes",
            minimum=0,
        ),
    )

    glp_raw = data.get("glp", {})
    if glp_raw is None:
        glp_raw = {}
    if not isinstance(glp_raw, dict):
        raise ValueError("glp must be an object")
    glp_default = default.glp
    glp = GLPChecklistSpec(
        statement_of_compliance=bool(
            glp_raw.get("statement_of_compliance", glp_default.statement_of_compliance)
        ),
        quality_assurance_unit=bool(
            glp_raw.get("quality_assurance_unit", glp_default.quality_assurance_unit)
        ),
        protocol_approved=bool(
            glp_raw.get("protocol_approved", glp_default.protocol_approved)
        ),
        sop_index=bool(glp_raw.get("sop_index", glp_default.sop_index)),
        instrument_calibration_records=bool(
            glp_raw.get(
                "instrument_calibration_records",
                glp_default.instrument_calibration_records,
            )
        ),
        computer_system_validation=bool(
            glp_raw.get(
                "computer_system_validation", glp_default.computer_system_validation
            )
        ),
        sample_chain_of_custody=bool(
            glp_raw.get("sample_chain_of_custody", glp_default.sample_chain_of_custody)
        ),
        raw_data_archival_plan=bool(
            glp_raw.get("raw_data_archival_plan", glp_default.raw_data_archival_plan)
        ),
    )

    objectives_raw = data.get("objectives", default.objectives)
    if not isinstance(objectives_raw, list):
        raise ValueError("objectives must be a list")
    objectives = [str(item).strip() for item in objectives_raw if str(item).strip()]
    if not objectives:
        objectives = list(default.objectives)

    metadata = data.get("metadata", {})
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be an object")

    spec = PreclinicalStudySpec(
        study_id=study_id,
        title=title,
        indication=indication,
        species=species,
        strain=strain,
        modality=str(data.get("modality", default.modality) or default.modality),
        study_type=str(
            data.get("study_type", default.study_type) or default.study_type
        ),
        start_date=str(
            data.get("start_date", default.start_date) or default.start_date
        ),
        duration_days=_required_int(
            data.get("duration_days", default.duration_days), "duration_days", minimum=1
        ),
        dosing_days=sorted(set(dosing_days)),
        objectives=objectives,
        arms=arms,
        sampling=sampling,
        glp=glp,
        metadata=dict(metadata),
    )
    return spec


def _required_str(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} must be non-empty")
    return text


def _required_int(value: Any, field_name: str, *, minimum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer") from exc
    if parsed < minimum:
        raise ValueError(f"{field_name} must be >= {minimum}")
    return parsed


def _required_float(value: Any, field_name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number") from exc
    return parsed


def _coerce_int_list(value: Any, *, field_name: str, minimum: int) -> list[int]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    out: list[int] = []
    for idx, item in enumerate(value):
        out.append(_required_int(item, f"{field_name}[{idx}]", minimum=minimum))
    return out


def _coerce_float_list(value: Any, *, field_name: str, minimum: float) -> list[float]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    out: list[float] = []
    for idx, item in enumerate(value):
        numeric = _required_float(item, f"{field_name}[{idx}]")
        if numeric < minimum:
            raise ValueError(f"{field_name}[{idx}] must be >= {minimum}")
        out.append(numeric)
    return out
