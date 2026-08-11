"""
AI NEWS FACTORY
EDITORIAL ANGLE ENGINE
"""

from typing import Any, Dict, List
import re


class AngleEngine:

    def __init__(self):
        self.name = "Editorial Angle Intelligence Engine"
        self.version = "2.0.0"

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
            "impact", "effect", "affect", "cost", "price",
            "jobs", "economy", "business", "market", "people",
            "families", "workers", "consumers", "government",
            "policy", "change", "risk", "warning", "benefit",
            "loss"
        }

        self.development_words = {
            "new", "latest", "update", "breaking", "announced",
            "announces", "confirmed", "approved", "rejected",
            "released", "launched", "agreed", "signed",
            "arrested", "resigned", "elected", "ordered", "banned"
        }

        self.uncertainty_words = {
            "may", "might", "could", "possible", "unclear",
            "unknown", "investigation", "alleged", "reportedly",
            "unconfirmed", "expected", "pending"
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

        story = story if isinstance(story, dict) else {}
        related_stories = (
            related_stories
            if isinstance(related_stories, list)
            else []
        )
        evidence = (
            evidence
            if isinstance(evidence, list)
            else []
        )
        trend_data = (
            trend_data
            if isinstance(trend_data, dict)
            else {}
        )

        text = self._story_text(story)
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
                candidates.append(candidate)

        candidates = self._deduplicate(candidates)
        candidates.sort(
            key=lambda item: item.get("angle_score", 0),
            reverse=True
        )

        primary = candidates[0] if candidates else None

        return {
            "engine": self.name,
            "version": self.version,
            "status": "ANGLE_ANALYSIS_COMPLETE",
            "primary_angle": primary,
            "alternative_angles": candidates[1:8],
            "all_angles": candidates,
            "editorial_recommendation": (
                self._recommendation(candidates)
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
        description = ""

        if angle_type == "BREAKING_DEVELOPMENT":
            score = (
                signals["newness"] * 0.45 +
                signals["recency"] * 0.30 +
                signals["evidence_strength"] * 0.25
            )
            reason = (
                "The story contains a potentially new "
                "or newly confirmed development."
            )
            description = (
                "Lead with what has just changed and "
                "what is newly confirmed."
            )

        elif angle_type == "WHY_IT_MATTERS":
            score = (
                signals["impact"] * 0.50 +
                signals["specificity"] * 0.25 +
                signals["evidence_strength"] * 0.25
            )
            reason = (
                "The available information suggests "
                "meaningful consequences for readers."
            )
            description = (
                "Explain the significance instead of "
                "merely repeating the announcement."
            )

        elif angle_type == "WHAT_CHANGED":
            score = (
                signals["newness"] * 0.40 +
                signals["comparison"] * 0.35 +
                signals["clarity"] * 0.25
            )
            reason = (
                "There is enough information to identify "
                "a meaningful change."
            )
            description = (
                "Clearly compare the situation before "
                "and after the development."
            )

        elif angle_type == "WHAT_HAPPENS_NEXT":
            score = (
                signals["future_signal"] * 0.45 +
                signals["impact"] * 0.30 +
                signals["specificity"] * 0.25
            )
            reason = (
                "The story contains identifiable next "
                "steps, deadlines or pending decisions."
            )
            description = (
                "Focus on the next confirmed steps and "
                "what readers should watch."
            )

        elif angle_type == "IMPACT":
            score = (
                signals["impact"] * 0.55 +
                signals["human_relevance"] * 0.25 +
                signals["evidence_strength"] * 0.20
            )
            reason = (
                "The development has a direct or indirect "
                "effect on people, organizations or markets."
            )
            description = (
                "Center the measurable or clearly "
                "supported consequences."
            )

        elif angle_type == "CONSEQUENCES":
            score = (
                signals["impact"] * 0.45 +
                signals["future_signal"] * 0.35 +
                signals["specificity"] * 0.20
            )
            reason = (
                "The story provides evidence of possible "
                "downstream effects."
            )
            description = (
                "Explore supported consequences while "
                "clearly separating facts from projections."
            )

        elif angle_type == "TIMELINE":
            score = (
                signals["timeline"] * 0.60 +
                signals["comparison"] * 0.25 +
                signals["clarity"] * 0.15
            )
            reason = (
                "Multiple developments or dates can be "
                "connected into a useful sequence."
            )
            description = (
                "Show readers how the story developed "
                "from the beginning to the latest update."
            )

        elif angle_type == "EXPLAINER":
            score = (
                signals["complexity"] * 0.40 +
                signals["reader_need"] * 0.35 +
                signals["context"] * 0.25
            )
            reason = (
                "The subject contains terminology, "
                "background or mechanics that readers "
                "may need explained."
            )
            description = (
                "Explain the underlying issue in simple "
                "language before discussing its impact."
            )

        elif angle_type == "CONTEXT":
            score = (
                signals["context"] * 0.50 +
                signals["comparison"] * 0.25 +
                signals["reader_need"] * 0.25
            )
            reason = (
                "Background information materially "
                "improves understanding."
            )
            description = (
                "Add only the background necessary to "
                "understand why this development matters."
            )

        elif angle_type == "HUMAN_IMPACT":
            score = (
                signals["human_relevance"] * 0.55 +
                signals["impact"] * 0.30 +
                signals["specificity"] * 0.15
            )
            reason = (
                "The story has a clear human consequence."
            )
            description = (
                "Show how the development affects real "
                "people without manufacturing emotion."
            )

        elif angle_type == "BUSINESS_IMPACT":
            score = (
                signals["business"] * 0.55 +
                signals["impact"] * 0.30 +
                signals["data"] * 0.15
            )
            reason = (
                "The story contains meaningful business, "
                "market, consumer or economic implications."
            )
            description = (
                "Focus on the verified business or "
                "economic consequences."
    )
