"""
AI NEWS FACTORY
WEBSITE PUBLISHER

Publishes approved news articles to a website through an API.

The publisher does NOT directly modify Git repositories.
Use a website/CMS API or a controlled backend endpoint.

Environment variables:
    NEWS_SITE_API_URL
    NEWS_SITE_API_KEY
"""

import os
import logging
from typing import Any, Dict, Optional

import requests


logger = logging.getLogger(__name__)


class WebsitePublisher:

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30
    ):

        self.api_url = (
            api_url
            or os.getenv(
                "NEWS_SITE_API_URL",
                ""
            )
        )

        self.api_key = (
            api_key
            or os.getenv(
                "NEWS_SITE_API_KEY",
                ""
            )
        )

        self.timeout = timeout
        self.name = "Website Publisher"
        self.version = "1.0.0"

    # =====================================================
    # PUBLISH
    # =====================================================

    def publish(
        self,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        if not self.api_url:

            return {
                "status":
                    "NOT_CONFIGURED",

                "published":
                    False,

                "message":
                    "Website API URL is not configured."
            }

        payload = self._build_payload(
            article
        )

        try:

            response = requests.post(

                self.api_url,

                json=payload,

                headers=self._headers(),

                timeout=self.timeout
            )

            response.raise_for_status()

            data = self._response_data(
                response
            )

            return {

                "status":
                    "PUBLISHED",

                "published":
                    True,

                "platform":
                    "website",

                "external_id":
                    self._extract(
                        data,
                        "id"
                    ),

                "url":
                    self._extract(
                        data,
                        "url"
                    ),

                "response":
                    data
            }

        except requests.RequestException as exc:

            logger.exception(
                "Website publishing failed."
            )

            return {

                "status":
                    "FAILED",

                "published":
                    False,

                "platform":
                    "website",

                "error":
                    str(exc)
            }

    # =====================================================
    # BUILD PAYLOAD
    # =====================================================

    def _build_payload(
        self,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {

            "title":
                article.get(
                    "title",
                    ""
                ),

            "slug":
                article.get(
                    "slug",
                    ""
                ),

            "content":
                article.get(
                    "content",
                    ""
                ),

            "excerpt":
                article.get(
                    "excerpt",
                    ""
                ),

            "category":
                article.get(
                    "category",
                    "general"
                ),

            "tags":
                article.get(
                    "tags",
                    []
                ),

            "image_url":
                article.get(
                    "image_url",
                    ""
                ),

            "source_url":
                article.get(
                    "source_url",
                    ""
                ),

            "seo":
                article.get(
                    "seo",
                    {}
                )
        }

    # =====================================================
    # HEADERS
    # =====================================================

    def _headers(
        self
    ) -> Dict[str, str]:

        headers = {

            "Content-Type":
                "application/json",

            "User-Agent":
                "AI-News-Factory/1.0"
        }

        if self.api_key:

            headers[
                "Authorization"
            ] = (
                f"Bearer {self.api_key}"
            )

        return headers

    # =====================================================
    # RESPONSE
    # =====================================================

    def _response_data(
        self,
        response
    ) -> Any:

        try:

            return response.json()

        except ValueError:

            return {
                "text":
                    response.text,

                "status_code":
                    response.status_code
            }

    # =====================================================
    # EXTRACT
    # =====================================================

    def _extract(
        self,
        data: Any,
        key: str
    ) -> str:

        if not isinstance(
            data,
            dict
        ):

            return ""

        value = data.get(
            key,
            ""
        )

        if value is None:

            return ""

        return str(
            value
        )


# =========================================================
# HELPER
# =========================================================

def create_website_publisher(
    api_url: Optional[str] = None,
    api_key: Optional[str] = None
) -> WebsitePublisher:

    return WebsitePublisher(
        api_url=api_url,
        api_key=api_key
    )
