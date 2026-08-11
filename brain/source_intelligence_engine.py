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
    # =====================================================
    # CLUSTERING
    # =====================================================

    def _cluster_sources(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        clusters = []

        for source in sources:

            placed = False

            for cluster in clusters:

                representative = (
                    cluster["sources"][0]
                )

                similarity = (
                    self._text_similarity(
                        source.get(
                            "title",
                            ""
                        ),
                        representative.get(
                            "title",
                            ""
                        )
                    )
                )

                same_original = (
                    bool(
                        source.get(
                            "original_source"
                        )
                    )
                    and
                    source.get(
                        "original_source"
                    )
                    ==
                    representative.get(
                        "original_source"
                    )
                )

                same_domain = (
                    bool(
                        source.get(
                            "domain"
                        )
                    )
                    and
                    source.get(
                        "domain"
                    )
                    ==
                    representative.get(
                        "domain"
                    )
                )

                if (
                    similarity >= 0.45
                    or same_original
                    or (
                        same_domain
                        and similarity >= 0.30
                    )
                ):

                    cluster[
                        "sources"
                    ].append(
                        source
                    )

                    placed = True
                    break

            if not placed:

                clusters.append({
                    "cluster_id":
                        f"cluster_{len(clusters) + 1}",

                    "sources": [
                        source
                    ]
                })

        result = []

        for cluster in clusters:

            cluster_sources = (
                cluster["sources"]
            )

            domains = self._unique(
                [
                    source.get(
                        "domain"
                    )
                    for source
                    in cluster_sources
                    if source.get(
                        "domain"
                    )
                ]
            )

            result.append({
                "cluster_id":
                    cluster["cluster_id"],

                "source_count":
                    len(cluster_sources),

                "independent_domains":
                    len(domains),

                "domains":
                    domains,

                "primary_sources": [
                    source.get(
                        "name"
                    )
                    for source
                    in cluster_sources
                    if source.get(
                        "primary"
                    )
                ],

                "likely_repetition": (
                    len(domains) <= 1
                    and
                    len(cluster_sources) > 1
                ),
            })

        return result

    # =====================================================
    # INDEPENDENCE
    # =====================================================

    def _independence_analysis(
        self,
        sources: List[Dict[str, Any]],
        clusters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        domains = self._unique(
            [
                source.get(
                    "domain"
                )
                for source in sources
                if source.get(
                    "domain"
                )
            ]
        )

        explicit_independent = sum(
            1
            for source in sources
            if source.get(
                "independent"
            )
        )

        primary_count = sum(
            1
            for source in sources
            if source.get(
                "primary"
            )
        )

        repeated_clusters = sum(
            1
            for cluster in clusters
            if cluster.get(
                "likely_repetition"
            )
        )

        independent_score = 0

        independent_score += min(
            len(domains) * 10,
            40
        )

        independent_score += min(
            explicit_independent * 10,
            30
        )

        independent_score += min(
            primary_count * 15,
            30
        )

        independent_score -= min(
            repeated_clusters * 15,
            30
        )

        independent_score = max(
            0,
            min(
                independent_score,
                100
            )
        )

        return {
            "unique_domains":
                len(domains),

            "domains":
                domains,

            "explicit_independent_sources":
                explicit_independent,

            "primary_sources":
                primary_count,

            "repeated_clusters":
                repeated_clusters,

            "independence_score":
                independent_score,

            "classification":
                self._independence_classification(
                    independent_score
                ),
        }

    # =====================================================
    # SOURCE CHAIN
    # =====================================================

    def _build_source_chain(
        self,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        primary = []
        secondary = []
        social = []
        unknown = []

        for source in sources:

            if (
                source.get("primary")
                or source.get("official")
            ):

                primary.append(
                    source.get("name")
                )

            elif self._is_social_source(
                source
            ):

                social.append(
                    source.get("name")
                )

            elif source.get(
                "type"
            ) in (
                "UNKNOWN",
                "USER_GENERATED",
            ):

                unknown.append(
                    source.get("name")
                )

            else:

                secondary.append(
                    source.get("name")
                )

        return {
            "original_source":
                primary,

            "primary_reports":
                primary,

            "secondary_reports":
                secondary,

            "social_amplification":
                social,

            "unknown_sources":
                unknown,

            "chain_depth": (
                len(primary)
                + len(secondary)
                + len(social)
            ),
        }

    # =====================================================
    # CONFLICT DETECTION
    # =====================================================

    def _detect_conflicts(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        conflicts = []

        titles = [
            source.get(
                "title",
                ""
            ).strip()
            for source in sources
            if source.get(
                "title"
            )
        ]

        if len(titles) < 2:
            return conflicts

        for index in range(
            len(sources)
        ):

            for other_index in range(
                index + 1,
                len(sources)
            ):

                first = sources[index]
                second = sources[
                    other_index
                ]

                first_title = str(
                    first.get(
                        "title",
                        ""
                    )
                ).lower().strip()

                second_title = str(
                    second.get(
                        "title",
                        ""
                    )
                ).lower().strip()

                if (
                    not first_title
                    or not second_title
                ):
                    continue

                similarity = (
                    self._text_similarity(
                        first_title,
                        second_title
                    )
                )

                if similarity < 0.25:

                    conflicts.append({
                        "type":
                            "LOW_TITLE_ALIGNMENT",

                        "source_a":
                            first.get(
                                "name"
                            ),

                        "source_b":
                            second.get(
                                "name"
                            ),

                        "severity":
                            "LOW",

                        "message":
                            "Sources appear to describe "
                            "the story differently.",
                    })

        return conflicts

    # =====================================================
    # OVERALL SOURCE QUALITY
    # =====================================================

    def _overall_source_quality(
        self,
        sources: List[Dict[str, Any]],
        independence: Dict[str, Any],
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not sources:

            return {
                "score": 0,
                "classification":
                    "NO_SOURCES",
            }

        quality_scores = [
            source.get(
                "quality_score",
                0
            )
            for source in sources
        ]

        average_quality = (
            sum(quality_scores)
            / len(quality_scores)
        )

        independence_score = (
            independence.get(
                "independence_score",
                0
            )
        )

        conflict_penalty = min(
            len(conflicts) * 5,
            25
        )

        final_score = (
            average_quality * 0.70
            +
            independence_score * 0.30
            -
            conflict_penalty
        )

        final_score = int(
            max(
                0,
                min(
                    final_score,
                    100
                )
            )
        )

        return {
            "score":
                final_score,

            "average_source_quality":
                int(
                    average_quality
                ),

            "independence_score":
                independence_score,

            "conflict_penalty":
                conflict_penalty,

            "classification":
                self._classification(
                    final_score
                ),
                        }
    # =====================================================
    # RECOMMENDATION
    # =====================================================

    def _recommendation(
        self,
        overall: Dict[str, Any],
        conflicts: List[Dict[str, Any]],
        independence: Dict[str, Any]
    ) -> Dict[str, Any]:

        score = int(
            overall.get(
                "score",
                0
            )
        )

        independence_score = int(
            independence.get(
                "independence_score",
                0
            )
        )

        if score >= 80 and independence_score >= 50:

            decision = "STRONG_SOURCE_BASE"

        elif score >= 65:

            decision = "ACCEPT_WITH_CORROBORATION"

        elif score >= 45:

            decision = "NEEDS_MORE_SOURCES"

        else:

            decision = "WEAK_SOURCE_BASE"

        if conflicts:
            note = (
                "Source differences detected; "
                "fact verification should resolve "
                "material disagreements before publication."
            )
        else:
            note = (
                "No major source-alignment conflicts "
                "were detected."
            )

        return {
            "decision":
                decision,

            "score":
                score,

            "independence_score":
                independence_score,

            "conflict_count":
                len(conflicts),

            "note":
                note,
        }

    # =====================================================
    # CLASSIFICATION HELPERS
    # =====================================================

    def _classification(
        self,
        score: int
    ) -> str:

        score = int(
            max(
                0,
                min(
                    score,
                    100
                )
            )
        )

        if score >= 85:
            return "EXCELLENT"

        if score >= 70:
            return "STRONG"

        if score >= 55:
            return "MODERATE"

        if score >= 40:
            return "WEAK"

        return "VERY_WEAK"

    def _independence_classification(
        self,
        score: int
    ) -> str:

        score = int(
            max(
                0,
                min(
                    score,
                    100
                )
            )
        )

        if score >= 80:
            return "HIGHLY_INDEPENDENT"

        if score >= 60:
            return "INDEPENDENT"

        if score >= 40:
            return "MIXED"

        if score >= 20:
            return "LOW_INDEPENDENCE"

        return "HIGH_REPETITION_RISK"

    # =====================================================
    # DOMAIN
    # =====================================================

    def _domain(
        self,
        url: str
    ) -> str:

        if not url:
            return ""

        try:

            parsed = urlparse(
                url
            )

            domain = (
                parsed.netloc
                or parsed.path.split("/")[0]
            )

            domain = domain.lower().strip()

            if domain.startswith(
                "www."
            ):
                domain = domain[4:]

            return domain

        except Exception:
            return ""

    # =====================================================
    # SOCIAL SOURCE
    # =====================================================

    def _is_social_source(
        self,
        source: Dict[str, Any]
    ) -> bool:

        source_type = str(
            source.get(
                "type",
                ""
            )
        ).upper()

        if source_type == "SOCIAL":
            return True

        domain = str(
            source.get(
                "domain",
                ""
            )
        ).lower().strip()

        if domain.startswith(
            "www."
        ):
            domain = domain[4:]

        if domain in self.social_domains:
            return True

        return any(
            domain.endswith(
                "." + social_domain
            )
            for social_domain
            in self.social_domains
        )

    # =====================================================
    # TEXT NORMALIZATION
    # =====================================================

    def _normalize_text(
        self,
        text: Any
    ) -> str:

        if text is None:
            return ""

        text = str(
            text
        ).lower()

        text = re.sub(
            r"https?://\S+",
            " ",
            text
        )

        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =====================================================
    # TEXT SIMILARITY
    # =====================================================

    def _text_similarity(
        self,
        first: Any,
        second: Any
    ) -> float:

        first_text = self._normalize_text(
            first
        )

        second_text = self._normalize_text(
            second
        )

        if not first_text or not second_text:
            return 0.0

        if first_text == second_text:
            return 1.0

        return SequenceMatcher(
            None,
            first_text,
            second_text
        ).ratio()

    # =====================================================
    # UNIQUE
    # =====================================================

    def _unique(
        self,
        values: List[Any]
    ) -> List[Any]:

        result = []
        seen = set()

        for value in values:

            if value is None:
                continue

            if isinstance(
                value,
                str
            ):
                normalized = value.strip()

                if not normalized:
                    continue

                key = normalized.lower()

            else:
                key = str(
                    value
                )

            if key in seen:
                continue

            seen.add(
                key
            )

            result.append(
                value
            )

        return result


# =========================================================
# DEFAULT ENGINE INSTANCE
# =========================================================

source_intelligence = (
    SourceIntelligenceEngine()
)


# =========================================================
# MODULE-LEVEL HELPERS
# =========================================================

def analyze_sources(
    sources: List[Dict[str, Any]]
) -> Dict[str, Any]:

    return source_intelligence.analyze(
        sources
    )


def analyze(
    sources: List[Dict[str, Any]]
) -> Dict[str, Any]:

    return source_intelligence.analyze(
        sources
            )
