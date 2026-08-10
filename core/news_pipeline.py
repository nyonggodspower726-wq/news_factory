"""
AI NEWS FACTORY
CORE NEWS PIPELINE

Connects the intelligence engines into one production pipeline.

Flow:

SOURCE DATA
    ↓
NORMALIZE
    ↓
VERIFY
    ↓
CLAIM ANALYSIS
    ↓
NEWS ANGLE
    ↓
READER PSYCHOLOGY
    ↓
ENGAGEMENT
    ↓
ARTICLE GENERATION
    ↓
IMAGE
    ↓
QUALITY CONTROL
    ↓
PUBLISHING
"""

from typing import Any, Dict, List
import logging
import time


logger = logging.getLogger(__name__)


class NewsPipeline:

    def __init__(
        self,
        claim_engine=None,
        angle_engine=None,
        psychology_engine=None,
        engagement_engine=None,
        journalist_engine=None,
        writer_engine=None,
        image_engine=None,
        quality_engine=None,
    ):

        self.claim_engine = claim_engine
        self.angle_engine = angle_engine
        self.psychology_engine = psychology_engine
        self.engagement_engine = engagement_engine
        self.journalist_engine = journalist_engine
        self.writer_engine = writer_engine
        self.image_engine = image_engine
        self.quality_engine = quality_engine

        self.version = "1.0.0"

    # =====================================================
    # PUBLIC API
    # =====================================================

    def process(
        self,
        story: Dict[str, Any],
        publish: bool = False
    ) -> Dict[str, Any]:

        started = time.time()

        result = {
            "status": "STARTED",
            "pipeline_version": self.version,
            "story": story,
            "stages": {},
            "errors": [],
        }

        try:

            story = self._normalize_story(
                story
            )

            result["stages"]["normalized"] = story

            claims = self._run_claim_analysis(
                story
            )

            result["stages"]["claims"] = claims

            if self._claims_failed(
                claims
            ):

                result["status"] = (
                    "REJECTED_VERIFICATION"
                )

                return self._finish(
                    result,
                    started
                )

            angle = self._run_angle_analysis(
                story,
                claims
            )

            result["stages"]["angle"] = angle

            psychology = self._run_psychology(
                story,
                angle
            )

            result["stages"]["psychology"] = psychology

            engagement = self._run_engagement(
                story,
                angle,
                psychology
            )

            result["stages"]["engagement"] = engagement

            journalism = self._run_journalist(
                story,
                claims,
                angle
            )

            result["stages"]["journalism"] = journalism

            article = self._run_writer(
                story,
                claims,
                angle,
                psychology,
                engagement,
                journalism
            )

            result["stages"]["article"] = article

            image = self._run_image_engine(
                story,
                article
            )

            result["stages"]["image"] = image

            quality = self._run_quality_control(
                story,
                claims,
                article,
                image
            )

            result["stages"]["quality"] = quality

            if not self._quality_passed(
                quality
            ):

                result["status"] = (
                    "REJECTED_QUALITY_CONTROL"
                )

                return self._finish(
                    result,
                    started
                )

            result["package"] = (
                self._build_content_package(
                    story,
                    claims,
                    angle,
                    psychology,
                    engagement,
                    journalism,
                    article,
                    image,
                    quality
                )
            )

            result["status"] = (
                "READY_TO_PUBLISH"
            )

            if publish:

                result["status"] = (
                    "PUBLISHING_PENDING"
                )

            return self._finish(
                result,
                started
            )

        except Exception as exc:

            logger.exception(
                "News pipeline failed"
            )

            result["status"] = (
                "PIPELINE_ERROR"
            )

            result["errors"].append(
                str(exc)
            )

            return self._finish(
                result,
                started
            )

    # =====================================================
    # NORMALIZATION
    # =====================================================

    def _normalize_story(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        if not isinstance(
            story,
            dict
        ):

            raise TypeError(
                "Story must be a dictionary."
            )

        normalized = dict(
            story
        )

        normalized.setdefault(
            "title",
            normalized.get(
                "headline",
                ""
            )
        )

        normalized.setdefault(
            "description",
            normalized.get(
                "summary",
                ""
            )
        )

        normalized.setdefault(
            "source",
            ""
        )

        normalized.setdefault(
            "source_url",
            ""
        )

        normalized.setdefault(
            "published_at",
            ""
        )

        normalized.setdefault(
            "category",
            "general"
        )

        normalized.setdefault(
            "country",
            ""
        )

        normalized.setdefault(
            "language",
            "en"
        )

        normalized.setdefault(
            "collected_at",
            time.time()
        )

        return normalized

    # =====================================================
    # CLAIM ENGINE
    # =====================================================

    def _run_claim_analysis(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        if self.claim_engine is None:

            return {
                "status":
                    "SKIPPED",

                "reason":
                    "Claim engine not connected."
            }

        return self._safe_engine_call(
            self.claim_engine,
            story
        )

    # =====================================================
    # ANGLE ENGINE
    # =====================================================

    def _run_angle_analysis(
        self,
        story: Dict[str, Any],
        claims: Dict[str, Any]
    ) -> Dict[str, Any]:

        if self.angle_engine is None:

            return {
                "status":
                    "SKIPPED"
            }

        return self._safe_engine_call(
            self.angle_engine,
            story,
            claims
        )

    # =====================================================
    # PSYCHOLOGY
    # =====================================================

    def _run_psychology(
        self,
        story: Dict[str, Any],
        angle: Dict[str, Any]
    ) -> Dict[str, Any]:

        if self.psychology_engine is None:

            return {
                "status":
                    "SKIPPED"
            }

        return self._safe_engine_call(
            self.psychology_engine,
            story,
            {},
            angle
        )

    # =====================================================
    # ENGAGEMENT
    # =====================================================

    def _run_engagement(
        self,
        story: Dict[str, Any],
        angle: Dict[str, Any],
        psychology: Dict[str, Any]
    ) -> Dict[str, Any]:

        if self.engagement_engine is None:

            return {
                "status":
                    "SKIPPED"
            }

        return self._safe_engine_call(
            self.engagement_engine,
            story,
            {},
            angle,
            psychology
        )

    # =====================================================
    # JOURNALIST
    # =====================================================

    def _run_journalist(
        self,
        story: Dict[str, Any],
        claims: Dict[str, Any],
        angle: Dict[str, Any]
    ) -> Dict[str, Any]:

        if self.journalist_engine is None:

            return {
                "status":
                    "SKIPPED"
            }

        return self._safe_engine_call(
            self.journalist_engine,
            story,
            claims,
            angle
        )

    # =====================================================
    # WRITER
    # =====================================================

    def _run_writer(
        self,
        story: Dict[str, Any],
        claims: Dict[str, Any],
        angle: Dict[str, Any],
        psychology: Dict[str, Any],
        engagement: Dict[str, Any],
        journalism: Dict[str, Any]
    ) -> Dict[str, Any]:

        if self.writer_engine is None:

            return {
                "status":
                    "SKIPPED",

                "title":
                    story.get(
                        "title",
                        ""
                    ),

                "content":
                    story.get(
                        "description",
                        ""
                    )
            }

        return self._safe_engine_call(
            self.writer_engine,
            story,
            claims,
            angle,
            psychology,
            engagement,
            journalism
        )

    # =====================================================
    # IMAGE
    # =====================================================

    def _run_image_engine(
        self,
        story: Dict[str, Any],
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        if self.image_engine is None:

            return {
                "status":
                    "SKIPPED"
            }

        return self._safe_engine_call(
            self.image_engine,
            story,
            article
        )

    # =====================================================
    # QUALITY CONTROL
    # =====================================================

    def _run_quality_control(
        self,
        story: Dict[str, Any],
        claims: Dict[str, Any],
        article: Dict[str, Any],
        image: Dict[str, Any]
    ) -> Dict[str, Any]:

        if self.quality_engine is None:

            return {
                "status":
                    "SKIPPED",

                "passed":
                    True
            }

        return self._safe_engine_call(
            self.quality_engine,
            story,
            claims,
            article,
            image
        )

    # =====================================================
    # SAFE ENGINE CALL
    # =====================================================

    def _safe_engine_call(
        self,
        engine,
        *args
    ) -> Dict[str, Any]:

        if hasattr(
            engine,
            "analyze"
        ):

            output = engine.analyze(
                *args
            )

        elif hasattr(
            engine,
            "process"
        ):

            output = engine.process(
                *args
            )

        elif hasattr(
            engine,
            "run"
        ):

            output = engine.run(
                *args
            )

        else:

            raise AttributeError(
                f"Engine {engine.__class__.__name__} "
                "has no analyze/process/run method."
            )

        if isinstance(
            output,
            dict
        ):

            return output

        return {
            "status":
                "COMPLETED",

            "result":
                output
        }

    # =====================================================
    # CLAIM FAILURE
    # =====================================================

    def _claims_failed(
        self,
        claims: Dict[str, Any]
    ) -> bool:

        if not claims:

            return False

        status = str(
            claims.get(
                "status",
                ""
            )
        ).upper()

        if status in {
            "FAILED",
            "REJECTED",
            "UNVERIFIED",
            "REJECTED_VERIFICATION"
        }:

            return True

        if claims.get(
            "publishable"
        ) is False:

            return True

        if claims.get(
            "verified"
        ) is False:

            return True

        return False

    # =====================================================
    # QUALITY PASS
    # =====================================================

    def _quality_passed(
        self,
        quality: Dict[str, Any]
    ) -> bool:

        if not quality:

            return True

        if quality.get(
            "passed"
        ) is False:

            return False

        status = str(
            quality.get(
                "status",
                ""
            )
        ).upper()

        if status in {
            "FAILED",
            "REJECTED",
            "BLOCKED"
        }:

            return False

        return True

    # =====================================================
    # PACKAGE
    # =====================================================

    def _build_content_package(
        self,
        story,
        claims,
        angle,
        psychology,
        engagement,
        journalism,
        article,
        image,
        quality
    ) -> Dict[str, Any]:

        title = (
            article.get(
                "title",
                article.get(
                    "headline",
                    story.get(
                        "title",
                        ""
                    )
                )
            )
            if isinstance(
                article,
                dict
            )
            else story.get(
                "title",
                ""
            )
        )

        content = (
            article.get(
                "content",
                article.get(
                    "body",
                    ""
                )
            )
            if isinstance(
                article,
                dict
            )
            else ""
        )

        return {

            "title":
                title,

            "content":
                content,

            "category":
                story.get(
                    "category",
                    "general"
                ),

            "source":
                story.get(
                    "source",
                    ""
                ),

            "source_url":
                story.get(
                    "source_url",
                    ""
                ),

            "published_at":
                story.get(
                    "published_at",
                    ""
                ),

            "image":
                image,

            "verification":
                claims,

            "angle":
                angle,

            "reader_intelligence":
                psychology,

            "engagement":
                engagement,

            "journalism":
                journalism,

            "quality":
                quality,

            "social_ready":
                True,

            "website_ready":
                True
        }

    # =====================================================
    # FINISH
    # =====================================================

    def _finish(
        self,
        result: Dict[str, Any],
        started: float
    ) -> Dict[str, Any]:

        result["processing_time"] = round(
            time.time() - started,
            3
        )

        return result


# =========================================================
# SIMPLE FACTORY
# =========================================================

def create_news_pipeline(
    claim_engine=None,
    angle_engine=None,
    psychology_engine=None,
    engagement_engine=None,
    journalist_engine=None,
    writer_engine=None,
    image_engine=None,
    quality_engine=None
):

    return NewsPipeline(

        claim_engine=claim_engine,

        angle_engine=angle_engine,

        psychology_engine=psychology_engine,

        engagement_engine=engagement_engine,

        journalist_engine=journalist_engine,

        writer_engine=writer_engine,

        image_engine=image_engine,

        quality_engine=quality_engine
    )
