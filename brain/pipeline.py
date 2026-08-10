"""
AI NEWS FACTORY
BRAIN PIPELINE

Central wiring system for all intelligence engines.

The rest of the factory should talk to this file instead of
calling individual brain engines directly.

Pipeline:

INPUT SOURCES
    ↓
STORY / EVENT RESOLUTION
    ↓
SOURCE INTELLIGENCE
    ↓
RESEARCH
    ↓
CORROBORATION / EVIDENCE
    ↓
CLAIMS / VERIFICATION / FACT CHECK
    ↓
STORY INTELLIGENCE
    ↓
EDITORIAL INTELLIGENCE
    ↓
JOURNALIST
    ↓
READER / PSYCHOLOGY / ENGAGEMENT
    ↓
HEADLINE
    ↓
EDITOR
    ↓
FINAL NEWSROOM PACKAGE
"""

from __future__ import annotations

import importlib
import inspect
import logging
from typing import Any, Dict, List


logger = logging.getLogger("NewsFactory.BrainPipeline")


# =========================================================
# BRAIN MODULES
# =========================================================

BRAIN_MODULES = [
    "story_cluster",
    "entity_resolution_engine",
    "event_resolution_engine",

    "story_analyzer",
    "news_brain",

    "source_intelligence",
    "source_intelligence_engine",
    "source_verification",
    "source_graph_engine",

    "research_engine",
    "corroboration_engine",
    "claim_engine",
    "evidence_engine",
    "claim_verification_engine",
    "fact_checker",
    "misinformation_engine",

    "context_engine",
    "investigation_engine",
    "novelty_engine",
    "significance_engine",
    "trend_engine",
    "story_synthesis_engine",

    "angle_finder",
    "angle_engine",
    "editor_engine",

    "narrative_engine",
    "journalist_engine",

    "reader_intelligence",
    "reader_psychology_engine",
    "psychology_engine",
    "engagement_engine",

    "headline_engine",
]


# =========================================================
# METHODS TO TRY FOR EACH ENGINE
# =========================================================

ENGINE_METHODS = {

    "story_cluster": [
        "cluster",
        "analyze",
        "build_cluster",
        "create_cluster",
    ],

    "entity_resolution_engine": [
        "resolve",
        "analyze",
    ],

    "event_resolution_engine": [
        "resolve",
        "analyze",
    ],

    "story_analyzer": [
        "analyze",
    ],

    "news_brain": [
        "process_story",
        "analyze",
        "process",
    ],

    "source_intelligence": [
        "analyze",
        "process",
    ],

    "source_intelligence_engine": [
        "analyze",
    ],

    "source_verification": [
        "verify",
        "analyze",
    ],

    "source_graph_engine": [
        "build_graph",
        "analyze",
    ],

    "research_engine": [
        "research",
        "analyze",
    ],

    "corroboration_engine": [
        "analyze",
    ],

    "claim_engine": [
        "analyze",
        "extract_claims",
        "process",
    ],

    "evidence_engine": [
        "analyze",
        "build_evidence",
        "process",
    ],

    "claim_verification_engine": [
        "verify",
        "analyze",
        "verify_claims",
    ],

    "fact_checker": [
        "verify_story",
        "verify",
        "analyze",
    ],

    "misinformation_engine": [
        "analyze",
        "detect",
        "check",
    ],

    "context_engine": [
        "analyze",
        "build_context",
        "process",
    ],

    "investigation_engine": [
        "investigate",
        "analyze",
        "research",
    ],

    "novelty_engine": [
        "analyze",
        "detect",
        "evaluate",
    ],

    "significance_engine": [
        "evaluate",
        "analyze",
    ],

    "trend_engine": [
        "analyze",
        "detect",
        "evaluate",
    ],

    "story_synthesis_engine": [
        "synthesize",
        "analyze",
        "build_story",
    ],

    "angle_finder": [
        "find",
        "find_angle",
        "analyze",
        "discover",
    ],

    "angle_engine": [
        "analyze",
        "generate",
        "find",
    ],

    "editor_engine": [
        "review",
        "edit",
        "analyze",
    ],

    "narrative_engine": [
        "build",
        "create",
        "analyze",
        "generate",
    ],

    "journalist_engine": [
        "write",
        "create",
        "generate",
        "build_article",
        "create_article_plan",
    ],

    "reader_intelligence": [
        "analyze",
    ],

    "reader_psychology_engine": [
        "analyze",
    ],

    "psychology_engine": [
        "analyze",
    ],

    "engagement_engine": [
        "analyze",
    ],

    "headline_engine": [
        "analyze",
    ],
}


# =========================================================
# PIPELINE
# =========================================================

