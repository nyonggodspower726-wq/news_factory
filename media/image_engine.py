"""
AI NEWS FACTORY
IMAGE ENGINE

Responsibilities:
- resolve article image sources
- validate image URLs
- prefer source-provided images
- prepare image metadata
- prevent unusable image URLs
- preserve attribution/source information

IMPORTANT:
Only use images that the factory has permission to use.
Do not download or republish copyrighted images merely
because they appear in a news feed.
"""

import logging
from typing import Any, Dict, Optional

import requests


logger = logging.getLogger(__name__)


class ImageEngine:

    def __init__(
        self,
        timeout: int = 15
    ):

        self.timeout = timeout
        self.name = "News Image Engine"
        self.version = "1.0.0"

    # =====================================================
    # RESOLVE
    # =====================================================

    def resolve(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        image_url = self._clean(
            story.get(
                "image_url",
                ""
            )
        )

        source_url = self._clean(
            story.get(
                "source_url",
                ""
            )
        )

        source = self._clean(
            story.get(
                "source",
                ""
            )
        )

        if not image_url:

            return {

                "status":
                    "NO_IMAGE",

                "available":
                    False,

                "image_url":
                    "",

                "source":
                    source,

                "source_url":
                    source_url
            }

        validation = self.validate(
            image_url
        )

        if not validation["valid"]:

            return {

                "status":
                    "INVALID_IMAGE",

                "available":
                    False,

                "image_url":
                    "",

                "source":
                    source,

                "source_url":
                    source_url,

                "error":
                    validation["error"]
            }

        return {

            "status":
                "IMAGE_READY",

            "available":
                True,

            "image_url":
                image_url,

            "source":
                source,

            "source_url":
                source_url,

            "content_type":
                validation.get(
                    "content_type",
                    ""
                )
        }

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(
        self,
        image_url: str
    ) -> Dict[str, Any]:

        image_url = self._clean(
            image_url
        )

        if not image_url:

            return {

                "valid":
                    False,

                "error":
                    "Empty image URL."
            }

        if not (
            image_url.startswith(
                "https://"
            )
            or image_url.startswith(
                "http://"
            )
        ):

            return {

                "valid":
                    False,

                "error":
                    "Image URL must use HTTP or HTTPS."
            }

        try:

            response = requests.head(

                image_url,

                allow_redirects=True,

                timeout=self.timeout,

                headers={
                    "User-Agent":
                        "AI-News-Factory/1.0"
                }
            )

            content_type = response.headers.get(
                "Content-Type",
                ""
            ).lower()

            if not response.ok:

                return {

                    "valid":
                        False,

                    "error":
                        f"Image server returned {response.status_code}."
                }

            if content_type:

                if not content_type.startswith(
                    "image/"
                ):

                    return {

                        "valid":
                            False,

                        "error":
                            "URL does not appear to point to an image."
                    }

            return {

                "valid":
                    True,

                "content_type":
                    content_type,

                "final_url":
                    response.url
            }

        except requests.RequestException as exc:

            return {

                "valid":
                    False,

                "error":
                    str(exc)
            }

    # =====================================================
    # BUILD ARTICLE MEDIA
    # =====================================================

    def build_article_media(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        result = self.resolve(
            story
        )

        if not result.get(
            "available"
        ):

            return {

                "image_url":
                    "",

                "has_image":
                    False,

                "alt":
                    self.create_alt_text(
                        story
                    ),

                "credit":
                    "",

                "source_url":
                    story.get(
                        "source_url",
                        ""
                    )
            }

        return {

            "image_url":
                result.get(
                    "image_url",
                    ""
                ),

            "has_image":
                True,

            "alt":
                self.create_alt_text(
                    story
                ),

            "credit":
                result.get(
                    "source",
                    ""
                ),

            "source_url":
                result.get(
                    "source_url",
                    ""
                )
        }

    # =====================================================
    # ALT TEXT
    # =====================================================

    def create_alt_text(
        self,
        story: Dict[str, Any]
    ) -> str:

        title = self._clean(
            story.get(
                "title",
                ""
            )
        )

        if not title:

            return "News image"

        return title[:125]

    # =====================================================
    # IMAGE PAYLOAD
    # =====================================================

    def build_social_media(
        self,
        image_url: str,
        title: str,
        source: str = ""
    ) -> Dict[str, Any]:

        return {

            "image_url":
                self._clean(
                    image_url
                ),

            "alt_text":
                self._clean(
                    title
                )[:125],

            "credit":
                self._clean(
                    source
                ),

            "usable":
                bool(
                    self._clean(
                        image_url
                    )
                )
        }

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


# =========================================================
# HELPER
# =========================================================

def create_image_engine(
    timeout: int = 15
) -> ImageEngine:

    return ImageEngine(
        timeout=timeout
      )
