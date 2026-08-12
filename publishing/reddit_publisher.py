"""
AI NEWS FACTORY
REDDIT PUBLISHER

Publishes approved news links through Reddit's official API.

Credentials must be supplied through environment variables.

Required:
    REDDIT_CLIENT_ID
    REDDIT_CLIENT_SECRET
    REDDIT_USERNAME
    REDDIT_PASSWORD
    REDDIT_USER_AGENT

Optional:
    REDDIT_SUBREDDIT

The factory should publish only to communities where the
content is allowed and should respect each community's rules.
"""

import logging
import os
from typing import Any, Dict, Optional

import requests


logger = logging.getLogger(__name__)


class RedditPublisher:

    platform = "reddit"

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        user_agent: Optional[str] = None,
        subreddit: Optional[str] = None,
        timeout: int = 30
    ):

        self.client_id = (
            client_id
            or os.getenv(
                "REDDIT_CLIENT_ID",
                ""
            )
        )

        self.client_secret = (
            client_secret
            or os.getenv(
                "REDDIT_CLIENT_SECRET",
                ""
            )
        )

        self.username = (
            username
            or os.getenv(
                "REDDIT_USERNAME",
                ""
            )
        )

        self.password = (
            password
            or os.getenv(
                "REDDIT_PASSWORD",
                ""
            )
        )

        self.user_agent = (
            user_agent
            or os.getenv(
                "REDDIT_USER_AGENT",
                "AI-News-Factory/1.0"
            )
        )

        self.subreddit = (
            subreddit
            or os.getenv(
                "REDDIT_SUBREDDIT",
                ""
            )
        )

        self.timeout = timeout

        self.name = "Reddit Publisher"
        self.version = "1.0.0"

        self.access_token = None

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
                    "Reddit credentials are not configured."
            }

        title = str(
            article.get(
                "title",
                ""
            )
        ).strip()

        url = str(
            article.get(
                "url",
                article.get(
                    "source_url",
                    ""
                )
            )
        ).strip()

        if not title:

            return self._failure(
                "Article title is missing."
            )

        if not url:

            return self._failure(
                "Article URL is missing."
            )

        try:

            self._authenticate()

            payload = {

                "sr":
                    self.subreddit,

                "title":
                    title,

                "url":
                    url,

                "kind":
                    "link"
            }

            response = requests.post(

                "https://oauth.reddit.com/api/submit",

                data=payload,

                headers={
                    "Authorization":
                        f"Bearer {self.access_token}",

                    "User-Agent":
                        self.user_agent
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

                "response":
                    data
            }

        except Exception as exc:

            logger.exception(
                "Reddit publishing failed."
            )

            return self._failure(
                str(exc)
            )

    # =====================================================
    # AUTHENTICATE
    # =====================================================

    def _authenticate(
        self
    ) -> None:

        response = requests.post(

            "https://www.reddit.com/api/v1/access_token",

            auth=(

                self.client_id,

                self.client_secret
            ),

            data={

                "grant_type":
                    "password",

                "username":
                    self.username,

                "password":
                    self.password
            },

            headers={

                "User-Agent":
                    self.user_agent
            },

            timeout=self.timeout
        )

        response.raise_for_status()

        data = response.json()

        token = data.get(
            "access_token"
        )

        if not token:

            raise RuntimeError(
                "Reddit authentication returned no access token."
            )

        self.access_token = token

    # =====================================================
    # CONFIGURATION
    # =====================================================

    def _configured(
        self
    ) -> bool:

        return all([

            self.client_id,

            self.client_secret,

            self.username,

            self.password,

            self.subreddit
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

def create_reddit_publisher(
    subreddit: Optional[str] = None
) -> RedditPublisher:

    return RedditPublisher(
        subreddit=subreddit
        )
