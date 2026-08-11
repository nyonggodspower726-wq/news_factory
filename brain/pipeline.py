"""
AI NEWS FACTORY
CENTRAL BRAIN PIPELINE

All brain engines are wired here.

main.py and scheduler.py communicate with this
pipeline instead of calling individual brain engines.

NVIDIA AI
---------
Four NVIDIA API keys are loaded from Railway variables:

NVIDIA_API_KEY_1
NVIDIA_API_KEY_2
NVIDIA_API_KEY_3
NVIDIA_API_KEY_4

The NVIDIA client automatically fails over from one key
to the next when a request fails.
"""

import logging
import os
from typing import Any, Dict, List

import requests


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


logger = logging.getLogger(
    "NewsFactory.BrainPipeline"
)


# =========================================================
# NVIDIA CENTRAL AI CLIENT
# =========================================================

class NvidiaBrainClient:

    def __init__(
        self,
        model: str = "meta/llama-3.3-70b-instruct",
        base_url: str = "https://integrate.api.nvidia.com/v1"
    ):

        self.name = "NVIDIA Brain Client"
        self.version = "1.0.0"

        self.model = model

        self.base_url = (
            base_url.rstrip("/")
        )

        # =================================================
        # LOAD FOUR NVIDIA KEYS FROM RAILWAY
        # =================================================

        self.api_keys = [

            os.getenv(
                "NVIDIA_API_KEY_1",
                ""
            ).strip(),

            os.getenv(
                "NVIDIA_API_KEY_2",
                ""
            ).strip(),

            os.getenv(
                "NVIDIA_API_KEY_3",
                ""
            ).strip(),

            os.getenv(
                "NVIDIA_API_KEY_4",
                ""
            ).strip()
        ]

        # Remove empty variables.
        self.api_keys = [
            key
            for key in self.api_keys
            if key
        ]

        self.current_key_index = 0

        self.timeout = 60

        logger.info(
            "NVIDIA client initialized with %s configured key(s).",
            len(self.api_keys)
        )

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self
    ) -> Dict[str, Any]:

        return {

            "provider":
                "NVIDIA",

            "client":
                self.name,

            "version":
                self.version,

            "model":
                self.model,

            "configured_keys":
                len(
                    self.api_keys
                ),

            "failover_enabled":
                True,

            "current_key_slot":
                (
                    self.current_key_index + 1
                    if self.api_keys
                    else None
                )
        }

    # =====================================================
    # CHAT
    # =====================================================

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> str:

        if not self.api_keys:

            raise RuntimeError(
                "No NVIDIA API keys found. "
                "Configure NVIDIA_API_KEY_1 through "
                "NVIDIA_API_KEY_4 in Railway."
            )

        last_error = None

        total_keys = len(
            self.api_keys
        )

        for attempt in range(
            total_keys
        ):

            key_index = (
                self.current_key_index
                + attempt
            ) % total_keys

            api_key = self.api_keys[
                key_index
            ]

            try:

                logger.info(
                    "NVIDIA AI request using key slot %s/%s.",
                    key_index + 1,
                    total_keys
                )

                result = self._request(
                    api_key=api_key,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                self.current_key_index = (
                    key_index
                )

                return result

            except Exception as error:

                last_error = error

                logger.warning(
                    "NVIDIA key slot %s failed: %s",
                    key_index + 1,
                    error
                )

                continue

        raise RuntimeError(
            "All NVIDIA API keys failed. "
            f"Last error: {last_error}"
        )

    # =====================================================
    # NVIDIA REQUEST
    # =====================================================

    def _request(
        self,
        api_key: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:

        url = (
            self.base_url
            + "/chat/completions"
        )

        headers = {

            "Authorization":
                f"Bearer {api_key}",

            "Content-Type":
                "application/json",

            "Accept":
                "application/json"
        }

        payload = {

            "model":
                self.model,

            "messages":
                messages,

            "temperature":
                temperature,

            "max_tokens":
                max_tokens
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )

        response.raise_for_status()

        data = response.json()

        choices = data.get(
            "choices",
            []
        )

        if not choices:

            raise RuntimeError(
                "NVIDIA API returned no choices."
            )

        message = choices[0].get(
            "message",
            {}
        )

        content = message.get(
            "content"
        )

        if not content:

            raise RuntimeError(
                "NVIDIA API returned empty content."
            )

        return str(
            content
        ).strip()


# =========================================================
# CENTRAL BRAIN PIPELINE
# =========================================================

class BrainPipeline:

    def __init__(self):

        logger.info(
            "Initializing central brain..."
        )

        # =================================================
        # CENTRAL NVIDIA AI
        # =================================================

        self.ai = NvidiaBrainClient()

        # =================================================
        # BRAIN ENGINES
        # =================================================

        self.story_analyzer = (
            StoryAnalyzer()
        )

        self.source_intelligence = (
            SourceIntelligenceEngine()
        )

        self.source_graph = (
            SourceGraphEngine()
        )

        self.claim_engine = (
            ClaimEngine()
        )

        self.corroboration = (
            CorroborationEngine()
        )

        self.fact_checker = (
            FactChecker()
        )

        self.story_synthesis = (
            StorySynthesisEngine()
        )

        self.significance = (
            SignificanceEngine()
        )

        self.angle_finder = (
            AngleFinder()
        )

        self.reader_psychology = (
            ReaderPsychologyEngine()
        )

        self.engagement = (
            EngagementEngine()
        )

        self.narrative = (
            NarrativeEngine()
        )

        self.journalist = (
            JournalistEngine()
        )

        self.headline = (
            HeadlineEngine()
        )

        self.editor = (
            EditorEngine()
        )

        logger.info(
            "Central brain initialized."
        )

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self
    ) -> Dict[str, Any]:

        loaded_brains = [

            "story_analyzer",
            "source_intelligence",
            "claim_engine",
            "source_graph",
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
            for brain_name
            in loaded_brains
        }

        return {

            "status":
                "READY",

            "engine":
                "BrainPipeline",

            "version":
                "1.0.0",

            "initialized":
                True,

            "total_brains":
                len(
                    loaded_brains
                ),

            "loaded_brains":
                loaded_brains,

            "brains":
                brains,

            "engines":
                brains,

            "ai_provider":
                self.ai.status()
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

        story = (
            story
            if isinstance(
                story,
                dict
            )
            else {}
        )

        sources = (
            sources
            if isinstance(
                sources,
                list
            )
            else []
        )

        logger.info("=" * 60)
        logger.info("BRAIN PIPELINE STARTED")
        logger.info("=" * 60)

        package = {

            "story":
                story,

            "sources":
                sources,

            "topic":
                topic,

            "claims":
                [],

            "claim_analysis":
                {},

            "evidence":
                {},

            "verification":
                {},

            "corroboration":
                {},

            "source_graph":
                {},

            "cluster":
                {},

            "significance":
                {},

            "angles":
                {},

            "psychology":
                {},

            "article_plan":
                {}
        }

        # Central AI available to every downstream engine.
        package["ai"] = self.ai

        # =================================================
        # 1. STORY ANALYSIS
        # =================================================

        logger.info(
            "1/15 Story analysis"
        )

        try:

            story_analysis = (
                self.story_analyzer.analyze(
                    story
                )
            )

            package[
                "story_analysis"
            ] = story_analysis

            if isinstance(
                story_analysis,
                dict
            ):

                package[
                    "story"
                ].update(
                    story_analysis
                )

        except Exception as error:

            logger.exception(
                "Story analysis failed: %s",
                error
            )

            package[
                "story_analysis"
            ] = {
                "status": "ERROR",
                "error": str(error)
            }


        # =================================================
        # 2. SOURCE INTELLIGENCE
        # =================================================

        logger.info(
            "2/15 Source intelligence"
        )

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
        # 3. CLAIM ANALYSIS
        # =================================================

        logger.info(
            "3/15 Claim analysis"
        )

        try:

            claim_analysis = (
                self.claim_engine.analyze(
                    package["story"]
                )
            )

            package[
                "claim_analysis"
            ] = claim_analysis

            if isinstance(
                claim_analysis,
                dict
            ):

                package[
                    "claims"
                ] = claim_analysis.get(
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
                "error": str(error),
                "claims": []
            }

            package[
                "claims"
            ] = []
        # =================================================
        # 4. SOURCE GRAPH
        # =================================================

        logger.info(
            "4/15 Source graph"
        )

        try:

            source_graph = (
                self.source_graph.build_graph(

                    sources=sources,

                    claims=package[
                        "claims"
                    ],

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
        # 5. CORROBORATION
        # =================================================

        logger.info(
            "5/15 Corroboration"
        )

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

        logger.info(
            "6/15 Fact checking"
        )

        try:

            verification = (
                self.fact_checker.verify_story(

                    story=package[
                        "story"
                    ],

                    sources=sources
                )
            )

            package[
                "verification"
            ] = verification

        except Exception as error:

            logger.exception(
                "Fact checking failed: %s",
                error
            )

            package[
                "verification"
            ] = {

                "publication_status":
                    "HUMAN_REVIEW_REQUIRED",

                "status":
                    "ERROR",

                "error":
                    str(error)
            }


        # =================================================
        # 7. STORY SYNTHESIS
        # =================================================

        logger.info(
            "7/15 Story synthesis"
        )

        try:

            synthesis = (
                self.story_synthesis.synthesize(

                    sources=sources,

                    evidence=package.get(
                        "claim_analysis",
                        {}
                    ),

                    metadata={

                        "topic":
                            topic,

                        "story":
                            package[
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
                            ),

                        "source_graph":
                            package.get(
                                "source_graph",
                                {}
                            ),

                        "claims":
                            package.get(
                                "claims",
                                []
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

        logger.info(
            "8/15 Significance"
        )

        try:

            significance = (
                self.significance.evaluate(
                    package[
                        "story"
                    ]
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

        logger.info(
            "9/15 Editorial angle"
        )

        try:

            angles = (
                self.angle_finder.find_angles(

                    package[
                        "story"
                    ],

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

        logger.info(
            "10/15 Reader psychology"
        )

        try:

            psychology = (
                self.reader_psychology.analyze(

                    story=package[
                        "story"
                    ],

                    article=package.get(
                        "article_plan",
                        {}
                    ),

                    angle=package.get(
                        "angles",
                        {}
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

        logger.info(
            "11/15 Narrative"
        )

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

        logger.info(
            "12/15 Journalist"
        )

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

        logger.info(
            "13/15 Engagement"
        )

        try:

            engagement = (
                self.engagement.analyze(
                    package[
                        "story"
                    ]
                )
            )

            package[
                "engagement"
            ] = engagement

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

        logger.info(
            "14/15 Headline"
        )

        try:

            headline_result = (
                self.headline.analyze(
                    package[
                        "story"
                    ]
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

        logger.info(
            "15/15 Final editorial gate"
        )

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

                "error":
                    str(error)
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

        logger.info(
            "=" * 60
        )

        logger.info(
            "BRAIN PIPELINE COMPLETE"
        )

        logger.info(
            "Decision: %s",
            decision
        )

        logger.info(
            "=" * 60
        )

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


# =========================================================
# BASIC TEST
# =========================================================

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO
    )

    pipeline = BrainPipeline()

    print(
        pipeline.status()
            )
