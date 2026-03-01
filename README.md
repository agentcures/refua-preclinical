# refua-preclinical

`refua-preclinical` adds operational preclinical R&D workflows to Refua:

- GLP tox/pharmacology study planning
- In vivo execution scheduling
- Bioanalytical ETL/QC/group summaries/NCA-like metrics
- CMC workflows: formulation/process development, batch records, stability studies, release criteria evaluation

The package is designed for direct integration into `refua-studio` and `refua-deploy`.

## What It Provides

- Typed study specs for repeat-dose tox/pharmacology programs.
- GLP readiness scoring/checklist (QA, protocol approval, CSV, chain-of-custody, archival).
- Calendar-ready in vivo schedules for dosing, observations, sampling, and necropsy.
- Bioanalytical pipeline:
  - row-level validation and QC flags
  - BLQ tracking vs LLOQ
  - grouped concentration summaries (mean/SD/CV)
  - AUC-last/Cmax/Tmax by arm/analyte
- CMC toolkit:
  - formulation and process development planning
  - electronic batch record templates
  - stability sample scheduling and trend analysis
  - release criteria assessment (pass/hold decisions)
- CLI + Python API.

## Install

```bash
cd refua-preclinical
pip install -e .
```

## CLI Quickstart

Write starter config:

```bash
refua-preclinical init-config --output examples/default_study.json
```

Build a study plan:

```bash
refua-preclinical plan \
  --config examples/default_study.json \
  --output artifacts/plan.json \
  --markdown artifacts/plan.md
```

Build the in vivo schedule:

```bash
refua-preclinical schedule \
  --config examples/default_study.json \
  --output artifacts/schedule.json
```

Run bioanalysis from sample rows (JSON/CSV):

```bash
refua-preclinical bioanalysis \
  --config examples/default_study.json \
  --samples artifacts/samples.json \
  --lloq 1.0 \
  --output artifacts/bioanalysis.json
```

Run full workup:

```bash
refua-preclinical workup \
  --config examples/default_study.json \
  --samples artifacts/samples.json \
  --output artifacts/workup.json
```

Build a CMC plan:

```bash
refua-preclinical cmc-plan \
  --output artifacts/cmc_plan.json
```

Generate a batch record:

```bash
refua-preclinical batch-record \
  --batch-id BATCH-001 \
  --output artifacts/batch_record.json
```

Build a stability schedule:

```bash
refua-preclinical stability-plan \
  --batch-id BATCH-001 \
  --output artifacts/stability_plan.json
```

Evaluate release criteria:

```bash
refua-preclinical release-eval \
  --batch-results artifacts/batch_results.json \
  --stability-results artifacts/stability_results.json \
  --output artifacts/release_eval.json
```

## Python API

```python
from refua_preclinical import (
    build_formulation_process_plan,
    build_in_vivo_schedule,
    build_stability_study_plan,
    build_study_plan,
    build_workup,
    default_study_spec,
    generate_batch_record,
)

study = default_study_spec()
plan = build_study_plan(study, seed=11)
schedule = build_in_vivo_schedule(study)
workup = build_workup(study)
cmc_plan = build_formulation_process_plan()
batch_record = generate_batch_record(batch_id="BATCH-001")
stability_plan = build_stability_study_plan(batch_ids=["BATCH-001"])
```

## Research Basis (Current as of March 2026)

The defaults/checks are intentionally aligned with recent primary guidance and standards.

1. FDA (April 10, 2025): plan to phase out animal testing requirements for some programs and increase NAM/model use.
   https://www.fda.gov/news-events/press-announcements/fda-announces-plan-phase-out-animal-testing-requirement-monoclonal-antibodies-and-other-drugs
2. EMA/ICH M10 (effective in EU from Jan 2023): bioanalytical method validation framework.
   https://www.ema.europa.eu/en/m10-bioanalytical-method-validation-scientific-guideline
3. FDA Study Data Technical Conformance Guide (December 2025): submission-facing data format expectations.
   https://www.fda.gov/regulatory-information/search-fda-guidance-documents/study-data-technical-conformance-guide-technical-specifications-document
4. OECD GLP Advisory Document No. 24 (Nov 2024): GLP and IT security.
   https://www.oecd.org/en/publications/advisory-document-of-the-working-group-on-good-laboratory-practice-on-position-paper-on-good-laboratory-practice-and-it-security_90f42001-en.html
5. ARRIVE resources update (Nov 2024): Essential 10 reporting and study design hygiene.
   https://arriveguidelines.org/resources/author-and-reviewer-resource-centre
6. EMA/ICH S5(R3) (2023): reproductive/developmental toxicity modernization.
   https://www.ema.europa.eu/en/ich-s5-r3-guideline-detection-toxicity-reproduction-human-medicinal-products-scientific-guideline
7. NIH statement (July 7, 2025): prioritization of human-based research technologies.
   https://www.nih.gov/about-nih/who-we-are/nih-director/statements/nih-prioritize-human-based-research-technologies
8. CDISC standards development page (accessed 2026): ongoing SEND evolution workstreams.
   https://www.cdisc.org/standards/develop

## Notes

- This package supports planning/operations and data processing; it does not establish efficacy.
- Regulatory expectations are jurisdiction- and program-dependent.
