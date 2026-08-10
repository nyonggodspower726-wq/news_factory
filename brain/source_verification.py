"""
AI NEWS FACTORY
SOURCE VERIFICATION & PROVENANCE ENGINE

Purpose
-------
Determine where information actually originated, how strong
the source is, whether multiple reports are independent, and
whether a claim is simply being repeated across the internet.

CORE PRINCIPLE
--------------
100 accounts repeating one claim does NOT equal
100 independent confirmations.

The engine attempts to distinguish:

    PRIMARY SOURCE
        ↓
    DIRECT REPORTING
        ↓
    INDEPENDENT SECONDARY REPORTING
        ↓
    AGGREGATOR
        ↓
    SOCIAL REPUBLISH
        ↓
    UNKNOWN

This engine does NOT decide whether something is true by
itself. It produces a provenance and confidence assessment
for the Fact Checker and Editor.

IMPORTANT
---------
Popularity ≠ credibility.

Virality ≠ verification.

Number of reposts ≠ number of independent sources.
"""

from typing import Any, Dict, List, Optional
from collections import defaultdict
from urllib.parse import urlparse
import re


class SourceVerificationEngine:

    def __init__(self):

        self.name = "Source Verification & Provenance Engine"
        self.version = "1.0.0"

        self.source_levels = {
            "PRIMARY": 100,
            "DIRECT_REPORTING": 85,
            "INDEPENDENT_SECONDARY": 70,
            "SPECIALIST": 65,
            "AGGREGATOR": 35,
            "SOCIAL_REPOST": 20,
            "UNKNOWN": 10
        }

        self.minimum_independent_sources = 2

    # =====================================================
    # MAIN
    # =====================================================

    def analyze(
        self,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not sources:

            return {
                "status": "NO_SOURCES",
                "confidence": 0,
                "sources": [],
                "independence": {
                    "independent_count": 0
                }
            }

        normalized = [
            self._normalize_source(
                source
            )
            for source in sources
        ]

        clusters = (
            self._build_provenance_clusters(
                normalized
            )
        )

        independent_sources = (
            self._find_independent_sources(
                normalized
            )
        )

        primary_sources = [
            source
            for source in normalized
            if source["classification"]
            == "PRIMARY"
        ]

        source_score = (
            self._calculate_source_score(
                normalized
            )
        )

        independence_score = (
            self._calculate_independence_score(
                independent_sources
            )
        )

        provenance_score = (
            self._calculate_provenance_score(
                normalized,
                clusters
            )
        )

        confidence = (
            self._overall_confidence(
                source_score,
                independence_score,
                provenance_score
            )
        )

        warnings = (
            self._generate_warnings(
                normalized,
                independent_sources,
                clusters
            )
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "ANALYZED",

            "source_count":
                len(normalized),

            "primary_source_count":
                len(primary_sources),

            "independent_source_count":
                len(independent_sources),

            "source_score":
                source_score,

            "independence_score":
                independence_score,

            "provenance_score":
                provenance_score,

            "confidence":
                confidence,

            "sources":
                normalized,

            "provenance_clusters":
                clusters,

            "warnings":
                warnings,

            "recommendation":
                self._recommendation(
                    confidence,
                    warnings
                )
        }

    # =====================================================
    # NORMALIZE
    # =====================================================

    def _normalize_source(
        self,
        source: Dict[str, Any]
    ) -> Dict[str, Any]:

        url = str(
            source.get(
                "url",
                ""
            )
        ).strip()

        domain = self._domain(
            url
        )

        source_type = str(
            source.get(
                "source_type",
                "UNKNOWN"
            )
        ).
