"""
AI NEWS FACTORY
NARRATIVE INTELLIGENCE ENGINE

Purpose
-------
Turn a synthesized news story into an intelligent narrative
blueprint for the journalist engine.

The engine decides:

    - the strongest legitimate opening
    - the information hierarchy
    - reader curiosity points
    - context placement
    - pacing
    - transition opportunities
    - consequence emphasis
    - unanswered questions
    - article structure

SAFETY PRINCIPLE
----------------
Engagement must come from information value.

Never manufacture:

    - facts
    - quotes
    - statistics
    - outrage
    - fear
    - controversy
    - certainty

The engine may create curiosity around REAL unknowns,
important consequences, surprising verified details and
meaningful context.

OUTPUT
------
A narrative blueprint.

It does NOT write the final article.
"""


from typing import Any, Dict, List
import re


class NarrativeEngine:

    def __init__(self):

        self.name = "Narrative Intelligence Engine"
        self.version = "1.0.0"

        self.opening_priorities = [
            "BREAKING_DEVELOPMENT",
            "HIGH_IMPACT_FACT",
            "HUMAN_CONSEQUENCE",
            "SURPRISING_CONTEXT",
            "IMPORTANT_CONFLICT",
            "TIMELINE"
        ]

        self.section_types = [
            "LEAD",
            "WHAT_HAPPENED",
            "KEY_DETAILS",
            "CONTEXT",
            "WHY_IT_MATTERS",
            "WHAT_COMES_NEXT",
            "UNANSWERED_QUESTIONS"
        ]

        self.curiosity_patterns = [
            "what happens next",
            "why it matters",
            "what changed",
            "what is known",
            "what remains unclear",
            "how it happened",
            "what comes next"
        ]

    # =====================================================
    # MAIN
    # =====================================================

    def build_blueprint(
        self,
        story: Dict[str, Any],
        psychology: Dict[str, Any] = None,
        audience: Dict[str, Any] = None
    ) -> Dict[str, Any]:

        story = (
            story
            if isinstance(
                story,
                dict
            )
            else {}
        )

        psychology = (
            psychology
            if isinstance(
                psychology,
                dict
            )
            else {}
        )

        audience = (
            audience
            if isinstance(
                audience,
                dict
            )
            else {}
        )

        facts = self._list(
            story.get(
                "confirmed_facts",
                []
            )
        )

        disputed = self._list(
            story.get(
                "disputed_information",
                []
            )
        )

        unknowns = self._list(
            story.get(
                "unknowns",
                []
            )
        )

        timeline = self._list(
            story.get(
                "timeline",
                []
            )
        )

        consequences = self._list(
            story.get(
                "consequences",
                []
            )
        )

        entities = story.get(
            "entities",
            {}
        )

        central_event = str(
            story.get(
                "central_event",
                ""
            )
        )

        story_type = str(
            story.get(
                "story_type",
                "GENERAL_NEWS"
            )
        )

        significance = story.get(
            "why_it_matters",
            {}
        )

        opening = self._select_opening(
            central_event,
            facts,
            consequences,
            disputed,
            significance,
            story_type
        )

        curiosity = self._build_curiosity(
            facts,
            unknowns,
            consequences,
            disputed
        )

        hierarchy = self._build_information_hierarchy(
            facts,
            consequences,
            disputed,
            unknowns
        )

        structure = self._build_structure(
            facts,
            consequences,
            unknowns,
            disputed,
            timeline,
            story_type
        )

        pacing = self._build_pacing(
            story_type,
            significance,
            psychology
        )

        transitions = self._build_transitions(
            structure
        )

        audience_angle = self._audience_angle(
            story,
            audience
        )

        headline_direction = (
            self._headline_direction(
                opening,
                story_type,
                significance
            )
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "BLUEPRINT_READY",

            "narrative": {

                "opening":
                    opening,

                "headline_direction":
                    headline_direction,

                "information_hierarchy":
                    hierarchy,

                "curiosity_points":
                    curiosity,

                "structure":
                    structure,

                "pacing":
                    pacing,

                "transitions":
                    transitions,

                "audience_angle":
                    audience_angle,

                "editorial_guardrails":
                    self._guardrails(
                        disputed,
                        unknowns
                    )
            }
        }

    # =====================================================
    # OPENING
    # =====================================================

    def _select_opening(
        self,
        central_event: str,
        facts: List[Any],
        consequences: List[Any],
        disputed: List[Any],
        significance: Dict[str, Any],
        story_type: str
    ) -> Dict[str, Any]:

        significance_score = self._number(
            significance.get(
                "score",
                0
            ),
            0
        )

        if central_event:

            primary = central_event

        elif facts:

            primary = self._text(
                facts[0]
            )

        else:

            primary = (
                "Lead with the clearest verified development."
            )

        if consequences:

            reason = (
                "The opening should quickly connect the development "
                "to why readers should care."
            )

        elif significance_score >= 70:

            reason = (
                "The story has substantial significance; lead directly "
                "with the strongest verified development."
            )

        elif disputed:

            reason = (
                "Because important details are disputed, lead with "
                "what is confirmed before explaining the disagreement."
            )

        else:

            reason = (
                "Lead with the clearest confirmed development and "
                "avoid unnecessary buildup."
            )

        return {

            "type":
                "DIRECT_NEWS_LEAD",

            "primary_material":
                primary,

            "reason":
                reason,

            "story_type":
                story_type
        }

    # =====================================================
    # CURIOSITY
    # =====================================================

    def _build_curiosity(
        self,
        facts: List[Any],
        unknowns: List[Any],
        consequences: List[Any],
        disputed: List[Any]
    ) -> List[Dict[str, Any]]:

        points = []

        if consequences:

            for item in consequences[:3]:

                text = self._text(
                    item
                )

                if text:

                    points.append({

                        "type":
                            "CONSEQUENCE",

                        "question":
                            "Why does this development matter?",

                        "basis":
                            text,

                        "safe":
                            True
                    })

        if unknowns:

            for item in unknowns[:3]:

                text = self._text(
                    item
                )

                if text:

                    points.append({

                        "type":
                            "OPEN_QUESTION",

                        "question":
                            text,

                        "basis":
                            "Known information gap",

                        "safe":
                            True
                    })

        if disputed:

            points.append({

                "type":
                    "CONFLICT",

                "question":
                    "What do the available sources agree and disagree about?",

                "basis":
                    "Conflicting evidence",

                "safe":
                    True
            })

        if facts:

            points.append({

                "type":
                    "KEY_DETAIL",

                "question":
                    "What is the most important verified detail?",

                "basis":
                    self._text(
                        facts[0]
                    ),

                "safe":
                    True
            })

        return points[:10]

    # =====================================================
    # INFORMATION HIERARCHY
    # =====================================================

    def _build_information_hierarchy(
        self,
        facts: List[Any],
        consequences: List[Any],
        disputed: List[Any],
        unknowns: List[Any]
    ) -> List[Dict[str, Any]]:

        hierarchy = []

        for index, fact in enumerate(
            facts[:10]
        ):

            hierarchy.append({

                "rank":
                    index + 1,

                "category":
                    "FACT",

                "content":
                    self._text(
                        fact
                    ),

                "priority":
                    self._priority(
                        fact
                    )
            })

        for consequence in consequences[:5]:

            hierarchy.append({

                "rank":
                    len(hierarchy) + 1,

                "category":
                    "CONSEQUENCE",

                "content":
                    self._text(
                        consequence
                    ),

                "priority":
                    75
            })

        for item in disputed[:5]:

            hierarchy.append({

                "rank":
                    len(hierarchy) + 1,

                "category":
                    "DISPUTED",

                "content":
                    self._text(
                        item
                    ),

                "priority":
                    70
            })

        for item in unknowns[:5]:

            hierarchy.append({

                "rank":
                    len(hierarchy) + 1,

                "category":
                    "UNKNOWN",

                "content":
                    self._text(
                        item
                    ),

                "priority":
                    55
            })

        hierarchy.sort(
            key=lambda item:
                item.get(
                    "priority",
                    0
                ),
            reverse=True
        )

        for index, item in enumerate(
            hierarchy
        ):

            item[
                "rank"
            ] = index + 1

        return hierarchy[:20]

    # =====================================================
    # STRUCTURE
    # =====================================================

    def _build_structure(
        self,
        facts: List[Any],
        consequences: List[Any],
        unknowns: List[Any],
        disputed: List[Any],
        timeline: List[Any],
        story_type: str
    ) -> List[Dict[str, Any]]:

        structure = []

        structure.append({

            "position":
                1,

            "section":
                "LEAD",

            "purpose":
                "State the strongest verified development immediately.",

            "source_material":
                self._texts(
                    facts[:2]
                )
        })

        structure.append({

            "position":
                2,

            "section":
                "WHAT_HAPPENED",

            "purpose":
                "Explain the core event in plain language.",

            "source_material":
                self._texts(
                    facts[:5]
                )
        })

        if len(
            facts
        ) > 5:

            structure.append({

                "position":
                    len(structure) + 1,

                "section":
                    "KEY_DETAILS",

                "purpose":
                    "Add important verified details.",

                "source_material":
                    self._texts(
                        facts[5:10]
                    )
            })

        if timeline:

            structure.append({

                "position":
                    len(structure) + 1,

                "section":
                    "TIMELINE",

                "purpose":
                    "Explain how the development unfolded.",

                "source_material":
                    self._texts(
                        timeline[:8]
                    )
            })

        structure.append({

            "position":
                len(structure) + 1,

            "section":
                "CONTEXT",

            "purpose":
                "Give readers enough background to understand the event.",

            "source_material":
                []
        })

        if consequences:

            structure.append({

                "position":
                    len(structure) + 1,

                "section":
                    "WHY_IT_MATTERS",

                "purpose":
                    "Explain verified or clearly attributed consequences.",

                "source_material":
                    self._texts(
                        consequences[:5]
                    )
            })

        if disputed:

            structure.append({

                "position":
                    len(structure) + 1,

                "section":
                    "WHAT_IS_DISPUTED",

                "purpose":
                    "Present disagreements fairly and identify who says what.",

                "source_material":
                    self._texts(
                        disputed[:5]
                    )
            })

        if unknowns:

            structure.append({

                "position":
                    len(structure) + 1,

                "section":
                    "WHAT_COMES_NEXT",

                "purpose":
                    "Explain what remains unresolved and what readers should watch.",

                "source_material":
                    self._texts(
                        unknowns[:5]
                    )
            })

        return structure

    # =====================================================
    # PACING
    # =====================================================

    def _build_pacing(
        self,
        story_type: str,
        significance: Dict[str, Any],
        psychology: Dict[str, Any]
    ) -> Dict[str, Any]:

        significance_score = self._number(
            significance.get(
                "score",
                50
            ),
            50
        )

        if significance_score >= 80:

            speed = "FAST"

        elif significance_score >= 60:

            speed = "MEDIUM_FAST"

        else:

            speed = "MODERATE"

        attention = psychology.get(
            "attention_strategy",
            {}
        )

        if isinstance(
            attention,
            dict
        ):

            preferred = attention.get(
                "pacing"
            )

            if preferred:

                speed = str(
                    preferred
                ).upper()

        return {

            "overall":
                speed,

            "lead":
                "FAST",

            "middle":
                "INFORMATIVE",

            "context":
                "CONTROLLED",

            "ending":
                "FORWARD_LOOKING",

            "rule":
                "Every section should add information, context or consequence."
        }

    # =====================================================
    # TRANSITIONS
    # =====================================================

    def _build_transitions(
        self,
        structure: List[Dict[str, Any]]
    ) -> List[str]:

        transitions = []

        for index in range(
            len(structure) - 1
        ):

            current = structure[
                index
            ].get(
                "section",
                ""
            )

            next_section = structure[
                index + 1
            ].get(
                "section",
                ""
            )

            transitions.append(
                self._transition(
                    current,
                    next_section
                )
            )

        return transitions

    def _transition(
        self,
        current: str,
        next_section: str
    ) -> str:

        mapping = {

            (
                "LEAD",
                "WHAT_HAPPENED"
            ):
                "Here is what is known so far.",

            (
                "WHAT_HAPPENED",
                "KEY_DETAILS"
            ):
                "Several details help put the development in perspective.",

            (
                "WHAT_HAPPENED",
                "TIMELINE"
            ):
                "The sequence of events helps explain how the situation reached this point.",

            (
                "TIMELINE",
                "CONTEXT"
            ):
                "To understand why this matters, some background is important.",

            (
                "CONTEXT",
                "WHY_IT_MATTERS"
            ):
                "That context makes the potential impact clearer.",

            (
                "WHY_IT_MATTERS",
                "WHAT_IS_DISPUTED"
            ):
                "But not every part of the story is settled.",

            (
                "WHAT_IS_DISPUTED",
                "WHAT_COMES_NEXT"
            ):
                "The remaining question is what happens from here."
        }

        return mapping.get(
            (
                current,
                next_section
            ),
            "The next part of the story adds important context."
        )

    # =====================================================
    # AUDIENCE ANGLE
    # =====================================================

    def _audience_angle(
        self,
        story: Dict[str, Any],
        audience: Dict[str, Any]
    ) -> Dict[str, Any]:

        location = audience.get(
            "location"
        )

        interest = audience.get(
            "interest"
        )

        if location:

            angle = (
                f"Prioritize how the development affects "
                f"readers in {location}, where evidence supports it."
            )

        elif interest:

            angle = (
                f"Prioritize the implications most relevant to "
                f"{interest} readers."
            )

        else:

            angle = (
                "Prioritize the information most useful to a general reader."
            )

        return {

            "angle":
                angle,

            "principle":
                "Audience relevance must come from the facts, not invented personalization."
        }

    # =====================================================
    # HEADLINE DIRECTION
    # =====================================================

    def _headline_direction(
        self,
        opening: Dict[str, Any],
        story_type: str,
        significance: Dict[str, Any]
    ) -> Dict[str, Any]:

        score = self._number(
            significance.get(
                "score",
                0
            ),
            0
        )

        if score >= 80:

            style = "IMPACT_FIRST"

        elif score >= 60:

            style = "DEVELOPMENT_FIRST"

        else:

            style = "CLEAR_FACT_FIRST"

        return {

            "style":
                style,

            "must_include":
                [
                    "verified core development"
                ],

            "avoid":
                [
                    "unsupported superlatives",
                    "fake urgency",
                    "misleading omissions",
                    "claims stronger than the evidence"
                ],

            "opening_basis":
                opening.get(
                    "primary_material",
                    ""
                )
        }

    # =====================================================
    # GUARDRAILS
    # =====================================================

    def _guardrails(
        self,
        disputed: List[Any],
        unknowns: List[Any]
    ) -> List[str]:

        rules = [

            "Never convert an allegation into a fact.",

            "Never invent missing details.",

            "Never create a quote that was not supplied.",

            "Do not hide material uncertainty.",

            "Do not use misleading clickbait.",

            "Do not repeat the same fact merely to increase article length."
        ]

        if disputed:

            rules.append(
                "Clearly attribute competing claims."
            )

        if unknowns:

            rules.append(
                "Use genuine unanswered questions as reader-interest points."
            )

        return rules

    # =====================================================
    # HELPERS
    # =====================================================

    def _text(
        self,
        item: Any
    ) -> str:

        if isinstance(
            item,
            str
        ):

            return item.strip()

        if isinstance(
            item,
            dict
        ):

            for key in [
                "text",
                "claim",
                "event",
                "content",
                "question"
            ]:

                if item.get(
                    key
                ):

                    return str(
                        item.get(
                            key
                        )
                    ).strip()

        return str(
            item
        ).strip()

    def _texts(
        self,
        items: List[Any]
    ) -> List[str]:

        output = []

        for item in items:

            text = self._text(
                item
            )

            if text:

                output.append(
                    text
                )

        return output

    def _list(
        self,
        value: Any
    ) -> List[Any]:

        if isinstance(
            value,
            list
        ):

            return value

        if isinstance(
            value,
            tuple
        ):

            return list(
                value
            )

        if value:

            return [
                value
            ]

        return []

    def _priority(
        self,
        item: Any
    ) -> int:

        if not isinstance(
            item,
            dict
        ):

            return 50

        confidence = self._number(
            item.get(
                "confidence",
                50
            ),
            50
        )

        return int(
            confidence
        )

    def _number(
        self,
        value: Any,
        default: float
    ) -> float:

        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return default


# =========================================================
# HELPER FUNCTION
# =========================================================

def build_narrative_blueprint(
    story: Dict[str, Any],
    psychology: Dict[str, Any] = None,
    audience: Dict[str, Any] = None
) -> Dict[str, Any]:

    engine = NarrativeEngine()

    return engine.build_blueprint(
        story,
        psychology,
        audience
    )
