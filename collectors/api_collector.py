"""
AI NEWS FACTORY
GENERIC API COLLECTOR

Provides a common collector for approved news/data APIs.

The collector expects an API returning JSON and supports
common response shapes such as:

{
    "articles": [...]
}

or:

{
    "results": [...]
}

or:

{
    "data": [...]
}

API credentials should come from environment variables,
never directly from this source file.
"""

from typing import Any, Dict, List, Optional
import logging
import os
import time

import requests


logger = logging.getLogger(__name__)


class APICollector:

    def __init__(
        self,
        url: str,
        name: str = "News API",
        api_key_env: Optional[str] = None,
        api_key_header: str = "X-API-Key",
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 20
    ):

        self.url = url
        self.name = name
        self.api_key_env = api_key_env
        self.api_key_header = api_key_header
        self.params = params or {}
        self.timeout = timeout
        self.version = "1.0.0"

    # =====================================================
    # COLLECT
    # =====================================================

    def collect(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:

        headers = {
            "User-Agent":
                "AI-News-Factory/1.0"
        }

        params = dict(
            self.params
        )

        if self.api_key_env:

            api_key = os.getenv(
                self.api_key_env
            )

            if api_key:

                headers[
                    self.api_key_header
                ] = api_key

        response = requests.get(
            self.url,
            headers=headers,
            params=params,
            timeout=self.timeout
        )

        response.raise_for_status()

        data = response.json()

        items = self._extract_items(
            data
        )

        results = []

        for item in items[:limit]:

            parsed = self._parse_item(
                item
            )

            if parsed:

                results.append(
                    parsed
                )

        return results

    # =====================================================
    # EXTRACT ITEMS
    # =====================================================

    def _extract_items(
        self,
        data: Any
    ) -> List[Any]:

        if isinstance(
            data,
            list
        ):

            return data

        if not isinstance(
            data,
            dict
        ):

            return []

        for key in (
            "articles",
            "results",
            "data",
            "items",
            "stories"
        ):

            value = data.get(
                key
            )

            if isinstance(
                value,
                list
            ):

                return value

        return []

    # =====================================================
    # PARSE ITEM
    # =====================================================

    def _parse_item(
        self,
        item: Any
    ) -> Optional[Dict[str, Any]]:

        if not isinstance(
            item,
            dict
        ):

            return None

        title = self._first(
            item,
            [
                "title",
                "headline",
                "name"
            ]
        )

        if not title:

            return None

        description = self._first(
            item,
            [
                "description",
                "summary",
                "excerpt",
                "content",
                "snippet"
            ]
        )

        url = self._first(
            item,
            [
                "url",
                "link",
                "source_url",
                "web_url"
            ]
        )

        published = self._first(
            item,
            [
                "published_at",
                "publishedAt",
                "published",
                "pubDate",
                "date",
                "created_at"
            ]
        )

        author = self._first(
            item,
            [
                "author",
                "creator",
                "byline"
            ]
        )

        image = self._first(
            item,
            [
                "urlToImage",
                "image_url",
                "image",
                "thumbnail"
            ]
        )

        source = self._extract_source(
            item
        )

        category = self._first(
            item,
            [
                "category",
                "section",
                "topic"
            ]
        )

        return {

            "title":
                str(title).strip(),

            "description":
                str(
                    description or ""
                ).strip(),

            "source_url":
                str(
                    url or ""
                ).strip(),

            "published_at":
                published,

            "author":
                author or "",

            "image_url":
                image or "",

            "source":
                source or self.name,

            "category":
                category or "general",

            "collector":
                self.name,

            "collected_at":
                time.time(),

            "raw":
                item
        }

    # =====================================================
    # SOURCE
    # =====================================================

    def _extract_source(
        self,
        item: Dict[str, Any]
    ) -> str:

        source = item.get(
            "source"
        )

        if isinstance(
            source,
            dict
        ):

            return str(
                source.get(
                    "name",
                    ""
                )
            )

        if source:

            return str(
                source
            )

        return ""

    # =====================================================
    # FIRST VALUE
    # =====================================================

    def _first(
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
    # HEALTH CHECK
    # =====================================================

    def health_check(self) -> Dict[str, Any]:

        try:

            headers = {
                "User-Agent":
                    "AI-News-Factory/1.0"
            }

            if self.api_key_env:

                api_key = os.getenv(
                    self.api_key_env
                )

                if api_key:

                    headers[
                        self.api_key_header
                    ] = api_key

            response = requests.get(
                self.url,
                headers=headers,
                params=self.params,
                timeout=self.timeout
            )

            return {

                "source":
                    self.name,

                "healthy":
                    response.ok,

                "status_code":
                    response.status_code
            }

        except Exception as exc:

            logger.exception(
                "API health check failed."
            )

            return {

                "source":
                    self.name,

                "healthy":
                    False,

                "error":
                    str(exc)
            }


# =========================================================
# HELPER
# =========================================================

def create_api_collector(
    url: str,
    name: str = "News API",
    api_key_env: Optional[str] = None,
    api_key_header: str = "X-API-Key",
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 20
) -> APICollector:

    return APICollector(
        url=url,
        name=name,
        api_key_env=api_key_env,
        api_key_header=api_key_header,
        params=params,
        timeout=timeout
)
