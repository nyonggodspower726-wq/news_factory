import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class ImageEngine:
    """
    Media/image utility layer for News AI Factory.

    This class does NOT generate AI images.
    AI image generation is handled by media.image_generator.ImageGenerator.
    """

    def __init__(
        self,
        timeout: int = 20,
    ):
        self.name = "News Media Image Engine"
        self.version = "2.0.0"
        self.timeout = timeout

    def build_article_media(
        self,
        story: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Detect an existing image attached to a news story.
        """

        if not isinstance(story, dict):
            raise TypeError("Story must be a dictionary.")

        image_url = self._clean(
            story.get(
                "image_url",
                story.get(
                    "image",
                    story.get(
                        "thumbnail",
                        story.get(
                            "featured_image",
                            ""
                        )
                    )
                )
            )
        )

        title = self._clean(
            story.get(
                "title",
                story.get("headline", "News image")
            )
        )

        alt = self._clean(
            story.get(
                "image_alt",
                story.get(
                    "alt_text",
                    title
                )
            )
        )

        credit = self._clean(
            story.get(
                "image_credit",
                story.get(
                    "credit",
                    ""
                )
            )
        )

        source_url = self._clean(
            story.get(
                "image_source_url",
                story.get(
                    "source_url",
                    ""
                )
            )
        )

        caption = self._clean(
            story.get(
                "image_caption",
                story.get(
                    "caption",
                    ""
                )
            )
        )

        has_image = bool(image_url)

        return {
            "image_url": image_url,
            "has_image": has_image,
            "alt": alt or "News image",
            "credit": credit,
            "source_url": source_url,
            "caption": caption,
            "source_type": (
                "EXISTING"
                if has_image
                else "NONE"
            ),
            "local_path": self._clean(
                story.get("image_local_path", "")
            ),
        }

    def build_social_media(
        self,
        image_url: str = "",
        title: str = "",
        source: str = "",
    ) -> Dict[str, Any]:
        """
        Prepare image metadata for social-media publishing.
        """

        image_url = self._clean(image_url)
        title = self._clean(title)
        source = self._clean(source)

        return {
            "status": (
                "READY"
                if image_url
                else "NO_IMAGE"
            ),
            "has_image": bool(image_url),
            "image_url": image_url,
            "title": title,
            "source": source,
            "alt_text": (
                title[:125]
                if title
                else "News image"
            ),
            "caption": (
                f"Editorial image illustrating: {title}"
                if title
                else "Editorial news image."
            ),
        }

    def validate(
        self,
        image_url: str,
    ) -> Dict[str, Any]:
        """
        Validate that an image URL is reachable and appears to
        return image content.
        """

        image_url = self._clean(image_url)

        if not image_url:
            return {
                "valid": False,
                "content_type": "",
                "error": "Image URL is empty.",
            }

        if not image_url.startswith(
            ("http://", "https://")
        ):
            return {
                "valid": False,
                "content_type": "",
                "error": "Image URL must use HTTP or HTTPS.",
            }

        try:
            response = requests.head(
                image_url,
                timeout=self.timeout,
                allow_redirects=True,
                headers={
                    "User-Agent": "AI-News-Factory/2.0"
                },
            )

            content_type = response.headers.get(
                "Content-Type",
                ""
            ).lower()

            # Some image hosts do not support HEAD requests.
            if response.status_code >= 400:
                response = requests.get(
                    image_url,
                    timeout=self.timeout,
                    stream=True,
                    allow_redirects=True,
                    headers={
                        "User-Agent": "AI-News-Factory/2.0"
                    },
                )

                content_type = response.headers.get(
                    "Content-Type",
                    ""
                ).lower()

            valid = (
                200 <= response.status_code < 400
                and (
                    content_type.startswith("image/")
                    or not content_type
                )
            )

            return {
                "valid": valid,
                "content_type": content_type,
                "status_code": response.status_code,
                "error": (
                    ""
                    if valid
                    else "URL did not return a valid image."
                ),
            }

        except requests.RequestException as exc:
            logger.warning(
                "Image validation failed: %s",
                exc
            )

            return {
                "valid": False,
                "content_type": "",
                "error": str(exc),
            }

        except Exception as exc:
            logger.exception(
                "Unexpected image validation error."
            )

            return {
                "valid": False,
                "content_type": "",
                "error": str(exc),
            }

    def status(self) -> Dict[str, Any]:
        return {
            "engine": self.name,
            "version": self.version,
            "status": "READY",
            "configured": True,
        }

    def _clean(self, value: Any) -> str:
        if value is None:
            return ""

        if isinstance(value, dict):
            return " ".join(
                str(v)
                for v in value.values()
                if v
            ).strip()

        if isinstance(value, list):
            return " ".join(
                str(v)
                for v in value
                if v
            ).strip()

        return str(value).strip()


def create_image_engine(
    timeout: int = 20,
) -> ImageEngine:
    """
    Factory function expected by media.__init__.py
    and other News AI Factory components.
    """

    return ImageEngine(
        timeout=timeout
    )


image_engine = ImageEngine()


if __name__ == "__main__":
    test_story = {
        "title": "Officials announce a new development",
        "image_url": "",
        "source_url": "",
    }

    print(
        image_engine.build_article_media(
            test_story
        )
    )

    print(
        image_engine.status()
        )
