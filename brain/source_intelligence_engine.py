"""
AI NEWS FACTORY
SOURCE INTELLIGENCE ENGINE

Evaluates and organizes news sources before information is allowed
to influence the reporting pipeline.
"""

from typing import Any, Dict, List
from urllib.parse import urlparse
from difflib import SequenceMatcher
import re


class SourceIntelligenceEngine:

    def __init__(self):
        self.name = "Source Intelligence Engine"
        self.version = "1.0.0"

        self.source_type_weights = {
            "PRIMARY": 100,
            "OFFICIAL": 100,
            "GOVERNMENT": 95,
            "COURT": 95,
            "REGULATORY": 95,
            "ACADEMIC": 90,
            "ESTABLISHED_NEWS": 85,
            "WIRE": 85,
            "SPECIALIST_MEDIA": 80,
            "LOCAL_NEWS": 75,
            "EXPERT": 75,
            "BLOG": 50,
            "SOCIAL": 30,
            "USER_GENERATED": 20,
            "UNKNOWN": 25,
        }

        self.high_risk_source_types = {
            "UNKNOWN",
            "USER_GENERATED",
        }

        self.social_domains = {
            "twitter.com",
            "x.com",
            "facebook.com",
            "instagram.com",
            "tiktok.com",
            "youtube.com",
            "reddit.com",
            "threads.net",
        }

        self.official_keywords = {
            "gov",
            "government",
            "official",
            "ministry",
            "court",
            "police",
            "agency",
            "regulator",
            "university",
        }

    # =====================================================
    # MAIN
    # =====================================================

    def analyze(
        self,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        normalized = self._normalize_sources(sources)

        scored = [
            self._score_source(source)
            for source in normalized
        ]

        clusters = self._cluster_sources(scored)

        independence = self._independence_analysis(
            scored,
            clusters
        )

        source_chain = self._build_source_chain(
            scored
        )

        conflicts = self._detect_conflicts(
            scored
        )

        overall = self._overall_source_quality(
            scored,
            independence,
            conflicts
        )

        return {
            "engine": self.name,
            "version": self.version,
            "status": "ANALYZED",
            "source_count": len(scored),
            "sources": scored,
            "source_clusters": clusters,
            "independence": independence,
            "source_chain": source_chain,
            "conflicts": conflicts,
            "overall_quality": overall,
            "recommendation": self._recommendation(
                overall,
                conflicts,
                independence
            ),
        }

    # =====================================================
    # NORMALIZATION
    # =====================================================

    def _normalize_sources(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        if isinstance(sources, dict):
            sources = list(sources.values())

        if not isinstance(sources, list):
            return []

        normalized = []

        for index, source in enumerate(sources):

            if isinstance(source, str):
                source = {
                    "url": source
                }

            if not isinstance(source, dict):
                continue

            url = str(
                source.get("url", "")
            ).strip()

            title = str(
                source.get(
                    "title",
                    source.get(
                        "headline",
                        ""
                    )
                )
            ).strip()

            name = str(
                source.get(
                    "name",
                    source.get(
                        "publisher",
                        ""
                    )
                )
            ).strip()

            source_type = str(
                source.get(
                    "type",
                    source.get(
                        "source_type",
                        "UNKNOWN"
                    )
                )
            ).upper()

            domain = self._domain(url)

            if not name:
                name = (
                    domain
                    or "Unknown Source"
                )

            normalized.append({
                "id": source.get(
                    "id",
                    f"source_{index + 1}"
                ),

                "url": url,

                "title": title,

                "name": name,

                "domain": domain,

                "type": source_type,

                "published_at":
                    source.get(
                        "published_at"
                    ),

                "retrieved_at":
                    source.get(
                        "retrieved_at"
                    ),

                "author":
                    source.get(
                        "author"
                    ),

                "text":
                    source.get(
                        "text",
                        source.get(
                            "excerpt",
                            ""
                        )
                    ),

                "primary":
                    bool(
                        source.get(
                            "primary",
                            False
                        )
                    ),

                "official":
                    bool(
                        source.get(
                            "official",
                            False
                        )
                    ),

                "independent":
                    bool(
                        source.get(
                            "independent",
                            False
                        )
                    ),

                "authority":
                    source.get(
                        "authority",
                        0
                    ),

                "original_source":
                    source.get(
                        "original_source"
                    ),

                "
