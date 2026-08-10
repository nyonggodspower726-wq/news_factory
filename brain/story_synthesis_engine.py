"""
AI NEWS FACTORY
STORY SYNTHESIS ENGINE

Purpose
-------
Combine information from multiple sources into one
structured story model.

The engine separates:

    - confirmed facts
    - attributed claims
    - disputed information
    - context
    - timeline events
    - consequences
    - unknowns
    - questions still requiring verification

CORE PRINCIPLE
--------------
Do not simply concatenate articles.

The factory should understand:

    WHAT HAPPENED
    WHO IS INVOLVED
    WHEN IT HAPPENED
    WHERE IT HAPPENED
    WHY IT MATTERS
    WHAT IS CONFIRMED
    WHAT IS DISPUTED
    WHAT HAPPENS NEXT

IMPORTANT
---------
This engine does not replace fact checking.
It creates a structured editorial model for downstream
journalist and editor systems.
"""

from typing import Any, Dict, List
import re


class StorySynthesisEngine:

    def __init__(self):

        self.name = "Story Synthesis Engine"
        self.version = "1.0.0"

        self.fact_markers = {
            "confirmed",
            "announced",
            "official",
            "according",
            "reported",
            "stated",
            "said"
        }

        self.uncertainty_markers = {
            "allegedly",
            "reportedly",
            "possibly",
            "may",
            "might",
            "could",
            "unconfirmed",
            "rumor",
            "rumour",
            "appears"
        }

        self.dispute_markers = {
            "denied",
            "disputed",
            "rejected",
            "false",
            "contradicted",
            "not true",
            "no evidence"
        }

    # =====================================================
    # MAIN
    # =====================================================

    def synthesize(
        self,
        sources: List[Dict[str, Any]],
        evidence: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:

        sources = self._normalize_sources(
            sources
        )

        evidence = (
            evidence
            if isinstance(evidence, dict)
            else {}
        )

        metadata = (
            metadata
            if isinstance(metadata, dict)
            else {}
        )

        documents = self._extract_documents(
            sources
        )

        entities = self._extract_entities(
            documents,
            metadata
        )

        events = self._extract_events(
            documents
        )

        timeline = self._build_timeline(
            events
        )

        facts = self._build_facts(
            documents,
            evidence
        )

        disputed = self._build_disputed_information(
            documents,
            evidence
        )

        unknowns = self._identify_unknowns(
            facts,
            disputed,
            documents
        )

        consequences = self._build_consequences(
            documents,
            metadata
        )

        significance = self._calculate_significance(
            facts,
            consequences,
            entities,
            events
        )

        story_type = self._classify_story(
            documents,
            metadata
        )

        synthesis = {

            "story_type":
                story_type,

            "entities":
                entities,

            "central_event":
                self._central_event(
                    events,
                    facts
                ),

            "confirmed_facts":
                facts,

            "disputed_information":
                disputed,

            "unknowns":
                unknowns,

            "timeline":
                timeline,

            "consequences":
                consequences,

            "why_it_matters":
                significance,

            "source_count":
                len(sources),

            "editorial_confidence":
                self._editorial_confidence(
                    facts,
                    disputed,
                    unknowns
                )
        }

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "SYNTHESIZED",

            "story":
                synthesis,

            "editorial_notes":
                self._editorial_notes(
                    synthesis
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

        output = []

        for index, source in enumerate(
            sources
        ):

            if isinstance(
                source,
                str
            ):
                source = {
                    "text": source
                }

            if not isinstance(
                source,
                dict
            ):
                continue

            text = str(
                source.get(
                    "text",
                    source.get(
                        "content",
                        source.get(
                            "body",
                            ""
                        )
                    )
                )
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

            output.append({

                "id":
                    source.get(
                        "id",
                        f"source_{index + 1}"
                    ),

                "name":
                    source.get(
                        "name",
                        source.get(
                            "publisher",
                            "Unknown"
                        )
                    ),

                "title":
                    title,

                "text":
                    text,

                "url":
                    source.get(
                        "url",
                        ""
                    ),

                "published_at":
                    source.get(
                        "published_at"
                    ),

                "type":
                    source.get(
                        "type",
                        source.get(
                            "source_type",
                            "UNKNOWN"
                        )
                    ),

                "primary":
                    bool(
                        source.get(
                            "primary",
                            False
                        )
                    )
            })

        return output

    # =====================================================
    # DOCUMENT EXTRACTION
    # =====================================================

    def _extract_documents(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        documents = []

        for source in sources:

            text = source.get(
                "text",
                ""
            )

            if not text:
                continue

            documents.append({

                "source_id":
                    source.get(
                        "id"
                    ),

                "source_name":
                    source.get(
                        "name"
                    ),

                "source_type":
                    source.get(
                        "type"
                    ),

                "title":
                    source.get(
                        "title"
                    ),

                "sentences":
                    self._sentences(
                        text
                    ),

                "published_at":
                    source.get(
                        "published_at"
                    )
            })

        return documents

    # =====================================================
    # ENTITY EXTRACTION
    # =====================================================

    def _extract_entities(
        self,
        documents: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> Dict[str, List[str]]:

        people = []
        organizations = []
        locations = []
        topics = []

        for key in [
            "people",
            "persons",
            "entities_people"
        ]:

            value = metadata.get(
                key,
                []
            )

            if isinstance(
                value,
                list
            ):

                people.extend(
                    str(item)
                    for item in value
                )

        for key in [
            "organizations",
            "companies",
            "entities_organizations"
        ]:

            value = metadata.get(
                key,
                []
            )

            if isinstance(
                value,
                list
            ):

                organizations.extend(
                    str(item)
                    for item in value
                )

        for key in [
            "locations",
            "places"
        ]:

            value = metadata.get(
                key,
                []
            )

            if isinstance(
                value,
                list
            ):

                locations.extend(
                    str(item)
                    for item in value
                )

        for key in [
            "topics",
            "keywords"
        ]:

            value = metadata.get(
                key,
                []
            )

            if isinstance(
                value,
                list
            ):

                topics.extend(
                    str(item)
                    for item in value
                )

        for document in documents:

            title = document.get(
                "title",
                ""
            )

            text = " ".join(
                document.get(
                    "sentences",
                    []
                )
            )

            combined = (
                title
                + " "
                + text
            )

            candidates = re.findall(
                r"\b[A-Z][a-z]{2,}"
                r"(?:\s+[A-Z][a-z]{2,}){0,3}",
                combined
            )

            for candidate in candidates:

                candidate = candidate.strip()

                if len(
                    candidate
                ) < 3:
                    continue

                if candidate not in people:
                    people.append(
                        candidate
                    )

        return {

            "people":
                self._unique(
                    people
                )[:30],

            "organizations":
                self._unique(
                    organizations
                )[:30],

            "locations":
                self._unique(
                    locations
                )[:30],

            "topics":
                self._unique(
                    topics
                )[:30]
        }

    # =====================================================
    # EVENT EXTRACTION
    # =====================================================

    def _extract_events(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        events = []

        event_verbs = {

            "announced",
            "approved",
            "rejected",
            "launched",
            "signed",
            "won",
            "lost",
            "arrested",
            "appointed",
            "resigned",
            "died",
            "opened",
            "closed",
            "banned",
            "released",
            "reported",
            "confirmed",
            "filed",
            "ordered",
            "started",
            "ended",
            "increased",
            "decreased"
        }

        for document in documents:

            for sentence in document.get(
                "sentences",
                []
            ):

                lowered = sentence.lower()

                matched = False

                for verb in event_verbs:

                    if re.search(
                        rf"\b{re.escape(verb)}\b",
                        lowered
                    ):

                        matched = True
                        break

                if not matched:
                    continue

                events.append({

                    "text":
                        sentence.strip(),

                    "source_id":
                        document.get(
                            "source_id"
                        ),

                    "source_name":
                        document.get(
                            "source_name"
                        ),

                    "published_at":
                        document.get(
                            "published_at"
                        )
                })

        return self._unique_events(
            events
        )[:50]

    # =====================================================
    # TIMELINE
    # =====================================================

    def _build_timeline(
        self,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        timeline = []

        for index, event in enumerate(
            events
        ):

            timeline.append({

                "sequence":
                    index + 1,

                "event":
                    event.get(
                        "text"
                    ),

                "source":
                    event.get(
                        "source_name"
                    ),

                "date":
                    event.get(
                        "published_at"
                    )
            })

        return timeline

    # =====================================================
    # FACTS
    # =====================================================

    def _build_facts(
        self,
        documents: List[Dict[str, Any]],
        evidence: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        facts = []

        evidence_claims = evidence.get(
            "claims",
            []
        )

        if isinstance(
            evidence_claims,
            list
        ):

            for claim in evidence_claims:

                if not isinstance(
                    claim,
                    dict
                ):
                    continue

                if claim.get(
                    "publication_status"
                ) in {
                    "STRONG_SUPPORT",
                    "MODERATE_SUPPORT"
                }:

                    facts.append({

                        "text":
                            claim.get(
                                "claim"
                            ),

                        "confidence":
                            claim.get(
                                "evidence_score",
                                0
                            ),

                        "sources":
                            claim.get(
                                "supporting_sources",
                                []
                            ),

                        "status":
                            "SUPPORTED"
                    })

        if facts:

            return self._unique_fact_objects(
                facts
            )[:50]

        for document in documents:

            for sentence in document.get(
                "sentences",
                []
            ):

                lowered = sentence.lower()

                if self._looks_like_fact(
                    lowered
                ):

                    facts.append({

                        "text":
                            sentence.strip(),

                        "confidence":
                            50,

                        "sources":
                            [
                                document.get(
                                    "source_name"
                                )
                            ],

                        "status":
                            "SOURCE_REPORTED"
                    })

        return self._unique_fact_objects(
            facts
        )[:50]

    # =====================================================
    # DISPUTED INFORMATION
    # =====================================================

    def _build_disputed_information(
        self,
        documents: List[Dict[str, Any]],
        evidence: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        disputed = []

        evidence_claims = evidence.get(
            "claims",
            []
        )

        if isinstance(
            evidence_claims,
            list
        ):

            for claim in evidence_claims:

                if not isinstance(
                    claim,
                    dict
                ):
                    continue

                status = claim.get(
                    "publication_status"
                )

                dimensions = claim.get(
                    "evidence_dimensions",
                    {}
                )

                if not isinstance(
                    dimensions,
                    dict
                ):
                    dimensions = {}

                contradiction = dimensions.get(
                    "contradiction",
                    0
                )

                try:
                    contradiction = float(
                        contradiction
                    )
                except (
                    TypeError,
                    ValueError
                ):
                    contradiction = 0

                if (
                    status == "HOLD_FOR_REVIEW"
                    or
                    contradiction >= 50
                ):

                    disputed.append({

                        "text":
                            claim.get(
                                "claim"
                            ),

                        "sources":
                            claim.get(
                                "supporting_sources",
                                []
                            ),

                        "opposing_sources":
                            claim.get(
                                "opposing_sources",
                                []
                            ),

                        "status":
                            "DISPUTED"
                    })

        for document in documents:

            for sentence in document.get(
                "sentences",
                []
            ):

                lowered = sentence.lower()

                if any(
                    marker in lowered
                    for marker
                    in self.dispute_markers
                ):

                    disputed.append({

                        "text":
                            sentence.strip(),

                        "sources":
                            [
                                document.get(
                                    "source_name"
                                )
                            ],

                        "opposing_sources":
                            [],

                        "status":
                            "SOURCE_DISPUTED"
                    })

        return self._unique_fact_objects(
            disputed
        )[:30]

    # =====================================================
    # UNKNOWN INFORMATION
    # =====================================================

    def _identify_unknowns(
        self,
        facts: List[Dict[str, Any]],
        disputed: List[Dict[str, Any]],
        documents: List[Dict[str, Any]]
    ) -> List[str]:

        unknowns = []

        if not facts:

            unknowns.append(
                "The central facts still require verification."
            )

        if disputed:

            unknowns.append(
                "Some information remains disputed."
            )

        if not documents:

            unknowns.append(
                "No source documents were available."
            )

        return self._unique(
            unknowns
        )[:10]

    # =====================================================
    # CONSEQUENCES
    # =====================================================

    def _build_consequences(
        self,
        documents: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> List[str]:

        consequences = []

        supplied = metadata.get(
            "consequences",
            []
        )

        if isinstance(
            supplied,
            list
        ):

            consequences.extend(
                str(item)
                for item in supplied
            )

        markers = [
            "impact",
            "effect",
            "consequence",
            "result",
            "could lead",
            "may lead",
            "will affect"
        ]

        for document in documents:

            for sentence in document.get(
                "sentences",
                []
            ):

                lowered = sentence.lower()

                if any(
                    marker in lowered
                    for marker
                    in markers
                ):

                    consequences.append(
                        sentence.strip()
                    )

        return self._unique(
            consequences
        )[:20]
