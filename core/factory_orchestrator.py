"""
AI NEWS FACTORY
FACTORY ORCHESTRATOR

Main pipeline:

COLLECT
   ↓
STORE
   ↓
QUEUE
   ↓
ANALYZE
   ↓
WRITE
   ↓
MEDIA
   ↓
QUALITY CHECK
   ↓
PUBLISH WEBSITE
   ↓
PUBLISH SOCIAL
   ↓
LOG EVERYTHING
"""

import logging
from typing import Any, Dict, List, Optional

from storage.database import NewsDatabase
from storage.queue import NewsQueue
from collectors.source_manager import SourceManager
from media.media_manager import MediaManager
from core.content_factory import ContentFactory


logger = logging.getLogger(__name__)


class FactoryOrchestrator:

    def __init__(
        self,
        source_manager: SourceManager,
        database: Optional[NewsDatabase] = None,
        queue: Optional[NewsQueue] = None,
        media_manager: Optional[MediaManager] = None,
        content_factory: Optional[ContentFactory] = None,
        intelligence: Optional[Any] = None,
        website_publisher: Optional[Any] = None,
        social_publisher: Optional[Any] = None
    ):

        self.source_manager = source_manager

        self.database = (
            database
            or NewsDatabase()
        )

        self.queue = (
            queue
            or NewsQueue()
        )

        self.media_manager = (
            media_manager
            or MediaManager()
        )

        self.content_factory = (
            content_factory
            or ContentFactory()
        )

        self.intelligence = intelligence
        self.website_publisher = website_publisher
        self.social_publisher = social_publisher

        self.name = "AI News Factory"
        self.version = "1.0.0"

    # =====================================================
    # COLLECT
    # =====================================================

    def collect(
        self,
        limit_per_source: int = 20
    ) -> Dict[str, Any]:

        result = self.source_manager.collect_all(
            limit_per_source=limit_per_source
        )

        stories = result.get(
            "stories",
            []
        )

        queued = 0

        for story in stories:

            story_id = self.database.save_story(
                story
            )

            self.queue.add(
                story_id=story_id,
                payload=story,
                priority=self._priority(
                    story
                )
            )

            self.database.log(
                story_id,
                "collection",
                "SUCCESS",
                "Story collected and queued."
            )

            queued += 1

        result["queued"] = queued

        return result

    # =====================================================
    # PROCESS NEXT
    # =====================================================

    def process_next(
        self
    ) -> Optional[Dict[str, Any]]:

        job = self.queue.next()

        if not job:

            return None

        job_id = job["job_id"]

        story_id = job["story_id"]

        story = self.database.get_story(
            story_id
        )

        if not story:

            self.queue.fail(
                job_id,
                "Story was not found in database.",
                retry=False
            )

            return {

                "status":
                    "FAILED",

                "job_id":
                    job_id,

                "story_id":
                    story_id
            }

        try:

            self.database.update_story_status(
                story_id,
                "processing"
            )

            self.database.log(
                story_id,
                "analysis",
                "STARTED"
            )

            analyzed = self._analyze(
                story
            )

            self.database.log(
                story_id,
                "analysis",
                "SUCCESS"
            )

            article = self._create_content(
                analyzed
            )

            article = self.media_manager.attach(
                article,
                story
            )

            quality = self._quality_check(
                article,
                analyzed
            )

            if not quality["approved"]:

                self.database.update_story_status(
                    story_id,
                    "rejected"
                )

                self.database.log(
                    story_id,
                    "quality",
                    "REJECTED",
                    quality.get(
                        "reason",
                        ""
                    )
                )

                self.queue.complete(
                    job_id,
                    {
                        "status":
                            "REJECTED",

                        "quality":
                            quality
                    }
                )

                return {

                    "status":
                        "REJECTED",

                    "story_id":
                        story_id,

                    "quality":
                        quality
                }

            article_id = self.database.save_article(
                article,
                story_id=story_id
            )

            self.database.update_story_status(
                story_id,
                "ready"
            )

            self.database.log(
                story_id,
                "content",
                "SUCCESS",
                "Article generated and approved."
            )

            website_result = self._publish_website(
                article
            )

            social_result = self._publish_social(
                article
            )

            published = (
                website_result.get(
                    "published",
                    False
                )
            )

            if published:

                self.database.update_article_status(
                    article_id,
                    "published"
                )

                self.database.update_story_status(
                    story_id,
                    "published"
                )

            else:

                self.database.update_article_status(
                    article_id,
                    "ready"
                )

            self.database.log(
                story_id,
                "publishing",
                "SUCCESS" if published else "PARTIAL",
                "Publishing stage completed."
            )

            result = {

                "status":
                    "COMPLETED",

                "job_id":
                    job_id,

                "story_id":
                    story_id,

                "article_id":
                    article_id,

                "article":
                    article,

                "quality":
                    quality,

                "website":
                    website_result,

                "social":
                    social_result
            }

            self.queue.complete(
                job_id,
                result
            )

            return result

        except Exception as exc:

            logger.exception(
                "Factory processing failed."
            )

            self.database.log(
                story_id,
                "factory",
                "FAILED",
                str(exc)
            )

            self.queue.fail(
                job_id,
                str(exc)
            )

            return {

                "status":
                    "FAILED",

                "job_id":
                    job_id,

                "story_id":
                    story_id,

                "error":
                    str(exc)
            }

    # =====================================================
    # PROCESS MANY
    # =====================================================

    def process(
        self,
        maximum: int = 10
    ) -> List[Dict[str, Any]]:

        results = []

        for _ in range(
            maximum
        ):

            result = self.process_next()

            if result is None:

                break

            results.append(
                result
            )

        return results

    # =====================================================
    # ANALYSIS
    # =====================================================

    def _analyze(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        if self.intelligence is None:

            return {

                "story":
                    story,

                "package": {

                    "title":
                        story.get(
                            "title",
                            ""
                        ),

                    "content":
                        story.get(
                            "description",
                            ""
                        ),

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
                        )
                }
            }

        if hasattr(
            self.intelligence,
            "analyze"
        ):

            return self.intelligence.analyze(
                story
            )

        if callable(
            self.intelligence
        ):

            return self.intelligence(
                story
            )

        raise TypeError(
            "Intelligence engine must provide analyze()."
        )

    # =====================================================
    # CONTENT
    # =====================================================

    def _create_content(
        self,
        analyzed: Dict[str, Any]
    ) -> Dict[str, Any]:

        result = self.content_factory.build(
            analyzed
        )

        article = result.get(
            "article",
            {}
        )

        article["seo"] = result.get(
            "seo",
            {}
        )

        article["social"] = result.get(
            "social",
            {}
        )

        return article

    # =====================================================
    # QUALITY
    # =====================================================

    def _quality_check(
        self,
        article: Dict[str, Any],
        analyzed: Dict[str, Any]
    ) -> Dict[str, Any]:

        title = str(
            article.get(
                "title",
                ""
            )
        ).strip()

        content = str(
            article.get(
                "content",
                ""
            )
        ).strip()

        source_url = str(
            article.get(
                "source_url",
                ""
            )
        ).strip()

        if not title:

            return {

                "approved":
                    False,

                "reason":
                    "Missing article title."
            }

        if len(title) < 10:

            return {

                "approved":
                    False,

                "reason":
                    "Article title is too short."
            }

        if not content:

            return {

                "approved":
                    False,

                "reason":
                    "Article content is empty."
            }

        if not source_url:

            return {

                "approved":
                    False,

                "reason":
                    "Source URL is missing."
            }

        return {

            "approved":
                True,

            "score":
                100,

            "checks": {

                "title":
                    True,

                "content":
                    True,

                "source":
                    True
            }
        }

    # =====================================================
    # WEBSITE
    # =====================================================

    def _publish_website(
        self,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        if self.website_publisher is None:

            return {

                "status":
                    "NOT_CONFIGURED",

                "published":
                    False
            }

        try:

            return self.website_publisher.publish(
                article
            )

        except Exception as exc:

            logger.exception(
                "Website publishing failed."
            )

            return {

                "status":
                    "FAILED",

                "published":
                    False,

                "error":
                    str(exc)
            }

    # =====================================================
    # SOCIAL
    # =====================================================

    def _publish_social(
        self,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        if self.social_publisher is None:

            return {

                "status":
                    "NOT_CONFIGURED",

                "successful":
                    0
            }

        try:

            return self.social_publisher.publish_all(
                article
            )

        except Exception as exc:

            logger.exception(
                "Social publishing failed."
            )

            return {

                "status":
                    "FAILED",

                "successful":
                    0,

                "error":
                    str(exc)
            }

    # =====================================================
    # PRIORITY
    # =====================================================

    def _priority(
        self,
        story: Dict[str, Any]
    ) -> int:

        category = str(
            story.get(
                "category",
                ""
            )
        ).lower()

        high_priority = {

            "breaking",
            "urgent",
            "world",
            "politics",
            "business",
            "technology"
        }

        if category in high_priority:

            return 80

        return 50


# =========================================================
# HELPER
# =========================================================

def create_factory(
    source_manager: SourceManager,
    **kwargs
) -> FactoryOrchestrator:

    return FactoryOrchestrator(
        source_manager=source_manager,
        **kwargs
    )
