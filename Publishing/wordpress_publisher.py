"""
AI NEWS FACTORY
WORDPRESS PUBLISHER

Publishes approved articles through the official
WordPress REST API.

Environment variables:

    WORDPRESS_URL
    WORDPRESS_USERNAME
    WORDPRESS_APP_PASSWORD

Example:

    WORDPRESS_URL=https://example.com
    WORDPRESS_USERNAME=admin
    WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx

The factory uses the WordPress REST API instead of
directly modifying the website database or files.
"""

import os
import logging
from typing import Any, Dict, Optional

import requests
from requests.auth import HTTPBasicAuth


logger = logging.getLogger(__name__)


class WordPressPublisher:

    platform = "wordpress"

    def __init__(
        self,
        site_url: Optional[str] = None,
        username: Optional[str] = None,
        app_password: Optional[str] = None,
        timeout: int = 30
    ):

        self.site_url = (
            site_url
            or os.getenv(
                "WORDPRESS_URL",
                ""
            )
        ).rstrip("/")

        self.username = (
            username
            or os.getenv(
                "WORDPRESS_USERNAME",
                ""
            )
        )

        self.app_password = (
            app_password
            or os.getenv(
                "WORDPRESS_APP_PASSWORD",
                ""
            )
        )

        self.timeout = timeout

        self.name = "WordPress Publisher"
        self.version = "1.0.0"

    # =====================================================
    # PUBLISH
    # =====================================================

    def publish(
        self,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        if not self._configured():

            return {

                "status":
                    "NOT_CONFIGURED",

                "published":
                    False,

                "platform":
                    self.platform,

                "message":
                    "WordPress credentials are not configured."
            }

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

        if not title:

            return self._failure(
                "Article title is missing."
            )

        if not content:

            return self._failure(
                "Article content is missing."
            )

        payload = self._build_payload(
            article
        )

        try:

            response = requests.post(

                self._endpoint(),

                json=payload,

                auth=HTTPBasicAuth(

                    self.username,

                    self.app_password
                ),

                headers={

                    "Accept":
                        "application/json",

                    "User-Agent":
                        "AI-News-Factory/1.0"
                },

                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            return {

                "status":
                    "PUBLISHED",

                "published":
                    True,

                "platform":
                    self.platform,

                "external_id":
                    data.get(
                        "id",
                        ""
                    ),

                "url":
                    data.get(
                        "link",
                        ""
                    ),

                "response":
                    data
            }

        except requests.RequestException as exc:

            logger.exception(
                "WordPress publishing failed."
            )

            return self._failure(
                str(exc)
            )

        except Exception as exc:

            logger.exception(
                "Unexpected WordPress error."
            )

            return self._failure(
                str(exc)
            )

    # =====================================================
    # BUILD PAYLOAD
    # =====================================================

    def _build_payload(
        self,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        payload = {

            "title":
                article.get(
                    "title",
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

            "status":
                article.get(
                    "status",
                    "draft"
                )
        }

        slug = article.get(
            "slug"
        )

        if slug:

            payload["slug"] = slug

        categories = article.get(
            "category_ids"
        )

        if categories:

            payload[
                "categories"
            ] = categories

        tags = article.get(
            "tag_ids"
        )

        if tags:

            payload[
                "tags"
            ] = tags

        return payload

    # =====================================================
    # ENDPOINT
    # =====================================================

    def _endpoint(
        self
    ) -> str:

        return (
            self.site_url
            + "/wp-json/wp/v2/posts"
        )

    # =====================================================
    # CONFIGURATION
    # =====================================================

    def _configured(
        self
    ) -> bool:

        return all([

            self.site_url,

            self.username,

            self.app_password
        ])

    # =====================================================
    # FAILURE
    # =====================================================

    def _failure(
        self,
        error: str
    ) -> Dict[str, Any]:

        return {

            "status":
                "FAILED",

            "published":
                False,

            "platform":
                self.platform,

            "error":
                error
        }


# =========================================================
# HELPER
# =========================================================

def create_wordpress_publisher(
    site_url: Optional[str] = None,
    username: Optional[str] = None,
    app_password: Optional[str] = None
) -> WordPressPublisher:

    return WordPressPublisher(

        site_url=site_url,

        username=username,

        app_password=app_password
      )
