"""
AI NEWS FACTORY
MEDIA MANAGER

Coordinates media preparation for articles and social posts.

Responsibilities:
- connect the Image Engine to the publishing pipeline
- prepare article media
- validate media before publishing
- keep image metadata attached to the article
- provide safe fallbacks when no image is available
"""

from typing import Any, Dict, Optional

from media.image_engine import ImageEngine


class MediaManager:

    def __init__(
        self,
        image_engine: Optional[ImageEngine] = None
    ):

        self.image_engine = (
            image_engine
            or ImageEngine()
        )

        self.name = "Media Manager"
        self.version = "1.0.0"

    # =====================================================
    # PREPARE ARTICLE MEDIA
    # =====================================================

    def prepare(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        if not isinstance(
            story,
            dict
        ):

            raise TypeError(
                "Story must be a dictionary."
            )

        media = self.image_engine.build_article_media(
            story
        )

        return {

            "status":
                "MEDIA_READY",

            "article_media":
                media,

            "has_image":
                media.get(
                    "has_image",
                    False
                )
        }

    # =====================================================
    # ATTACH TO ARTICLE
    # =====================================================

    def attach(
        self,
        article: Dict[str, Any],
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        prepared = self.prepare(
            story
        )

        media = prepared.get(
            "article_media",
            {}
        )

        updated = dict(
            article
        )

        updated[
            "image_url"
        ] = media.get(
            "image_url",
            ""
        )

        updated[
            "image_alt"
        ] = media.get(
            "alt",
            ""
        )

        updated[
            "image_credit"
        ] = media.get(
            "credit",
            ""
        )

        updated[
            "image_source_url"
        ] = media.get(
            "source_url",
            ""
        )

        updated[
            "has_image"
        ] = media.get(
            "has_image",
            False
        )

        return updated

    # =====================================================
    # SOCIAL MEDIA
    # =====================================================

    def prepare_social(
        self,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        image_url = self._clean(
            article.get(
                "image_url",
                ""
            )
        )

        title = self._clean(
            article.get(
                "title",
                ""
            )
        )

        source = self._clean(
            article.get(
                "image_credit",
                ""
            )
        )

        return self.image_engine.build_social_media(
            image_url=image_url,
            title=title,
            source=source
        )

    # =====================================================
    # VALIDATE ARTICLE MEDIA
    # =====================================================

    def validate_article_media(
        self,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        image_url = self._clean(
            article.get(
                "image_url",
                ""
            )
        )

        if not image_url:

            return {

                "valid":
                    True,

                "has_image":
                    False,

                "message":
                    "Article has no image."
            }

        validation = self.image_engine.validate(
            image_url
        )

        return {

            "valid":
                validation.get(
                    "valid",
                    False
                ),

            "has_image":
                validation.get(
                    "valid",
                    False
                ),

            "image_url":
                image_url,

            "error":
                validation.get(
                    "error",
                    ""
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

def create_media_manager(
    image_engine: Optional[ImageEngine] = None
) -> MediaManager:

    return MediaManager(
        image_engine=image_engine
          )
