"""
AI NEWS FACTORY
CORROBORATION ENGINE

Determines whether information is genuinely corroborated
across multiple sources.

Important principle:

    MANY ARTICLES != MANY INDEPENDENT SOURCES

The engine identifies:

- independent sources
- shared source chains
- copied reporting
- primary-source support
- independent confirmation
- source diversity
- corroboration strength

The engine does not declare a claim true merely because
it appears frequently.
"""

from typing import Any, Dict, List, Set
from collections import Counter
from urllib.parse import urlparse
import re


class CorroborationEngine:

    def __init__(self):

        self.name = "Corroboration Intelligence Engine"
        self.version = "1.0.0"

        self.primary_types = {
            "official",
            "government",
            "court",
            "police",
            "company",
            "document",
            "transcript",
            "direct_statement",
            "original_video",
            "original_image"
        }

        self.strong_news_types = {
            "news",
            "newspaper",
            "broadcast",
            "wire",
            "journalist"
        }

        self.weak_types = {
            "social",
            "social_media",
            "forum",
            "anonymous",
            "unknown"
        }

    # =====================================================
    # MAIN
    # =====================================================

    def analyze(
        self,
        sources: List[Dict[str, Any]],
        claims: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        sources = self._normalize_sources(
            sources
        )

        claims = (
            claims
            if isinstance(
                claims,
                list
            )
            else []
        )

        groups = self._build_source_groups(
            sources
        )

        source_chains = self._detect_source_chains(
            sources
        )

        independence = self._calculate_independence(
            sources,
            groups,
            source_chains
        )

        diversity = self._source_diversity(
            sources
        )

        primary_support = self._primary_source_analysis(
            sources
        )

        claim_results = self._analyze_claims(
            claims,
            sources,
            groups,
            source_chains
        )

        score = self._overall_score(
            independence,
            diversity,
            primary_support,
            claim_results
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "CORROBORATION_ANALYSIS_COMPLETE",

            "source_count":
                len(
                    sources
                ),

            "source_groups":
                groups,

            "source_chains":
                source_chains,

            "independence":
                independence,

            "source_diversity":
                diversity,

            "primary_source_analysis":
                primary_support,

            "claim_analysis":
                claim_results,

            "corroboration_score":
                score,

            "corroboration_level":
                self._level(
                    score
                ),

            "editorial_warning":
                self._warning(
                    score,
                    independence
                )
        }

    # =====================================================
    # NORMALIZE SOURCES
    # =====================================================

    def _normalize_sources(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        if isinstance(
            sources,
            dict
        ):

            sources = list(
                sources.values()
            )

        if not isinstance(
            sources,
            list
        ):

            return []

        normalized = []

        for index, source in enumerate(
            sources
        ):

            if isinstance(
                source,
                str
            ):

                source = {
                    "content":
                        source
                }

            if not isinstance(
                source,
                dict
            ):

                continue

            url = str(
                source.get(
                    "url",
                    ""
                )
            )

            content = str(
                source.get(
                    "content",
                    source.get(
                        "text",
                        source.get(
                            "body",
                            ""
                        )
                    )
                )
            )

            title = str(
                source.get(
                    "title",
                    source.get(
                        "headline",
                        ""
                    )
                )
            )

            normalized.append({

                "source_id":
                    source.get(
                        "source_id",
                        source.get(
                            "id",
                            f"source_{index + 1}"
                        )
                    ),

                "name":
                    source.get(
                        "name",
                        source.get(
                            "publisher",
                            ""
                        )
                    ),

                "publisher":
                    source.get(
                        "publisher",
                        source.get(
                            "name",
                            ""
                        )
                    ),

                "url":
                    url,

                "domain":
                    self._domain(
                        url
                    ),

                "type":
                    str(
                        source.get(
                            "type",
                            source.get(
                                "source_type",
                                "unknown"
                            )
                        )
                    ).lower(),

                "title":
                    title,

                "content":
                    content,

                "author":
                    source.get(
                        "author",
                        ""
                    ),

                "original_source":
                    source.get(
                        "original_source",
                        ""
                    ),

                "quoted_source":
                    source.get(
                        "quoted_source",
                        ""
                    ),

                "published_at":
                    source.get(
                        "published_at"
                    ),

                "primary":
                    bool(
                        source.get(
                            "primary",
                            False
                        )
                    ),

                "verified":
                    bool(
                        source.get(
                            "verified",
                            False
                        )
                    )
            })

        return normalized

    # =====================================================
    # SOURCE GROUPS
    # =====================================================

    def _build_source_groups(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        groups = []

        assigned: Set[str] = set()

        for source in sources:

            source_id = str(
                source.get(
                    "source_id"
                )
            )

            if source_id in assigned:
                continue

            group = [
                source
            ]

            assigned.add(
                source_id
            )

            for other in sources:

                other_id = str(
                    other.get(
                        "source_id"
                    )
                )

                if other_id in assigned:
                    continue

                similarity = self._similarity(
                    source.get(
                        "content",
                        ""
                    ),
                    other.get(
                        "content",
                        ""
                    )
                )

                title_similarity = self._similarity(
                    source.get(
                        "title",
                        ""
                    ),
                    other.get(
                        "title",
                        ""
                    )
                )

                same_original = (
                    self._same_original_source(
                        source,
                        other
                    )
                )

                if (
                    similarity >= 0.65
                    or
                    title_similarity >= 0.75
                    or
                    same_original
                ):

                    group.append(
                        other
                    )

                    assigned.add(
                        other_id
                    )

            groups.append({

                "group_id":
                    f"source_group_{len(groups) + 1}",

                "source_ids":
                    [
                        item.get(
                            "source_id"
                        )
                        for item
                        in group
                    ],

                "domains":
                    self._unique([
                        item.get(
                            "domain",
                            ""
                        )
                        for item
                        in group
                    ]),

                "size":
                    len(
                        group
                    ),

                "likely_shared_information":
                    len(
                        group
                    ) > 1
            })

        return groups

    # =====================================================
    # SOURCE CHAINS
    # =====================================================

    def _detect_source_chains(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        chains = []

        for source in sources:

            original = str(
                source.get(
                    "original_source",
                    ""
                )
            ).strip()

            quoted = str(
                source.get(
                    "quoted_source",
                    ""
                )
            ).strip()

            if not original and not quoted:
                continue

            parent = (
                original
                if original
                else quoted
            )

            chains.append({

                "source_id":
                    source.get(
                        "source_id"
                    ),

                "publisher":
                    source.get(
                        "publisher"
                    ),

                "reported_parent_source":
                    parent,

                "chain_type":
                    (
                        "original_source"
                        if original
                        else
                        "quoted_source"
                    )
            })

        return chains

    # =====================================================
    # INDEPENDENCE
    # =====================================================

    def _calculate_independence(
        self,
        sources: List[Dict[str, Any]],
        groups: List[Dict[str, Any]],
        chains: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        domains = set()
        publishers = set()

        for source in sources:

            domain = source.get(
                "domain"
            )

            publisher = str(
                source.get(
                    "publisher",
                    ""
                )
            ).lower().strip()

            if domain:
                domains.add(
                    domain
                )

            if publisher:
                publishers.add(
                    publisher
                )

        group_count = len(
            groups
        )

        source_count = len(
            sources
        )

        independent_ratio = (
            group_count
            /
            max(
                source_count,
                1
            )
        )

        if independent_ratio >= 0.75:

            assessment = (
                "Most sources appear reasonably independent."
            )

        elif independent_ratio >= 0.50:

            assessment = (
                "Moderate independence; some sources may share reporting."
            )

        else:

            assessment = (
                "Low independence; many reports may derive from the same information."
            )

        return {

            "unique_domains":
                len(
                    domains
                ),

            "unique_publishers":
                len(
                    publishers
                ),

            "source_groups":
                group_count,

            "source_count":
                source_count,

            "independent_ratio":
                round(
                    independent_ratio,
                    3
                ),

            "assessment":
                assessment,

            "source_chain_count":
                len(
                    chains
                )
        }

    # =====================================================
    # SOURCE DIVERSITY
    # =====================================================

    def _source_diversity(
        self,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        domains = Counter()
        types = Counter()
        publishers = Counter()

        for source in sources:

            if source.get(
                "domain"
            ):

                domains[
                    source[
                        "domain"
                    ]
                ] += 1

            if source.get(
                "type"
            ):

                types[
                    source[
                        "type"
                    ]
                ] += 1

            publisher = str(
                source.get(
                    "publisher",
                    ""
                )
            ).strip().lower()

            if publisher:

                publishers[
                    publisher
                ] += 1

        return {

            "domains":
                dict(
                    domains
                ),

            "types":
                dict(
                    types
                ),

            "publishers":
                dict(
                    publishers
                ),

            "domain_count":
                len(
                    domains
                ),

            "type_count":
                len(
                    types
                ),

            "publisher_count":
                len(
                    publishers
                )
        }

    # =====================================================
    # PRIMARY SOURCES
    # =====================================================

    def _primary_source_analysis(
        self,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        primary = []

        for source in sources:

            source_type = source.get(
                "type",
                "unknown"
            )

            if (
                source.get(
                    "primary"
                )
                or
                source_type
                in
                self.primary_types
            ):

                primary.append({

                    "source_id":
                        source.get(
                            "source_id"
                        ),

                    "publisher":
                        source.get(
                            "publisher"
                        ),

                    "domain":
                        source.get(
                            "domain"
                        ),

                    "type":
                        source_type
                })

        if primary:

            strength = min(
                100,
                50
                +
                (
                    len(
                        primary
                    )
                    *
                    15
                )
            )

        else:

            strength = 0

        return {

            "count":
                len(
                    primary
                ),

            "sources":
                primary,

            "strength":
                strength,

            "assessment":
                (
                    "Primary or direct evidence is available."
                    if primary
                    else
                    "No clear primary evidence identified."
                )
        }
    # =====================================================
    # CLAIM ANALYSIS
    # =====================================================

    def _analyze_claims(
        self,
        claims: List[Dict[str, Any]],
        sources: List[Dict[str, Any]],
        groups: List[Dict[str, Any]],
        source_chains: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        results = []

        if not claims:

            return results

        for index, claim in enumerate(
            claims
        ):

            if isinstance(
                claim,
                str
            ):

                claim_text = claim

            elif isinstance(
                claim,
                dict
            ):

                claim_text = str(
                    claim.get(
                        "claim",
                        claim.get(
                            "text",
                            claim.get(
                                "statement",
                                ""
                            )
                        )
                    )
                )

            else:

                continue

            claim_text = claim_text.strip()

            if not claim_text:
                continue

            supporting_sources = []

            for source in sources:

                content = str(
                    source.get(
                        "content",
                        ""
                    )
                )

                title = str(
                    source.get(
                        "title",
                        ""
                    )
                )

                combined = (
                    title
                    + " "
                    + content
                )

                similarity = (
                    self._similarity(
                        claim_text,
                        combined
                    )
                )

                # Exact or strong lexical overlap.
                claim_words = set(
                    self._tokens(
                        claim_text
                    )
                )

                source_words = set(
                    self._tokens(
                        combined
                    )
                )

                overlap = 0.0

                if claim_words:

                    overlap = (
                        len(
                            claim_words
                            &
                            source_words
                        )
                        /
                        len(
                            claim_words
                        )
                    )

                if (
                    similarity >= 0.15
                    or overlap >= 0.35
                ):

                    supporting_sources.append({

                        "source_id":
                            source.get(
                                "source_id"
                            ),

                        "publisher":
                            source.get(
                                "publisher"
                            ),

                        "domain":
                            source.get(
                                "domain"
                            ),

                        "type":
                            source.get(
                                "type"
                            ),

                        "similarity":
                            round(
                                similarity,
                                3
                            ),

                        "word_overlap":
                            round(
                                overlap,
                                3
                            ),

                        "primary":
                            bool(
                                source.get(
                                    "primary"
                                )
                            )
                    })

            unique_domains = self._unique(
                [
                    item.get(
                        "domain"
                    )
                    for item
                    in supporting_sources
                    if item.get(
                        "domain"
                    )
                ]
            )

            primary_count = sum(
                1
                for item
                in supporting_sources
                if item.get(
                    "primary"
                )
                or
                item.get(
                    "type"
                )
                in self.primary_types
            )

            support_count = len(
                supporting_sources
            )

            if support_count == 0:

                level = "UNSUPPORTED"

            elif (
                primary_count >= 1
                and
                support_count >= 2
            ):

                level = "STRONG"

            elif (
                len(
                    unique_domains
                ) >= 2
                and
                support_count >= 2
            ):

                level = "MODERATE"

            elif support_count >= 1:

                level = "WEAK"

            else:

                level = "UNSUPPORTED"

            results.append({

                "claim_id":
                    (
                        claim.get(
                            "claim_id",
                            claim.get(
                                "id",
                                f"claim_{index + 1}"
                            )
                        )
                        if isinstance(
                            claim,
                            dict
                        )
                        else
                        f"claim_{index + 1}"
                    ),

                "claim":
                    claim_text,

                "supporting_source_count":
                    support_count,

                "unique_supporting_domains":
                    len(
                        unique_domains
                    ),

                "primary_support_count":
                    primary_count,

                "supporting_sources":
                    supporting_sources,

                "corroboration_level":
                    level,

                "independent_confirmation":
                    (
                        len(
                            unique_domains
                        ) >= 2
                    )
            })

        return results

    # =====================================================
    # OVERALL SCORE
    # =====================================================

    def _overall_score(
        self,
        independence: Dict[str, Any],
        diversity: Dict[str, Any],
        primary_support: Dict[str, Any],
        claim_results: List[Dict[str, Any]]
    ) -> float:

        independence_score = (
            float(
                independence.get(
                    "independent_ratio",
                    0
                )
            )
            * 100
        )

        diversity_score = min(
            100,
            (
                diversity.get(
                    "domain_count",
                    0
                )
                * 20
            )
            +
            (
                diversity.get(
                    "type_count",
                    0
                )
                * 10
            )
        )

        primary_score = float(
            primary_support.get(
                "strength",
                0
            )
        )

        if claim_results:

            level_values = {
                "STRONG": 100,
                "MODERATE": 70,
                "WEAK": 40,
                "UNSUPPORTED": 0
            }

            claim_score = sum(
                level_values.get(
                    item.get(
                        "corroboration_level"
                    ),
                    0
                )
                for item
                in claim_results
            ) / len(
                claim_results
            )

        else:

            # When no explicit claims are supplied,
            # score the source network instead.
            claim_score = (
                independence_score
            )

        score = (
            (
                independence_score
                * 0.35
            )
            +
            (
                diversity_score
                * 0.20
            )
            +
            (
                primary_score
                * 0.20
            )
            +
            (
                claim_score
                * 0.25
            )
        )

        return round(
            max(
                0.0,
                min(
                    100.0,
                    score
                )
            ),
            2
        )

    # =====================================================
    # CORROBORATION LEVEL
    # =====================================================

    def _level(
        self,
        score: float
    ) -> str:

        if score >= 80:

            return "STRONG"

        if score >= 60:

            return "MODERATE"

        if score >= 40:

            return "LIMITED"

        return "WEAK"

    # =====================================================
    # EDITORIAL WARNING
    # =====================================================

    def _warning(
        self,
        score: float,
        independence: Dict[str, Any]
    ) -> str:

        ratio = float(
            independence.get(
                "independent_ratio",
                0
            )
        )

        if ratio < 0.40:

            return (
                "Multiple reports may derive from "
                "the same underlying source. "
                "Do not treat article count as "
                "independent corroboration."
            )

        if score < 40:

            return (
                "Corroboration is weak. "
                "Additional independent evidence "
                "should be obtained before publication."
            )

        if score < 60:

            return (
                "Corroboration is limited. "
                "Editorial verification remains necessary."
            )

        if score < 80:

            return (
                "Corroboration is moderate. "
                "Review primary evidence where available."
            )

        return (
            "Strong corroboration detected, "
            "subject to final fact-checking and editorial review."
        )

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
                or
                parsed.path
            )

            domain = domain.lower()

            domain = re.sub(
                r"^www\.",
                "",
                domain
            )

            return domain

        except Exception:

            return ""

    # =====================================================
    # SAME ORIGINAL SOURCE
    # =====================================================

    def _same_original_source(
        self,
        first: Dict[str, Any],
        second: Dict[str, Any]
    ) -> bool:

        first_original = str(
            first.get(
                "original_source",
                first.get(
                    "quoted_source",
                    ""
                )
            )
        ).strip().lower()

        second_original = str(
            second.get(
                "original_source",
                second.get(
                    "quoted_source",
                    ""
                )
            )
        ).strip().lower()

        if not first_original:
            return False

        if not second_original:
            return False

        return (
            first_original
            ==
            second_original
        )

    # =====================================================
    # TEXT TOKENS
    # =====================================================

    def _tokens(
        self,
        text: str
    ) -> List[str]:

        text = str(
            text
            or
            ""
        ).lower()

        words = re.findall(
            r"\b[a-z0-9]{3,}\b",
            text
        )

        # Remove common words so that similarity
        # focuses more on meaningful terms.
        stopwords = {
            "the",
            "and",
            "that",
            "this",
            "with",
            "from",
            "have",
            "has",
            "were",
            "been",
            "will",
            "would",
            "could",
            "should",
            "about",
            "after",
            "before",
            "into",
            "their",
            "there",
            "they",
            "them",
            "than",
            "then",
            "when",
            "where",
            "which",
            "while",
            "what",
            "said",
            "says"
        }

        return [
            word
            for word
            in words
            if word
            not in stopwords
        ]

    # =====================================================
    # TEXT SIMILARITY
    # =====================================================

    def _similarity(
        self,
        first: str,
        second: str
    ) -> float:

        first_tokens = set(
            self._tokens(
                first
            )
        )

        second_tokens = set(
            self._tokens(
                second
            )
        )

        if not first_tokens:
            return 0.0

        if not second_tokens:
            return 0.0

        intersection = (
            first_tokens
            &
            second_tokens
        )

        union = (
            first_tokens
            |
            second_tokens
        )

        if not union:
            return 0.0

        return (
            len(
                intersection
            )
            /
            len(
                union
            )
        )

    # =====================================================
    # UNIQUE VALUES
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

            value_key = str(
                value
            ).strip()

            if not value_key:
                continue

            normalized = (
                value_key.lower()
            )

            if normalized in seen:
                continue

            seen.add(
                normalized
            )

            result.append(
                value_key
            )

        return result


# =========================================================
# SIMPLE FUNCTION API
# =========================================================

def analyze_corroboration(
    sources: List[Dict[str, Any]],
    claims: List[Dict[str, Any]] = None
) -> Dict[str, Any]:

    engine = CorroborationEngine()

    return engine.analyze(
        sources=sources,
        claims=claims
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    test_sources = [

        {
            "source_id": "source_1",
            "publisher": "Example News",
            "url": "https://example.com/story",
            "type": "news",
            "title": "Example story",
            "content": (
                "Officials announced a new development "
                "in the investigation."
            )
        },

        {
            "source_id": "source_2",
            "publisher": "Example Wire",
            "url": "https://wire.example.com/story",
            "type": "wire",
            "title": "Officials announce development",
            "content": (
                "Officials announced a new development "
                "in the investigation."
            )
        }
    ]

    test_claims = [

        {
            "claim_id": "claim_1",
            "claim": (
                "Officials announced a new development "
                "in the investigation."
            )
        }
    ]

    engine = CorroborationEngine()

    result = engine.analyze(
        sources=test_sources,
        claims=test_claims
    )

    print(
        result
    )
