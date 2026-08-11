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

                "reliability":
                    source.get(
                        "reliability"
                    ),

                "freshness_score":
                    source.get(
                        "freshness_score"
                    ),
            })

        return normalized

    # =====================================================
    # SOURCE SCORING
    # =====================================================

    def _score_source(
        self,
        source: Dict[str, Any]
    ) -> Dict[str, Any]:

        authority = self._authority_score(
            source
        )

        transparency = self._transparency_score(
            source
        )

        primary_score = (
            100
            if source.get("primary")
            else 0
        )

        freshness = self._freshness_score(
            source
        )

        independence = (
            100
            if source.get("independent")
            else 50
        )

        duplication_risk = (
            20
            if self._is_social_source(source)
            else 0
        )

        if not source.get("author"):
            duplication_risk += 5

        total = (
            authority * 0.30
            + transparency * 0.15
            + primary_score * 0.20
            + freshness * 0.10
            + independence * 0.10
            + (100 - duplication_risk) * 0.15
        )

        total = int(
            max(
                0,
                min(
                    total,
                    100
                )
            )
        )

        return {
            **source,

            "authority_score":
                authority,

            "transparency_score":
                transparency,

            "primary_source_score":
                primary_score,

            "freshness_score":
                freshness,

            "independence_score":
                independence,

            "duplication_risk":
                duplication_risk,

            "quality_score":
                total,

            "classification":
                self._classification(
                    total
                ),
        }

    # =====================================================
    # AUTHORITY
    # =====================================================

    def _authority_score(
        self,
        source: Dict[str, Any]
    ) -> int:

        explicit = source.get(
            "authority"
        )

        if explicit is not None:

            try:
                value = float(
                    explicit
                )

                if value > 0:
                    return int(
                        max(
                            0,
                            min(
                                value,
                                100
                            )
                        )
                    )

            except (
                TypeError,
                ValueError
            ):
                pass

        source_type = str(
            source.get(
                "type",
                "UNKNOWN"
            )
        ).upper()

        score = self.source_type_weights.get(
            source_type,
            25
        )

        if source.get("official"):
            score = max(
                score,
                90
            )

        domain = str(
            source.get(
                "domain",
                ""
            )
        ).lower()

        if any(
            keyword in domain
            for keyword in self.official_keywords
        ):
            score += 5

        return min(
            score,
            100
        )

    # =====================================================
    # TRANSPARENCY
    # =====================================================

    def _transparency_score(
        self,
        source: Dict[str, Any]
    ) -> int:

        score = 35

        if source.get("name"):
            score += 15

        if source.get("author"):
            score += 15

        if source.get("published_at"):
            score += 15

        if source.get("url"):
            score += 10

        if source.get("text"):
            score += 10

        return min(
            score,
            100
        )

    # =====================================================
    # FRESHNESS
    # =====================================================

    def _freshness_score(
        self,
        source: Dict[str, Any]
    ) -> int:

        if source.get(
            "freshness_score"
        ) is not None:

            try:
                return int(
                    max(
                        0,
                        min(
                            int(
                                source[
                                    "freshness_score"
                                ]
                            ),
                            100
                        )
                    )
                )

            except (
                TypeError,
                ValueError
            ):
                pass

        if source.get(
            "published_at"
        ):
            return 80

        return 50