class BrainPipeline:

    def __init__(self):

        self.engines: Dict[str, Any] = {}
        self.engine_status: Dict[str, str] = {}

        self._load_engines()

    # =====================================================
    # LOAD ENGINES
    # =====================================================

    def _load_engines(self):

        for module_name in BRAIN_MODULES:

            try:

                module = importlib.import_module(
                    f"brain.{module_name}"
                )

                engine = self._find_engine_instance(
                    module
                )

                if engine is None:

                    self.engine_status[
                        module_name
                    ] = "NO_ENGINE_CLASS"

                    logger.warning(
                        "No engine class found: %s",
                        module_name
                    )

                    continue

                self.engines[
                    module_name
                ] = engine

                self.engine_status[
                    module_name
                ] = "LOADED"

                logger.info(
                    "Loaded brain: %s",
                    module_name
                )

            except Exception as error:

                self.engine_status[
                    module_name
                ] = f"LOAD_ERROR: {error}"

                logger.exception(
                    "Could not load brain: %s",
                    module_name
                )

    # =====================================================
    # FIND ENGINE INSTANCE
    # =====================================================

    def _find_engine_instance(
        self,
        module
    ):

        classes = []

        for name, obj in vars(module).items():

            if not inspect.isclass(obj):
                continue

            if obj.__module__ != module.__name__:
                continue

            classes.append(obj)

        # Prefer classes whose name looks like an engine/brain.
        classes.sort(
            key=lambda cls: (
                0
                if (
                    "engine" in cls.__name__.lower()
                    or "brain" in cls.__name__.lower()
                )
                else 1,
                cls.__name__
            )
        )

        for cls in classes:

            try:

                return cls()

            except TypeError:

                continue

            except Exception:

                logger.exception(
                    "Could not instantiate %s",
                    cls.__name__
                )

        return None

    # =====================================================
    # FIND METHOD
    # =====================================================

    def _find_method(
        self,
        module_name: str,
        engine: Any
    ):

        methods = ENGINE_METHODS.get(
            module_name,
            []
        )

        for method_name in methods:

            method = getattr(
                engine,
                method_name,
                None
            )

            if callable(method):

                return method

        return None

    # =====================================================
    # CALL ENGINE SAFELY
    # =====================================================

    def _call_engine(
        self,
        module_name: str,
        package: Dict[str, Any]
    ):

        engine = self.engines.get(
            module_name
        )

        if engine is None:

            return {
                "status": "ENGINE_NOT_LOADED",
                "engine": module_name
            }

        method = self._find_method(
            module_name,
            engine
        )

        if method is None:

            return {
                "status": "NO_SUPPORTED_METHOD",
                "engine": module_name
            }

        try:

            signature = inspect.signature(
                method
            )

            kwargs = {}

            for parameter_name, parameter in signature.parameters.items():

                if parameter_name == "self":
                    continue

                if parameter.kind in {
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD
                }:
                    continue

                if parameter_name in package:

                    kwargs[
                        parameter_name
                    ] = package[
                        parameter_name
                    ]

            result = method(
                **kwargs
            )

            if isinstance(result, dict):

                return result

            return {
                "status": "SUCCESS",
                "result": result
            }

        except Exception as error:

            logger.exception(
                "Brain failed: %s",
                module_name
            )

            return {
                "status": "ERROR",
                "engine": module_name,
                "error": str(error)
            }

    # =====================================================
    # RUN ONE STAGE
    # =====================================================

    def _run(
        self,
        module_name: str,
        package: Dict[str, Any]
    ):

        logger.info(
            "Running brain: %s",
            module_name
        )

        result = self._call_engine(
            module_name,
            package
        )

        package[
            module_name
        ] = result

        return result

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
            if isinstance(story, dict)
            else {}
        )

        sources = (
            sources
            if isinstance(sources, list)
            else []
        )

        # -------------------------------------------------
        # CENTRAL PACKAGE
        # -------------------------------------------------

        package = {

            "sources": sources,

            "story": story,

            "topic": topic,

            "event": story.get(
                "event",
                {}
            ),

            "entities": story.get(
                "entities",
                {}
            ),

            "claims": story.get(
                "claims",
                []
            ),

            "facts": story.get(
                "facts",
                []
            ),

            "cluster": story.get(
                "cluster",
                {}
            ),

            "article": {},

            "article_plan": {},

            "psychology": {},

            "verification": {},

        }

        # =================================================
        # STAGE 1
        # STORY STRUCTURE
        # =================================================

        self._run(
            "story_cluster",
            package
        )

        cluster = package.get(
            "story_cluster",
            {}
        )

        if isinstance(cluster, dict):
            package["cluster"] = cluster

        self._run(
            "entity_resolution_engine",
            package
        )

        entity_result = package.get(
            "entity_resolution_engine",
            {}
        )

        if isinstance(entity_result, dict):
            package["entities"] = entity_result

        self._run(
            "event_resolution_engine",
            package
        )

        event_result = package.get(
            "event_resolution_engine",
            {}
        )

        if isinstance(event_result, dict):
            package["event"] = event_result

        # =================================================
        # STAGE 2
        # NEWS INTELLIGENCE
        # =================================================

        self._run(
            "story_analyzer",
            package
        )

        self._run(
            "news_brain",
            package
        )

        # =================================================
        # STAGE 3
        # SOURCE / RESEARCH INTELLIGENCE
        # =================================================

        self._run(
            "source_intelligence",
            package
        )

        self._run(
            "source_intelligence_engine",
            package
        )

        self._run(
            "source_verification",
            package
        )

        self._run(
            "source_graph_engine",
            package
        )

        self._run(
            "research_engine",
            package
        )

        # =================================================
        # STAGE 4
        # CORROBORATION / CLAIMS / EVIDENCE
        # =================================================

        self._run(
            "corroboration_engine",
            package
        )

        self._run(
            "claim_engine",
            package
        )

        claim_result = package.get(
            "claim_engine",
            {}
        )

        if isinstance(claim_result, dict):

            if isinstance(
                claim_result.get("claims"),
                list
            ):
                package["claims"] = (
                    claim_result["claims"]
                )

        self._run(
            "evidence_engine",
            package
        )

        self._run(
            "claim_verification_engine",
            package
        )

        self._run(
            "fact_checker",
            package
        )

        verification = package.get(
            "fact_checker",
            {}
        )

        if isinstance(
            verification,
            dict
        ):

            package[
                "verification"
            ] = verification

        self._run(
            "misinformation_engine",
            package
        )

        # =================================================
        # STAGE 5
        # STORY INTELLIGENCE
        # =================================================

        self._run(
            "context_engine",
            package
        )

        self._run(
            "investigation_engine",
            package
        )

        self._run(
            "novelty_engine",
            package
        )

        self._run(
            "significance_engine",
            package
        )

        self._run(
            "trend_engine",
            package
        )

        self._run(
            "story_synthesis_engine",
            package
        )

        # =================================================
        # STAGE 6
        # EDITORIAL INTELLIGENCE
        # =================================================

        self._run(
            "angle_finder",
            package
        )

        self._run(
            "angle_engine",
            package
        )

        # =================================================
        # STAGE 7
        # NARRATIVE / JOURNALIST
        # =================================================

        self._run(
            "narrative_engine",
            package
        )

        self._run(
            "journalist_engine",
            package
        )

        article_result = package.get(
            "journalist_engine",
            {}
        )

        if isinstance(
            article_result,
            dict
        ):

            package[
                "article_plan"
            ] = article_result

            package[
                "article"
            ] = article_result

        # =================================================
        # STAGE 8
        # READER INTELLIGENCE
        # =================================================

        self._run(
            "reader_intelligence",
            package
        )

        self._run(
            "reader_psychology_engine",
            package
        )

        psychology_result = package.get(
            "reader_psychology_engine",
            {}
        )

        if isinstance(
            psychology_result,
            dict
        ):

            package[
                "psychology"
            ] = psychology_result

        self._run(
            "psychology_engine",
            package
        )

        self._run(
            "engagement_engine",
            package
        )

        # =================================================
        # STAGE 9
        # HEADLINE
        # =================================================

        self._run(
            "headline_engine",
            package
        )

        headline_result = package.get(
            "headline_engine",
            {}
        )

        if isinstance(
            headline_result,
            dict
        ):

            recommended = (
                headline_result.get(
                    "recommended_headline"
                )
            )

            if recommended:

                package[
                    "story"
                ][
                    "headline"
                ] = recommended

        # =================================================
        # STAGE 10
        # FINAL EDITORIAL GATE
        # =================================================

        editorial_result = self._run(
            "editor_engine",
            package
        )

        package[
            "editorial"
        ] = editorial_result

        # =================================================
        # FINAL STATUS
        # =================================================

        package[
            "pipeline_status"
        ] = self._final_status(
            editorial_result
        )

        package[
            "brains_loaded"
        ] = len(
            self.engines
        )

        package[
            "brains_total"
        ] = len(
            BRAIN_MODULES
        )

        return package

    # =====================================================
    # FINAL STATUS
    # =====================================================

    def _final_status(
        self,
        editorial: Dict[str, Any]
    ) -> str:

        if not isinstance(
            editorial,
            dict
        ):
            return "REVIEW_REQUIRED"

        decision = str(
            editorial.get(
                "decision",
                editorial.get(
                    "publication_status",
                    ""
                )
            )
        ).upper()

        if decision == "BLOCKED":

            return "BLOCKED"

        if decision == "NEEDS_REVISION":

            return "NEEDS_REVISION"

        if decision in {
            "APPROVED",
            "APPROVED_WITH_WARNINGS"
        }:

            return decision

        return "REVIEW_REQUIRED"

    # =====================================================
    # STATUS
    # =====================================================

    def status(self) -> Dict[str, Any]:

        return {
            "total_brains": len(
                BRAIN_MODULES
            ),

            "loaded_brains": len(
                self.engines
            ),

            "brains": self.engine_status
        }


# =========================================================
# SIMPLE HELPER
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
# TEST
# =========================================================

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    pipeline = BrainPipeline()

    print("=" * 60)
    print("AI NEWS FACTORY - BRAIN PIPELINE")
    print("=" * 60)

    status = pipeline.status()

    print(
        f"Brains loaded: "
        f"{status['loaded_brains']}/"
        f"{status['total_brains']}"
    )

    for brain, state in status[
        "brains"
    ].items():

        print(
            f"{brain}: {state}"
        )
