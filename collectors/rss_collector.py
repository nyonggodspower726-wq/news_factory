"""
AI NEWS FACTORY
RSS COLLECTOR

Collects publicly available RSS/Atom feed entries.

The collector only gathers metadata and feed-provided
content. It does not bypass paywalls or access controls.
"""

from typing import Any, Dict, List, Optional
import logging
import time

try:
    import feedparser
except ImportError:
    feedparser = None


logger = logging.getLogger(__name__)


class RSSCollector:

    def __init__(
        self,
        feeds: Optional[List[str]] = None,
        name: str = "RSS News Sources"
    ):

        self.name = name
        self.feeds = feeds or []
        self.version = "1.0.0"

    # =====================================================
    # COLLECT
    # =====================================================

    def collect(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:

        if feedparser is None:

            raise ImportError(
                "feedparser is required. "
                "Install it with: pip install feedparser"
            )

        results = []

        for feed_url in self.feeds:

            if not feed_url:
                continue

            try:

                parsed = feedparser.parse(
                    feed_url
                )

                entries = getattr(
                    parsed,
                    "entries",
                    []
                )

                for entry in entries[:limit]:

                    item = self._parse_entry(
                        entry,
                        feed_url
                    )

                    if item:

                        results.append(
                            item
                        )

            except Exception as exc:

                logger.exception(
                    "RSS feed failed: %s",
                    feed_url
                )

        return results

    # =====================================================
    # PARSE ENTRY
    # =====================================================

    def _parse_entry(
        self,
        entry: Any,
        feed_url: str
    ) -> Optional[Dict[str, Any]]:

        title = self._get(
            entry,
            "title"
        )

        if not title:

            return None

        summary = self._get(
            entry,
            "summary"
        )

        link = self._get(
            entry,
            "link"
        )

        author = self._get(
            entry,
            "author"
        )

        published = self._get(
            entry,
            "published"
        )

        image_url = self._extract_image(
            entry
        )

        return {

            "title":
                title,

            "description":
                summary,

            "source_url":
                link,

            "published_at":
                published,

            "author":
                author,

            "image_url":
                image_url,

            "feed_url":
                feed_url,

            "collector":
                self.name,

            "collected_at":
                time.time()
        }

    # =====================================================
    # GET VALUE
    # =====================================================

    def _get(
        self,
        entry: Any,
        key: str
    ) -> str:

        try:

            value = entry.get(
                key,
                ""
            )

        except Exception:

            value = getattr(
                entry,
                key,
                ""
            )

        if value is None:

            return ""

        return str(
            value
        ).strip()

    # =====================================================
    # IMAGE
    # =====================================================

    def _extract_image(
        self,
        entry: Any
    ) -> str:

        try:

            media_content = entry.get(
                "media_content",
                []
            )

            if media_content:

                first = media_content[0]

                if isinstance(
                    first,
                    dict
                ):

                    return str(
                        first.get(
                            "url",
                            ""
                        )
                    )

            media_thumbnail = entry.get(
                "media_thumbnail",
                []
            )

            if media_thumbnail:

                first = media_thumbnail[0]

                if isinstance(
                    first,
                    dict
                ):

                    return str(
                        first.get(
                            "url",
                            ""
                        )
                    )

            enclosures = entry.get(
                "enclosures",
                []
            )

            for enclosure in enclosures:

                if not isinstance(
                    enclosure,
                    dict
                ):
                    continue

                media_type = str(
                    enclosure.get(
                        "type",
                        ""
                    )
                ).lower()

                if media_type.startswith(
                    "image/"
                ):

                    return str(
                        enclosure.get(
                            "href",
                            enclosure.get(
                                "url",
                                ""
                            )
                        )
                    )

        except Exception:

            logger.exception(
                "Could not extract RSS image."
            )

        return ""


# =========================================================
# HELPER
# =========================================================

def create_rss_collector(
    feeds: Optional[List[str]] = None,
    name: str = "RSS News Sources"
) -> RSSCollector:

    return RSSCollector(
        feeds=feeds,
        name=name
      )
