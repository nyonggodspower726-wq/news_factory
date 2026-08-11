"""
AI NEWS FACTORY
CENTRAL BRAIN PIPELINE

All brain engines are wired here.

main.py and scheduler.py should communicate with this
pipeline instead of calling individual brain engines.
"""

import logging
from typing import Any, Dict, List

from brain.claim_engine import ClaimEngine
from brain.corroboration_engine import CorroborationEngine
from brain.fact_checker import FactChecker
from brain.story_synthesis_engine import StorySynthesisEngine
from brain.journalist_engine import JournalistEngine
from brain.headline_engine import HeadlineEngine
from brain.editor_engine import EditorEngine

from brain.story_analyzer import StoryAnalyzer
from brain.source_intelligence_engine import SourceIntelligenceEngine
from brain.source_graph_engine import SourceGraphEngine
from brain.significance_engine import SignificanceEngine
from brain.angle_finder import AngleFinder
from brain.reader_psychology_engine import ReaderPsychologyEngine
from brain.engagement_engine import EngagementEngine
from brain.narrative_engine import NarrativeEngine


logger = logging.getLogger("NewsFactory.BrainPipeline")


class BrainPipeline:

    def __init__(self):

        logger.info("Initializing central brain...")

        self.story_analyzer = StoryAnalyzer()
        self.source_intelligence = SourceIntelligenceEngine()
        self.source_graph = SourceGraphEngine()

        self.claim_engine = ClaimEngine()
        self.corroboration = CorroborationEngine()
        self.fact_checker = FactChecker()

        self.story_synthesis = StorySynthesisEngine()

        self.significance = SignificanceEngine()
        self.angle_finder = AngleFinder()

        self.reader_psychology = ReaderPsychologyEngine()
        self.engagement = EngagementEngine()

        self.narrative = NarrativeEngine()
        self.journalist = JournalistEngine()

        self.headline = HeadlineEngine()
        self.editor = EditorEngine()

        logger.info("Central brain initialized.")

    # =====================================================
    # STATUS
    # =====================================================

    def status(self) -> Dict[str, Any]:
        """
        Return the current status of the central brain.

        Compatible with main.py fields:
        - total_brains
        - loaded_brains
        - brains
        """

        loaded_brains = [
            "story_analyzer",
            "source_intelligence",
            "source_graph",
            "claim_engine",
            "corroboration",
            "fact_checker",
            "story_synthesis",
            "significance",
            "angle_finder",
            "reader_psychology",
            "engagement",
            "narrative",
            "journalist",
            "headline",
            "editor"
        ]

        brains = {
            brain_name: True
            for brain_name in loaded_brains
        }

        return {
            "status": "READY",
            "engine": "BrainPipeline",
            "version": "1.0.0",
            "initialized": True,
            "total_brains": len(loaded_brains),
            "loaded_brains": loaded_brains,
            "brains": brains,
            "engines": brains
        }

    # =====================================================
    # MAIN PIPELINE
    # =====================================================

    def run(
        self,
        sources: List[Dict[str, Any]],
        story: Dict[str, Any] = None,
        topic: str = ""
    ) -> Dict[str, Any]:

        story = story or {}
        sources = sources or []

        logger.info("=" * 60)
        logger.info("BRAIN PIPELINE STARTED")
        logger.info("=" * 60)

        package = {
            "story": story,
            "sources": sources,
            "topic": topic,
            "claims": [],
            "evidence": {},
            "verification": {},
            "cluster": {},
            "significance": {},
            "angles": {},
            "psychology": {},
            "article_plan": {}
        }

        # =================================================
        # 1. STORY ANALYSIS
        # =================================================

        logger.info("1/15 Story analysis")

        try:

            story_analysis = self.story_analyzer.analyze(
                story
            )

            package["story_analysis"] = story_analysis

            if isinstance(story_analysis, dict):

                package["story"].update(
                    story_analysis
                )

        except Exception as error:

            logger.exception(
                "Story analysis failed: %s",
                error
            )

            package["story_analysis"] = {
                "status": "ERROR",
                "error": str(error)
            }

        # =================================================
        # 2. SOURCE INTELLIGENCE
        # =================================================

        logger.info("2/15 Source intelligence")

        try:

            source_intelligence = (
                self.source_intelligence.analyze(
                    sources
                )
            )

            package["source_intelligence"] = (
                source_intelligence
            )

        except Exception as error:

            logger.exception(
                "Source intelligence failed: %s",
                error
            )

            package["source_intelligence"] = {
                "status": "ERROR",
                "error": str(error)
            }

        # =================================================
        # 3. SOURCE GRAPH
        # =================================================

        logger.info("3/15 Source graph")

        try:

            source_graph = (
                self.source_graph.build_graph(
                    sources=sources,
                    claims=package["claims"],
                    entities=package["story"].get(
                        "entities",
                        []
                    )
                )
            )

            package["source_graph"] = source_graph

        except Exception as error:

            logger.exception(
                "Source graph failed: %s",
                error
            )

            package["source_graph"] = {
                "status": "ERROR",
                "error": str(error)
            }

        # =================================================
        # 4. CLAIM ANALYSIS
        # =================================================

        logger.info("4/15 Claim analysis")

        try:

            claim_result = (
                self.claim_engine.analyze(
                    package["story"]
                )
            )

            package["claim_analysis"] = claim_result

            if isinstance(claim_result, dict):

                package["claims"] = claim_result.get(
                    "claims",
                    []
                )

        except Exception as error:

            logger.exception(
                "Claim analysis failed: %s",
                error
            )

            package["claim_analysis"] = {
                "status": "ERROR",
                "error": str(error)
            }

        # =================================================
        # 5. CORROBORATION
        # =================================================

        logger.info("5/15 Corroboration")

        try:

            corroboration = (
                self.corroboration.analyze(
                    sources=sources,
                    claims=package["claims"]
                )
            )

            package["corroboration"] = corroboration

        except Exception as error:

            logger.exception(
                "Corroboration failed: %s",
                error
            )

            package["corroboration"] = {
                "status": "ERROR",
                "error": str(error)
            }

        # =================================================
        # 6. FACT CHECKING
        # =================================================

        logger.info("6/15 Fact checking")

        try:

            verification = (
                self.fact_checker.verify_story(
                    story=package["story"],
                    sources=sources
                )
            )

            package["verification"] = verification

            if isinstance(verification, dict):

                verified_claims = (
                    verification.get(
                        "claims",
                        []
                    )
                )

                if verified_claims:

                    package["claims"] = verified_claims

        except Exception as error:

            logger.exception(
                "Fact checking failed: %s",
                error
            )

            package["verification"] = {
                "publication_status":
                    "REQUIRES_EDITORIAL_REVIEW",
                "error": str(error),
                "claims": []
    }
