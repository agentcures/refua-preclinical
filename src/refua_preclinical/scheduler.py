"""In vivo schedule generation for preclinical studies."""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from typing import Any

from .models import PreclinicalStudySpec


def build_in_vivo_schedule(spec: PreclinicalStudySpec) -> dict[str, Any]:
    start_date = _parse_start_date(spec.start_date)
    events: list[dict[str, Any]] = []
    index = 1

    for day in range(1, spec.duration_days + 1):
        for arm in spec.arms:
            events.append(
                {
                    "event_id": f"evt-{index:06d}",
                    "study_day": day,
                    "calendar_date": (start_date + timedelta(days=day - 1)).date().isoformat(),
                    "event_type": "observation",
                    "arm_id": arm.arm_id,
                    "time_offset_hr": 10.0,
                    "details": {
                        "check": "clinical_observation",
                        "severity_scale": "none_mild_moderate_severe",
                    },
                }
            )
            index += 1

    for day in sorted(set(spec.dosing_days)):
        if day < 1 or day > spec.duration_days:
            continue
        for arm in spec.arms:
            for dose_idx in range(arm.frequency_per_day):
                time_offset_hr = 8.0 + dose_idx * (12.0 / max(arm.frequency_per_day, 1))
                events.append(
                    {
                        "event_id": f"evt-{index:06d}",
                        "study_day": day,
                        "calendar_date": (start_date + timedelta(days=day - 1)).date().isoformat(),
                        "event_type": "dose",
                        "arm_id": arm.arm_id,
                        "time_offset_hr": round(time_offset_hr, 2),
                        "details": {
                            "treatment": arm.treatment,
                            "dose_mg_per_kg": arm.dose_mg_per_kg,
                            "route": arm.route,
                            "frequency_per_day": arm.frequency_per_day,
                        },
                    }
                )
                index += 1

    for day in sorted(set(spec.sampling.days)):
        if day < 1 or day > spec.duration_days:
            continue
        for arm in spec.arms:
            for time_hr in sorted(set(spec.sampling.timepoints_hr)):
                events.append(
                    {
                        "event_id": f"evt-{index:06d}",
                        "study_day": day,
                        "calendar_date": (start_date + timedelta(days=day - 1)).date().isoformat(),
                        "event_type": "sample",
                        "arm_id": arm.arm_id,
                        "time_offset_hr": float(time_hr),
                        "details": {
                            "matrix": spec.sampling.matrix,
                            "analyte": spec.sampling.analyte,
                            "stabilization_minutes": spec.sampling.stabilization_minutes,
                        },
                    }
                )
                index += 1

    events.append(
        {
            "event_id": f"evt-{index:06d}",
            "study_day": spec.duration_days,
            "calendar_date": (start_date + timedelta(days=spec.duration_days - 1)).date().isoformat(),
            "event_type": "necropsy",
            "arm_id": "all",
            "time_offset_hr": 12.0,
            "details": {
                "histopathology": True,
                "toxicokinetics": True,
            },
        }
    )

    events.sort(key=lambda item: (item["study_day"], item["time_offset_hr"], item["event_id"]))

    counts: dict[str, int] = {}
    by_day: dict[int, int] = {}
    for event in events:
        event_type = str(event.get("event_type"))
        counts[event_type] = counts.get(event_type, 0) + 1
        day = int(event["study_day"])
        by_day[day] = by_day.get(day, 0) + 1

    return {
        "study_id": spec.study_id,
        "start_date": start_date.date().isoformat(),
        "duration_days": spec.duration_days,
        "event_count": len(events),
        "event_counts": counts,
        "max_events_single_day": max(by_day.values()) if by_day else 0,
        "events": events,
        "arms": [asdict(arm) for arm in spec.arms],
    }


def _parse_start_date(value: str) -> datetime:
    text = str(value).strip()
    if not text:
        return datetime.now(UTC)
    try:
        # Accept full ISO timestamps or date-only values.
        if len(text) == 10:
            parsed = datetime.fromisoformat(text + "T00:00:00")
        else:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(UTC)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
