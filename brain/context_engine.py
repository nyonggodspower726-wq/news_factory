"""
AI NEWS FACTORY
CONTEXT & CONSEQUENCE ENGINE

Purpose
-------
Transform verified events into useful context.

The engine identifies:

    - what happened
    - what led to it
    - timeline
    - affected groups
    - geographic relevance
    - immediate consequences
    - potential next steps
    - historical context
    - unanswered questions
    - reader relevance

IMPORTANT
---------
The engine separates:

    FACT
    CONTEXT
    INFERENCE
    POSSIBILITY

It must never present speculation as established fact.

This engine does NOT replace the fact checker.
It works downstream of factual verification.
"""

from typing import Any, Dict, List
from collections import defaultdict
import re


class ContextEngine:

    def __init__(self):

        self.name = "Context & Consequence Engine"
        self.version = "1.0.0"

        self.max_timeline_events = 20
        self.max_consequences = 10
        self.max_questions = 10

    # =====================================================
    # MAIN
    # =====================================================

    def analyze(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        facts = self._extract_facts(
            story
        )

        timeline = self._build_timeline(
            story
        )

        affected_groups = (
            self._identify_affected_groups(
                story
            )
        )

        locations = (
            self._identify_locations(
                story
            )
        )

        causes = (
            self._identify_causes(
                story
            )
        )

        consequences = (
            self._identify_consequences(
                story
            )
        )

        next_steps = (
            self._identify_next_steps(
                story
            )
        )

        historical_context = (
            self._historical_context(
                story
            )
        )

        reader_questions = (
            self._reader_questions(
                story
            )
        )

        relevance = (
            self._relevance_score(
                story,
                affected_groups,
                locations,
                consequences
            )
        )

        context_quality = (
            self._context_quality(
                facts,
                timeline,
                causes,
                consequences,
                next_steps,
                historical_context
            )
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "ANALYZED",

            "facts":
                facts,

            "timeline":
                timeline,

            "causes":
                causes,

            "affected_groups":
                affected_groups,

            "locations":
                locations,

            "consequences":
                consequences,

            "what_happens_next":
                next_steps,

            "historical_context":
                historical_context,

            "reader_questions":
                reader_questions,

            "reader_relevance_score":
                relevance,

            "context_quality_score":
                context_quality,

            "editorial_structure":
                self._editorial_structure(
                    context_quality,
                    relevance
                )
        }

    # =====================================================
    # FACT EXTRACTION
    # =====================================================

    def _extract_facts(
        self,
        story: Dict[str, Any]
    ) -> List[str]:

        facts = []

        candidates = [
            story.get(
                "facts"
            ),
            story.get(
                "verified_facts"
            ),
            story.get(
                "key_facts"
            )
        ]

        for candidate in candidates:

            if isinstance(
                candidate,
                list
            ):

                facts.extend(
                    str(item)
                    for item in candidate
                    if item
                )

            elif isinstance(
                candidate,
                str
            ):

                facts.append(
                    candidate
                )

        return self._unique(
            facts
        )

    # =====================================================
    # TIMELINE
    # =====================================================

    def _build_timeline(
        self,
        story: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        raw = story.get(
            "timeline",
            []
        )

        events = []

        if isinstance(
            raw,
            dict
        ):

            raw = [
                {
                    "date": key,
                    "event": value
                }
                for key, value
                in raw.items()
            ]

        if not isinstance(
            raw,
            list
        ):

            return []

        for item in raw:

            if isinstance(
                item,
                str
            ):

                events.append({

                    "date":
                        None,

                    "event":
                        item,

                    "status":
                        "UNSPECIFIED"
                })

            elif isinstance(
                item,
                dict
            ):

                events.append({

                    "date":
                        item.get(
                            "date"
                        ),

                    "event":
                        item.get(
                            "event",
                            item.get(
                                "description",
                                ""
                            )
                        ),

                    "status":
                        item.get(
                            "status",
                            "FACT"
                        )
                })

        return events[
            :self.max_timeline_events
        ]

    # =====================================================
    # AFFECTED GROUPS
    # =====================================================

    def _identify_affected_groups(
        self,
        story: Dict[str, Any]
    ) -> List[str]:

        groups = []

        for field in [
            "affected_groups",
            "people_affected",
            "audiences",
            "stakeholders"
        ]:

            value = story.get(
                field
            )

            if isinstance(
                value,
                list
            ):

                groups.extend(
                    str(item)
                    for item in value
                    if item
                )

            elif isinstance(
                value,
                str
            ):

                groups.append(
                    value
                )

        return self._unique(
            groups
        )

    # =====================================================
    # LOCATIONS
    # =====================================================

    def _identify_locations(
        self,
        story: Dict[str, Any]
    ) -> List[str]:

        locations = []

        for field in [
            "locations",
            "countries",
            "cities",
            "regions"
        ]:

            value = story.get(
                field
            )

            if isinstance(
                value,
                list
            ):

                locations.extend(
                    str(item)
                    for item in value
                    if item
                )

            elif isinstance(
                value,
                str
            ):

                locations.append(
                    value
                )

        return self._unique(
            locations
        )

    # =====================================================
    # CAUSES
    # =====================================================

    def _identify_causes(
        self,
        story: Dict[str, Any]
    ) -> List[Dict[str, str]]:

        causes = []

        raw = story.get(
            "causes",
            story.get(
                "background_factors",
                []
            )
        )

        if isinstance(
            raw,
            str
        ):

            raw = [
                raw
            ]

        if isinstance(
            raw,
            dict
        ):

            raw = [
                {
                    "factor": key,
                    "explanation": value
                }
                for key, value
                in raw.items()
            ]

        if not isinstance(
            raw,
            list
        ):

            return []

        for item in raw:

            if isinstance(
                item,
                str
            ):

                causes.append({

                    "factor":
                        item,

                    "explanation":
                        "",

                    "status":
                        "CONTEXT"
                })

            elif isinstance(
                item,
                dict
            ):

                causes.append({

                    "factor":
                        item.get(
                            "factor",
                            item.get(
                                "cause",
                                ""
                            )
                        ),

                    "explanation":
                        item.get(
                            "explanation",
                            ""
                        ),

                    "status":
                        item.get(
                            "status",
                            "CONTEXT"
                        )
                })

        return causes

    # =====================================================
    # CONSEQUENCES
    # =====================================================

    def _identify_consequences(
        self,
        story: Dict[str, Any]
    ) -> List[Dict[str, str]]:

        consequences = []

        raw = story.get(
            "consequences",
            story.get(
                "impact",
                []
            )
        )

        if isinstance(
            raw,
            str
        ):

            raw = [
                raw
            ]

        if isinstance(
            raw,
            dict
        ):

            raw = [
                {
                    "area": key,
                    "impact": value
                }
                for key, value
                in raw.items()
            ]

        if not isinstance(
            raw,
            list
        ):

            return []

        for item in raw:

            if isinstance(
                item,
                str
            ):

                consequences.append({

                    "area":
                        "GENERAL",

                    "impact":
                        item,

                    "certainty":
                        "UNSPECIFIED"
                })

            elif isinstance(
                item,
                dict
            ):

                consequences.append({

                    "area":
                        item.get(
                            "area",
                            "GENERAL"
                        ),

                    "impact":
                        item.get(
                            "impact",
                            item.get(
                                "description",
                                ""
                            )
                        ),

                    "certainty":
                        item.get(
                            "certainty",
                            "UNSPECIFIED"
                        )
                })

        return consequences[
            :self.max_consequences
        ]

    # =====================================================
    # NEXT STEPS
    # =====================================================

    def _identify_next_steps(
        self,
        story: Dict[str, Any]
    ) -> List[Dict[str, str]]:

        next_steps = []

        raw = story.get(
            "what_happens_next",
            story.get(
                "next_steps",
                []
            )
        )

        if isinstance(
            raw,
            str
        ):

            raw = [
                raw
            ]

        if isinstance(
            raw,
            dict
        ):

            raw = [
                {
                    "event": key,
                    "description": value
                }
                for key, value
                in raw.items()
            ]

        if not isinstance(
            raw,
            list
        ):

            return []

        for item in raw:

            if isinstance(
                item,
                str
            ):

                next_steps.append({

                    "event":
                        item,

                    "certainty":
                        "POSSIBLE"
                })

            elif isinstance(
                item,
                dict
            ):

                next_steps.append({

                    "event":
                        item.get(
                            "event",
                            item.get(
                                "description",
                                ""
                            )
                        ),

                    "certainty":
                        item.get(
                            "certainty",
                            "POSSIBLE"
                        )
                })

        return next_steps

    # =====================================================
    # HISTORICAL CONTEXT
    # =====================================================

    def _historical_context(
        self,
        story: Dict[str, Any]
    ) -> List[str]:

        context = story.get(
            "historical_context",
            story.get(
                "background",
                []
            )
        )

        if isinstance(
            context,
            str
        ):

            return [
                context
            ]

        if isinstance(
            context,
            dict
        ):

            return [
                str(value)
                for value
                in context.values()
                if value
            ]

        if isinstance(
            context,
            list
        ):

            return self._unique(
                [
                    str(item)
                    for item in context
                    if item
                ]
            )

        return []

    # =====================================================
    # READER QUESTIONS
    # =====================================================

    def _reader_questions(
        self,
        story: Dict[str, Any]
    ) -> List[str]:

        questions = story.get(
            "reader_questions",
            story.get(
                "questions",
                []
            )
        )

        if isinstance(
            questions,
            str
        ):

            questions = [
                questions
            ]

        if isinstance(
            questions,
            dict
        ):

            questions = list(
                questions.values()
            )

        if not isinstance(
            questions,
            list
        ):

            questions = []

        questions = [
            str(question)
            for question
            in questions
            if question
        ]

        # Add useful generic questions only when the
        # relevant information exists.

        if (
            story.get(
                "what_happens_next"
            )
            and
            "What happens next?"
            not in questions
        ):

            questions.append(
                "What happens next?"
            )

        if (
            story.get(
                "affected_groups"
            )
            and
            "Who is affected?"
            not in questions
        ):

            questions.append(
                "Who is affected?"
            )

        if (
            story.get(
                "why_it_matters"
            )
            and
            "Why does this matter?"
            not in questions
        ):

            questions.append(
                "Why does this matter?"
            )

        return self._unique(
            questions
        )[
            :self.max_questions
        ]

    # =====================================================
    # RELEVANCE
    # =====================================================

    def _relevance_score(
        self,
        story: Dict[str, Any],
        affected_groups: List[str],
        locations: List[str],
        consequences: List[Dict[str, str]]
    ) -> int:

        score = 0

        if affected_groups:
            score += 30

        if locations:
            score += 15

        if consequences:
            score += 25

        if story.get(
            "why_it_matters"
        ):

            score += 20

        if story.get(
            "practical_impact"
        ):

            score += 10

        return min(
            score,
            100
        )

    # =====================================================
    # CONTEXT QUALITY
    # =====================================================

    def _context_quality(
        self,
        facts: List[str],
        timeline: List[Dict[str, Any]],
        causes: List[Dict[str, str]],
        consequences: List[Dict[str, str]],
        next_steps: List[Dict[str, str]],
        historical_context: List[str]
    ) -> int:

        score = 0

        if facts:
            score += 20

        if timeline:
            score += 15

        if causes:
            score += 15

        if consequences:
            score += 20

        if next_steps:
            score += 15

        if historical_context:
            score += 15

        return min(
            score,
            100
        )

    # =====================================================
    # EDITORIAL STRUCTURE
    # =====================================================

    def _editorial_structure(
        self,
        context_quality: int,
        relevance: int
    ) -> List[str]:

        structure = [
            "What happened"
        ]

        if context_quality >= 30:
            structure.append(
                "What led to it"
            )

        if relevance >= 30:
            structure.append(
                "Who is affected"
            )

        if context_quality >= 50:
            structure.append(
                "Why it matters"
            )

        if context_quality >= 65:
            structure.append(
                "What happens next"
            )

        structure.append(
            "What remains unknown"
        )

        return structure

    # =====================================================
    # UNIQUE
    # =====================================================

    def _unique(
        self,
        items: List[str]
    ) -> List[str]:

        seen = set()
        output = []

        for item in items:

            normalized = (
                str(item)
                .strip()
                .lower()
            )

            if not normalized:
                continue

          
