"""
AI NEWS FACTORY
EVENT RESOLUTION ENGINE

Purpose
-------
Determine whether multiple reports refer to:

    1. The SAME event
    2. RELATED events
    3. DIFFERENT events
    4. An EVOLVING event

The engine compares:

    - people
    - organizations
    - locations
    - dates
    - times
    - event keywords
    - titles
    - descriptions
    - source information

Important:
-----------
Similarity is NOT proof that two reports describe the same
real-world event.

The engine therefore produces confidence scores and lets
verification/editorial systems make the final decision.

Pipeline:

COLLECTORS
    ↓
STORY CLUSTERING
    ↓
ENTITY RESOLUTION
    ↓
EVENT RESOLUTION
    ↓
CORROBORATION
    ↓
VERIFICATION
    ↓
EDITORIAL
"""


from typing import Any, Dict, List, Set
from datetime import datetime
import re


class EventResolutionEngine:

    def __init__(self):

        self.name = "Event Resolution Intelligence Engine"
        self.version = "1.0.0"

        self.event_words = {
            "attack",
            "arrest",
            "election",
            "protest",
            "explosion",
            "fire",
            "flood",
            "earthquake",
            "crash",
            "accident",
            "court",
            "ruling",
            "verdict",
            "resignation",
            "appointment",
            "launch",
            "meeting",
            "summit",
            "agreement",
            "deal",
            "strike",
            "war",
            "conflict",
            "death",
            "killing",
            "injury",
            "announcement",
            "ban",
            "sanction",
            "outage",
            "recall",
            "investigation"
        }

        self.stop_words = {
            "this",
            "that",
            "with",
            "from",
            "have",
            "were",
            "been",
            "will",
            "they",
            "their",
            "about",
            "after",
            "before",
            "said",
            "says",
            "into",
            "what",
            "when",
            "where",
            "which",
            "there",
            "while",
            "would",
            "could",
            "should"
        }

    # =====================================================
    # MAIN
    # =====================================================

    def resolve(
        self,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        events = self._normalize_events(
            events
        )

        relationships = []

        for index, first in enumerate(
            events
        ):

            for second in events[
                index + 1:
            ]:

                comparison = self._compare_events(
                    first,
                    second
                )

                if comparison["relationship"] != "DIFFERENT":

                    relationships.append({

                        "event_a":
                            first.get(
                                "event_id"
                            ),

                        "event_b":
                            second.get(
                                "event_id"
                            ),

                        **comparison
                    })

        clusters = self._build_clusters(
            events,
            relationships
        )

        timeline = self._build_timeline(
            events,
            clusters
        )

        duplicates = self._find_duplicate_groups(
            clusters
        )

        evolving = self._find_evolving_events(
            clusters,
            relationships
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "EVENT_RESOLUTION_COMPLETE",

            "event_count":
                len(
                    events
                ),

            "relationships":
                relationships,

            "clusters":
                clusters,

            "duplicate_event_groups":
                duplicates,

            "evolving_events":
                evolving,

            "timeline":
                timeline
        }

    # =====================================================
    # NORMALIZE EVENTS
    # =====================================================

    def _normalize_events(
        self,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        if not isinstance(
            events,
            list
        ):

            return []

        normalized = []

        for index, event in enumerate(
            events
        ):

            if isinstance(
                event,
                str
            ):

                event = {
                    "title":
                        event
                }

            if not isinstance(
                event,
                dict
            ):

                continue

            event_id = str(
                event.get(
                    "event_id",
                    event.get(
                        "id",
                        f"event:{index + 1}"
                    )
                )
            )

            title = str(
                event.get(
                    "title",
                    event.get(
                        "headline",
                        ""
                    )
                )
            ).strip()

            description = str(
                event.get(
                    "description",
                    event.get(
                        "summary",
                        event.get(
                            "content",
                            ""
                        )
                    )
                )
            ).strip()

            entities = event.get(
                "entities",
                {}
            )

            if not isinstance(
                entities,
                dict
            ):

                entities = {}

            normalized.append({

                "event_id":
                    event_id,

                "title":
                    title,

                "description":
                    description,

                "text":
                    title
                    +
                    " "
                    +
                    description,

                "people":
                    self._entity_values(
                        entities,
                        "people"
                    ),

                "organizations":
                    self._entity_values(
                        entities,
                        "organizations"
                    ),

                "locations":
                    self._entity_values(
                        entities,
                        "locations"
                    ),

                "date":
                    self._extract_date(
                        event
                    ),

                "time":
                    self._extract_time(
                        event
                    ),

                "source_id":
                    event.get(
                        "source_id"
                    ),

                "published_at":
                    event.get(
                        "published_at"
                    ),

                "event_type":
                    event.get(
                        "event_type",
                        ""
                    )
            })

        return normalized

    # =====================================================
    # ENTITY VALUES
    # =====================================================

    def _entity_values(
        self,
        entities: Dict[str, Any],
        key: str
    ) -> Set[str]:

        values = entities.get(
            key,
            []
        )

        if isinstance(
            values,
            str
        ):

            values = [
                values
            ]

        if not isinstance(
            values,
            list
        ):

            return set()

        return {
            self._normalize_text(
                value
            )
            for value
            in values
            if str(
                value
            ).strip()
        }

    # =====================================================
    # COMPARE EVENTS
    # =====================================================

    def _compare_events(
        self,
        first: Dict[str, Any],
        second: Dict[str, Any]
    ) -> Dict[str, Any]:

        title_score = self._similarity(
            first.get(
                "title",
                ""
            ),
            second.get(
                "title",
                ""
            )
        )

        content_score = self._similarity(
            first.get(
                "text",
                ""
            ),
            second.get(
                "text",
                ""
            )
        )

        people_score = self._set_similarity(
            first.get(
                "people",
                set()
            ),
            second.get(
                "people",
                set()
            )
        )

        organization_score = self._set_similarity(
            first.get(
                "organizations",
                set()
            ),
            second.get(
                "organizations",
                set()
            )
        )

        location_score = self._set_similarity(
            first.get(
                "locations",
                set()
            ),
            second.get(
                "locations",
                set()
            )
        )

        date_score = self._date_similarity(
            first.get(
                "date"
            ),
            second.get(
                "date"
            )
        )

        event_type_score = self._text_exact_score(
            first.get(
                "event_type",
                ""
            ),
            second.get(
                "event_type",
                ""
            )
        )

        total = (

            title_score
            * 0.20

            +
            content_score
            * 0.25

            +
            people_score
            * 0.15

            +
            organization_score
            * 0.10

            +
            location_score
            * 0.15

            +
            date_score
            * 0.10

            +
            event_type_score
            * 0.05
        )

        total = min(
            1.0,
            total
        )

        # Strong same-event signals.

        same_location = (
            location_score >= 0.80
            and
            bool(
                first.get(
                    "locations"
                )
            )
        )

        same_people = (
            people_score >= 0.80
            and
            bool(
                first.get(
                    "people"
                )
            )
        )

        same_date = (
            date_score >= 0.90
        )

        strong_text = (
            title_score >= 0.65
            or
            content_score >= 0.60
        )

        if (
            total >= 0.78
            and
            (
                same_location
                or
                same_people
                or
                same_date
            )
            and
            strong_text
        ):

            relationship = "SAME_EVENT"

        elif total >= 0.55:

            relationship = "RELATED"

        elif self._developing_relationship(
            first,
            second
        ):

            relationship = "EVOLVING_EVENT"

        else:

            relationship = "DIFFERENT"

        return {

            "relationship":
                relationship,

            "confidence":
                round(
                    total,
                    3
                ),

            "signals": {

                "title_similarity":
                    round(
                        title_score,
                        3
                    ),

                "content_similarity":
                    round(
                        content_score,
                        3
                    ),

                "people_similarity":
                    round(
                        people_score,
                        3
                    ),

                "organization_similarity":
                    round(
                        organization_score,
                        3
                    ),

                "location_similarity":
                    round(
                        location_score,
                        3
                    ),

                "date_similarity":
                    round(
                        date_score,
                        3
                    ),

                "event_type_similarity":
                    round(
                        event_type_score,
                        3
                    )
            }
        }

    # =====================================================
    # DEVELOPING RELATIONSHIP
    # =====================================================

    def _developing_relationship(
        self,
        first: Dict[str, Any],
        second: Dict[str, Any]
    ) -> bool:

        shared_people = (
            first.get(
                "people",
                set()
            )
            &
            second.get(
                "people",
                set()
            )
        )

        shared_orgs = (
            first.get(
                "organizations",
                set()
            )
            &
            second.get(
                "organizations",
                set()
            )
        )

        shared_locations = (
            first.get(
                "locations",
                set()
            )
            &
            second.get(
                "locations",
                set()
            )
        )

        if (
            shared_people
            and
            shared_locations
        ):

            return True

        if (
            shared_orgs
            and
            shared_locations
        ):

            return True

        return False

    # =====================================================
    # CLUSTERS
    # =====================================================

    def _build_clusters(
        self,
        events: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        adjacency = {}

        for event in events:

            adjacency[
                event.get(
                    "event_id"
                )
            ] = set()

        for relation in relationships:

            if relation.get(
                "relationship"
            ) not in {
                "SAME_EVENT",
                "EVOLVING_EVENT"
            }:

                continue

            first = relation.get(
                "event_a"
            )

            second = relation.get(
                "event_b"
            )

            if first in adjacency:

                adjacency[
                    first
                ].add(
                    second
                )

            if second in adjacency:

                adjacency[
                    second
                ].add(
                    first
                )

        clusters = []

        visited = set()

        for event_id in adjacency:

            if event_id in visited:

                continue

            stack = [
                event_id
            ]

            cluster_ids = []

            while stack:

                current = stack.pop()

                if current in visited:

                    continue

                visited.add(
                    current
                )

                cluster_ids.append(
                    current
                )

                stack.extend(
                    adjacency.get(
                        current,
                        set()
                    )
                )

            clusters.append({

                "cluster_id":
                    f"event_cluster_{len(clusters) + 1}",

                "event_ids":
                    cluster_ids,

                "size":
                    len(
                        cluster_ids
                    ),

                "cluster_type":
                    (
                        "DUPLICATE_OR_DEVELOPING"
                        if len(
                            cluster_ids
                        ) > 1
                        else
                        "SINGLE_EVENT"
                    )
            })

        return clusters

    # =====================================================
    # DUPLICATE GROUPS
    # =====================================================

    def _find_duplicate_groups(
        self,
        clusters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        duplicates = []

        for cluster in clusters:

            if cluster.get(
                "size",
                0
            ) <= 1:

                continue

            duplicates.append({

                "cluster_id":
                    cluster.get(
                        "cluster_id"
                    ),

                "event_ids":
                    cluster.get(
                        "event_ids",
                        []
                    ),

                "recommendation":
                    "Merge reports into one event record and preserve source-specific updates."
            })

        return duplicates

    # =====================================================
    # EVOLVING EVENTS
    # =====================================================

    def _find_evolving_events(
        self,
        clusters: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        evolving_pairs = []

        for relation in relationships:

            if relation.get(
                "relationship"
            ) != "EVOLVING_EVENT":

                continue

            evolving_pairs.append({

                "event_a":
                    relation.get(
                        "event_a"
                    ),

                "event_b":
                    relation.get(
                        "event_b"
                    ),

                "confidence":
                    relation.get(
                        "confidence"
                    ),

                "recommendation":
                    "Treat as potentially related developments and verify chronology before merging."
            })

        return evolving_pairs

    # =====================================================
    # TIMELINE
    # =====================================================

    def _build_timeline(
        self,
        events: List[Dict[str, Any]],
        clusters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        event_map = {
            event.get(
                "event_id"
            ):
                event

            for event
            in events
        }

        timeline = []

        for cluster in clusters:

            cluster_events = []

            for event_id in cluster.get(
                "event_ids",
                []
            ):

                event = event_map.get(
                    event_id
                )

                if event:

                    cluster_events.append(
                        event
                    )

            cluster_events.sort(
                key=lambda event:
                    str(
                        event.get(
                            "published_at",
             
