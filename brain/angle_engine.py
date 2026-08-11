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
        elif angle_type == "POLITICAL_IMPACT":
            score = (
                signals["political"] * 0.50 +
                signals["impact"] * 0.30 +
                signals["evidence_strength"] * 0.20
            )
            reason = (
                "Political institutions, policies or "
                "official decisions are central to the story."
            )
            description = (
                "Explain the political significance while "
                "keeping factual reporting separate from opinion."
            )

        elif angle_type == "TECHNOLOGY_IMPACT":
            score = (
                signals["technology"] * 0.50 +
                signals["impact"] * 0.30 +
                signals["reader_need"] * 0.20
            )
            reason = (
                "Technology is central and the development "
                "has practical implications."
            )
            description = (
                "Explain what the technology actually "
                "changes for users or organizations."
            )

        elif angle_type == "PUBLIC_REACTION":
            score = (
                signals["reaction"] * 0.55 +
                signals["source_diversity"] * 0.25 +
                signals["evidence_strength"] * 0.20
            )
            reason = (
                "There is enough verified reaction from "
                "relevant people or institutions."
            )
            description = (
                "Report meaningful reactions and distinguish "
                "verified statements from online speculation."
            )

        elif angle_type == "CONTROVERSY":
            score = (
                signals["controversy"] * 0.45 +
                signals["source_diversity"] * 0.30 +
                signals["evidence_strength"] * 0.25
            )
            reason = (
                "There are clearly documented competing "
                "claims, disputes or disagreements."
            )
            description = (
                "Present competing positions fairly and "
                "identify what is actually established."
            )

        elif angle_type == "UNANSWERED_QUESTIONS":
            score = (
                signals["uncertainty"] * 0.50 +
                signals["reader_need"] * 0.30 +
                signals["complexity"] * 0.20
            )
            reason = (
                "Important information remains unresolved."
            )
            description = (
                "Identify important unanswered questions "
                "without turning uncertainty into speculation."
            )

        elif angle_type == "DATA_ANGLE":
            score = (
                signals["data"] * 0.60 +
                signals["comparison"] * 0.25 +
                signals["specificity"] * 0.15
            )
            reason = (
                "Numbers, measurable changes or datasets "
                "could materially improve the story."
            )
            description = (
                "Lead with verified numbers and explain "
                "what they mean."
            )

        elif angle_type == "COMPARISON":
            score = (
                signals["comparison"] * 0.55 +
                signals["context"] * 0.25 +
                signals["reader_need"] * 0.20
            )
            reason = (
                "The story can be better understood "
                "through a factual comparison."
            )
            description = (
                "Compare the current development with "
                "a relevant previous situation."
            )

        else:
            return {}

        score = max(
            0.0,
            min(
                1.0,
                score / 100.0
            )
        )

        if score < 0.20:
            return {}

        numeric_score = round(
            score * 100,
            2
        )

        confidence = self._confidence(
            numeric_score,
            signals
        )

        return {
            "angle_type": angle_type,
            "angle_score": numeric_score,
            "confidence": confidence,
            "reason": reason,
            "angle_description": description,
            "headline_direction": (
                self._headline_direction(
                    angle_type,
                    story
                )
            ),
            "supporting_signals": signals,
            "safety_note": (
                "Use only claims supported by available "
                "evidence and clearly distinguish confirmed "
                "facts from uncertainty."
            ),
            "publication_safe": (
                numeric_score >= 60
                and confidence != "LOW"
            )
        }

    # =====================================================
    # SIGNALS
    # =====================================================

    def _signals(
        self,
        story: Dict[str, Any],
        related_stories: List[Dict[str, Any]],
        evidence: List[Dict[str, Any]],
        trend_data: Dict[str, Any],
        text: str
    ) -> Dict[str, int]:

        lowered = str(text or "").lower()
        words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                lowered
            )
        )

        development_hits = sum(
            1
            for word in self.development_words
            if word in words
        )
        newness = min(
            100,
            development_hits * 20
        )

        recency = 50

        if story.get("published_at"):
            recency = 80

        if story.get("updated_at"):
            recency = 90

        if any(
            marker in lowered
            for marker in (
                "today",
                "just now",
                "breaking",
                "latest",
                "minutes ago",
                "hours ago"
            )
        ):
            recency = 100

        impact_hits = sum(
            1
            for word in self.impact_words
            if word in words
        )
        impact = min(
            100,
            impact_hits * 12
        )

        if story.get("impact"):
            impact = max(
                impact,
                self._numeric_signal(
                    story.get("impact")
                )
            )

        evidence_strength = (
            20
            if not evidence
            else min(
                100,
                len(evidence) * 20
            )
        )

        specificity = 40

        if story.get("entities"):
            specificity += 20

        if story.get("location"):
            specificity += 10

        if story.get("date"):
            specificity += 10

        if re.search(
            r"\b\d+(?:\.\d+)?%?\b",
            lowered
        ):
            specificity += 10

        specificity = min(
            specificity,
            100
        )

        comparison = 20

        if related_stories:
            comparison += min(
                50,
                len(related_stories) * 10
            )

        if any(
            marker in lowered
            for marker in (
                "compared with",
                "compared to",
                "previously",
                "last year",
                "last month",
                "earlier",
                "unlike",
                "versus",
                "vs"
            )
        ):
            comparison += 30

        comparison = min(
            comparison,
            100
        )

        future_hits = sum(
            1
            for marker in (
                "next",
                "will",
                "expected",
                "plans",
                "planned",
                "deadline",
                "coming",
                "future",
                "pending",
                "scheduled",
                "set to"
            )
            if marker in lowered
        )

        future_signal = min(
            100,
            20 + future_hits * 15
        )

        human_hits = sum(
            1
            for marker in (
                "people",
                "families",
                "workers",
                "students",
                "children",
                "patients",
                "residents",
                "customers",
                "consumers",
                "victims",
                "community",
                "public"
            )
            if marker in lowered
        )

        human_relevance = min(
            100,
            human_hits * 15
        )

        business_hits = sum(
            1
            for marker in (
                "business",
                "company",
                "companies",
                "market",
                "stock",
                "shares",
                "profit",
                "revenue",
                "investment",
                "investors",
                "economy",
                "economic",
                "trade",
                "jobs",
                "consumer",
                "customers"
            )
            if marker in lowered
        )

        business = min(
            100,
            business_hits * 15
        )

        political_hits = sum(
            1
            for marker in (
                "government",
                "president",
                "minister",
                "senate",
                "senator",
                "congress",
                "parliament",
                "election",
                "vote",
                "policy",
                "political",
                "party",
                "law",
                "legislation"
            )
            if marker in lowered
        )

        political = min(
            100,
            political_hits * 12
        )
