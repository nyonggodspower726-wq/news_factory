"""
AI NEWS FACTORY
Significance Engine

Purpose:
Determine how important a story is before the newsroom
spends resources writing and distributing it.

The engine evaluates:
- Public impact
- Number of people potentially affected
- Urgency
- Freshness
- Source strength
- Geographic relevance
- Economic/social significance
- Uniqueness
- Reader interest
- Development potential

IMPORTANT:
This is an editorial ranking system, NOT a truth detector.
A high score means "worth investigating", not "confirmed true".
"""

from typing import Any, Dict


class SignificanceEngine:

    def __init__(self):

        self.name = "Significance Engine"
        self.version = "1.0.0"

        # -------------------------------------------------
        # Weighting
        # -------------------------------------------------

        self.weights = {
            "public_impact": 0.20,
            "urgency": 0.15,
            "freshness": 0.10,
            "source_strength": 0.15,
            "reader_interest": 0.15,
            "geographic_relevance": 0.10,
            "uniqueness": 0.05,
            "development_potential": 0.10
        }

    # =====================================================
    # MAIN SCORING
    # =====================================================

    def evaluate(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        scores = self._build_scores(story)

        total_score = 0

        for category, weight in self.weights.items():

            total_score += (
                scores[category] * weight
            )

        total_score = round(
            total_score,
            2
        )

        classification = self._classify(
            total_score
        )

        recommendation = self._recommendation(
            total_score,
            scores
        )

        return {
            "engine": self.name,

            "score": total_score,

            "classification": classification,

            "recommendation": recommendation,

            "breakdown": scores,

            "reasoning": self._generate_reasoning(
                scores
            )
        }

    # =====================================================
    # BUILD SCORES
    # =====================================================

    def _build_scores(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, float]:

        story_data = story.get(
            "story",
            {}
        )

        original = story.get(
            "original",
            {}
        )

        urgency = story_data.get(
            "urgency",
            "normal"
        )

        impact = story_data.get(
            "initial_impact",
            "low"
        )

        source_score = self._source_strength(
            story
        )

        return {

            "public_impact":
                self._impact_score(
                    impact
                ),

            "urgency":
                self._urgency_score(
                    urgency
                ),

            "freshness":
                self._freshness_score(
                    original
                ),

            "source_strength":
                source_score,

            "reader_interest":
                self._reader_interest(
                    story
                ),

            "geographic_relevance":
                self._geographic_relevance(
                    story
                ),

            "uniqueness":
                self._uniqueness(
                    story
                ),

            "development_potential":
                self._development_potential(
                    story
                )
        }

    # =====================================================
    # PUBLIC IMPACT
    # =====================================================

    def _impact_score(
        self,
        impact: str
    ) -> float:

        mapping = {
            "high": 100,
            "medium": 65,
            "low": 30
        }

        return mapping.get(
            impact,
            30
        )

    # =====================================================
    # URGENCY
    # =====================================================

    def _urgency_score(
        self,
        urgency: str
    ) -> float:

        mapping = {
            "high": 100,
            "medium": 65,
            "normal": 35
        }

        return mapping.get(
            urgency,
            35
        )

    # =====================================================
    # FRESHNESS
    # =====================================================

    def _freshness_score(
        self,
        original: Dict[str, Any]
    ) -> float:

        published_at = original.get(
            "published_at"
        )

        if not published_at:
            return 50

        # The full timestamp intelligence system will be
        # added later. For now, having a timestamp gives
        # the story a reasonable baseline.

        return 75

    # =====================================================
    # SOURCE STRENGTH
    # =====================================================

    def _source_strength(
        self,
        story: Dict[str, Any]
    ) -> float:

        intelligence = story.get(
            "source_intelligence",
            {}
        )

        score = intelligence.get(
            "score"
        )

        if score is not None:
            return float(score)

        # If source intelligence hasn't been attached yet,
        # don't pretend we have strong evidence.

        return 40

    # =====================================================
    # READER INTEREST
    # =====================================================

    def _reader_interest(
        self,
        story: Dict[str, Any]
    ) -> float:

        story_data = story.get(
            "story",
            {}
        )

        keywords = story_data.get(
            "keywords",
            []
        )

        questions = story_data.get(
            "reader_questions",
            []
        )

        score = 40

        # More meaningful concepts generally provide more
        # opportunity for useful explanation.

        if len(keywords) >= 5:
            score += 15

        if len(questions) >= 4:
            score += 20

        story_type = story_data.get(
            "story_type",
            "general"
        )

        high_interest_categories = {
            "politics",
            "business",
            "technology",
            "sports"
        }

        if story_type in high_interest_categories:
            score += 15

        return min(
            score,
            100
        )

    # =====================================================
    # GEOGRAPHIC RELEVANCE
    # =====================================================

    def _geographic_relevance(
        self,
        story: Dict[str, Any]
    ) -> float:

        story_data = story.get(
            "story",
            {}
        )

        locations = story_data.get(
            "locations",
            []
        )

        if not locations:
            return 40

        nigeria_locations = {
            "Nigeria",
            "Lagos",
            "Abuja",
            "Port Harcourt",
            "Kano",
            "Rivers",
            "Akwa Ibom"
        }

        for location in locations:

            if location in nigeria_locations:
                return 100

        return 60

    # =====================================================
    # UNIQUENESS
    # =====================================================

    def _uniqueness(
        self,
        story: Dict[str, Any]
    ) -> float:

        """
        A proper duplicate/story-clustering engine will
        eventually provide this value.

        For now we use a neutral baseline.
        """

        if story.get(
            "is_duplicate"
        ):
            return 10

        return 60

    # =====================================================
    # DEVELOPMENT POTENTIAL
    # =====================================================

    def _development_potential(
        self,
        story: Dict[str, Any]
    ) -> float:

        story_data = story.get(
            "story",
            {}
        )

        urgency = story_data.get(
            "urgency",
            "normal"
        )

        story_type = story_data.get(
            "story_type",
            "general"
        )

        score = 40

        if urgency == "high":
            score += 30

        if story_type in {
            "politics",
            "business",
            "world",
            "technology"
        }:
            score += 15

        if story_data.get(
            "reader_questions"
        ):
            score += 15

        return min(
            score,
            100
        )

    # =====================================================
    # CLASSIFICATION
    # =====================================================

    def _classify(
        self,
        score: float
    ) -> str:

        if score >= 85:
            return "MAJOR_STORY"

        if score >= 70:
            return "HIGH_VALUE"

        if score >= 55:
            return "WORTH_MONITORING"

        if score >= 40:
            return "LOW_PRIORITY"

        return "REJECT"

    # =====================================================
    # RECOMMENDATION
    # =====================================================

    def _recommendation(
        self,
        score: float,
        scores: Dict[str, float]
    ) -> str:

        if score >= 85:
            return (
                "INVESTIGATE_IMMEDIATELY"
            )

        if score >= 70:
            return (
                "SEND_TO_EDITORIAL_PIPELINE"
            )

        if score >= 55:
            return (
                "MONITOR_FOR_DEVELOPMENTS"
            )

        if score >= 40:
            return (
                "HOLD_UNLESS_NEW_INFORMATION_APPEARS"
            )

        return "DO_NOT_PUBLISH"

    # =====================================================
    # REASONING
    # =====================================================

    def _generate_reasoning(
        self,
        scores: Dict[str, float]
    ) -> Dict[str, str]:

        reasoning = {}

        if scores["public_impact"] >= 80:
            reasoning["impact"] = (
                "Potentially significant public impact."
            )
        else:
            reasoning["impact"] = (
                "Limited immediate public impact detected."
            )

        if scores["urgency"] >= 80:
            reasoning["urgency"] = (
                "Story appears time-sensitive."
            )
        else:
            reasoning["urgency"] = (
                "No strong breaking-news signal detected."
            )

        if scores["source_strength"] >= 80:
            reasoning["source"] = (
                "Strong source signal available."
            )
        else:
            reasoning["source"] = (
                "Additional source verification recommended."
            )

        if scores["reader_interest"] >= 75:
            reasoning["reader_interest"] = (
                "Strong potential reader relevance."
            )
        else:
            reasoning["reader_interest"] = (
                "Reader value may require stronger context or angle."
            )

        if scores["development_potential"] >= 75:
            reasoning["development"] = (
                "Story may develop further."
            )
        else:
            reasoning["development"] = (
                "Limited development potential detected."
            )

        return reasoning


# =========================================================
# HELPER FUNCTION
# =========================================================

def evaluate_story(
    story: Dict[str, Any]
) -> Dict[str, Any]:

    engine = SignificanceEngine()

    return engine.evaluate(
        story
    )
