"""
AI NEWS FACTORY
GITHUB WEBSITE PUBLISHER

Publishes generated articles to a GitHub repository through
the GitHub Contents API.

This is useful when the news website is a static site hosted
from GitHub Pages.

The publisher:
- creates/updates article files
- commits through GitHub's API
- does not need git installed
- does not need shell access to the server

Environment variables:

    GITHUB_TOKEN
    GITHUB_REPOSITORY
    GITHUB_BRANCH

Example:

    GITHUB_REPOSITORY=owner/news-site
    GITHUB_BRANCH=main

The token should have only the minimum repository permissions
required for the publishing repository.
"""

import base64
import os
import logging
from typing import Any, Dict, Optional

import requests


logger = logging.getLogger(__name__)


class GitHubPublisher:

    platform = "github"

    def __init__(
        self,
        repository: Optional[str] = None,
        token: Optional[str] = None,
        branch: Optional[str] = None,
        articles_path: str = "content/news",
        timeout: int = 30
    ):

        self.repository = (
            repository
            or os.getenv(
                "GITHUB_REPOSITORY",
                ""
            )
        )

        self.token = (
            token
            or os.getenv(
                "GITHUB_TOKEN",
                ""
            )
        )

        self.branch = (
            branch
            or os.getenv(
                "GITHUB_BRANCH",
                "main"
            )
        )

        self.articles_path = (
            articles_path
            .strip("/")
        )

        self.timeout = timeout

        self.name = "GitHub Website Publisher"
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
                    "GitHub publishing credentials are not configured."
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

        slug = str(
            article.get(
                "slug",
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

        if not slug:

            return self._failure(
                "Article slug is missing."
            )

        try:

            path = self._article_path(
                slug
            )

            markdown = self._build_markdown(
                article
            )

            existing = self._get_file(
                path
            )

            payload = {

                "message":
                    f"Publish news: {title}",

                "content":
                    self._encode(
                        markdown
                    ),

                "branch":
                    self.branch
            }

            if existing.get(
                "sha"
            ):

                payload["sha"] = existing[
                    "sha"
                ]

            response = requests.put(

                self._contents_endpoint(
                    path
                ),

                json=payload,

                headers=self._headers(),

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
                        "content",
                        {}
                    ).get(
                        "sha",
                        ""
                    ),

                "url":
                    data.get(
                        "content",
                        {}
                    ).get(
                        "html_url",
                        ""
                    ),

                "commit":
                    data.get(
                        "commit",
                        {}
                    ),

                "response":
                    data
            }

        except requests.RequestException as exc:

            logger.exception(
                "GitHub publishing failed."
            )

            return self._failure(
                str(exc)
            )

        except Exception as exc:

            logger.exception(
                "Unexpected GitHub publishing error."
            )

            return self._failure(
                str(exc)
            )

    # =====================================================
    # BUILD MARKDOWN
    # =====================================================

    def _build_markdown(
        self,
        article: Dict[str, Any]
    ) -> str:

        title = article.get(
            "title",
            ""
        )

        excerpt = article.get(
            "excerpt",
            ""
        )

        content = article.get(
            "content",
            ""
        )

        category = article.get(
            "category",
            "general"
        )

        tags = article.get(
            "tags",
            []
        )

        source_url = article.get(
            "source_url",
            ""
        )

        lines = [

            "---",

            f'title: "{self._yaml_escape(title)}"',

            f'category: "{self._yaml_escape(category)}"',

            f'description: "{self._yaml_escape(excerpt)}"',

        ]

        if tags:

            formatted_tags = ", ".join(

                f'"{self._yaml_escape(str(tag))}"'

                for tag in tags
            )

            lines.append(
                f"tags: [{formatted_tags}]"
            )

        if source_url:

            lines.append(
                f'source_url: "{self._yaml_escape(source_url)}"'
            )

        lines.extend([

            "---",

            "",

            content,

            ""
        ])

        return "\n".join(
            lines
        )

    # =====================================================
    # GET EXISTING FILE
    # =====================================================

    def _get_file(
        self,
        path: str
    ) -> Dict[str, Any]:

        try:

            response = requests.get(

                self._contents_endpoint(
                    path
                ),

                params={
                    "ref":
                        self.branch
                },

                headers=self._headers(),

                timeout=self.timeout
            )

            if response.status_code == 404:

                return {}

            response.raise_for_status()

            return response.json()

        except requests.RequestException:

            return {}

    # =====================================================
    # PATH
    # =====================================================

    def _article_path(
        self,
        slug: str
    ) -> str:

        safe_slug = "".join(

            character

            for character in slug

            if character.isalnum()
            or character in (
                "-",
                "_"
            )
        )

        return (
            f"{self.articles_path}/"
            f"{safe_slug}.md"
        )

    # =====================================================
    # ENDPOINT
    # =====================================================

    def _contents_endpoint(
        self,
        path: str
    ) -> str:

        return (
            "https://api.github.com/repos/"
            f"{self.repository}/contents/"
            f"{path}"
        )

    # =====================================================
    # HEADERS
    # =====================================================

    def _headers(
        self
    ) -> Dict[str, str]:

        return {

            "Accept":
                "application/vnd.github+json",

            "Authorization":
                f"Bearer {self.token}",

            "X-GitHub-Api-Version":
                "2022-11-28",

            "User-Agent":
                "AI-News-Factory/1.0"
        }

    # =====================================================
    # ENCODE
    # =====================================================

    def _encode(
        self,
        text: str
    ) -> str:

        return base64.b64encode(
            text.encode(
                "utf-8"
            )
        ).decode(
            "ascii"
        )

    # =====================================================
    # YAML ESCAPE
    # =====================================================

    def _yaml_escape(
        self,
        value: Any
    ) -> str:

        return str(
            value
        ).replace(
            "\\",
            "\\\\"
        ).replace(
            '"',
            '\\"'
        ).replace(
            "\n",
            " "
        )

    # =====================================================
    # CONFIGURATION
    # =====================================================

    def _configured(
        self
    ) -> bool:

        return bool(
            self.repository
            and self.token
        )

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

def create_github_publisher(
    repository: Optional[str] = None,
    token: Optional[str] = None,
    branch: Optional[str] = None
) -> GitHubPublisher:

    return GitHubPublisher(

        repository=repository,

        token=token,

        branch=branch
  )
