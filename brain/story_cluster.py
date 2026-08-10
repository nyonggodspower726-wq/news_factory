"""
AI NEWS FACTORY
Story Clustering & Deduplication Engine

Purpose
-------
Identify when multiple sources are reporting the same
underlying event.

Instead of treating:

    Source A
    Source B
    Source C
    Source D

as four independent stories, the factory attempts to build:

    ONE STORY CLUSTER
        ├── Source A
        ├── Source B
        ├── Source C
        └── Source D

The cluster can then be passed to the verification and
journalist engines.

Goals
-----
- Detect duplicate stories
- Group related coverage
- Identify new information
- Identify conflicting claims
- Track source diversity
- Prevent repetitive publishing
- Prepare stories for multi-source verification

This engine intentionally uses deterministic signals first.
A future semantic/LLM layer can provide deeper similarity
analysis without changing the public interface.
"""

import hashlib
import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse


class StoryCluster:

    def __init__(self):

        self.name = "Story Clustering Engine"
        self.version = "1.0.0"

        # Similarity thresholds.
        self.STRONG_MATCH = 0.80
        self.POSSIBLE_MATCH = 0.60

        self.stop_words = {
            "about",
            "after",
            "again",
            "against",
            "being",
            "before",
            "between",
            "could",
            "from",
            "have",
            "having",
            "into",
            "more",
            "other",
            "over",
            "said",
            "same",
            "some",
            "than",
            "that",
            "their",
            "there",
            "these",
            "they",
            "this",
            "those",
            "through",
            "under",
            "were",
            "which",
            "while",
            "with",
            "would",
            "according"
        }

    # =====================================================
    # MAIN CLUSTERING FUNCTION
    # =====================================================

    def cluster_stories(
        self,
        stories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        clusters: List[Dict[str, Any]] = []

        for story in stories:

            placed = False

            for cluster in clusters:

                similarity = self._story_similarity(
                    story,
                    cluster["representative"]
                )

                if similarity >= self.STRONG_MATCH:

                    self._add_to_cluster(
                        cluster,
                        story,
                        similarity
                    )

                    placed = True
                    break

            if not placed:

                clusters.append(
                    self._create_cluster(
                        story
                    )
                )

        return [
            self._finalize_cluster(cluster)
            for cluster in clusters
        ]

    # =====================================================
    # CREATE CLUSTER
    # =====================================================

    def _create_cluster(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {
            "cluster_id":
                self._generate_cluster_id(
                    story
                ),

            "representative":
                story,

            "stories": [
                story
            ],

            "similarity_scores": [],

            "sources": self._source_name(
                story
            ),

            "domains": [
                self._domain(
                    story.get(
                        "url",
                        ""
                    )
                )
            ],

            "created_at":
                datetime.utcnow().isoformat()
        }

    # =====================================================
    # ADD STORY
    # =====================================================

    def _add_to_cluster(
        self,
        cluster: Dict[str, Any],
        story: Dict[str, Any],
        similarity: float
    ) -> None:

        cluster["stories"].append(
            story
        )

        cluster["similarity_scores"].append(
            round(
                similarity,
                4
            )
        )

        source_name = self._source_name(
            story
        )

        if source_name not in cluster["sources"]:

            cluster["sources"].append(
                source_name
            )

        domain = self._domain(
            story.get(
                "url",
                ""
            )
        )

        if domain and domain not in cluster["domains"]:

            cluster["domains"].append(
                domain
            )

    # =====================================================
    # FINALIZE
    # =====================================================

    def _finalize_cluster(
        self,
        cluster: Dict[str, Any]
    ) -> Dict[str, Any]:

        stories = cluster["stories"]

        source_count = len(
            cluster["sources"]
        )

        domain_count = len(
            [
                domain
                for domain in cluster["domains"]
                if domain
            ]
        )

        # Find the story with the richest content.
        representative = max(
            stories,
            key=self._content_richness
        )

        # Determine whether this cluster deserves
        # additional investigation.
        verification_level = (
            self._verification_level(
                source_count,
                domain_count
            )
        )

        # Look for potentially different information.
        information_map = (
            self._extract_information_map(
                stories
            )
        )

        return {
            "cluster_id":
                cluster["cluster_id"],

            "story_count":
                len(stories),

            "source_count":
                source_count,

            "independent_domain_count":
                domain_count,

            "representative":
                representative,

            "stories":
                stories,

            "sources":
                cluster["sources"],

            "domains":
                cluster["domains"],

            "verification_level":
                verification_level,

            "information_map":
                information_map,

            "coverage_strength":
                self._coverage_strength(
                    source_count,
                    domain_count
                ),

            "duplicate_risk":
                self._duplicate_risk(
                    len(stories)
                )
        }

    # =====================================================
    # STORY SIMILARITY
    # =====================================================

    def _story_similarity(
        self,
        first: Dict[str, Any],
        second: Dict[str, Any]
    ) -> float:

        title_a = self._normalize(
            first.get(
                "title",
                ""
            )
        )

        title_b = self._normalize(
            second.get(
                "title",
                ""
            )
        )

        content_a = self._normalize(
            (
                first.get(
                    "description",
                    ""
                )
                + " "
                +
                first.get(
                    "content",
                    ""
                )
            )
        )

        content_b = self._normalize(
            (
                second.get(
                    "description",
                    ""
                )
                + " "
                +
                second.get(
                    "content",
                    ""
                )
            )
        )

        title_similarity = (
            self._token_similarity(
                title_a,
                title_b
            )
        )

        content_similarity = (
            self._token_similarity(
                content_a,
                content_b
            )
        )

        entity_similarity = (
            self._entity_similarity(
                first,
                second
            )
        )

        # Titles are deliberately given significant weight,
        # while entities help distinguish unrelated stories.
        score = (
            title_similarity * 0.45
            +
            content_similarity * 0.35
            +
            entity_similarity * 0.20
        )

        return round(
            min(
                score,
                1.0
            ),
            4
        )

    # =====================================================
    # TOKEN SIMILARITY
    # =====================================================

    def _token_similarity(
        self,
        first: str,
        second: str
    ) -> float:

        tokens_a = self._tokens(
            first
        )

        tokens_b = self._tokens(
            second
        )

        if not tokens_a or not tokens_b:
            return 0.0

        intersection = (
            tokens_a & tokens_b
        )

        union = (
            tokens_a | tokens_b
        )

        if not union:
            return 0.0

        return (
            len(intersection)
            /
            len(union)
        )

    # =====================================================
    # ENTITY SIMILARITY
    # =====================================================

    def _entity_similarity(
        self,
        first: Dict[str, Any],
        second: Dict[str, Any]
    ) -> float:

        people_a = set(
            first.get(
                "people",
                []
            )
        )

        people_b = set(
            second.get(
                "people",
                []
            )
        )

        locations_a = set(
            first
