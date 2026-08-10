"""
AI NEWS FACTORY
READER PSYCHOLOGY & ENGAGEMENT ENGINE

Purpose
-------
Optimize news for human attention, comprehension and
retention WITHOUT manufacturing facts or using deceptive
clickbait.

The engine evaluates:

    Attention
    Curiosity
    Relevance
    Emotional salience
    Cognitive load
    Readability
    Information pacing
    Headline strength
    Lead strength
    Section momentum
    Reader questions
    Drop-off risk

IMPORTANT EDITORIAL RULE
------------------------
Psychology can improve PRESENTATION.

Psychology must NEVER override:
    - fact verification
    - source attribution
    - uncertainty
    - editorial integrity

The system should create:
    "I need to understand this."

Not:
    "I was tricked into clicking this."

The engine outputs an optimization plan. A later language
model can use this plan when writing the final article.
"""

import re
from typing import Any, Dict, List


class PsychologyEngine:

    def __init__(self):

        self.name = "Reader Psychology & Engagement Engine"
        self.version = "1.0.0"

        self.target_readability = {
            "minimum": 55,
            "ideal": 75,
            "maximum": 95
        }

        self.forbidden_engagement_patterns = [
            "you won't believe",
            "shocking",
            "this will blow your mind",
            "the internet is going crazy",
            "what happened next",
            "doctors hate this",
            "they don't want you to know"
        ]

    # =====================================================
    # MAIN ANALYSIS
    # =====================================================

    def analyze(
        self,
        article_plan: Dict[str, Any]
    ) -> Dict[str, Any]:

        article = article_plan.get(
            "article",
            {}
        )

        headline = article.get(
            "headline",
            {}
        )

        lead = article.get(
            "lead",
            {}
        )

        facts = article.get(
            "key_facts",
            {}
        )

        questions = self._reader_questions(
            article_plan
        )

        attention = self._attention_score(
            article_plan
        )

        curiosity = self._curiosity_score(
            article_plan
        )

        relevance = self._relevance_score(
            article_plan
        )

        emotional_salience = (
            self._emotional_salience(
                article_plan
            )
        )

        cognitive_load = (
            self._cognitive_load(
                article_plan
            )
        )

        retention = (
            self._retention_score(
                attention,
                curiosity,
                relevance,
                cognitive_load
            )
        )

        risks = self._detect_manipulation(
            headline,
            lead
        )

        recommendations = (
            self._generate_recommendations(
                article_plan,
                attention,
                curiosity,
                relevance,
                cognitive_load,
                risks
            )
        )

        return {

            "engine": self.name,
            "version": self.version,

            "scores": {

                "attention":
                    attention,

                "curiosity":
                    curiosity,

                "relevance":
                    relevance,

                "emotional_salience":
                    emotional_salience,

                "cognitive_load":
                    cognitive_load,

                "retention":
                    retention
            },

            "reader_questions":
                questions,

            "manipulation_risks":
                risks,

            "recommendations":
                recommendations,

            "engagement_strategy":
                self._engagement_strategy(
                    retention,
                    risks
                )
        }

    # =====================================================
    # ATTENTION
    # =====================================================

    def _attention_score(
        self,
        article_plan: Dict[str, Any]
    ) -> int:

        significance = article_plan.get(
            "significance",
            {}
        )

        score = significance.get(
            "score",
            50
        )

        # Attention should primarily follow real relevance.
        return max(
            0,
            min(
                int(score),
                100
            )
        )

    # =====================================================
    # CURIOSITY
    # =====================================================

    def _curiosity_score(
        self,
        article_plan: Dict[str, Any]
    ) -> int:

        angles = article_plan.get(
            "angles",
            {}
        )

        primary = angles.get(
            "primary_angle",
            {}
        )

        angle_score = primary.get(
            "total_score",
            50
        )

        questions = (
            article_plan
            .get(
                "story",
                {}
            )
            .get(
                "story",
                {}
            )
            .get(
                "reader_questions",
                []
            )
        )

        score = angle_score

        if len(questions) >= 3:
            score += 10

        return min(
            int(score),
            100
        )

    # =====================================================
    # RELEVANCE
    # =====================================================

    def _relevance_score(
        self,
        article_plan: Dict[str, Any]
    ) -> int:

        significance = article_plan.get(
            "significance",
            {}
        )

        breakdown = significance.get(
            "breakdown",
            {}
        )

        return int(
            breakdown.get(
                "reader_interest",
                50
            )
        )

    # =====================================================
    # EMOTIONAL SALIENCE
    # =====================================================

    def _emotional_salience(
        self,
        article_plan: Dict[str, Any]
    ) -> int:

        """
        Emotional salience is not the same as emotional
        manipulation.

        Important real-world events naturally carry emotion.
        The system should identify that relevance rather than
        manufacture it.
        """

        story = article_plan.get(
            "story",
            {}
        )

        story_data = story.get(
            "story",
            {}
        )

        impact = story_data.get(
            "initial_impact",
            "low"
        )

        mapping = {
            "high": 90,
            "medium": 65,
            "low": 35
        }

        return mapping.get(
            impact,
            35
        )

    # =====================================================
    # COGNITIVE LOAD
    # =====================================================

    def _cognitive_load(
        self,
        article_plan: Dict[str, Any]
    ) -> int:

        article = article_plan.get(
            "article",
            {}
        )

        facts = article.get(
            "key_facts",
            {}
        ).get(
            "facts",
            []
        )

        context = article.get(
            "context",
            {}
        )

        score = 30

        if len(facts) > 8:
            score += 20

        if len(facts) > 15:
            score += 20

        if context:
            score += 10

        # Higher score means more cognitive load.
        return min(
            score,
            100
        )

    # =====================================================
    # RETENTION
    # =====================================================

    def _retention_score(
        self,
        attention: int,
        curiosity: int,
        relevance: int,
        cognitive_load: int
    ) -> int:

        score = (
            attention * 0.30
            +
            curiosity * 0.25
            +
            relevance * 0.30
            +
            (100 - cognitive_load) * 0.15
        )

        return max(
            0,
            min(
                int(score),
                100
            )
        )

    # =====================================================
    # READER QUESTIONS
    # =====================================================

    def _reader_questions(
        self,
        article_plan: Dict[str, Any]
    ) -> List[str]:

        story = article_plan.get(
            "story",
            {}
        )

        story_data = story.get(
            "story",
            {}
        )

        supplied_questions = story_data.get(
            "reader_questions",
            []
        )

        questions = list(
            supplied_questions
        )

        standard_questions = [
            "What happened?",
            "Why does it matter?",
            "Who is affected?",
            "What changes now?",
            "What happens next?",
            "What is still unknown?"
        ]

        for question in standard_questions:

            if question not in questions:
                questions.append(
                    question
                )

        return questions[:10]

    # =====================================================
    # MANIPULATION DETECTION
    # =====================================================

    def _detect_manipulation(
        self,
        headline: Dict[str, Any],
        lead: Dict[str, Any]
    ) -> List[Dict[str, str]]:

        risks = []

        headline_text = str(
            headline
        ).lower()

        lead_text = str(
            lead
        ).lower()

        combined = (
            headline_text
            +
            " "
            +
            lead_text
        )

        for pattern in (
            self.forbidden_engagement_patterns
        ):

            if pattern in combined:

                risks.append({
                    "pattern": pattern,
                    "severity": "HIGH",
                    "action":
                        "REMOVE_MANIPULATIVE
