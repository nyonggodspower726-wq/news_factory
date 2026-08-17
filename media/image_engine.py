import os
import re
import time
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import requests


logger = logging.getLogger(__name__)


class ImageGenerator:
    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        output_dir: str = "media/generated",
    ):
        self.name = "Cloudflare Workers AI Image Generator"
        self.version = "2.0.0"

        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
        self.api_key = api_key or os.getenv("CLOUDFLARE_API_TOKEN", "").strip()

        self.model = (
            model
            or os.getenv(
                "IMAGE_MODEL",
                "@cf/bytedance/stable-diffusion-xl-lightning",
            ).strip()
        )

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.timeout = 120

        self.styles = {
            "breaking_news": (
                "professional editorial news photography, "
                "realistic scene, natural lighting, photojournalism style"
            ),
            "politics": (
                "professional editorial political photography, "
                "formal environment, realistic people and setting"
            ),
            "business": (
                "professional editorial business photography, "
                "realistic corporate or economic setting"
            ),
            "technology": (
                "professional editorial technology photography, "
                "realistic modern environment"
            ),
            "sports": (
                "professional editorial sports photography, "
                "realistic action and stadium environment"
            ),
            "crime": (
                "professional editorial documentary scene, "
                "respectful, non-graphic, realistic environment"
            ),
            "health": (
                "professional editorial health photography, "
                "clinical and realistic environment, non-graphic"
            ),
            "general": (
                "professional editorial news photography, "
                "realistic documentary style"
            ),
        }

        self.forbidden_terms = {
            "fake evidence",
            "fabricated evidence",
            "fake photograph",
            "altered evidence",
            "misleading proof",
        }

    # ---------------------------------------------------------
    # CLOUDFLARE CONFIGURATION
    # ---------------------------------------------------------

    @property
    def api_url(self) -> str:
        return (
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{self.account_id}/ai/run/{self.model}"
        )

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ---------------------------------------------------------
    # TEXT HELPERS
    # ---------------------------------------------------------

    def _text(self, value) -> str:
        if value is None:
            return ""

        if isinstance(value, dict):
            return " ".join(str(v) for v in value.values() if v)

        if isinstance(value, list):
            return " ".join(str(v) for v in value if v)

        return str(value).strip()

    def _clean(self, text: str) -> str:
        text = self._text(text)
        text = re.sub(r"\s+", " ", text).strip()

        for term in self.forbidden_terms:
            text = re.sub(
                re.escape(term),
                "",
                text,
                flags=re.IGNORECASE,
            )

        return text.strip()

    # ---------------------------------------------------------
    # STORY TYPE
    # ---------------------------------------------------------

    def story_type(self, article) -> str:
        text = self._text(
            " ".join(
                str(article.get(k, ""))
                for k in (
                    "title",
                    "headline",
                    "topic",
                    "category",
                    "content",
                    "excerpt",
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
                "politics",
                "political",
                "policy",
            ],
            "business": [
                "business",
                "company",
                "market",
                "stock",
                "economy",
                "economic",
                "investment",
                "bank",
                "finance",
            ],
            "technology": [
                "technology",
                "software",
                "ai",
                "artificial intelligence",
                "cyber",
                "robot",
                "chip",
                "app",
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
                "player",
            ],
            "crime": [
                "police",
                "arrest",
                "murder",
                "crime",
                "court",
                "suspect",
                "investigation",
            ],
            "health": [
                "doctor",
                "hospital",
                "disease",
                "health",
                "medical",
                "virus",
                "medicine",
            ],
            "breaking_news": [
                "breaking",
                "explosion",
                "earthquake",
                "flood",
                "fire",
                "crash",
                "attack",
            ],
        }

        scores = {
            key: sum(1 for word in words if word in text)
            for key, words in mapping.items()
        }

        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return "general"

    # ---------------------------------------------------------
    # PROMPT CREATION
    # ---------------------------------------------------------

    def build_prompt(self, article) -> str:
        location = self._text(article.get("location", ""))
        event = self._text(
            article.get(
                "event_type",
                article.get("story_type", "general"),
            )
        )

        story = self.story_type(article)

        style = self.styles.get(
            story,
            self.styles["general"],
        )

        title = self._text(
            article.get(
                "title",
                article.get("headline", "News"),
            )
        )

        summary = self._text(
            article.get(
                "summary",
                article.get(
                    "excerpt",
                    article.get("content", ""),
                ),
            )
        )

        prompt = (
            f"{style}. "
            f"Create an original editorial news photograph illustrating "
            f"the verified news topic. "
            f"Topic: {title}. "
            f"Event: {event}. "
            f"Location: {location}. "
            f"Context: {summary[:600]}. "
            f"The image must be visually relevant, realistic, "
            f"non-deceptive, and suitable for a professional news website. "
            f"Do not create fake evidence, documents, screenshots, "
            f"logos, fabricated proof, or misleading evidence. "
            f"Do not add text unless absolutely necessary."
        )

        return self._clean(prompt)

    # ---------------------------------------------------------
    # ALT TEXT / CAPTION
    # ---------------------------------------------------------

    def create_alt_text(self, article) -> str:
        title = self._text(
            article.get(
                "title",
                article.get("headline", ""),
            )
        )

        return (title or "News Image")[:125]

    def create_caption(self, article) -> str:
        title = self._text(
            article.get(
                "title",
                article.get("headline", ""),
            )
        )

        if title:
            return f"Editorial image illustrating: {title}"

        return "Editorial news image."

    # ---------------------------------------------------------
    # CLOUDFLARE REQUEST
    # ---------------------------------------------------------

    def _generate_cloudflare(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
    ) -> bytes:

        if not self.account_id:
            raise RuntimeError(
                "CLOUDFLARE_ACCOUNT_ID is not configured."
            )

        if not self.api_key:
            raise RuntimeError(
                "CLOUDFLARE_API_TOKEN is not configured."
            )

        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
        }

        response = requests.post(
            self.api_url,
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        )

        if response.status_code != 200:
            try:
                error_data = response.json()
            except Exception:
                error_data = response.text[:1000]

            raise RuntimeError(
                f"Cloudflare image generation failed "
                f"(HTTP {response.status_code}): {error_data}"
            )

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        # Cloudflare can return the JPEG directly.
        if (
            response.content.startswith(b"\xff\xd8\xff")
            or "image/jpeg" in content_type
            or "image/png" in content_type
        ):
            return response.content

        # Some responses may be JSON containing image data.
        try:
            data = response.json()
        except Exception:
            raise RuntimeError(
                "Cloudflare returned an unexpected image response."
            )

        result = data.get("result")

        if isinstance(result, dict):
            # Possible direct image bytes/data fields
            for key in (
                "image",
                "image_url",
                "url",
                "b64_json",
                "data",
            ):
                value = result.get(key)

                if isinstance(value, str):
                    if value.startswith("http://") or value.startswith(
                        "https://"
                    ):
                        image_response = requests.get(
                            value,
                            timeout=self.timeout,
                        )
                        image_response.raise_for_status()
                        return image_response.content

                    if value.startswith("data:image"):
                        value = value.split(",", 1)[1]

                    try:
                        import base64

                        return base64.b64decode(value)
                    except Exception:
                        pass

                if isinstance(value, list) and value:
                    first = value[0]

                    if isinstance(first, dict):
                        value = (
                            first.get("image")
                            or first.get("b64_json")
                            or first.get("data")
                            or first.get("url")
                        )

                        if isinstance(value, str):
                            if value.startswith("http"):
                                image_response = requests.get(
                                    value,
                                    timeout=self.timeout,
                                )
                                image_response.raise_for_status()
                                return image_response.content

                            try:
                                import base64

                                return base64.b64decode(value)
                            except Exception:
                                pass

        raise RuntimeError(
            f"Cloudflare response did not contain usable image data: "
            f"{str(data)[:1000]}"
        )

    # ---------------------------------------------------------
    # SAVE IMAGE
    # ---------------------------------------------------------

    def _save(
        self,
        image: bytes,
        article,
        output_format: str = "png",
    ) -> Path:

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        title = self._text(
            article.get(
                "title",
                article.get("headline", "news"),
            )
        ).lower()

        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            title,
        ).strip("-")[:70]

        if not slug:
            slug = "news"

        # Cloudflare SDXL Lightning returns JPEG.
        ext = "jpg"

        filename = (
            f"{slug}_{abs(hash(title)) % 1000000}.{ext}"
        )

        path = self.output_dir / filename

        path.write_bytes(image)

        logger.info(
            "Cloudflare image saved: %s (%d bytes)",
            path,
            len(image),
        )

        return path

    # ---------------------------------------------------------
    # PUBLIC URL
    # ---------------------------------------------------------

    def _public_url(self, path: Path) -> str:
        base = os.getenv(
            "MEDIA_PUBLIC_BASE_URL",
            "",
        ).rstrip("/")

        if base:
            relative = path.as_posix()

            if relative.startswith("./"):
                relative = relative[2:]

            return f"{base}/{relative}"

        return str(path)

    # ---------------------------------------------------------
    # MAIN GENERATOR
    # ---------------------------------------------------------

    def generate(
        self,
        article: Dict[str, Any],
        platform: str = "website",
        mode: str = "auto",
        width: int = 1024,
        height: int = 1024,
    ) -> Dict[str, Any]:

        if not isinstance(article, dict):
            raise TypeError(
                "Article must be a dictionary."
            )

        prompt = self.build_prompt(article)

        if mode == "licensed":
            return {
                "status": "LICENSE_REQUIRED",
                "generated": False,
                "source_type": "LICENSED",
                "prompt": prompt,
            }

        if not self.account_id or not self.api_key:
            return {
                "status": "NOT_CONFIGURED",
                "generated": False,
                "source_type": "AI_GENERATED",
                "prompt": prompt,
                "message": (
                    "CLOUDFLARE_ACCOUNT_ID and "
                    "CLOUDFLARE_API_TOKEN are required."
                ),
            }

        try:
            image = self._generate_cloudflare(
                prompt=prompt,
                width=width,
                height=height,
            )

            path = self._save(
                image,
                article,
                "jpg",
            )

            return {
                "status": "IMAGE_READY",
                "generated": True,
                "source_type": "AI_GENERATED",
                "path": str(path),
                "image_url": self._public_url(path),
                "alt_text": self.create_alt_text(article),
                "caption": self.create_caption(article),
                "prompt": prompt,
                "model": self.model,
            }

        except Exception as exc:
            logger.exception(
                "Cloudflare image generation failed"
            )

            return {
                "status": "IMAGE_ERROR",
                "generated": False,
                "source_type": "AI_GENERATED",
                "prompt": prompt,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # PROMPT ONLY
    # ---------------------------------------------------------

    def generate_prompt_only(
        self,
        article: Dict[str, Any],
    ) -> Dict[str, Any]:

        prompt = self.build_prompt(article)

        return {
            "status": "PROMPT_READY",
            "prompt": prompt,
            "story_type": self.story_type(article),
            "alt_text": self.create_alt_text(article),
            "caption": self.create_caption(article),
        }

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        configured = bool(
            self.account_id and self.api_key
        )

        return {
            "engine": self.name,
            "version": self.version,
            "status": "READY" if configured else "NOT_CONFIGURED",
            "configured": configured,
            "model": self.model,
        }

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    def validate_result(
        self,
        result,
    ) -> bool:

        return (
            isinstance(result, dict)
            and result.get("status") == "IMAGE_READY"
            and bool(result.get("image_url"))
        )


# -------------------------------------------------------------
# MODULE-LEVEL FUNCTIONS USED BY NEWS FACTORY
# -------------------------------------------------------------

image_generator = ImageGenerator()


def generate_news_image(
    article,
    platform="website",
    mode="auto",
    width=1024,
    height=1024,
):
    return image_generator.generate(
        article,
        platform,
        mode,
        width,
        height,
    )


def build_image_prompt(article):
    return image_generator.generate_prompt_only(article)


if __name__ == "__main__":
    test_article = {
        "title": "Officials announce a new development",
        "topic": "breaking news",
        "excerpt": (
            "Officials announced a new development today."
        ),
        "location": "Lagos, Nigeria",
    }

    result = generate_news_image(test_article)

    print(result)
