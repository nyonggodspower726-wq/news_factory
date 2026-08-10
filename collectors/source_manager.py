"""
AI NEWS FACTORY
SOURCE MANAGER

Responsibilities:
- manage multiple news sources
- collect stories from registered collectors
- normalize collector output
- remove obvious duplicates
- attach source metadata
- keep collection failures isolated

Collectors should use official APIs, RSS feeds, or other
sources whose terms permit automated access.

Never scrape or republish protected content in violation
of a source's terms.
"""

from typing import Any, Dict, List, Optional
import hashlib
import logging
import time


logger = logging.getLogger(__name__)


class SourceManager:

    def __init__(
        self,
        collectors: Optional[List[Any]] = None
    ):

        self.collectors = []

        if collectors:

            for collector in collectors:

                self.register(
                    collector
                )

        self.version = "1.0.0"

    # =====================================================
    # REGISTER
    # =====================================================

    def register(
        self,
        collector: Any
    ) -> None:

        if collector is None:

            return

        if not hasattr(
            collector,
            "collect"
        ):

            raise ValueError(
                "Collector must provide a collect() method."
            )

        self.collectors.append(
            collector
        )

    # =====================================================
    # COLLECT EVERYTHING
    # =====================================================

    def collect_all(
        self,
        limit_per_source: int = 20
    ) -> Dict[str, Any]:

        started = time.time()

        stories = []

        source_results = []

        errors = []

        for collector in self.collectors:

            source_name = self._source_name(
                collector
            )

            try:

                raw_items = collector.collect(
                    limit=limit_per_source
                )

                if raw_items is None:

                    raw_items = []

                if not isinstance(
                    raw_items,
                    list
                ):

                    raw_items = list(
                        raw_items
                    )

                normalized = []

                for item in raw_items:

                    story = self.normalize(
                        item,
                        source_name
                    )

                    if story:

                        normalized.append(
                            story
                        )

                        stories.append(
                            story
                        )

                source_results.append({

                    "source":
                        source_name,

                    "status":
                        "SUCCESS",

                    "count":
                        len(
                            normalized
                        )
                })

            except Exception as exc:

                logger.exception(
                    "Source collection failed: %s",
                    source_name
                )

                errors.append({

                    "source":
                        source_name,

                    "error":
                        str(exc)
                })

                source_results.append({

                    "source":
                        source_name,

                    "status":
                        "FAILED",

                    "count":
                        0
                })

        unique_stories = self.deduplicate(
            stories
        )

        return {

            "status":
                "COLLECTION_COMPLETE",

            "version":
                self.version,

            "stories":
                unique_stories,

            "count":
                len(
                    unique_stories
                ),

            "sources":
                source_results,

            "errors":
                errors,

            "processing_time":
                round(
                    time.time() - started,
                    3
                )
        }

    # =====================================================
    # NORMALIZE
    # =====================================================

    def normalize(
        self,
        item: Any,
        source_name: str
    ) -> Optional[Dict[str, Any]]:

        if not isinstance(
            item,
            dict
        ):

            return None

        title = self._first_value(
            item,
            [
                "title",
                "headline",
                "name"
            ]
        )

        description = self._first_value(
            item,
            [
                "description",
                "summary",
                "excerpt",
                "content",
                "body"
            ]
        )

        source_url = self._first_value(
            item,
            [
                "source_url",
                "url",
                "link",
                "web_url"
            ]
        )

        published_at = self._first_value(
            item,
            [
                "published_at",
                "published",
                "pubDate",
                "date",
                "timestamp"
            ]
        )

        image_url = self._first_value(
            item,
            [
                "image_url",
                "image",
                "thumbnail",
                "urlToImage"
            ]
        )

        category = self._first_value(
            item,
            [
                "category",
                "section",
                "topic"
            ]
        )

        author = self._first_value(
            item,
            [
                "author",
                "creator",
                "byline"
            ]
        )

        title = self._clean(
            title
        )

        description = self._clean(
            description
        )

        source_url = self._clean(
            source_url
        )

        if not title:

            return None

        story_id = self._story_id(
            title,
            source_url
        )

        return {

            "id":
                story_id,

            "title":
                title,

            "description":
                description,

            "source":
                source_name,

            "source_url":
                source_url,

            "published_at":
                published_at,

            "image_url":
                image_url,

            "category":
                category or "general",

            "author":
                author or "",

            "collected_at":
                time.time(),

            "raw":
                item
        }

    # =====================================================
    # DEDUPLICATION
    # =====================================================

    def deduplicate(
        self,
        stories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        unique = []

        seen_ids = set()

        seen_titles = set()

        for story in stories:

            story_id = story.get(
                "id"
            )

            title = self._normalize_title(
                story.get(
                    "title",
                    ""
                )
            )

            if story_id in seen_ids:

                continue

            if title and title in seen_titles:

                continue

            seen_ids.add(
                story_id
            )

            if title:

                seen_titles.add(
                    title
                )

            unique.append(
                story
            )

        return unique

    # =====================================================
    # STORY ID
    # =====================================================

    def _story_id(
        self,
        title: str,
        source_url: str
    ) -> str:

        identity = (
            self._normalize_title(
                title
            )
            +
            "|"
            +
            self._clean(
                source_url
            )
        )

        return hashlib.sha256(
            identity.encode(
                "utf-8"
            )
        ).hexdigest()[:24]

    # =====================================================
    # SOURCE NAME
    # =====================================================

    def _source_name(
        self,
        collector: Any
    ) -> str:

        name = getattr(
            collector,
            "name",
            None
        )

        if name:

            return str(
                name
            )

        return collector.__class__.__name__

    # =====================================================
    # FIRST VALUE
    # =====================================================

    def _first_value(
        self,
        item: Dict[str, Any],
        keys: List[str]
    ) -> Any:

        for key in keys:

            value = item.get(
                key
            )

            if value not in (
                None,
                ""
            ):

                return value

        return ""

    # =====================================================
    # CLEAN
    # =====================================================

    def _clean(
        self,
        value: Any
    ) -> str:

        if value is None:

            return ""

        return str(
            value
        ).strip()

    # =====================================================
    # NORMALIZE TITLE
    # =====================================================

    def _normalize_title(
        self,
        title: str
    ) -> str:

        return " ".join(
            self._clean(
                title
            ).lower().split()
        )


# =========================================================
# SIMPLE HELPER
# =========================================================

def create_source_manager(
    collectors: Optional[List[Any]] = None
) -> SourceManager:

    return SourceManager(
        collectors=collectors
)
