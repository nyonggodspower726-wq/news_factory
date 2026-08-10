"""
AI NEWS FACTORY
EDITORIAL ANGLE ENGINE

Purpose
-------
Find the strongest editorial angle for a developing story.

The factory should not simply rewrite existing articles.

It should ask:

    - What is actually new?
    - What matters most?
    - Who is affected?
    - What changed?
    - Why should the reader care?
    - What is the consequence?
    - What remains unknown?
    - Is there a useful context angle?
    - Is there a human-interest angle?
    - Is there a business/economic angle?
    - Is there a timeline/development angle?

This engine generates candidate angles.

It does NOT invent facts.

Every angle must ultimately be supported by available
evidence before publication.
"""


from typing import Any, Dict, List, Set
import re


class AngleEngine:

    def __init__(self):

        self.name = "Editorial Angle Intelligence Engine"
        self.version = "1.0.0"

        self.angle_types = [

            "BREAKING_DEVELOPMENT",
            "WHY_IT_MATTERS",
            "WHAT_CHANGED",
            "WHAT_HAPPENS_NEXT",
            "IMPACT",
            "CONSEQUENCES",
            "TIMELINE",
            "EXPLAINER",
            "CONTEXT",
            "HUMAN_IMPACT",
            "BUSINESS_IMPACT",
            "POLITICAL_IMPACT",
            "TECHNOLOGY_IMPACT",
            "PUBLIC_REACTION",
            "CONTROVERSY",
            "UNANSWERED_QUESTIONS",
            "DATA_ANGLE",
            "COMPARISON"
        ]

        self.impact_words = {

            "impact",
            "effect",
            "affect",
            "cost",
            "price",
            "jobs",
            "economy",
            "business",
            "market",
            "people",
            "families",
            "workers",
            "consumers",
            "government",
            "policy",
            "change",
            "risk",
            "warning",
            "benefit",
            "loss"
        }

        self.development_words = {

            "new",
            "latest",
            "update",
            "breaking",
            "announced",
            "announces",
            "confirmed",
            "approved",
            "rejected",
            "released",
            "launched",
            "agreed",
            "signed",
            "arrested",
            "resigned",
            "elected",
            "ordered",
            "banned"
        }

        self.uncertainty_words = {

            "may",
            "might",
            "could",
            "possible",
            "unclear",
            "unknown",
            "investigation",
            "alleged",
            "reportedly",
            "unconfirmed",
            "expected",
            "pending"
        }

    # =====================================================
    # MAIN
    # =====================================================

    def analyze(
        self,
        story: Dict[str, Any],
        related_stories: List[Dict[str, Any]] = None,
        evidence: List[Dict[str, Any]] = None,
        trend_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:

        story = (
            story
            if isinstance(
                story,
                dict
            )
            else {}
        )

        related_stories = (
            related_stories
            if isinstance(
                related_stories,
                list
            )
            else []
        )

        evidence = (
            evidence
            if isinstance(
                evidence,
                list
            )
            else []
        )

        trend_data = (
            trend_data
            if isinstance(
                trend_data,
                dict
            )
            else {}
        )

        text = self._story_text(
            story
        )

        candidates = []

        for angle_type in self.angle_types:

            candidate = self._generate_angle(
                angle_type,
                story,
                related_stories,
                evidence,
                trend_data,
                text
            )

            if candidate:

                candidates.append(
                    candidate
                )

        candidates = self._deduplicate(
            candidates
        )

        candidates.sort(
            key=lambda item:
                item.get(
                    "angle_score",
                    0
                ),
            reverse=True
        )

        primary = (
            candidates[0]
            if candidates
            else None
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "ANGLE_ANALYSIS_COMPLETE",

            "primary_angle":
                primary,

            "alternative_angles":
                candidates[1:8],

            "all_angles":
                candidates,

            "editorial_recommendation":
                self._recommendation(
                    candidates
                )
        }

    # =====================================================
    # GENERATE ANGLE
    # =====================================================

    def _generate_angle(
        self,
        angle_type: str,
        story: Dict[str, Any],
        related_stories: List[Dict[str, Any]],
        evidence: List[Dict[str, Any]],
        trend_data: Dict[str, Any],
        text: str
    ) -> Dict[str, Any]:

        signals = self._signals(
            story,
            related_stories,
            evidence,
            trend_data,
            text
        )

        score = 0.0

        reason = ""

        angle_description = ""

        # -------------------------------------------------
        # BREAKING DEVELOPMENT
        # -------------------------------------------------

        if angle_type == "BREAKING_DEVELOPMENT":

            score = (
                signals["newness"] * 0.45
                +
                signals["recency"] * 0.30
                +
                signals["evidence_strength"] * 0.25
            )

            reason = (
                "The story contains a potentially new "
                "or newly confirmed development."
            )

            angle_description = (
                "Lead with what has just changed and "
                "what is newly confirmed."
            )

        # -------------------------------------------------
        # WHY IT MATTERS
        # -------------------------------------------------

        elif angle_type == "WHY_IT_MATTERS":

            score = (
                signals["impact"] * 0.50
                +
                signals["specificity"] * 0.25
                +
                signals["evidence_strength"] * 0.25
            )

            reason = (
                "The available information suggests "
                "meaningful consequences for readers."
            )

            angle_description = (
                "Explain the significance instead of "
                "merely repeating the announcement."
            )

        # -------------------------------------------------
        # WHAT CHANGED
        # -------------------------------------------------

        elif angle_type == "WHAT_CHANGED":

            score = (
                signals["newness"] * 0.40
                +
                signals["comparison"] * 0.35
                +
                signals["clarity"] * 0.25
            )

            reason = (
                "There is enough information to identify "
                "a meaningful change."
            )

            angle_description = (
                "Clearly compare the situation before "
                "and after the development."
            )

        # -------------------------------------------------
        # WHAT HAPPENS NEXT
        # -------------------------------------------------

        elif angle_type == "WHAT_HAPPENS_NEXT":

            score = (
                signals["future_signal"] * 0.45
                +
                signals["impact"] * 0.30
                +
                signals["specificity"] * 0.25
            )

            reason = (
                "The story contains identifiable next "
                "steps, deadlines or pending decisions."
            )

            angle_description = (
                "Focus on the next confirmed steps and "
                "what readers should watch."
            )

        # -------------------------------------------------
        # IMPACT
        # -------------------------------------------------

        elif angle_type == "IMPACT":

            score = (
                signals["impact"] * 0.55
                +
                signals["human_relevance"] * 0.25
                +
                signals["evidence_strength"] * 0.20
            )

            reason = (
                "The development has a direct or indirect "
                "effect on people, organizations or markets."
            )

            angle_description = (
                "Center the measurable or clearly "
                "supported consequences."
            )

        # -------------------------------------------------
        # CONSEQUENCES
        # -------------------------------------------------

        elif angle_type == "CONSEQUENCES":

            score = (
                signals["impact"] * 0.45
                +
                signals["future_signal"] * 0.35
                +
                signals["specificity"] * 0.20
            )

            reason = (
                "The story provides evidence of possible "
                "downstream effects."
            )

            angle_description = (
                "Explore supported consequences while "
                "clearly separating facts from projections."
            )

        # -------------------------------------------------
        # TIMELINE
        # -------------------------------------------------

        elif angle_type == "TIMELINE":

            score = (
                signals["timeline"] * 0.60
                +
                signals["comparison"] * 0.25
                +
                signals["clarity"] * 0.15
            )

            reason = (
                "Multiple developments or dates can be "
                "connected into a useful sequence."
            )

            angle_description = (
                "Show readers how the story developed "
                "from the beginning to the latest update."
            )

        # -------------------------------------------------
        # EXPLAINER
        # -------------------------------------------------

        elif angle_type == "EXPLAINER":

            score = (
                signals["complexity"] * 0.40
                +
                signals["reader_need"] * 0.35
                +
                signals["context"] * 0.25
            )

            reason = (
                "The subject contains terminology, "
                "background or mechanics that readers "
                "may need explained."
            )

            angle_description = (
                "Explain the underlying issue in simple "
                "language before discussing its impact."
            )

        # -------------------------------------------------
        # CONTEXT
        # -------------------------------------------------

        elif angle_type == "CONTEXT":

            score = (
                signals["context"] * 0.50
                +
                signals["comparison"] * 0.25
                +
                signals["reader_need"] * 0.25
            )

            reason = (
                "Background information materially "
                "improves understanding."
            )

            angle_description = (
                "Add only the background necessary to "
                "understand why this development matters."
            )

        # -------------------------------------------------
        # HUMAN IMPACT
        # -------------------------------------------------

        elif angle_type == "HUMAN_IMPACT":

            score = (
                signals["human_relevance"] * 0.55
                +
                signals["impact"] * 0.30
                +
                signals["specificity"] * 0.15
            )

            reason = (
                "The story has a clear human consequence."
            )

            angle_description = (
                "Show how the development affects real "
                "people without manufacturing emotion."
            )

        # -------------------------------------------------
        # BUSINESS IMPACT
        # -------------------------------------------------

        elif angle_type == "BUSINESS_IMPACT":

            score = (
                signals["business"] * 0.55
                +
                signals["impact"] * 0.30
                +
                signals["data"] * 0.15
            )

            reason = (
                "The story contains meaningful business, "
                "market, consumer or economic implications."
            )

            angle_description = (
                "Focus on the verified business or "
                "economic consequences."
            )

        # -------------------------------------------------
        # POLITICAL IMPACT
        # -------------------------------------------------

        elif angle_type == "POLITICAL_IMPACT":

            score = (
                signals["political"] * 0.50
                +
                signals["impact"] * 0.30
                +
                signals["evidence_strength"] * 0.20
            )

            reason = (
                "Political institutions, policies or "
                "official decisions are central to the story."
            )

            angle_description = (
                "Explain the political significance while "
                "keeping factual reporting separate from opinion."
            )

        # -------------------------------------------------
        # TECHNOLOGY IMPACT
        # -------------------------------------------------

        elif angle_type == "TECHNOLOGY_IMPACT":

            score = (
                signals["technology"] * 0.50
                +
                signals["impact"] * 0.30
                +
                signals["reader_need"] * 0.20
            )

            reason = (
                "Technology is central and the development "
                "has practical implications."
            )

            angle_description = (
                "Explain what the technology actually "
                "changes for users or organizations."
            )

        # -------------------------------------------------
        # PUBLIC REACTION
        # -------------------------------------------------

        elif angle_type == "PUBLIC_REACTION":

            score = (
                signals["reaction"] * 0.55
                +
                signals["source_diversity"] * 0.25
                +
                signals["evidence_strength"] * 0.20
            )

            reason = (
                "There is enough verified reaction from "
                "relevant people or institutions."
            )

            angle_description = (
                "Report meaningful reactions and distinguish "
                "verified statements from online speculation."
            )

        # -------------------------------------------------
        # CONTROVERSY
        # -------------------------------------------------

        elif angle_type == "CONTROVERSY":

            score = (
                signals["controversy"] * 0.45
                +
                signals["source_diversity"] * 0.30
                +
                signals["evidence_strength"] * 0.25
            )

            reason = (
                "There are clearly documented competing "
                "claims, disputes or disagreements."
            )

            angle_description = (
                "Present the competing positions fairly "
                "and identify what is actually established."
            )

        # -------------------------------------------------
        # UNANSWERED QUESTIONS
        # -------------------------------------------------

        elif angle_type == "UNANSWERED_QUESTIONS":

            score = (
                signals["uncertainty"] * 0.50
                +
                signals["reader_need"] * 0.30
                +
                signals["complexity"] * 0.20
            )

            reason = (
                "Important information remains unresolved."
            )

            angle_description = (
                "Identify the important unanswered questions "
                "without turning uncertainty into speculation."
            )

        # -------------------------------------------------
        # DATA ANGLE
        # -------------------------------------------------

        elif angle_type == "DATA_ANGLE":

            score = (
                signals["data"] * 0.60
                +
                signals["comparison"] * 0.25
                +
                signals["specificity"] * 0.15
            )

            reason = (
                "Numbers, measurable changes or datasets "
                "could materially improve the story."
            )

            angle_description = (
                "Lead with verified numbers and explain "
                "what they mean."
            )

        # -------------------------------------------------
        # COMPARISON
        # -------------------------------------------------

        elif angle_type == "COMPARISON":

            score = (
                signals["comparison"] * 0.55
                +
                signals["context"] * 0.25
                +
                signals["reader_need"] * 0.20
            )

            reason = (
                "The story can be better understood through "
                "a factual comparison."
            )

            angle_description = (
                "Compare the current development with a "
                "relevant previous situation."
            )

        else:

            return {}

        score = min(
            1.0,
            max(
                0.0,
                score
            )
        )

        if score < 0.20:

            return {}

        headline_direction = (
            self._headline_direction(
                angle_type,
                story
            )
        )

        return {

            "angle_type":
                angle_type,

            "angle_score":
                round(
                    score * 100,
                    2
                ),

            "reason":
                reason,

            "angle_description":
                angle_description,

            "headline_direction":
                headline_direction,

            "supporting_signals":
                signals,

            "safety_note":
                (
                    "Use only claims supported by "
                    "
