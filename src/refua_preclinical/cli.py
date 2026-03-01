"""CLI for refua-preclinical."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import __version__
from .cmc import (
    assess_stability_results,
    build_formulation_process_plan,
    build_stability_study_plan,
    default_cmc_templates,
    evaluate_release_criteria,
    generate_batch_record,
)
from .io import dump_json, load_mapping, load_rows
from .models import default_study_spec, study_spec_from_mapping, study_spec_to_mapping
from .planning import (
    build_study_plan,
    build_workup,
    default_templates,
    render_plan_markdown,
)
from .scheduler import build_in_vivo_schedule


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="refua-preclinical",
        description=(
            "GLP tox/pharmacology study planning, in vivo scheduling, and bioanalytical "
            "pipelines for Refua, with optional CMC workflows."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"refua-preclinical {__version__}"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init-config", help="Write starter study config JSON")
    init_parser.add_argument(
        "--output", required=True, type=Path, help="Output JSON path"
    )
    init_parser.set_defaults(handler=_cmd_init_config)

    templates_parser = sub.add_parser("templates", help="Print default templates JSON")
    templates_parser.add_argument(
        "--output", type=Path, default=None, help="Optional output JSON"
    )
    templates_parser.set_defaults(handler=_cmd_templates)

    cmc_templates_parser = sub.add_parser(
        "cmc-templates",
        help="Print default CMC templates JSON",
    )
    cmc_templates_parser.add_argument(
        "--output", type=Path, default=None, help="Optional output JSON"
    )
    cmc_templates_parser.set_defaults(handler=_cmd_cmc_templates)

    plan_parser = sub.add_parser("plan", help="Build preclinical plan from config")
    plan_parser.add_argument(
        "--config", required=True, type=Path, help="Study config JSON/YAML"
    )
    plan_parser.add_argument("--seed", type=int, default=7, help="Randomization seed")
    plan_parser.add_argument("--output", required=True, type=Path, help="Output JSON")
    plan_parser.add_argument(
        "--markdown", type=Path, default=None, help="Optional markdown report"
    )
    plan_parser.set_defaults(handler=_cmd_plan)

    schedule_parser = sub.add_parser(
        "schedule", help="Build in vivo schedule from config"
    )
    schedule_parser.add_argument(
        "--config", required=True, type=Path, help="Study config JSON/YAML"
    )
    schedule_parser.add_argument(
        "--output", required=True, type=Path, help="Output JSON"
    )
    schedule_parser.set_defaults(handler=_cmd_schedule)

    bio_parser = sub.add_parser("bioanalysis", help="Run bioanalytical pipeline")
    bio_parser.add_argument(
        "--config", required=True, type=Path, help="Study config JSON/YAML"
    )
    bio_parser.add_argument(
        "--samples", required=True, type=Path, help="Samples JSON/CSV"
    )
    bio_parser.add_argument("--lloq", type=float, default=1.0, help="LLOQ in ng/mL")
    bio_parser.add_argument("--output", required=True, type=Path, help="Output JSON")
    bio_parser.set_defaults(handler=_cmd_bioanalysis)

    workup_parser = sub.add_parser(
        "workup", help="Run full preclinical planning workup"
    )
    workup_parser.add_argument(
        "--config", required=True, type=Path, help="Study config JSON/YAML"
    )
    workup_parser.add_argument(
        "--samples", type=Path, default=None, help="Optional samples JSON/CSV"
    )
    workup_parser.add_argument(
        "--cmc-config", type=Path, default=None, help="Optional CMC config JSON/YAML"
    )
    workup_parser.add_argument(
        "--stability-results",
        type=Path,
        default=None,
        help="Optional stability results JSON/CSV",
    )
    workup_parser.add_argument(
        "--batch-results",
        type=Path,
        default=None,
        help="Optional batch release results JSON/CSV",
    )
    workup_parser.add_argument(
        "--batch-id",
        type=str,
        default="BATCH-001",
        help="CMC batch id for workup output",
    )
    workup_parser.add_argument("--seed", type=int, default=7, help="Randomization seed")
    workup_parser.add_argument("--lloq", type=float, default=1.0, help="LLOQ in ng/mL")
    workup_parser.add_argument("--output", required=True, type=Path, help="Output JSON")
    workup_parser.set_defaults(handler=_cmd_workup)

    cmc_plan_parser = sub.add_parser(
        "cmc-plan",
        help="Build formulation/process development plan",
    )
    cmc_plan_parser.add_argument(
        "--config", type=Path, default=None, help="Optional CMC config JSON/YAML"
    )
    cmc_plan_parser.add_argument(
        "--output", required=True, type=Path, help="Output JSON"
    )
    cmc_plan_parser.set_defaults(handler=_cmd_cmc_plan)

    batch_record_parser = sub.add_parser(
        "batch-record",
        help="Generate batch manufacturing record template",
    )
    batch_record_parser.add_argument(
        "--config", type=Path, default=None, help="Optional CMC config JSON/YAML"
    )
    batch_record_parser.add_argument(
        "--batch-id", required=True, type=str, help="Batch id"
    )
    batch_record_parser.add_argument(
        "--operator", type=str, default="TBD", help="Operator name"
    )
    batch_record_parser.add_argument(
        "--site", type=str, default="TBD", help="Manufacturing site"
    )
    batch_record_parser.add_argument(
        "--manufacture-date", type=str, default=None, help="ISO date"
    )
    batch_record_parser.add_argument(
        "--output", required=True, type=Path, help="Output JSON"
    )
    batch_record_parser.set_defaults(handler=_cmd_batch_record)

    stability_plan_parser = sub.add_parser(
        "stability-plan",
        help="Build stability sample schedule",
    )
    stability_plan_parser.add_argument(
        "--config", type=Path, default=None, help="Optional CMC config JSON/YAML"
    )
    stability_plan_parser.add_argument(
        "--batch-id",
        action="append",
        default=None,
        help="Batch id (repeat flag to add multiple batches)",
    )
    stability_plan_parser.add_argument(
        "--output", required=True, type=Path, help="Output JSON"
    )
    stability_plan_parser.set_defaults(handler=_cmd_stability_plan)

    stability_analyze_parser = sub.add_parser(
        "stability-analyze",
        help="Assess stability results against criteria and trends",
    )
    stability_analyze_parser.add_argument(
        "--results", required=True, type=Path, help="Results JSON/CSV"
    )
    stability_analyze_parser.add_argument(
        "--config", type=Path, default=None, help="Optional CMC config JSON/YAML"
    )
    stability_analyze_parser.add_argument(
        "--output", required=True, type=Path, help="Output JSON"
    )
    stability_analyze_parser.set_defaults(handler=_cmd_stability_analyze)

    release_eval_parser = sub.add_parser(
        "release-eval",
        help="Evaluate release criteria from batch results",
    )
    release_eval_parser.add_argument(
        "--batch-results",
        required=True,
        type=Path,
        help="Batch results JSON/CSV",
    )
    release_eval_parser.add_argument(
        "--config", type=Path, default=None, help="Optional CMC config JSON/YAML"
    )
    release_eval_parser.add_argument(
        "--stability-results",
        type=Path,
        default=None,
        help="Optional stability results JSON/CSV",
    )
    release_eval_parser.add_argument(
        "--output", required=True, type=Path, help="Output JSON"
    )
    release_eval_parser.set_defaults(handler=_cmd_release_eval)

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
        print(json.dumps(payload, indent=2))
        return 0

    dump_json(args.output, payload)
    print(f"Wrote templates: {Path(args.output).resolve()}")
    return 0


def _cmd_cmc_templates(args: argparse.Namespace) -> int:
    payload = default_cmc_templates()
    if args.output is None:
        print(json.dumps(payload, indent=2))
        return 0

    dump_json(args.output, payload)
    print(f"Wrote CMC templates: {Path(args.output).resolve()}")
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
    stability_results: list[dict[str, Any]] | None = None
    batch_results: dict[str, Any] | list[dict[str, Any]] | None = None
    if args.samples is not None:
        samples = load_rows(args.samples)
    if args.stability_results is not None:
        stability_payload = _load_payload(args.stability_results)
        if isinstance(stability_payload, list):
            stability_results = [
                dict(item) for item in stability_payload if isinstance(item, dict)
            ]
        elif isinstance(stability_payload, dict) and isinstance(
            stability_payload.get("rows"), list
        ):
            stability_results = [
                dict(item)
                for item in stability_payload["rows"]
                if isinstance(item, dict)
            ]
        else:
            raise ValueError(
                "stability_results payload must be a list of objects or {rows:[...]}."
            )
    if args.batch_results is not None:
        batch_payload = _load_payload(args.batch_results)
        if isinstance(batch_payload, dict):
            batch_results = dict(batch_payload)
        elif isinstance(batch_payload, list):
            batch_results = [
                dict(item) for item in batch_payload if isinstance(item, dict)
            ]
        else:
            raise ValueError(
                "batch_results payload must be an object or list of objects."
            )
    cmc_config = _load_cmc_config(args.cmc_config)
    payload = build_workup(
        spec,
        samples=samples,
        seed=int(args.seed),
        lloq_ng_ml=float(args.lloq),
        cmc_config=cmc_config,
        stability_results=stability_results,
        batch_results=batch_results,
        batch_id=str(args.batch_id),
    )
    dump_json(args.output, payload)
    print(f"Wrote workup: {Path(args.output).resolve()}")
    return 0


def _cmd_cmc_plan(args: argparse.Namespace) -> int:
    payload = build_formulation_process_plan(_load_cmc_config(args.config))
    dump_json(args.output, payload)
    print(f"Wrote CMC plan: {Path(args.output).resolve()}")
    return 0


def _cmd_batch_record(args: argparse.Namespace) -> int:
    payload = generate_batch_record(
        _load_cmc_config(args.config),
        batch_id=str(args.batch_id),
        operator=str(args.operator),
        site=str(args.site),
        manufacture_date=args.manufacture_date,
    )
    dump_json(args.output, payload)
    print(f"Wrote batch record: {Path(args.output).resolve()}")
    return 0


def _cmd_stability_plan(args: argparse.Namespace) -> int:
    batch_ids = args.batch_id if args.batch_id else None
    payload = build_stability_study_plan(
        _load_cmc_config(args.config),
        batch_ids=batch_ids,
    )
    dump_json(args.output, payload)
    print(f"Wrote stability plan: {Path(args.output).resolve()}")
    return 0


def _cmd_stability_analyze(args: argparse.Namespace) -> int:
    rows_payload = _load_payload(args.results)
    if isinstance(rows_payload, dict):
        rows_raw = rows_payload.get("rows", rows_payload.get("results"))
        if not isinstance(rows_raw, list):
            raise ValueError(
                "stability results object must include rows or results list."
            )
        rows = [dict(item) for item in rows_raw if isinstance(item, dict)]
    elif isinstance(rows_payload, list):
        rows = [dict(item) for item in rows_payload if isinstance(item, dict)]
    else:
        raise ValueError("stability results payload must be a list/object.")
    cmc = _load_cmc_config(args.config)
    criteria = None
    if cmc is not None:
        plan = build_formulation_process_plan(cmc)
        criteria = plan["cmc"]["release_criteria"]
    payload = assess_stability_results(rows, release_criteria=criteria)
    dump_json(args.output, payload)
    print(f"Wrote stability assessment: {Path(args.output).resolve()}")
    return 0


def _cmd_release_eval(args: argparse.Namespace) -> int:
    batch_payload = _load_payload(args.batch_results)
    if isinstance(batch_payload, dict):
        batch_results: dict[str, Any] | list[dict[str, Any]] = dict(batch_payload)
    elif isinstance(batch_payload, list):
        batch_results = [dict(item) for item in batch_payload if isinstance(item, dict)]
    else:
        raise ValueError("batch_results payload must be an object or list of objects.")

    cmc = _load_cmc_config(args.config)
    plan = build_formulation_process_plan(cmc)
    criteria = plan["cmc"]["release_criteria"]
    critical_quality_attributes = plan["cmc"]["critical_quality_attributes"]

    stability_assessment: dict[str, Any] | None = None
    if args.stability_results is not None:
        stability_payload = _load_payload(args.stability_results)
        if isinstance(stability_payload, dict):
            stability_rows_raw = stability_payload.get(
                "rows", stability_payload.get("results")
            )
            if not isinstance(stability_rows_raw, list):
                raise ValueError(
                    "stability_results object must include rows or results list."
                )
            stability_rows = [
                dict(item) for item in stability_rows_raw if isinstance(item, dict)
            ]
        elif isinstance(stability_payload, list):
            stability_rows = [
                dict(item) for item in stability_payload if isinstance(item, dict)
            ]
        else:
            raise ValueError("stability_results payload must be a list/object.")
        stability_assessment = assess_stability_results(
            stability_rows,
            release_criteria=criteria,
        )

    payload = evaluate_release_criteria(
        batch_results=batch_results,
        release_criteria=criteria,
        stability_assessment=stability_assessment,
        critical_quality_attributes=critical_quality_attributes,
    )
    dump_json(args.output, payload)
    print(f"Wrote release assessment: {Path(args.output).resolve()}")
    return 0


def _load_study(path: Path) -> Any:
    mapping = load_mapping(path)
    return study_spec_from_mapping(mapping)


def _load_cmc_config(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    mapping = load_mapping(path)
    nested = mapping.get("cmc")
    if isinstance(nested, dict):
        return dict(nested)
    return dict(mapping)


def _load_payload(path: Path) -> Any:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_rows(path)
    if suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if suffix in {".yml", ".yaml"}:
        try:
            import yaml  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "PyYAML is required for YAML input; install pyyaml or use JSON files."
            ) from exc
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    raise ValueError("Unsupported payload extension. Use .json, .yml, .yaml, or .csv")
