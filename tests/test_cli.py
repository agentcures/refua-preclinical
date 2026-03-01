from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from refua_preclinical.cli import main
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

    rc = main(["schedule", "--config", str(config_path), "--output", str(schedule_path)])
    assert rc == 0
    assert schedule_path.exists()

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
    assert plan["summary"]["total_animals"] > 0
    assert schedule["event_count"] > 0
