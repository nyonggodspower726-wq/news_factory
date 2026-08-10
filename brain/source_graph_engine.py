"""
AI NEWS FACTORY
SOURCE GRAPH ENGINE

Purpose
-------
Build a relationship graph around collected news sources.

The graph helps the factory understand:

    SOURCE A
       ↓
    quoted by
       ↓
    SOURCE B
       ↓
    repeated by
       ↓
    SOURCE C

It can also connect:

    PERSON
    ORGANIZATION
    CLAIM
    EVENT
    SOURCE
    PUBLISHER

Important principle
-------------------
A graph relationship is evidence about relationships,
NOT proof that a claim is true.

This engine therefore provides structure for the research
and verification systems rather than making final factual
decisions.

Pipeline:

COLLECTORS
    ↓
RESEARCH
    ↓
CORROBORATION
    ↓
SOURCE GRAPH
    ↓
CLAIM / EVIDENCE / FACT CHECK
"""


from typing import Any, Dict, List, Set
from collections import defaultdict
from urllib.parse import urlparse
import re


class SourceGraphEngine:

    def __init__(self):

        self.name = "Source Relationship Graph Engine"
        self.version = "1.0.0"

        self.entity_types = {
            "source",
            "publisher",
            "person",
            "organization",
            "claim",
            "event",
            "location"
        }

        self.relationship_types = {
            "PUBLISHED_BY",
            "QUOTES",
            "CITES",
            "REPOSTS",
            "REFERENCES",
            "SUPPORTS",
            "CONTRADICTS",
            "MENTIONS",
            "ABOUT",
            "LOCATED_IN",
            "INVOLVES"
        }

    # =====================================================
    # MAIN
    # =====================================================

    def build_graph(
        self,
        sources: List[Dict[str, Any]],
        claims: List[Dict[str, Any]] = None,
        entities: Dict[str, List[str]] = None
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

        entities = (
            entities
            if isinstance(
                entities,
                dict
            )
            else {}
        )

        nodes = []
        edges = []

        source_nodes = {}

        # -------------------------------------------------
        # SOURCE NODES
        # -------------------------------------------------

        for source in sources:

            node = self._source_node(
                source
            )

            nodes.append(
                node
            )

            source_nodes[
                str(
                    source.get(
                        "source_id"
                    )
                )
            ] = node

        # -------------------------------------------------
        # PUBLISHER NODES
        # -------------------------------------------------

        publishers = {}

        for source in sources:

            publisher = str(
                source.get(
                    "publisher",
                    source.get(
                        "name",
                        ""
                    )
                )
            ).strip()

            if not publisher:

                continue

            publisher_id = (
                "publisher:"
                +
                self._slug(
                    publisher
                )
            )

            if publisher_id not in publishers:

                publishers[
                    publisher_id
                ] = {

                    "id":
                        publisher_id,

                    "type":
                        "publisher",

                    "name":
                        publisher
                }

                nodes.append(
                    publishers[
                        publisher_id
                    ]
                )

            edges.append({

                "from":
                    source.get(
                        "source_id"
                    ),

                "to":
                    publisher_id,

                "relationship":
                    "PUBLISHED_BY"
            })

        # -------------------------------------------------
        # SOURCE RELATIONSHIPS
        # -------------------------------------------------

        edges.extend(
            self._source_relationships(
                sources
            )
        )

        # -------------------------------------------------
        # CLAIM NODES
        # -------------------------------------------------

        claim_nodes = []

        for index, claim in enumerate(
            claims
        ):

            claim_id = str(
                claim.get(
                    "claim_id",
                    claim.get(
                        "id",
                        f"claim:{index + 1}"
                    )
                )
            )

            if not claim_id.startswith(
                "claim:"
            ):

                claim_node_id = (
                    "claim:"
                    +
                    claim_id
                )

            else:

                claim_node_id = claim_id

            claim_node = {

                "id":
                    claim_node_id,

                "type":
                    "claim",

                "text":
                    str(
                        claim.get(
                            "text",
                            claim.get(
                                "claim",
                                ""
                            )
                        )
                    )
            }

            nodes.append(
                claim_node
            )

            claim_nodes.append(
                claim_node
            )

            source_id = claim.get(
                "source_id"
            )

            if source_id:

                edges.append({

                    "from":
                        source_id,

                    "to":
                        claim_node_id,

                    "relationship":
                        "REFERENCES"
                })

        # -------------------------------------------------
        # EXTERNAL ENTITIES
        # -------------------------------------------------

        entity_nodes, entity_edges = (
            self._build_entity_nodes(
                entities,
                sources
            )
        )

        nodes.extend(
            entity_nodes
        )

        edges.extend(
            entity_edges
        )

        # -------------------------------------------------
        # GRAPH METRICS
        # -------------------------------------------------

        metrics = self._metrics(
            nodes,
            edges
        )

        hubs = self._find_hubs(
            nodes,
            edges
        )

        isolated = self._isolated_nodes(
            nodes,
            edges
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "SOURCE_GRAPH_COMPLETE",

            "nodes":
                nodes,

            "edges":
                edges,

            "metrics":
                metrics,

            "hubs":
                hubs,

            "isolated_nodes":
                isolated,

            "source_lineage":
                self._source_lineage(
                    sources,
                    edges
                )
        }

    # =====================================================
    # NORMALIZE
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

            normalized.append({

                "source_id":
                    source.get(
                        "source_id",
                        source.get(
                            "id",
                            f"source:{index + 1}"
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
                    source.get(
                        "url",
                        ""
                    ),

                "title":
                    source.get(
                        "title",
                        source.get(
                            "headline",
                            ""
                        )
                    ),

                "content":
                    source.get(
                        "content",
                        source.get(
                            "text",
                            source.get(
                                "body",
                                ""
                            )
                        )
                    ),

                "type":
                    source.get(
                        "type",
                        "unknown"
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

                "author":
                    source.get(
                        "author",
                        ""
                    ),

                "primary":
                    source.get(
                        "primary",
                        False
                    )
            })

        return normalized

    # =====================================================
    # SOURCE NODE
    # =====================================================

    def _source_node(
        self,
        source: Dict[str, Any]
    ) -> Dict[str, Any]:

        source_id = str(
            source.get(
                "source_id"
            )
        )

        if not source_id.startswith(
            "source:"
        ):

            source_id = (
                "source:"
                +
                source_id
            )

        return {

            "id":
                source_id,

            "type":
                "source",

            "name":
                source.get(
                    "name"
                ),

            "publisher":
                source.get(
                    "publisher"
                ),

            "domain":
                self._domain(
                    source.get(
                        "url",
                        ""
                    )
                ),

            "title":
                source.get(
                    "title"
                ),

            "source_type":
                source.get(
                    "type"
                ),

            "primary":
                bool(
                    source.get(
                        "primary"
                    )
                )
        }

    # =====================================================
    # SOURCE RELATIONSHIPS
    # =====================================================

    def _source_relationships(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        edges = []

        for source in sources:

            source_id = self._source_id(
                source.get(
                    "source_id"
                )
            )

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

            if original:

                target = self._resolve_source(
                    original,
                    sources
                )

                if target:

                    edges.append({

                        "from":
                            source_id,

                        "to":
                            target,

                        "relationship":
                            "REPOSTS"
                    })

            if quoted:

                target = self._resolve_source(
                    quoted,
                    sources
                )

                if target:

                    edges.append({

                        "from":
                            source_id,

                        "to":
                            target,

                        "relationship":
                            "QUOTES"
                    })

        # -------------------------------------------------
        # Similar reporting relationships
        # -------------------------------------------------

        for index, first in enumerate(
            sources
        ):

            for second in sources[
                index + 1:
            ]:

                first_text = (
                    str(
                        first.get(
                            "title",
                            ""
                        )
                    )
                    +
                    " "
                    +
                    str(
                        first.get(
                            "content",
                            ""
                        )
                    )
                )

                second_text = (
                    str(
                        second.get(
                            "title",
                            ""
                        )
                    )
                    +
                    " "
                    +
                    str(
                        second.get(
                            "content",
                            ""
                        )
                    )
                )

                similarity = self._similarity(
                    first_text,
                    second_text
                )

                if similarity >= 0.70:

                    edges.append({

                        "from":
                            self._source_id(
                                first.get(
                                    "source_id"
                                )
                            ),

                        "to":
                            self._source_id(
                                second.get(
                                    "source_id"
                                )
                            ),

                        "relationship":
                            "REPOSTS",

                        "confidence":
                            round(
                                similarity,
                                3
                            )
                    })

        return edges

    # =====================================================
    # ENTITY NODES
    # =====================================================

    def _build_entity_nodes(
        self,
        entities: Dict[str, List[str]],
        sources: List[Dict[str, Any]]
    ):

        nodes = []
        edges = []

        entity_map = {

            "people":
                "person",

            "organizations":
                "organization",

            "locations":
                "location"
        }

        for category, entity_type in entity_map.items():

            values = entities.get(
                category,
                []
            )

            if not isinstance(
                values,
                list
            ):

                continue

            for value in values:

                value = str(
                    value
                ).strip()

                if not value:

                    continue

                entity_id = (
                    entity_type
                    +
                    ":"
                    +
                    self._slug(
                        value
                    )
                )

                nodes.append({

                    "id":
                        entity_id,

                    "type":
                        entity_type,

                    "name":
                        value
                })

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
                    ).lower()

                    if value.lower() in source_text:

                        edges.append({

                            "from":
                                self._source_id(
                                    source.get(
                                        "source_id"
                                    )
                                ),

                            "to":
                                entity_id,

                            "relationship":
                                "MENTIONS"
                        })

        return nodes, edges

    # =====================================================
    # RESOLVE SOURCE
    # =====================================================

    def _resolve_source(
        self,
        reference: str,
        sources: List[Dict[str, Any]]
    ) -> str:

        reference = reference.lower().strip()

        for source in sources:

            source_id = str(
                source.get(
                    "source_id",
                    ""
                )
            )

            publisher = str(
                source.get(
                    "publisher",
                    ""
                )
            ).lower()

            name = str(
                source.get(
                    "name",
                    ""
                )
            ).lower()

            domain = self._domain(
                source.get(
                    "url",
                    ""
                )
            ).lower()

            if reference in {
                source_id.lower(),
                publisher,
                name,
                domain
            }:

                return self._source_id(
                    source_id
                )

        return ""

    # =====================================================
    # SOURCE ID
    # ====
