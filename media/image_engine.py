"""
AI NEWS FACTORY
MEDIA IMAGE ENGINE

Responsibilities:
- Detect existing article images
- Normalize image metadata
- Build social media image metadata
- Validate image URLs
- Provide the interface expected by MediaManager
- Delegate generation to ImageGenerator when appropriate
"""

import re
import requests

from typing import Any, Dict

from media.image_generator import ImageGenerator


class ImageEngine:

    def __init__(
        self,
        image_generator: ImageGenerator = None
    ):
        self.name = "Media Image Engine"
        self.version = "2.0.0"

        self.image_generator = (
            image_generator
            or ImageGenerator()
        )

    # =========================================================
    # ARTICLE MEDIA
    # =========================================================

    def build_article_media(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        if not isinstance(story, dict):
            raise TypeError(
                "Story must be a dictionary."
            )

        image_url = self._clean(
            story.get(
                "image_url",
                story.get(
                    "image",
                    story.get(
                        "imageUrl",
                        ""
                    )
                )
            )
        )

        if image_url:

            return {
                "image_url": image_url,
                "has_image": True,
                "alt": self._clean(
                    story.get(
                        "image_alt",
                        story.get(
                            "alt",
                            self.image_generator.create_alt_text(
                                story
                            )
                        )
                    )
                ),
                "credit": self._clean(
                    story.get(
                        "image_credit",
                        story.get(
                            "credit",
                            ""
                        )
                    )
                ),
                "source_url": self._clean(
                    story.get(
                        "image_source_url",
                        story.get(
                            "source_url",
                            ""
                        )
                    )
                ),
                "caption": self._clean(
                    story.get(
                        "image_caption",
                        story.get(
                            "caption",
                            ""
                        )
                    )
                ),
                "source_type": self._clean(
                    story.get(
                        "image_source_type",
                        "EXISTING"
                    )
                ),
                "local_path": self._clean(
                    story.get(
                        "image_local_path",
                        story.get(
                            "local_path",
                            ""
                        )
                    )
                )
            }

        return {
            "image_url": "",
            "has_image": False,
            "alt": self.image_generator.create_alt_text(
                story
            ),
            "credit": "",
            "source_url": self._clean(
                story.get(
                    "source_url",
                    ""
                )
            ),
            "caption": "",
            "source_type": "NONE",
            "local_path": ""
        }

    # =========================================================
    # SOCIAL MEDIA
    # =========================================================

    def build_social_media(
        self,
        image_url: str = "",
        title: str = "",
        source: str = ""
    ) -> Dict[str, Any]:

        image_url = self._clean(image_url)
        title = self._clean(title)
        source = self._clean(source)

        return {
            "status": "READY",
            "has_image": bool(image_url),
            "image_url": image_url,
            "title": title,
            "source": source,
            "alt_text": (
                title
                or "News image"
            )
        }

    # =========================================================
    # IMAGE VALIDATION
    # =========================================================

    def validate(
        self,
        image_url: str
    ) -> Dict[str, Any]:

        image_url = self._clean(
            image_url
        )

        if not image_url:

            return {
                "valid": False,
                "content_type": "",
                "error": "Image URL is empty."
            }

        if image_url.startswith(
            "data:image"
        ):

            return {
                "valid": True,
                "content_type": "image",
                "error": ""
            }

        if image_url.startswith(
            "/"
        ) or image_url.startswith(
            "media/"
        ):

            return {
                "valid": True,
                "content_type": "image",
                "error": ""
            }

        if not image_url.startswith(
            (
                "http://",
                "https://"
            )
        ):

            return {
                "valid": False,
                "content_type": "",
                "error": "Invalid image URL."
            }

        try:

            response = requests.head(
                image_url,
                allow_redirects=True,
                timeout=15,
                headers={
                    "User-Agent":
                        "AI-News-Factory/2.0"
                }
            )

            content_type = (
                response.headers
                .get(
                    "Content-Type",
                    ""
                )
                .lower()
            )

            if response.ok and (
                content_type.startswith(
                    "image/"
                )
                or not content_type
            ):

                return {
                    "valid": True,
                    "content_type":
                        content_type,
                    "error": ""
                }

            return {
                "valid": False,
                "content_type":
                    content_type,
                "error":
                    f"HTTP {response.status_code}"
            }

        except Exception as exc:

            return {
                "valid": False,
                "content_type": "",
                "error": str(exc)
            }

    # =========================================================
    # STATUS
    # =========================================================

    def status(self) -> Dict[str, Any]:

        return {
            "engine": self.name,
            "version": self.version,
            "status": "READY",
            "generator":
                self.image_generator.status()
        }

    # =========================================================
    # HELPERS
    # =========================================================

    def _clean(
        self,
        value: Any
    ) -> str:

        if value is None:
            return ""

        return str(value).strip()


def create_image_engine(
    image_generator: ImageGenerator = None
) -> ImageEngine:

    return ImageEngine(
        image_generator=image_generator
                        )
