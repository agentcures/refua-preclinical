"""Bioanalytical ETL and QC helpers."""

from __future__ import annotations

import math
from typing import Any

from .models import BioanalyticalSample, PreclinicalStudySpec

_REQUIRED_SAMPLE_FIELDS = {
    "sample_id",
    "arm_id",
    "animal_id",
    "analyte",
    "matrix",
    "day",
    "time_hr",
    "concentration_ng_ml",
}


def run_bioanalytical_pipeline(
    study: PreclinicalStudySpec,
    rows: list[dict[str, Any]],
    *,
    lloq_ng_ml: float = 1.0,
) -> dict[str, Any]:
    samples: list[BioanalyticalSample] = []
    flags: list[dict[str, Any]] = []
    missing_required = 0

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            missing_required += 1
            flags.append({"row": index, "flag": "invalid_row_type"})
            continue

        missing_keys = sorted(_REQUIRED_SAMPLE_FIELDS - set(row.keys()))
        if missing_keys:
            missing_required += 1
            flags.append(
                {
                    "row": index,
                    "flag": "missing_required_fields",
                    "fields": missing_keys,
                }
            )
            continue

        try:
            concentration_raw = row.get("concentration_ng_ml")
            concentration = (
                None if concentration_raw in (None, "") else float(concentration_raw)
            )
            sample = BioanalyticalSample(
                sample_id=str(row["sample_id"]),
                arm_id=str(row["arm_id"]),
                animal_id=str(row["animal_id"]),
                analyte=str(row["analyte"]),
                matrix=str(row["matrix"]),
                day=int(row["day"]),
                time_hr=float(row["time_hr"]),
                concentration_ng_ml=concentration,
            )
        except (TypeError, ValueError) as exc:
            flags.append(
                {
                    "row": index,
                    "flag": "type_conversion_error",
                    "error": str(exc),
                }
            )
            continue

        if sample.concentration_ng_ml is None:
            flags.append({"row": index, "flag": "missing_concentration"})
        elif sample.concentration_ng_ml < 0:
            flags.append({"row": index, "flag": "negative_concentration"})
        elif sample.concentration_ng_ml < lloq_ng_ml:
            flags.append(
                {
                    "row": index,
                    "flag": "below_lloq",
                    "lloq_ng_ml": lloq_ng_ml,
                    "value": sample.concentration_ng_ml,
                }
            )

        samples.append(sample)

    grouped = _group_summary(samples, lloq_ng_ml=lloq_ng_ml)
    nca = _nca_summary(grouped)

    total_rows = len(rows)
    flag_count = len(flags)
    blq_count = sum(1 for item in flags if item.get("flag") == "below_lloq")

    return {
        "study_id": study.study_id,
        "input_rows": total_rows,
        "parsed_rows": len(samples),
        "missing_required_rows": missing_required,
        "lloq_ng_ml": lloq_ng_ml,
        "flags": flags,
        "flag_count": flag_count,
        "blq_count": blq_count,
        "blq_rate": (float(blq_count / total_rows) if total_rows > 0 else None),
        "grouped_summary": grouped,
        "nca": nca,
    }


def _group_summary(
    samples: list[BioanalyticalSample], *, lloq_ng_ml: float
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, float], list[float]] = {}
    blq_counts: dict[tuple[str, str, float], int] = {}

    for sample in samples:
        key = (sample.arm_id, sample.analyte, float(sample.time_hr))
        grouped.setdefault(key, [])
        blq_counts.setdefault(key, 0)
        value = sample.concentration_ng_ml
        if value is None:
            continue
        grouped[key].append(value)
        if value < lloq_ng_ml:
            blq_counts[key] += 1

    rows: list[dict[str, Any]] = []
    for key in sorted(grouped.keys(), key=lambda item: (item[0], item[1], item[2])):
        values = grouped[key]
        n = len(values)
        mean = (sum(values) / n) if n else None
        sd = _stdev(values) if n > 1 else None
        cv = (
            float(sd / mean * 100.0)
            if (sd is not None and mean not in (None, 0.0))
            else None
        )
        rows.append(
            {
                "arm_id": key[0],
                "analyte": key[1],
                "time_hr": key[2],
                "n": n,
                "mean_concentration_ng_ml": mean,
                "sd_concentration_ng_ml": sd,
                "cv_percent": cv,
                "n_blq": blq_counts.get(key, 0),
            }
        )
    return rows


def _nca_summary(grouped_summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_arm_analyte: dict[tuple[str, str], list[tuple[float, float]]] = {}

    for row in grouped_summary:
        mean = row.get("mean_concentration_ng_ml")
        if mean is None:
            continue
        key = (str(row.get("arm_id")), str(row.get("analyte")))
        by_arm_analyte.setdefault(key, []).append((float(row["time_hr"]), float(mean)))

    results: list[dict[str, Any]] = []
    for (arm_id, analyte), points in sorted(by_arm_analyte.items()):
        ordered = sorted(points, key=lambda item: item[0])
        auc = 0.0
        cmax = 0.0
        tmax = 0.0
        for idx, (time_hr, conc) in enumerate(ordered):
            if conc > cmax:
                cmax = conc
                tmax = time_hr
            if idx == 0:
                continue
            prev_time, prev_conc = ordered[idx - 1]
            delta_t = time_hr - prev_time
            auc += 0.5 * (conc + prev_conc) * delta_t

        results.append(
            {
                "arm_id": arm_id,
                "analyte": analyte,
                "auc_last_ng_h_per_ml": auc,
                "cmax_ng_ml": cmax,
                "tmax_hr": tmax,
                "timepoints": len(ordered),
            }
        )

    return results


def _stdev(values: list[float]) -> float | None:
    n = len(values)
    if n < 2:
        return None
    mean = sum(values) / n
    variance = sum((value - mean) ** 2 for value in values) / (n - 1)
    if variance < 0:
        return None
    return math.sqrt(variance)
