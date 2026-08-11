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
        """

        return {
            "status": "READY",
            "engine": "BrainPipeline",
            "version": "1.0.0",
            "initialized": True,
            "engines": {
                "story_analyzer": True,
                "source_intelligence": True,
                "source_graph": True,
                "claim_engine": True,
                "corroboration": True,
                "fact_checker": True,
                "story_synthesis": True,
                "significance": True,
                "angle_finder": True,
                "reader_psychology": True,
                "engagement": True,
                "narrative": True,
                "journalist": True,
                "headline": True,
                "editor": True
            }
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

            if isinstance(
                story_analysis,
                dict
            ):

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

            package[
                "source_intelligence"
            ] = source_intelligence

        except Exception as error:

            logger.exception(
                "Source intelligence failed: %s",
                error
            )

            package[
                "source_intelligence"
            ] = {
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
                    entities=package[
                        "story"
                    ].get(
                        "entities",
                        []
                    )
                )
            )

            package[
                "source_graph"
            ] = source_graph

        except Exception as error:

            logger.exception(
                "Source graph failed: %s",
                error
            )

            package[
                "source_graph"
            ] = {
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

            package[
                "claim_analysis"
            ] = claim_result

            if isinstance(
                claim_result,
                dict
            ):

                package[
                    "claims"
                ] = claim_result.get(
                    "claims",
                    []
                )

        except Exception as error:

            logger.exception(
                "Claim analysis failed: %s",
                error
            )

            package[
                "claim_analysis"
            ] = {
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
                    claims=package[
                        "claims"
                    ]
                )
            )

            package[
                "corroboration"
            ] = corroboration

        except Exception as error:

            logger.exception(
                "Corroboration failed: %s",
                error
            )

            package[
                "corroboration"
            ] = {
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

            package[
                "verification"
            ] = verification

            if isinstance(
                verification,
                dict
            ):

                verified_claims = (
                    verification.get(
                        "claims",
                        []
                    )
                )

                if verified_claims:

                    package[
                        "claims"
                    ] = verified_claims

        except Exception as error:

            logger.exception(
                "Fact checking failed: %s",
                error
            )

            package[
                "verification"
            ] = {
                "publication_status":
                    "REQUIRES_EDITORIAL_REVIEW",
                "error": str(error),
                "claims": []
            }

        # =================================================
        # 7. STORY SYNTHESIS
        # =================================================

        logger.info("7/15 Story synthesis")

        try:

            synthesis = (
                self.story_synthesis.synthesize(
                    sources=sources,
                    evidence=package.get(
                        "claim_analysis",
                        {}
                    ),
                    metadata={
                        "topic": topic,
                        "story": package[
                            "story"
                        ],
                        "verification":
                            package[
                                "verification"
                            ],
                        "corroboration":
                            package.get(
                                "corroboration",
                                {}
                            )
                    }
                )
            )

            package[
                "synthesis"
            ] = synthesis

            if isinstance(
                synthesis,
                dict
            ):

                package[
                    "story_model"
                ] = synthesis

        except Exception as error:

            logger.exception(
                "Story synthesis failed: %s",
                error
            )

            package[
                "synthesis"
            ] = {
                "status": "ERROR",
                "error": str(error)
            }

        # =================================================
        # 8. SIGNIFICANCE
        # =================================================

        logger.info("8/15 Significance")

        try:

            significance = (
                self.significance.evaluate(
                    package["story"]
                )
            )

            package[
                "significance"
            ] = significance

        except Exception as error:

            logger.exception(
                "Significance failed: %s",
                error
            )

            package[
                "significance"
            ] = {
                "status": "ERROR",
                "error": str(error)
            }

        # =================================================
        # 9. EDITORIAL ANGLE
        # =================================================

        logger.info("9/15 Editorial angle")

        try:

            angles = (
                self.angle_finder.find_angles(
                    package["story"],
                    package[
                        "significance"
                    ]
                )
            )

            package[
                "angles"
            ] = angles

        except Exception as error:

            logger.exception(
                "Angle finder failed: %s",
                error
            )

            package[
                "angles"
            ] = {
                "status": "ERROR",
                "error": str(error)
            }

        # =================================================
        # 10. READER PSYCHOLOGY
        # =================================================

        logger.info("10/15 Reader psychology")

        try:

            psychology = (
                self.reader_psychology.analyze(
                    story=package[
                        "story"
                    ],
                    article=package.get(
                        "article_plan"
                    ),
                    angle=package.get(
                        "angles"
                    )
                )
            )

            package[
                "psychology"
            ] = psychology

        except Exception as error:

            logger.exception(
                "Reader psychology failed: %s",
                error
            )

            package[
                "psychology"
            ] = {
                "status": "ERROR",
                "error": str(error)
            }

        # =================================================
        # 11. NARRATIVE
        # =================================================

        logger.info("11/15 Narrative")

        try:

            narrative = (
                self.narrative.build_blueprint(
                    story=package[
                        "story"
                    ],
                    psychology=package[
                        "psychology"
                    ],
                    audience=package.get(
                        "reader_intelligence",
                        {}
                    )
                )
            )

            package[
                "narrative"
            ] = narrative

        except Exception as error:

            logger.exception(
                "Narrative failed: %s",
                error
            )

            package[
                "narrative"
            ] = {
                "status": "ERROR",
                "error": str(error)
                    }
        # =================================================
        # 12. JOURNALIST
        # =================================================

        logger.info("12/15 Journalist")

        try:

            article_plan = (
                self.journalist.create_article_plan(
                    package
                )
            )

            package[
                "article_plan"
            ] = article_plan

        except Exception as error:

            logger.exception(
                "Journalist failed: %s",
                error
            )

            package[
                "article_plan"
            ] = {
                "status": "ERROR",
                "error": str(error)
            }

        # =================================================
        # 13. ENGAGEMENT
        # =================================================

        logger.info("13/15 Engagement")

        try:

            package[
                "engagement"
            ] = self.engagement.analyze(
                package["story"]
            )

        except Exception as error:

            logger.exception(
                "Engagement failed: %s",
                error
            )

            package[
                "engagement"
            ] = {
                "status": "ERROR",
                "error": str(error)
            }

        # =================================================
        # 14. HEADLINE
        # =================================================

        logger.info("14/15 Headline")

        try:

            headline_result = (
                self.headline.analyze(
                    package["story"]
                )
            )

            package[
                "headline"
            ] = headline_result

            if isinstance(
                headline_result,
                dict
            ):

                headline = (
                    headline_result.get(
                        "recommended_headline"
                    )
                )

                if headline:

                    package[
                        "story"
                    ][
                        "headline"
                    ] = headline

        except Exception as error:

            logger.exception(
                "Headline failed: %s",
                error
            )

            package[
                "headline"
            ] = {
                "status": "ERROR",
                "error": str(error)
            }

        # =================================================
        # 15. FINAL EDITOR
        # =================================================

        logger.info("15/15 Final editorial gate")

        try:

            editorial = (
                self.editor.review(
                    article_plan=package[
                        "article_plan"
                    ],
                    psychology=package[
                        "psychology"
                    ],
                    verification=package[
                        "verification"
                    ],
                    cluster=package.get(
                        "cluster",
                        {}
                    )
                )
            )

            package[
                "editorial"
            ] = editorial

        except Exception as error:

            logger.exception(
                "Editor failed: %s",
                error
            )

            package[
                "editorial"
            ] = {
                "decision":
                    "NEEDS_REVISION",
                "publication_gate":
                    False,
                "error": str(error)
            }

        # =================================================
        # FINAL RESULT
        # =================================================

        editorial = package.get(
            "editorial",
            {}
        )

        decision = editorial.get(
            "decision",
            "NEEDS_REVISION"
        )

        package[
            "pipeline_status"
        ] = decision

        package[
            "publication_ready"
        ] = (
            decision == "APPROVED"
        )

        logger.info("=" * 60)

        logger.info(
            "BRAIN PIPELINE COMPLETE"
        )

        logger.info(
            "Decision: %s",
            decision
        )

        logger.info("=" * 60)

        return package


# =========================================================
# HELPER
# =========================================================

def run_brain_pipeline(
    sources: List[Dict[str, Any]],
    story: Dict[str, Any] = None,
    topic: str = ""
) -> Dict[str, Any]:

    pipeline = BrainPipeline()

    return pipeline.run(
        sources=sources,
        story=story,
        topic=topic
                )
