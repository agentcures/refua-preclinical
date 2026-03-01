"""Curated references used by refua-preclinical defaults and checks."""

from __future__ import annotations

from typing import Any


def latest_preclinical_references() -> list[dict[str, Any]]:
    """Return curated references for recent preclinical standards and research direction.

    This list intentionally focuses on primary guidance and standards sources.
    """

    return [
        {
            "topic": "Regulatory modernization",
            "title": "FDA announces plan to phase out animal testing requirement for monoclonal antibodies and other drugs",
            "organization": "U.S. FDA",
            "date": "2025-04-10",
            "url": "https://www.fda.gov/news-events/press-announcements/fda-announces-plan-phase-out-animal-testing-requirement-monoclonal-antibodies-and-other-drugs",
            "relevance": "Supports explicit planning hooks for NAMs and model-based evidence in preclinical packages.",
        },
        {
            "topic": "Bioanalysis",
            "title": "M10 Bioanalytical method validation - Scientific guideline",
            "organization": "EMA / ICH",
            "date": "2023-01-25",
            "url": "https://www.ema.europa.eu/en/m10-bioanalytical-method-validation-scientific-guideline",
            "relevance": "Basis for assay QC fields and validation-aware bioanalytical pipeline outputs.",
        },
        {
            "topic": "Study data standards",
            "title": "Study Data Technical Conformance Guide",
            "organization": "U.S. FDA",
            "date": "2025-12",
            "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/study-data-technical-conformance-guide-technical-specifications-document",
            "relevance": "Informs preclinical outputs designed for SEND-compatible submission readiness.",
        },
        {
            "topic": "GLP and data integrity",
            "title": "Advisory Document No. 24: Position Paper on GLP and IT Security",
            "organization": "OECD",
            "date": "2024-11-04",
            "url": "https://www.oecd.org/en/publications/advisory-document-of-the-working-group-on-good-laboratory-practice-on-position-paper-on-good-laboratory-practice-and-it-security_90f42001-en.html",
            "relevance": "Supports explicit computerized system validation and data-security checklist items.",
        },
        {
            "topic": "Reproducibility",
            "title": "ARRIVE Essential 10 compliance questionnaire and resources",
            "organization": "NC3Rs / ARRIVE",
            "date": "2024-11-08",
            "url": "https://arriveguidelines.org/resources/author-and-reviewer-resource-centre",
            "relevance": "Motivates built-in operational metadata for randomization, blinding, and reporting quality.",
        },
        {
            "topic": "DART guidance",
            "title": "ICH S5(R3) guideline on reproductive and developmental toxicity",
            "organization": "EMA / ICH",
            "date": "2023-04-25",
            "url": "https://www.ema.europa.eu/en/ich-s5-r3-guideline-detection-toxicity-reproduction-human-medicinal-products-scientific-guideline",
            "relevance": "Provides structure for study-type extensions toward developmental and reproductive toxicology.",
        },
        {
            "topic": "NAM adoption",
            "title": "NIH to prioritize human-based research technologies",
            "organization": "NIH",
            "date": "2025-07-07",
            "url": "https://www.nih.gov/about-nih/who-we-are/nih-director/statements/nih-prioritize-human-based-research-technologies",
            "relevance": "Supports dual-tracking of in vivo and NAM evidence in study-planning artifacts.",
        },
        {
            "topic": "Standards roadmap",
            "title": "CDISC standards in development (includes SEND implementation guide workstreams)",
            "organization": "CDISC",
            "date": "2026-01",
            "url": "https://www.cdisc.org/standards/develop",
            "relevance": "Supports keeping preclinical export fields aligned with upcoming SEND structure evolution.",
        },
    ]
