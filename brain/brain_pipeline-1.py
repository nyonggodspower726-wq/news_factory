from __future__ import annotations

import inspect
import logging
import os
import re
import requests
from typing import TYPE_CHECKING, Any, Dict, List, Optional

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
from brain.event_resolution_engine import EventResolutionEngine
from brain.evidence_engine import EvidenceEngine
from brain.investigation_engine import InvestigationEngine
from brain.misinformation_engine import MisinformationEngine
from brain.source_verification import SourceVerificationEngine
from brain.story_cluster import StoryCluster
from brain.psychology_engine import PsychologyEngine
if TYPE_CHECKING:
    from factory_pipeline import FactoryPipeline

logger = logging.getLogger("NewsFactory.BrainPipeline")


class NvidiaBrainClient:
    def __init__(
        self,
        model: str = "meta/llama-3.3-70b-instruct",
        base_url: str = "https://integrate.api.nvidia.com/v1",
    ):
        self.name = "NVIDIA Brain Client"
        self.version = "2.3.0"
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_keys = [
            os.getenv("NVIDIA_API_KEY_1", "").strip(),
            os.getenv("NVIDIA_API_KEY_2", "").strip(),
            os.getenv("NVIDIA_API_KEY_3", "").strip(),
            os.getenv("NVIDIA_API_KEY_4", "").strip(),
        ]
        self.api_keys = [key for key in self.api_keys if key]
        self.current_key_index = 0
        try:
            self.timeout = int(os.getenv("NVIDIA_TIMEOUT", "60"))
        except (TypeError, ValueError):
            self.timeout = 60

    def status(self) -> Dict[str, Any]:
        return {
            "provider": "NVIDIA",
            "client": self.name,
            "version": self.version,
            "model": self.model,
            "configured_keys": len(self.api_keys),
            "configured": bool(self.api_keys),
            "failover_enabled": len(self.api_keys) > 1,
            "current_key_slot": (
                self.current_key_index + 1 if self.api_keys else None
            ),
        }

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        if not self.api_keys:
            raise RuntimeError(
                "No NVIDIA API keys configured. "
                "Set NVIDIA_API_KEY_1 in the environment."
            )

        if not isinstance(messages, list) or not messages:
            raise ValueError("messages must be a non-empty list.")

        last_error = None
        total = len(self.api_keys)

        for attempt in range(total):
            index = (self.current_key_index + attempt) % total
            key = self.api_keys[index]

            try:
                result = self._request(
                    key,
                    messages,
                    temperature,
                    max_tokens,
                )
                self.current_key_index = index
                return result
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "NVIDIA key slot %s/%s failed: %s",
                    index + 1,
                    total,
                    exc,
                )

        raise RuntimeError(
            f"All NVIDIA API keys failed. Last error: {last_error}"
        )

    def _request(
        self,
        api_key: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        response = requests.post(
            self.base_url + "/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()
        data = response.json()

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("NVIDIA API returned no choices.")

        message = choices[0].get("message", {})
        content = message.get("content")

        if not content:
            raise RuntimeError("NVIDIA API returned empty content.")

        return str(content).strip()


class BrainPipeline:
    def __init__(self, factory_pipeline: Optional[FactoryPipeline] = None):
        logger.info("Initializing central brain...")

        self.version = "2.3.0"
        self.ai = NvidiaBrainClient()

        self.story_analyzer = StoryAnalyzer()
        self.source_intelligence = SourceIntelligenceEngine()
        self.source_verification = SourceVerificationEngine()
        self.story_cluster = StoryCluster()
        self.event_resolution = EventResolutionEngine()

        self.claim_engine = ClaimEngine()
        self.evidence = EvidenceEngine()
        self.source_graph = SourceGraphEngine()
        self.corroboration = CorroborationEngine()
        self.fact_checker = FactChecker()
        self.investigation = InvestigationEngine()
        self.misinformation = MisinformationEngine()

        self.story_synthesis = StorySynthesisEngine()
        self.significance = SignificanceEngine()
        self.angle_finder = AngleFinder()
        self.reader_psychology = ReaderPsychologyEngine()
        self.psychology = PsychologyEngine()
        self.engagement = EngagementEngine()
        self.narrative = NarrativeEngine()

        self.journalist = JournalistEngine()
        self.headline = HeadlineEngine()
        self.editor = EditorEngine()

        if factory_pipeline is not None:
            self.factory_pipeline = factory_pipeline
        else:
            from factory_pipeline import FactoryPipeline
            self.factory_pipeline = FactoryPipeline()

        logger.info("Central brain initialized with full intelligence stack.")

    def status(self) -> Dict[str, Any]:
        names = [
            "story_analyzer",
            "source_intelligence",
            "source_verification",
            "story_cluster",
            "event_resolution",
            "claim_engine",
            "evidence",
            "source_graph",
            "corroboration",
            "fact_checker",
            "investigation",
            "misinformation",
            "story_synthesis",
            "significance",
            "angle_finder",
            "reader_psychology",
            "psychology",
            "engagement",
            "narrative",
            "journalist",
            "headline",
            "editor",
        ]

        components = {
            name: self._component_ready(getattr(self, name, None))
            for name in names
        }

        return {
            "status": "READY",
            "engine": "BrainPipeline",
            "version": self.version,
            "initialized": True,
            "total_brains": len(names),
            "loaded_brains": [
                name for name, ready in components.items() if ready
            ],
            "brains": components,
            "ai_provider": self.ai.status(),
            "factory_pipeline": self._component_status(
                self.factory_pipeline
            ),
        }

    def run(
        self,
        sources: List[Dict[str, Any]],
        story: Optional[Dict[str, Any]] = None,
        topic: str = "",
        platform: str = "website",
        prepare_publication: bool = True,
    ) -> Dict[str, Any]:
        sources = sources if isinstance(sources, list) else []
        story = self._safe_dict(story)

        package = {
            "story": story,
            "sources": sources,
            "topic": topic or "",
            "claims": [],
            "claim_analysis": {},
            "evidence": {},
            "verification": {},
            "source_verification": {},
            "corroboration": {},
            "source_graph": {},
            "source_intelligence": {},
            "cluster": {},
            "event_resolution": {},
            "investigation": {},
            "misinformation": {},
            "significance": {},
            "angles": {},
            "psychology": {},
            "reader_psychology": {},
            "engagement": {},
            "narrative": {},
            "synthesis": {},
            "story_model": {},
            "article_plan": {},
            "article": {},
            "headline": {},
            "editorial": {},
            "publication": {},
            "publication_ready": False,
            "ai": self.ai,
        }

        logger.info("=" * 70)
        logger.info("CENTRAL BRAIN PIPELINE STARTED")
        logger.info("=" * 70)

        try:
            package["story_analysis"] = self._safe(
                "story_analysis",
                self.story_analyzer,
                ["analyze"],
                {"story": package["story"]},
            )

            if isinstance(package["story_analysis"], dict):
                analyzed_story = package["story_analysis"].get("story")
                if isinstance(analyzed_story, dict):
                    package["story"].update(analyzed_story)

            package["source_intelligence"] = self._safe(
                "source_intelligence",
                self.source_intelligence,
                ["analyze"],
                {"sources": sources},
            )

            package["source_verification"] = self._safe(
                "source_verification",
                self.source_verification,
                ["analyze", "verify"],
                {"sources": sources},
            )

            package["cluster"] = self._safe(
                "story_cluster",
                self.story_cluster,
                ["cluster_stories", "cluster", "analyze"],
                {
                    "stories": sources,
                    "sources": sources,
                    "story": package["story"],
                },
            )

            events = self._build_events(
                sources,
                package["story"],
            )

            package["event_resolution"] = self._safe(
                "event_resolution",
                self.event_resolution,
                ["resolve", "analyze"],
                {
                    "events": events,
                    "sources": sources,
                    "story": package["story"],
                },
            )

            package["claim_analysis"] = self._safe(
                "claim_engine",
                self.claim_engine,
                ["analyze", "extract"],
                {
                    "story": package["story"],
                    "sources": sources,
                    "topic": topic,
                    "research": package["source_intelligence"],
                },
            )

            package["claims"] = self._extract_claims(
                package["claim_analysis"]
            )

            package["evidence"] = self._safe(
                "evidence_engine",
                self.evidence,
                ["analyze", "evaluate"],
                {
                    "claims": package["claims"],
                    "sources": sources,
                    "story": package["story"],
                },
            )

            package["source_graph"] = self._safe(
                "source_graph",
                self.source_graph,
                ["build_graph", "analyze"],
                {
                    "sources": sources,
                    "claims": package["claims"],
                    "entities": self._extract_entities(
                        package["story"]
                    ),
                },
            )

            package["corroboration"] = self._safe(
                "corroboration",
                self.corroboration,
                ["analyze", "corroborate"],
                {
                    "sources": sources,
                    "claims": package["claims"],
                    "evidence": package["evidence"],
                },
            )

            package["verification"] = self._safe(
                "fact_checker",
                self.fact_checker,
                ["verify_story", "verify", "analyze"],
                {
                    "story": package["story"],
                    "sources": sources,
                    "claims": package["claims"],
                    "evidence": package["evidence"],
                },
            )

            package["investigation"] = self._safe(
                "investigation",
                self.investigation,
                ["investigate", "analyze"],
                {
                    "story": package["story"],
                    "research": package["source_intelligence"],
                    "claims": package["claims"],
                    "sources": sources,
                },
            )

            package["misinformation"] = self._safe(
                "misinformation",
                self.misinformation,
                ["analyze", "assess"],
                {
                    "claims": package["claims"],
                    "sources": sources,
                    "story": package["story"],
                },
            )

            package["significance"] = self._safe(
                "significance",
                self.significance,
                ["evaluate", "analyze", "assess"],
                {
                    "story": package["story"],
                    "sources": sources,
                    "claims": package["claims"],
                    "evidence": package["evidence"],
                },
            )

            package["angles"] = self._safe(
                "angle_finder",
                self.angle_finder,
                ["analyze", "find", "find_angles", "evaluate"],
                {
                    "story": package["story"],
                    "related_stories": self._related_stories(
                        package["cluster"]
                    ),
                    "evidence": package["evidence"],
                    "trend_data": package["significance"],
                    "article_plan": package["article_plan"],
                    "cluster": package["cluster"],
                },
            )

            package["synthesis"] = self._safe(
                "story_synthesis",
                self.story_synthesis,
                ["synthesize", "analyze"],
                {
                    "sources": sources,
                    "evidence": package["evidence"],
                    "metadata": {
                        "topic": topic,
                        "story": package["story"],
                        "claims": package["claims"],
                        "verification": package["verification"],
                        "corroboration": package["corroboration"],
                        "source_graph": package["source_graph"],
                        "source_intelligence": package[
                            "source_intelligence"
                        ],
                        "investigation": package["investigation"],
                        "misinformation": package["misinformation"],
                        "significance": package["significance"],
                        "angles": package["angles"],
                    },
                },
            )

            package["story_model"] = self._safe_dict(
                package["synthesis"]
            )

            package["article_plan"] = (
                self._build_provisional_article_plan(package)
            )

            package["reader_psychology"] = self._safe(
                "reader_psychology",
                self.reader_psychology,
                ["analyze", "evaluate", "assess"],
                {
                    "article_plan": package["article_plan"],
                    "story": package["story"],
                    "significance": package["significance"],
                    "angles": package["angles"],
                    "claims": package["claims"],
                    "evidence": package["evidence"],
                },
            )

            package["psychology"] = self._safe(
                "psychology",
                self.psychology,
                ["analyze", "evaluate", "assess"],
                {
                    "article_plan": package["article_plan"],
                    "story": package["story"],
                    "significance": package["significance"],
                    "angles": package["angles"],
                    "reader_psychology": package["reader_psychology"],
                    "claims": package["claims"],
                    "evidence": package["evidence"],
                },
            )

            package["engagement"] = self._safe(
                "engagement",
                self.engagement,
                ["analyze", "evaluate", "optimize"],
                {
                    "article_plan": package["article_plan"],
                    "story": package["story"],
                    "significance": package["significance"],
                    "angles": package["angles"],
                    "psychology": package["psychology"],
                    "reader_psychology": package[
                        "reader_psychology"
                    ],
                    "claims": package["claims"],
                },
            )

            package["narrative"] = self._safe(
                "narrative",
                self.narrative,
                ["analyze", "build", "construct", "create"],
                {
                    "article_plan": package["article_plan"],
                    "story": package["story"],
                    "synthesis": package["synthesis"],
                    "story_model": package["story_model"],
                    "claims": package["claims"],
                    "evidence": package["evidence"],
                    "angles": package["angles"],
                    "psychology": package["psychology"],
                    "reader_psychology": package[
                        "reader_psychology"
                    ],
                    "engagement": package["engagement"],
                },
            )

            final_plan = self._safe(
                "journalist",
                self.journalist,
                [
                    "write",
                    "create",
                    "generate",
                    "produce",
                    "compose",
                    "analyze",
                ],
                {
                    "article_plan": package["article_plan"],
                    "story": package["story"],
                    "sources": sources,
                    "claims": package["claims"],
                    "evidence": package["evidence"],
                    "verification": package["verification"],
                    "synthesis": package["synthesis"],
                    "story_model": package["story_model"],
                    "narrative": package["narrative"],
                    "angles": package["angles"],
                    "psychology": package["psychology"],
                    "reader_psychology": package[
                        "reader_psychology"
                    ],
                    "engagement": package["engagement"],
                    "significance": package["significance"],
                    "ai": self.ai,
                },
            )

            package["article_plan"] = self._merge_article_plan(
                package["article_plan"],
                final_plan,
            )

            package["article"] = self._extract_article(
                package["article_plan"]
            )

            package["headline"] = self._safe(
                "headline",
                self.headline,
                ["generate", "create", "analyze", "optimize"],
                {
                    "article_plan": package["article_plan"],
                    "article": package["article"],
                    "story": package["story"],
                    "significance": package["significance"],
                    "angles": package["angles"],
                    "psychology": package["psychology"],
                    "platform": platform,
                },
            )

            package["editorial"] = self._safe(
                "editor",
                self.editor,
                [
                    "review",
                    "edit",
                    "evaluate",
                    "analyze",
                    "approve",
                ],
                {
                    "article_plan": package["article_plan"],
                    "article": package["article"],
                    "story": package["story"],
                    "claims": package["claims"],
                    "evidence": package["evidence"],
                    "verification": package["verification"],
                    "misinformation": package["misinformation"],
                    "investigation": package["investigation"],
                    "headline": package["headline"],
                    "narrative": package["narrative"],
                    "cluster": package["cluster"],
                    "psychology": package["psychology"],
                },
            )

            package["publication_ready"] = (
                self._editor_allows_publication(
                    package["editorial"]
                )
            )

            package["brain_summary"] = {
                "status": "BRAIN_COMPLETE",
                "topic": topic,
                "source_count": len(sources),
                "claim_count": len(package["claims"]),
                "publication_ready": package["publication_ready"],
                "verification": self._status_value(
                    package["verification"]
                ),
                "misinformation": self._status_value(
                    package["misinformation"]
                ),
                "investigation": self._status_value(
                    package["investigation"]
                ),
                "editorial": self._status_value(
                    package["editorial"]
                ),
            }

            if prepare_publication:
                try:
                    publication = self.factory_pipeline.prepare(
                        package,
                        platform,
                    )
                    package["publication"] = self._safe_dict(
                        publication
                    )

                    package["publication_ready"] = (
                        package["publication"].get("status")
                        == "READY"
                    )
                except Exception as exc:
                    logger.exception(
                        "Brain-to-factory handoff failed."
                    )
                    package["publication"] = {
                        "status": "FAILED",
                        "stage": "FACTORY_HANDOFF",
                        "error": str(exc),
                    }
                    package["publication_ready"] = False

            package["pipeline_status"] = "BRAIN_COMPLETE"
            package["status"] = "BRAIN_COMPLETE"

        except Exception as exc:
            logger.exception("Central brain pipeline failed.")

            package["pipeline_status"] = "PIPELINE_ERROR"
            package["status"] = "PIPELINE_ERROR"
            package["error"] = str(exc)

            package["brain_summary"] = {
                "status": "PIPELINE_ERROR",
                "topic": topic,
                "source_count": len(sources),
                "claim_count": len(package.get("claims", [])),
                "publication_ready": False,
                "error": str(exc),
            }

        logger.info(
            "BRAIN PIPELINE STATUS: %s",
            package.get("pipeline_status"),
        )
        logger.info("=" * 70)
        logger.info("CENTRAL BRAIN PIPELINE COMPLETE")
        logger.info("=" * 70)

        return package

    def _safe(
        self,
        name: str,
        engine: Any,
        methods: List[str],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        context = self._normalize_context(context)

        if engine is None:
            return {
                "status": "MISSING",
                "engine": name,
            }

        method = None
        method_name = ""

        for candidate in methods:
            fn = getattr(engine, candidate, None)
            if callable(fn):
                method = fn
                method_name = candidate
                break

        if method is None:
            return {
                "status": "UNSUPPORTED",
                "engine": name,
                "error": "No compatible method found.",
                "methods": methods,
            }

        try:
            arguments = self._adapt_arguments(
                method,
                context,
            )

            result = method(**arguments)

            if result is None:
                return {
                    "status": "COMPLETE",
                    "engine": name,
                    "method": method_name,
                    "result": {},
                }

            if isinstance(result, dict):
                return result

            return {
                "status": "COMPLETE",
                "engine": name,
                "method": method_name,
                "result": result,
            }

        except TypeError as first_error:
            logger.warning(
                "%s.%s keyword call failed: %s",
                name,
                method_name,
                first_error,
            )

            try:
                result = self._positional_fallback(
                    method,
                    context,
                )

                if result is None:
                    return {
                        "status": "COMPLETE",
                        "engine": name,
                        "method": method_name,
                        "result": {},
                    }

                if isinstance(result, dict):
                    return result

                return {
                    "status": "COMPLETE",
                    "engine": name,
                    "method": method_name,
                    "result": result,
                }

            except Exception as fallback_error:
                logger.exception(
                    "%s fallback failed.",
                    name,
                )

                return {
                    "status": "ERROR",
                    "engine": name,
                    "method": method_name,
                    "error": str(fallback_error),
                    "original_error": str(first_error),
                }

        except Exception as exc:
            logger.exception(
                "%s.%s failed.",
                name,
                method_name,
            )

            return {
                "status": "ERROR",
                "engine": name,
                "method": method_name,
                "error": str(exc),
            }

    def _adapt_arguments(
        self,
        method: Any,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            signature = inspect.signature(method)
        except (TypeError, ValueError):
            return context

        aliases = {
            "source": "sources",
            "source_list": "sources",
            "source_data": "sources",
            "claim": "claims",
            "claim_list": "claims",
            "claim_data": "claims",
            "research_data": "research",
            "article_data": "article",
            "story_data": "story",
            "trend": "trend_data",
            "event_list": "events",
            "items": "stories",
            "plan": "article_plan",
            "cluster_data": "cluster",
            "evidence_data": "evidence",
            "headline_data": "headline",
            "editor_data": "editorial",
        }

        fallback_defaults = {
            "article_plan": {},
            "story": {},
            "sources": [],
            "claims": [],
            "evidence": {},
            "research": {},
            "metadata": {},
            "article": {},
            "events": [],
            "stories": [],
            "trend_data": {},
            "cluster": {},
            "psychology": {},
            "reader_psychology": {},
            "engagement": {},
            "verification": {},
            "corroboration": {},
            "source_graph": {},
            "source_intelligence": {},
            "misinformation": {},
            "investigation": {},
            "headline": {},
            "narrative": {},
            "significance": {},
            "angles": {},
            "journalism": {},
            "editorial": {},
            "topic": "",
            "platform": "website",
        }

        arguments = {}

        for name, parameter in signature.parameters.items():
            if name == "self":
                continue

            if parameter.kind in {
                inspect.Parameter.VAR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
            }:
                continue

            if name in context:
                value = context[name]

            elif aliases.get(name) in context:
                value = context[aliases[name]]

            elif name in fallback_defaults:
                value = fallback_defaults[name]

            elif parameter.default is not inspect.Parameter.empty:
                continue

            else:
                raise TypeError(
                    f"Required parameter '{name}' cannot be mapped."
                )

            arguments[name] = value

        return arguments

    def _positional_fallback(
        self,
        method: Any,
        context: Dict[str, Any],
    ) -> Any:
        signature = inspect.signature(method)
        args = []

        for name, parameter in signature.parameters.items():
            if name == "self":
                continue

            if parameter.kind in {
                inspect.Parameter.VAR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
            }:
                continue

            if name in context:
                args.append(context[name])
            elif name in {"sources", "source_list"}:
                args.append(context.get("sources", []))
            elif name in {"claims", "claim_list"}:
                args.append(context.get("claims", []))
            elif name == "story":
                args.append(context.get("story", {}))
            elif name == "article_plan":
                args.append(context.get("article_plan", {}))
            elif name == "article":
                args.append(context.get("article", {}))
            elif name == "evidence":
                args.append(context.get("evidence", {}))
            elif name == "research":
                args.append(context.get("research", {}))
            elif name == "metadata":
                args.append(context.get("metadata", {}))
            elif name == "events":
                args.append(context.get("events", []))
            elif name == "stories":
                args.append(context.get("stories", []))
            elif name == "cluster":
                args.append(context.get("cluster", {}))
            elif name == "psychology":
                args.append(context.get("psychology", {}))
            elif name == "reader_psychology":
                args.append(context.get("reader_psychology", {}))
            elif name == "engagement":
                args.append(context.get("engagement", {}))
            elif name == "verification":
                args.append(context.get("verification", {}))
            elif name == "corroboration":
                args.append(context.get("corroboration", {}))
            elif name == "source_graph":
                args.append(context.get("source_graph", {}))
            elif name == "source_intelligence":
                args.append(context.get("source_intelligence", {}))
            elif name == "misinformation":
                args.append(context.get("misinformation", {}))
            elif name == "investigation":
                args.append(context.get("investigation", {}))
            elif name == "headline":
                args.append(context.get("headline", {}))
            elif name == "narrative":
                args.append(context.get("narrative", {}))
            elif name == "significance":
                args.append(context.get("significance", {}))
            elif name == "angles":
                args.append(context.get("angles", {}))
            elif name == "journalism":
                args.append(context.get("journalism", {}))
            elif name == "editorial":
                args.append(context.get("editorial", {}))
            elif name == "topic":
                args.append(context.get("topic", ""))
            elif name == "platform":
                args.append(context.get("platform", "website"))
            elif parameter.default is not inspect.Parameter.empty:
                continue
            else:
                args.append(None)

        return method(*args)

    def _normalize_context(
        self,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        normalized = dict(context or {})

        dictionary_keys = (
            "article_plan",
            "story",
            "evidence",
            "verification",
            "corroboration",
            "source_graph",
            "source_intelligence",
            "significance",
            "angles",
            "psychology",
            "reader_psychology",
            "engagement",
            "narrative",
            "synthesis",
            "story_model",
            "investigation",
            "misinformation",
            "headline",
            "editorial",
            "article",
            "cluster",
            "research",
            "metadata",
            "journalism",
        )

        for key in dictionary_keys:
            if normalized.get(key) is None:
                normalized[key] = {}

        list_keys = (
            "sources",
            "claims",
            "events",
            "stories",
        )

        for key in list_keys:
            if not isinstance(normalized.get(key), list):
                normalized[key] = []

        return normalized

    def _extract_claims(
        self,
        result: Any,
    ) -> List[Dict[str, Any]]:
        if not isinstance(result, dict):
            return []

        raw_claims = result.get("claims")

        if raw_claims is None:
            raw_claims = result.get("claim_list")

        if raw_claims is None:
            raw_claims = result.get("items")

        if raw_claims is None:
            raw_claims = result.get("result")

        if isinstance(raw_claims, dict):
            raw_claims = raw_claims.get("claims", [])

        if not isinstance(raw_claims, list):
            return []

        claims = []

        for index, item in enumerate(raw_claims):
            if isinstance(item, str):
                text = item.strip()

                if text:
                    claims.append(
                        {
                            "id": f"claim_{index + 1}",
                            "text": text,
                            "type": "FACT",
                        }
                    )

            elif isinstance(item, dict):
                text = str(
                    item.get(
                        "text",
                        item.get(
                            "claim",
                            item.get("statement", ""),
                        ),
                    )
                    or ""
                ).strip()

                if not text:
                    continue

                claim = dict(item)

                claim.setdefault(
                    "id",
                    f"claim_{index + 1}",
                )
                claim["text"] = text

                claims.append(claim)

        return self._deduplicate_items(
            claims,
            "text",
        )

    def _extract_entities(
        self,
        story: Dict[str, Any],
    ) -> List[str]:
        if not isinstance(story, dict):
            return []

        existing = story.get("entities")

        if isinstance(existing, list):
            return self._unique_strings(existing)

        text_parts = []

        for key in (
            "title",
            "headline",
            "description",
            "summary",
            "body",
            "content",
        ):
            value = story.get(key)

            if isinstance(value, str):
                text_parts.append(value)

        text = " ".join(text_parts)

        if not text:
            return []

        entities = []

        for match in re.findall(
            r"\b[A-Z][A-Za-z0-9&.'-]*(?:\s+[A-Z][A-Za-z0-9&.'-]*){0,3}",
            text,
        ):
            cleaned = match.strip(" ,.;:!?()[]{}\"'")

            if len(cleaned) >= 2:
                entities.append(cleaned)

        return self._unique_strings(entities)

    def _build_events(
        self,
        sources: List[Dict[str, Any]],
        story: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        events = []

        if isinstance(story, dict):
            existing = story.get("events")

            if isinstance(existing, list):
                for event in existing:
                    if isinstance(event, dict):
                        events.append(dict(event))

        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                continue

            event = {
                "id": source.get(
                    "event_id",
                    source.get(
                        "id",
                        f"source_event_{index + 1}",
                    ),
                ),
                "title": source.get(
                    "title",
                    source.get(
                        "headline",
                        "",
                    ),
                ),
                "description": source.get(
                    "description",
                    source.get(
                        "summary",
                        source.get(
                            "text",
                            source.get(
                                "content",
                                "",
                            ),
                        ),
                    ),
                ),
                "source": source.get(
                    "source",
                    source.get(
                        "name",
                        source.get(
                            "url",
                            "",
                        ),
                    ),
                ),
                "source_url": source.get(
                    "source_url",
                    source.get(
                        "url",
                        "",
                    ),
                ),
                "published_at": source.get(
                    "published_at",
                    source.get(
                        "date",
                        "",
                    ),
                ),
            }

            if any(
                str(value).strip()
                for value in event.values()
                if value is not None
            ):
                events.append(event)

        return self._deduplicate_items(
            events,
            "id",
        )

    def _related_stories(
        self,
        cluster: Any,
    ) -> List[Dict[str, Any]]:
        if not isinstance(cluster, dict):
            return []

        for key in (
            "related_stories",
            "stories",
            "cluster_stories",
            "related",
            "items",
        ):
            value = cluster.get(key)

            if isinstance(value, list):
                return [
                    item
                    for item in value
                    if isinstance(item, dict)
                ]

        return []

    def _build_provisional_article_plan(
        self,
        package: Dict[str, Any],
    ) -> Dict[str, Any]:
        story = self._safe_dict(
            package.get("story")
        )

        synthesis = self._safe_dict(
            package.get("synthesis")
        )

        angles = self._safe_dict(
            package.get("angles")
        )

        narrative = self._safe_dict(
            package.get("narrative")
        )

        psychology = self._safe_dict(
            package.get("psychology")
        )

        engagement = self._safe_dict(
            package.get("engagement")
        )

        title = (
            synthesis.get("title")
            or synthesis.get("headline")
            or angles.get("headline")
            or story.get("title")
            or story.get("headline")
            or ""
        )

        angle = (
            angles.get("primary_angle")
            or angles.get("best_angle")
            or angles.get("angle")
            or ""
        )

        return {
            "title": title,
            "headline": title,
            "topic": package.get("topic", ""),
            "category": story.get(
                "category",
                "general",
            ),
            "source": story.get(
                "source",
                "",
            ),
            "source_url": story.get(
                "source_url",
                "",
            ),
            "claims": package.get(
                "claims",
                [],
            ),
            "evidence": package.get(
                "evidence",
                {},
            ),
            "verification": package.get(
                "verification",
                {},
            ),
            "angle": angle,
            "angles": angles,
            "synthesis": synthesis,
            "story_model": package.get(
                "story_model",
                {},
            ),
            "narrative": narrative,
            "reader_psychology": package.get(
                "reader_psychology",
                {},
            ),
            "psychology": psychology,
            "engagement": engagement,
            "significance": package.get(
                "significance",
                {},
            ),
            "journalism": {},
            "article": {},
            "status": "PROVISIONAL",
        }

    def _merge_article_plan(
        self,
        original: Any,
        final: Any,
    ) -> Dict[str, Any]:
        base = (
            dict(original)
            if isinstance(original, dict)
            else {}
        )

        if not isinstance(final, dict):
            return base

        nested = final.get("result")

        if isinstance(nested, dict):
            merged = dict(nested)
            merged.update(base)
            merged.update(final)
            return merged

        merged = dict(base)

        for key, value in final.items():
            if value is None:
                continue

            if isinstance(value, dict) and isinstance(
                merged.get(key),
                dict,
            ):
                combined = dict(merged[key])
                combined.update(value)
                merged[key] = combined
            else:
                merged[key] = value

        merged["status"] = (
            final.get(
                "status",
                merged.get(
                    "status",
                    "READY",
                ),
            )
        )

        return merged

    def _extract_article(
        self,
        article_plan: Any,
    ) -> Dict[str, Any]:
        if not isinstance(article_plan, dict):
            return {}

        candidates = [
            article_plan.get("article"),
            article_plan.get("result"),
            article_plan,
        ]

        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue

            title = (
                candidate.get("title")
                or candidate.get("headline")
                or ""
            )

            content = (
                candidate.get("content")
                or candidate.get("body")
                or candidate.get("article")
                or candidate.get("text")
                or ""
            )

            if title or content:
                return {
                    "title": str(title),
                    "headline": str(
                        candidate.get(
                            "headline",
                            title,
                        )
                    ),
                    "content": str(content),
                    "body": str(content),
                }

        return {
            "title": str(
                article_plan.get(
                    "title",
                    article_plan.get(
                        "headline",
                        "",
                    ),
                )
                or ""
            ),
            "content": str(
                article_plan.get(
                    "content",
                    article_plan.get(
                        "body",
                        "",
                    ),
                )
                or ""
            ),
        }

    def _editor_allows_publication(
        self,
        editorial: Any,
    ) -> bool:
        if not isinstance(editorial, dict):
            return True

        if editorial.get("approved") is False:
            return False

        if editorial.get("publishable") is False:
            return False

        if editorial.get("publication_allowed") is False:
            return False

        if editorial.get("passed") is False:
            return False

        status = str(
            editorial.get(
                "status",
                "",
            )
        ).upper()

        blocked_statuses = {
            "FAILED",
            "REJECTED",
            "BLOCKED",
            "HOLD",
            "HOLD_FOR_REVIEW",
            "HOLD_FOR_VERIFICATION",
            "NOT_READY",
        }

        if status in blocked_statuses:
            return False

        return True

    def _status_value(
        self,
        value: Any,
    ) -> str:
        if not isinstance(value, dict):
            return "UNKNOWN"

        for key in (
            "status",
            "verification_status",
            "result_status",
            "decision",
        ):
            if value.get(key) is not None:
                return str(
                    value[key]
                )

        if value.get("verified") is True:
            return "VERIFIED"

        if value.get("passed") is True:
            return "PASSED"

        if value.get("approved") is True:
            return "APPROVED"

        return "UNKNOWN"

    def _component_ready(
        self,
        component: Any,
    ) -> bool:
        if component is None:
            return False

        try:
            status_method = getattr(
                component,
                "status",
                None,
            )

            if callable(status_method):
                value = status_method()

                if isinstance(value, dict):
                    status = str(
                        value.get(
                            "status",
                            "READY",
                        )
                    ).upper()

                    return status not in {
                        "ERROR",
                        "FAILED",
                        "MISSING",
                        "UNAVAILABLE",
                    }

            return True

        except Exception:
            return False

    def _component_status(
        self,
        component: Any,
    ) -> Dict[str, Any]:
        if component is None:
            return {
                "status": "MISSING"
            }

        try:
            status_method = getattr(
                component,
                "status",
                None,
            )

            if callable(status_method):
                value = status_method()

                if isinstance(value, dict):
                    return value

            return {
                "status": "READY"
            }

        except Exception as exc:
            return {
                "status": "ERROR",
                "error": str(exc),
            }

    def _safe_dict(
        self,
        value: Any,
    ) -> Dict[str, Any]:
        return (
            dict(value)
            if isinstance(value, dict)
            else {}
        )

    def _unique_strings(
        self,
        values: List[Any],
    ) -> List[str]:
        result = []
        seen = set()

        for value in values:
            text = str(value).strip()

            if not text:
                continue

            key = text.lower()

            if key in seen:
                continue

            seen.add(key)
            result.append(text)

        return result

    def _deduplicate_items(
        self,
        items: List[Dict[str, Any]],
        key_name: str,
    ) -> List[Dict[str, Any]]:
        result = []
        seen = set()

        for item in items:
            if not isinstance(item, dict):
                continue

            value = item.get(key_name)

            if value is None:
                value = item.get("text", "")

            key = str(value).strip().lower()

            if not key:
                key = repr(
                    sorted(item.items())
                )

            if key in seen:
                continue

            seen.add(key)
            result.append(item)

        return result


def create_brain_pipeline(
    factory_pipeline: Optional[FactoryPipeline] = None,
) -> BrainPipeline:
    return BrainPipeline(
        factory_pipeline=factory_pipeline
    )


brain_pipeline = BrainPipeline()


def run_brain_pipeline(
    sources: List[Dict[str, Any]],
    story: Optional[Dict[str, Any]] = None,
    topic: str = "",
    platform: str = "website",
    prepare_publication: bool = True,
) -> Dict[str, Any]:
    return brain_pipeline.run(
        sources=sources,
        story=story,
        topic=topic,
        platform=platform,
        prepare_publication=prepare_publication,
    )


def brain_status() -> Dict[str, Any]:
    return brain_pipeline.status()


if __name__ == "__main__":
    import json

    print(
        json.dumps(
            brain_pipeline.status(),
            indent=2,
            default=str,
        )
    )
