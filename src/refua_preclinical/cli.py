"""CLI for refua-preclinical."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from . import __version__
from .io import dump_json, load_mapping, load_rows
from .models import default_study_spec, study_spec_from_mapping, study_spec_to_mapping
from .planning import build_study_plan, build_workup, default_templates, render_plan_markdown
from .scheduler import build_in_vivo_schedule


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="refua-preclinical",
        description=(
            "GLP tox/pharmacology study planning, in vivo scheduling, and bioanalytical "
            "pipelines for Refua."
        ),
    )
    parser.add_argument("--version", action="version", version=f"refua-preclinical {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init-config", help="Write starter study config JSON")
    init_parser.add_argument("--output", required=True, type=Path, help="Output JSON path")
    init_parser.set_defaults(handler=_cmd_init_config)

    templates_parser = sub.add_parser("templates", help="Print default templates JSON")
    templates_parser.add_argument("--output", type=Path, default=None, help="Optional output JSON")
    templates_parser.set_defaults(handler=_cmd_templates)

    plan_parser = sub.add_parser("plan", help="Build preclinical plan from config")
    plan_parser.add_argument("--config", required=True, type=Path, help="Study config JSON/YAML")
    plan_parser.add_argument("--seed", type=int, default=7, help="Randomization seed")
    plan_parser.add_argument("--output", required=True, type=Path, help="Output JSON")
    plan_parser.add_argument("--markdown", type=Path, default=None, help="Optional markdown report")
    plan_parser.set_defaults(handler=_cmd_plan)

    schedule_parser = sub.add_parser("schedule", help="Build in vivo schedule from config")
    schedule_parser.add_argument("--config", required=True, type=Path, help="Study config JSON/YAML")
    schedule_parser.add_argument("--output", required=True, type=Path, help="Output JSON")
    schedule_parser.set_defaults(handler=_cmd_schedule)

    bio_parser = sub.add_parser("bioanalysis", help="Run bioanalytical pipeline")
    bio_parser.add_argument("--config", required=True, type=Path, help="Study config JSON/YAML")
    bio_parser.add_argument("--samples", required=True, type=Path, help="Samples JSON/CSV")
    bio_parser.add_argument("--lloq", type=float, default=1.0, help="LLOQ in ng/mL")
    bio_parser.add_argument("--output", required=True, type=Path, help="Output JSON")
    bio_parser.set_defaults(handler=_cmd_bioanalysis)

    workup_parser = sub.add_parser("workup", help="Run full preclinical planning workup")
    workup_parser.add_argument("--config", required=True, type=Path, help="Study config JSON/YAML")
    workup_parser.add_argument("--samples", type=Path, default=None, help="Optional samples JSON/CSV")
    workup_parser.add_argument("--seed", type=int, default=7, help="Randomization seed")
    workup_parser.add_argument("--lloq", type=float, default=1.0, help="LLOQ in ng/mL")
    workup_parser.add_argument("--output", required=True, type=Path, help="Output JSON")
    workup_parser.set_defaults(handler=_cmd_workup)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler")
    return int(handler(args))


def _cmd_init_config(args: argparse.Namespace) -> int:
    spec = default_study_spec()
    payload = study_spec_to_mapping(spec)
    dump_json(args.output, payload)
    print(f"Wrote starter config: {Path(args.output).resolve()}")
    return 0


def _cmd_templates(args: argparse.Namespace) -> int:
    payload = default_templates()
    if args.output is None:
        import json

        print(json.dumps(payload, indent=2))
        return 0

    dump_json(args.output, payload)
    print(f"Wrote templates: {Path(args.output).resolve()}")
    return 0


def _cmd_plan(args: argparse.Namespace) -> int:
    spec = _load_study(args.config)
    payload = build_study_plan(spec, seed=int(args.seed))
    dump_json(args.output, payload)
    print(f"Wrote plan: {Path(args.output).resolve()}")

    markdown_path = args.markdown
    if markdown_path is not None:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_plan_markdown(payload), encoding="utf-8")
        print(f"Wrote markdown: {markdown_path.resolve()}")
    return 0


def _cmd_schedule(args: argparse.Namespace) -> int:
    spec = _load_study(args.config)
    payload = build_in_vivo_schedule(spec)
    dump_json(args.output, payload)
    print(f"Wrote schedule: {Path(args.output).resolve()}")
    return 0


def _cmd_bioanalysis(args: argparse.Namespace) -> int:
    spec = _load_study(args.config)
    rows = load_rows(args.samples)
    from .bioanalytics import run_bioanalytical_pipeline

    payload = run_bioanalytical_pipeline(spec, rows, lloq_ng_ml=float(args.lloq))
    dump_json(args.output, payload)
    print(f"Wrote bioanalysis: {Path(args.output).resolve()}")
    return 0


def _cmd_workup(args: argparse.Namespace) -> int:
    spec = _load_study(args.config)
    samples: list[dict[str, Any]] | None = None
    if args.samples is not None:
        samples = load_rows(args.samples)
    payload = build_workup(
        spec,
        samples=samples,
        seed=int(args.seed),
        lloq_ng_ml=float(args.lloq),
    )
    dump_json(args.output, payload)
    print(f"Wrote workup: {Path(args.output).resolve()}")
    return 0


def _load_study(path: Path) -> Any:
    mapping = load_mapping(path)
    return study_spec_from_mapping(mapping)
