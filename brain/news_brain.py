"""
AI NEWS FACTORY
NEWS BRAIN

Central intelligence orchestrator.

The News Brain combines:

    Story Analyzer
          ↓
    Source Intelligence
          ↓
    Significance Engine
          ↓
    Angle Finder
          ↓
    Editorial Decision

Important:
This layer coordinates intelligence. It does not claim that
a story is true simply because an algorithm gives it a high
score. Verification remains a separate mandatory stage.
"""

from typing import Any, Dict, List

from brain.story_analyzer import StoryAnalyzer
from brain.source_intelligence import SourceIntelligence
from brain.significance_engine import SignificanceEngine
from brain.angle_finder import AngleFinder


class NewsBrain:

    def __init__(self):

        self.name = "AI News Brain"
        self.version = "1.0.0"

        self.story_analyzer = StoryAnalyzer()
        self.source_intelligence = SourceIntelligence()
        self.significance_engine = SignificanceEngine()
        self.angle_finder = AngleFinder()

    # =====================================================
    # ANALYZE ONE STORY
    # =====================================================

    def process_story(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        # -------------------------------------------------
        # STEP 1
        # Understand the raw story
        # -------------------------------------------------

        analyzed_story = (
            self.story_analyzer.analyze(
                story
            )
        )

        if analyzed_story.get(
            "status"
        ) == "rejected":

            return {
                "status": "rejected",
                "reason": analyzed_story.get(
                    "reason"
                )
            }

        # -------------------------------------------------
        # STEP 2
        # Evaluate source
        # -------------------------------------------------

        source = {
            "name": story.get(
                "source",
                "Unknown"
            ),

            "url": story.get(
                "url",
                ""
            ),

            "title": story.get(
                "title",
                ""
            ),

            "content": story.get(
                "content",
                ""
            ),

            "published_at": story.get(
                "published_at"
            )
        }

        source_result = (
            self.source_intelligence.analyze_source(
                source
            )
        )

        # Attach source intelligence so later engines
        # can use it.

        analyzed_story[
            "source_intelligence"
        ] = source_result[
            "intelligence"
        ]

        # -------------------------------------------------
        # STEP 3
        # Determine significance
        # -------------------------------------------------

        significance = (
            self.significance_engine.evaluate(
                analyzed_story
            )
        )

        # -------------------------------------------------
        # STEP 4
        # Find editorial angles
        # -------------------------------------------------

        angles = (
            self.angle_finder.find_angles(
                analyzed_story
            )
        )

        # -------------------------------------------------
        # STEP 5
        # Editorial decision
        # -------------------------------------------------

        decision = self._make_editorial_decision(
            significance,
            source_result,
            angles
        )

        # -------------------------------------------------
        # FINAL INTELLIGENCE PACKAGE
        # -------------------------------------------------

        return {
            "status": "processed",

            "story": analyzed_story,

            "source_intelligence": source_result,

            "significance": significance,

            "angles": angles,

            "editorial_decision": decision
        }

    # =====================================================
    # PROCESS MULTIPLE STORIES
    # =====================================================

    def process_stories(
        self,
        stories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        results = []

        for story in stories:

            try:

                result = self.process_story(
                    story
                )

                results.append(
                    result
                )

            except Exception as error:

                results.append({
                    "status": "error",
                    "error": str(error)
                })

        return self._rank_stories(
            results
        )

    # =====================================================
    # RANK STORIES
    # =====================================================

    def _rank_stories(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        valid_results = [
            result
            for result in results
            if result.get(
                "status"
            ) == "processed"
        ]

        rejected_results = [
            result
            for result in results
            if result.get(
                "status"
            ) != "processed"
        ]

        valid_results.sort(
            key=lambda item:
                item.get(
                    "significance",
                    {}
                ).get(
                    "score",
                    0
                ),
            reverse=True
        )

        return (
            valid_results +
            rejected_results
        )

    # =====================================================
    # EDITORIAL DECISION
    # =====================================================

    def _make_editorial_decision(
        self,
        significance: Dict[str, Any],
        source_result: Dict[str, Any],
        angles: Dict[str, Any]
    ) -> Dict[str, Any]:

        significance_score = significance.get(
            "score",
            0
        )

        source_score = (
            source_result
            .get(
                "intelligence",
                {}
            )
            .get(
                "score",
                0
            )
        )

        primary_angle = angles.get(
            "primary_angle"
        )

        # -------------------------------------------------
        # Never publish directly from this decision.
        #
        # Verification and quality control must happen
        # before publishing.
        # -------------------------------------------------

        if significance_score >= 85:

            priority = "URGENT"

        elif significance_score >= 70:

            priority = "HIGH"

        elif significance_score >= 55:

            priority = "NORMAL"

        else:

            priority = "LOW"

        # -------------------------------------------------
        # Verification requirement
        # -------------------------------------------------

        if source_score < 75:

            verification = (
                "MANDATORY_MULTISOURCE_VERIFICATION"
            )

        else:

            verification = (
                "STANDARD_VERIFICATION"
            )

        # -------------------------------------------------
        # Angle decision
        # -------------------------------------------------

        if primary_angle:

            angle_decision = primary_angle.get(
                "decision",
                "UNKNOWN"
            )

        else:

            angle_decision = "NO_RELIABLE_ANGLE"

        # -------------------------------------------------
        # Overall recommendation
        # -------------------------------------------------

        if (
            significance_score >= 70
            and
            angle_decision in {
                "STRONG_PRIMARY_ANGLE",
                "GOOD_ANGLE"
            }
        ):

            recommendation = (
                "SEND_TO_EDITORIAL_PIPELINE"
            )

        elif significance_score >= 55:

            recommendation = (
                "MONITOR_AND_REASSESS"
            )

        else:

            recommendation = (
                "DO_NOT_PRIORITIZE"
            )

        return {
            "priority": priority,

            "verification": verification,

            "angle_quality": angle_decision,

            "recommendation": recommendation,

            "publication_allowed": False,

            "reason": (
                "Publication remains blocked until "
                "verification and quality control pass."
            )
        }


# =========================================================
# HELPER
# =========================================================

def process_news_story(
    story: Dict[str, Any]
) -> Dict[str, Any]:

    brain = NewsBrain()

    return brain.process_story(
        story
    )


def process_news_batch(
    stories: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    brain = NewsBrain()

    return brain.process_stories(
        stories
    )
