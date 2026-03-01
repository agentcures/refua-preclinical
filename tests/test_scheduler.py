from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from refua_preclinical.models import default_study_spec
from refua_preclinical.scheduler import build_in_vivo_schedule


def test_schedule_contains_dosing_sampling_and_necropsy_events() -> None:
    study = default_study_spec()
    payload = build_in_vivo_schedule(study)

    assert payload["event_count"] > 0
    counts = payload["event_counts"]
    assert counts.get("dose", 0) > 0
    assert counts.get("sample", 0) > 0
    assert counts.get("observation", 0) > 0

    event_types = {event["event_type"] for event in payload["events"]}
    assert "necropsy" in event_types
