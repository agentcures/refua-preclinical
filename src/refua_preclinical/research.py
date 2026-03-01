"""Curated references used by refua-preclinical defaults and checks."""

from __future__ import annotations

from typing import Any


def latest_preclinical_references() -> list[dict[str, Any]]:
    """Return curated references for recent preclinical standards and direction."""

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


def latest_cmc_references() -> list[dict[str, Any]]:
    """Return curated CMC references grounded in current ICH/FDA/EMA guidance."""

    return [
        {
            "topic": "Quality by Design",
            "title": "Q8(R2) Pharmaceutical Development",
            "organization": "ICH",
            "date": "2009-08",
            "status": "Final",
            "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/q8r2-pharmaceutical-development",
            "relevance": "Framework for linking formulation and process design decisions to product quality objectives.",
        },
        {
            "topic": "Quality Risk Management",
            "title": "Q9(R1) Quality Risk Management",
            "organization": "ICH",
            "date": "2023-05",
            "status": "Final",
            "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/q9r1-quality-risk-management",
            "relevance": "Supports risk ranking/control logic across CQAs, CPPs, IPCs, and release decisions.",
        },
        {
            "topic": "Pharmaceutical Quality System",
            "title": "Q10 Pharmaceutical Quality System",
            "organization": "ICH",
            "date": "2009-04",
            "status": "Final",
            "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/q10-pharmaceutical-quality-system",
            "relevance": "Basis for lifecycle controls, CAPA, change management, and management review expectations.",
        },
        {
            "topic": "Drug Substance Development",
            "title": "Q11 Development and Manufacture of Drug Substances",
            "organization": "ICH",
            "date": "2012-11",
            "status": "Final",
            "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/q11-development-and-manufacture-drug-substances-chemical-entities-and-biotechnologicalbiological",
            "relevance": "Guides material and process understanding for control strategies that begin at drug substance.",
        },
        {
            "topic": "Lifecycle Management",
            "title": "Q12 Technical and Regulatory Considerations for Pharmaceutical Product Lifecycle Management",
            "organization": "ICH",
            "date": "2020-08",
            "status": "Final",
            "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/q12-technical-and-regulatory-considerations-pharmaceutical-product-lifecycle-management",
            "relevance": "Supports established conditions, post-approval change pathways, and comparability planning.",
        },
        {
            "topic": "Continuous Manufacturing",
            "title": "Q13 Continuous Manufacturing of Drug Substances and Drug Products",
            "organization": "ICH",
            "date": "2023-03",
            "status": "Final",
            "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/q13-continuous-manufacturing-drug-substances-and-drug-products",
            "relevance": "Informs process monitoring and control strategy fields for modern process platforms.",
        },
        {
            "topic": "Analytical Lifecycle",
            "title": "Q2(R2) Validation of Analytical Procedures",
            "organization": "ICH",
            "date": "2024-03",
            "status": "Final",
            "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/q2r2-validation-analytical-procedures",
            "relevance": "Defines analytical performance expectations for release and stability methods.",
        },
        {
            "topic": "Analytical Procedure Development",
            "title": "Q14 Analytical Procedure Development",
            "organization": "ICH",
            "date": "2024-03",
            "status": "Final",
            "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/q14-analytical-procedure-development",
            "relevance": "Supports method development context tied to release criteria and stability methods.",
        },
        {
            "topic": "Stability Testing",
            "title": "ICH Q1A(R2) Stability testing of new drug substances and products",
            "organization": "EMA / ICH",
            "date": "2003-02",
            "status": "Final",
            "url": "https://www.ema.europa.eu/en/ich-q1a-r2-stability-testing-new-drug-substances-products-scientific-guideline",
            "relevance": "Foundation for long-term/accelerated conditions and timepoint-driven shelf-life assessment.",
        },
        {
            "topic": "Process Validation",
            "title": "Process Validation: General Principles and Practices",
            "organization": "U.S. FDA",
            "date": "2011-01",
            "status": "Final",
            "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/process-validation-general-principles-and-practices",
            "relevance": "Defines process design, PPQ, and continued process verification lifecycle expectations.",
        },
        {
            "topic": "Emerging CMC Work",
            "title": "ICH Q1: Stability Testing of Drug Substances and Drug Products (Step 2 draft)",
            "organization": "EMA / ICH",
            "date": "2025-04",
            "status": "Draft",
            "url": "https://www.ema.europa.eu/en/ich-q1-stability-testing-drug-substances-drug-products-scientific-guideline",
            "relevance": "Signals near-term harmonization updates that may affect stability program design assumptions.",
        },
    ]
