"""
AI NEWS FACTORY
IMAGE GENERATOR

Responsibilities:
- Generate original editorial images through the configured image API
- Build safe prompts from verified news articles
- Save generated images locally
- Return public media URLs
- Provide image metadata for publishing
- Remain compatible with existing ImageEngine imports

IMPORTANT:
AI-generated images must not be presented as real photographic evidence.
Do not create fabricated evidence, fake documents, fake screenshots,
or misleading images that could be mistaken for authentic evidence.
"""

import os
import re
import base64
import logging
import requests

from typing import Any, Dict, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class ImageGenerator:

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        output_dir: str = "media/generated"
    ):

        self.name = "AI News Image Generator"
        self.version = "1.1.0"

        self.api_url = (
            api_url
            or os.getenv("IMAGE_API_URL", "")
        ).strip()

        self.api_key = (
            api_key
            or os.getenv("IMAGE_API_KEY", "")
        ).strip()

        self.model = (
            model
            or os.getenv("IMAGE_MODEL", "")
        ).strip()

        self.output_dir = Path(output_dir)

        self.timeout = 120

        self.styles = {

            "breaking_news":
                "professional editorial news photography, "
                "realistic documentary composition, "
                "natural lighting",

            "politics":
                "professional editorial political news image, "
                "formal realistic environment, "
                "documentary composition",

            "business":
                "professional editorial business news image, "
                "realistic economic or corporate environment",

            "technology":
                "professional editorial technology news image, "
                "realistic modern environment",

            "sports":
                "professional editorial sports news image, "
                "realistic action and stadium environment",

            "crime":
                "professional editorial crime news illustration, "
                "respectful non-graphic documentary environment",

            "health":
                "professional editorial health news image, "
                "realistic clinical environment, non-graphic",

            "general":
                "professional editorial news image, "
                "realistic documentary style"
        }

        self.forbidden_terms = {
            "fake evidence",
            "fabricated evidence",
            "fake photograph",
            "altered evidence",
            "misleading proof",
            "fake document",
            "fake screenshot"
        }

    # =========================================================
    # MAIN GENERATOR
    # =========================================================

    def generate(
        self,
        article: Dict[str, Any],
        platform: str = "website",
        mode: str = "auto",
        output_format: str = "png",
        width: int = 1280,
        height: int = 720
    ) -> Dict[str, Any]:

        if not isinstance(article, dict):

            raise TypeError(
                "Article must be a dictionary."
            )

        prompt = self.build_prompt(article)

        story_type = self.story_type(article)

        if mode == "licensed":

            return {
                "status":
                    "LICENSE_REQUIRED",

                "generated":
                    False,

                "source_type":
                    "LICENSED",

                "prompt":
                    prompt
            }

        if not self.api_url:

            return {

                "status":
                    "NOT_CONFIGURED",

                "generated":
                    False,

                "source_type":
                    "AI_GENERATED",

                "prompt":
                    prompt,

                "message":
                    "IMAGE_API_URL is not configured."
            }

        if not self.api_key:

            return {

                "status":
                    "NOT_CONFIGURED",

                "generated":
                    False,

                "source_type":
                    "AI_GENERATED",

                "prompt":
                    prompt,

                "message":
                    "IMAGE_API_KEY is not configured."
            }

        try:

            payload = self._payload(
                prompt,
                width,
                height,
                output_format
            )

            response = requests.post(

                self.api_url,

                headers=self._headers(),

                json=payload,

                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            image = self._extract_image(data)

            if not image:

                return {

                    "status":
                        "FAILED",

                    "generated":
                        False,

                    "source_type":
                        "AI_GENERATED",

                    "prompt":
                        prompt,

                    "error":
                        "Image API returned no usable image."
                }

            path = self._save(
                image,
                article,
                output_format
            )

            public_url = self._public_url(
                path
            )

            return {

                "status":
                    "IMAGE_READY",

                "generated":
                    True,

                "source_type":
                    "AI_GENERATED",

                "image_url":
                    public_url,

                "local_path":
                    str(path),

                "prompt":
                    prompt,

                "story_type":
                    story_type,

                "platform":
                    platform,

                "width":
                    width,

                "height":
                    height,

                "alt_text":
                    self.create_alt_text(
                        article
                    ),

                "caption":
                    self.create_caption(
                        article
                    ),

                "credit":
                    "AI-generated editorial illustration"
            }

        except requests.RequestException as exc:

            logger.exception(
                "Image generation request failed."
            )

            return {

                "status":
                    "FAILED",

                "generated":
                    False,

                "source_type":
                    "AI_GENERATED",

                "prompt":
                    prompt,

                "error":
                    str(exc)
            }

        except Exception as exc:

            logger.exception(
                "Image generation failed."
            )

            return {

                "status":
                    "FAILED",

                "generated":
                    False,

                "source_type":
                    "AI_GENERATED",

                "prompt":
                    prompt,

                "error":
                    str(exc)
            }

    # =========================================================
    # PROMPT
    # =========================================================

    def build_prompt(
        self,
        article: Dict[str, Any]
    ) -> str:

        title = self._text(
            article.get(
                "title",
                article.get("headline", "")
            )
        )

        summary = self._text(
            article.get(
                "excerpt",
                article.get(
                    "summary",
                    article.get("lead", "")
                )
            )
        )

        topic = self._text(
            article.get(
                "topic",
                article.get(
                    "category",
                    "general"
                )
            )
        )

        location = self._text(
            article.get(
                "location",
                ""
            )
        )

        event = self._text(
            article.get(
                "event_type",
                article.get(
                    "story_type",
                    "general"
                )
            )
        )

        style = self.styles.get(
            self.story_type(article),
            self.styles["general"]
        )

        prompt = (

            f"{style}. "

            "Create an original editorial image "
            "illustrating the verified news topic. "

            f"Topic: {topic}. "

            f"Event: {event}. "

            f"Headline: {title}. "

            f"Context: {summary}. "

            f"Location: {location}. "

            "The image must be visually relevant, "
            "realistic, non-deceptive and non-graphic. "

            "Do not create fabricated evidence, "
            "fake documents, fake screenshots, "
            "fake logos, fake records or misleading text."
        )

        return self._clean(prompt)

    # =========================================================
    # STORY TYPE
    # =========================================================

    def story_type(
        self,
        article: Dict[str, Any]
    ) -> str:

        text = self._text(

            " ".join(
                str(
                    article.get(key, "")
                )

                for key in (
                    "title",
                    "headline",
                    "topic",
                    "category",
                    "content",
                    "excerpt"
                )
            )

        ).lower()

        mapping = {

            "politics": [
                "president",
                "minister",
                "government",
                "election",
                "parliament",
                "senate",
                "political",
                "policy"
            ],

            "business": [
                "business",
                "company",
                "market",
                "stock",
                "economy",
                "economic",
                "investment",
                "bank"
            ],

            "technology": [
                "technology",
                "software",
                "ai",
                "artificial intelligence",
                "cyber",
                "robot",
                "chip",
                "app"
            ],

            "sports": [
                "football",
                "soccer",
                "basketball",
                "tennis",
                "sports",
                "league",
                "match",
                "coach",
                "player"
            ],

            "crime": [
                "police",
                "arrest",
                "murder",
                "crime",
                "court",
                "suspect",
                "investigation"
            ],

            "health": [
                "doctor",
                "hospital",
                "disease",
                "health",
                "medical",
                "virus",
                "medicine"
            ],

            "breaking_news": [
                "breaking",
                "explosion",
                "earthquake",
                "flood",
                "fire",
                "crash",
                "attack"
            ]
        }

        scores = {}

        for category, words in mapping.items():

            scores[category] = sum(
                1
                for word in words
                if word in text
            )

        if not scores:

            return "general"

        best = max(
            scores.values()
        )

        if best == 0:

            return "general"

        return max(
            scores,
            key=scores.get
        )

    # =========================================================
    # ALT TEXT
    # =========================================================

    def create_alt_text(
        self,
        article: Dict[str, Any]
    ) -> str:

        title = self._text(
            article.get(
                "title",
                article.get(
                    "headline",
                    ""
                )
            )
        )

        return (
            title
            or "News image"
        )[:125]

    # =========================================================
    # CAPTION
    # =========================================================

    def create_caption(
        self,
        article: Dict[str, Any]
    ) -> str:

        title = self._text(
            article.get(
                "title",
                article.get(
                    "headline",
                    ""
                )
            )
        )

        if title:

            return (
                "Editorial image illustrating: "
                + title
            )

        return "Editorial news image."

    # =========================================================
    # PROMPT ONLY
    # =========================================================

    def generate_prompt_only(
        self,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {

            "status":
                "PROMPT_READY",

            "prompt":
                self.build_prompt(
                    article
                ),

            "story_type":
                self.story_type(
                    article
                ),

            "alt_text":
                self.create_alt_text(
                    article
                ),

            "caption":
                self.create_caption(
                    article
                )
        }

    # =========================================================
    # API PAYLOAD
    # =========================================================

    def _payload(
        self,
        prompt: str,
        width: int,
        height: int,
        output_format: str
    ) -> Dict[str, Any]:

        payload = {

            "prompt":
                prompt,

            "width":
                width,

            "height":
                height,

            "format":
                output_format
        }

        if self.model:

            payload["model"] = self.model

        return payload

    # =========================================================
    # HEADERS
    # =========================================================

    def _headers(self) -> Dict[str, str]:

        return {

            "Authorization":
                f"Bearer {self.api_key}",

            "Content-Type":
                "application/json",

            "Accept":
                "application/json",

            "User-Agent":
                "AI-News-Factory/1.1"
        }

    # =========================================================
    # EXTRACT IMAGE
    # =========================================================

    def _extract_image(
        self,
        data: Any
    ) -> Optional[str]:

        if not isinstance(
            data,
            dict
        ):

            return None

        for key in (
            "image_url",
            "url",
            "image",
            "b64_json",
            "data"
        ):

            value = data.get(
                key
            )

            if key == "data":

                if isinstance(
                    value,
                    list
                ) and value:

                    item = value[0]

                    if isinstance(
                        item,
                        dict
                    ):

                        value = item.get(
                            "url",
                            item.get(
                                "b64_json"
                            )
                        )

            if not value:

                continue

            if isinstance(
                value,
                str
            ):

                return value

        return None

    # =========================================================
    # SAVE IMAGE
    # =========================================================

    def _save(
        self,
        image: Any,
        article: Dict[str, Any],
        output_format: str
    ) -> Path:

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        title = self._text(
            article.get(
                "title",
                article.get(
                    "headline",
                    "news"
                )
            )
        ).lower()

        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            title
        ).strip("-")[:70]

        if not slug:

            slug = "news"

        ext = (
            "jpg"
            if output_format.lower()
            in {"jpg", "jpeg"}
            else "png"
        )

        path = (
            self.output_dir
            / f"{slug}_{abs(hash(title)) % 100000}.{ext}"
        )

        # -----------------------------------------------------
        # URL IMAGE
        # -----------------------------------------------------

        if isinstance(
            image,
            str
        ) and image.startswith(
            (
                "http://",
                "https://"
            )
        ):

            response = requests.get(

                image,

                timeout=self.timeout,

                headers={
                    "User-Agent":
                        "AI-News-Factory/1.1"
                }
            )

            response.raise_for_status()

            path.write_bytes(
                response.content
            )

        # -----------------------------------------------------
        # BASE64 IMAGE
        # -----------------------------------------------------

        elif isinstance(
            image,
            str
        ):

            if image.startswith(
                "data:image"
            ):

                image = image.split(
                    ",",
                    1
                )[1]

            path.write_bytes(
                base64.b64decode(
                    image
                )
            )

        # -----------------------------------------------------
        # BYTES
        # -----------------------------------------------------

        elif isinstance(
            image,
            (
                bytes,
                bytearray
            )
        ):

            path.write_bytes(
                bytes(image)
            )

        else:

            raise ValueError(
                "Unsupported image response."
            )

        return path

    # =========================================================
    # PUBLIC URL
    # =========================================================

    def _public_url(
        self,
        path: Path
    ) -> str:

        base = os.getenv(
            "MEDIA_PUBLIC_BASE_URL",
            ""
        ).rstrip("/")

        if base:

            return (
                f"{base}/{path.name}"
            )

        return str(path)

    # =========================================================
    # VALIDATE RESULT
    # =========================================================

    def validate_result(
        self,
        result: Dict[str, Any]
    ) -> bool:

        return (

            isinstance(
                result,
                dict
            )

            and result.get(
                "status"
            ) == "IMAGE_READY"

            and bool(
                result.get(
                    "image_url"
                )
            )
        )

    # =========================================================
    # TEXT HELPERS
    # =========================================================

    def _text(
        self,
        value: Any
    ) -> str:

        if value is None:

            return ""

        if isinstance(
            value,
            dict
        ):

            return " ".join(
                str(v)
                for v in value.values()
                if v
            )

        if isinstance(
            value,
            list
        ):

            return " ".join(
                str(v)
                for v in value
                if v
            )

        return str(
            value
        ).strip()

    def _clean(
        self,
        text: Any
    ) -> str:

        return re.sub(
            r"\s+",
            " ",
            str(text or "")
        ).strip()

    # =========================================================
    # STATUS
    # =========================================================

    def status(
        self
    ) -> Dict[str, Any]:

        configured = bool(
            self.api_url
            and self.api_key
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "READY"
                if configured
                else "NOT_CONFIGURED",

            "configured":
                configured
        }


# =============================================================
# BACKWARD COMPATIBILITY
# =============================================================
#
# Existing News Factory code may expect ImageEngine.
# Keep that name available without changing the rest
# of the factory.
#

ImageEngine = ImageGenerator


# =============================================================
# GLOBAL INSTANCE
# =============================================================

image_generator = ImageGenerator()


# Existing generator helper
def generate_news_image(
    article,
    platform="website",
    mode="auto",
    width=1280,
    height=720
):

    return image_generator.generate(
        article=article,
        platform=platform,
        mode=mode,
        output_format="png",
        width=width,
        height=height
    )


# Prompt helper
def build_image_prompt(
    article
):

    return image_generator.generate_prompt_only(
        article
    )


# Compatibility helper
def create_image_engine(
    timeout=15
):

    return ImageGenerator(
        timeout=timeout
    )


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    test = {

        "title":
            "Officials announce a new development",

        "topic":
            "breaking news",

        "excerpt":
            "Officials announced a new development today.",

        "location":
            "Lagos"
    }

    print(
        build_image_prompt(
            test
        )
    )
