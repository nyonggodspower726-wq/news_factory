"""
AI NEWS FACTORY
CORROBORATION ENGINE

Purpose
-------
Determine whether information is genuinely corroborated across
multiple sources.

Important principle:

    MANY ARTICLES != MANY INDEPENDENT SOURCES

Ten websites may all be repeating one original report.

This engine attempts to identify:
    - independent sources
    - shared source chains
    - copied reporting
    - primary-source support
    - independent confirmation
    - source diversity
    - corroboration strength

The engine does not declare a claim true merely because it
appears frequently.

Pipeline position:

SOURCE COLLECTION
        ↓
RESEARCH ENGINE
        ↓
CORROBORATION ENGINE
        ↓
EVIDENCE / CLAIM VERIFICATION
        ↓
FACT CHECKING
        ↓
EDITORIAL SYSTEM
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
        chains: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        results = []

        for claim in claims:

            claim_text = str(
                claim.get(
                    "text",
                    claim.get(
                        "claim",
                        ""
                    )
                )
            )

            supporting = []

            for source in sources:

                source_text = (
                    str(
                        source.get(
                            "title",
                            ""
                        )
                    )
                    +
                    " "
                    +
                    str(
                        source.get(
                            "content",
                            ""
                        )
                    )
                )

                similarity = self._similarity(
                    claim_text,
                    source_text
                )

                if similarity >= 0.20:

                    supporting.append(
                        source
                    )

            source_groups = set()

            for source in supporting:

                source_id = source.get(
                    "source_id"
                )

                for group in groups:

                    if source_id in group.get(
                        "source_ids",
                        []
                    ):

                        source_groups.add(
                            group.get(
                
