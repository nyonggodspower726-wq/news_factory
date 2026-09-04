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
            or os.getenv("IMAGE_API_URL", "").strip()
        )

        # Use the existing Cloudflare token first.
        # Do NOT put the actual token inside this file.
        self.api_key = (
            api_key
            or os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
            or os.getenv("IMAGE_API_KEY", "").strip()
        )

        self.model = (
            model
            or os.getenv("IMAGE_MODEL", "").strip()
        )

        self.output_dir = Path(output_dir)
        self.timeout = 120

        self.styles = {
            "breaking_news": (
                "professional editorial news photography, realistic scene, "
                "natural lighting, documentary composition"
            ),
            "politics": (
                "professional editorial news photograph, formal environment, "
                "realistic people and setting"
            ),
            "business": (
                "professional editorial business photograph, realistic "
                "corporate or economic setting"
            ),
            "technology": (
                "professional editorial technology photograph, realistic "
                "modern environment"
            ),
            "sports": (
                "professional editorial sports photograph, realistic action "
                "and stadium environment"
            ),
            "crime": (
                "professional editorial documentary scene, respectful, "
                "non-graphic, realistic environment"
            ),
            "health": (
                "professional editorial health photograph, clinical and "
                "realistic environment, non-graphic"
            ),
            "general": (
                "professional editorial news photograph, realistic "
                "documentary style"
            ),
        }

        self.forbidden_terms = {
            "fake evidence",
            "fabricated evidence",
            "fake photograph",
            "altered evidence",
            "misleading proof",
        }

    def generate(
        self,
        article: Dict[str, Any],
        platform: str = "website",
        mode: str = "auto",
        output_format: str = "png",
        width: int = 1280,
        height: int = 720,
    ) -> Dict[str, Any]:

        if not isinstance(article, dict):
            raise TypeError("Article must be a dictionary.")

        prompt = self.build_prompt(article)
        story_type = self.story_type(article)

        if mode == "licensed":
            return {
                "status": "LICENSE_REQUIRED",
                "generated": False,
                "source_type": "LICENSED",
                "prompt": prompt,
            }

        if not self.api_url or not self.api_key:
            return {
                "status": "NOT_CONFIGURED",
                "generated": False,
                "source_type": "AI_GENERATED",
                "prompt": prompt,
                "message": (
                    "IMAGE_API_URL and a valid API token are not configured."
                ),
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
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()
            image = self._extract_image(data)

            if not image:
                return {
                    "status": "FAILED",
                    "generated": False,
                    "source_type": "AI_GENERATED",
                    "prompt": prompt,
                    "error": "Image API returned no usable image.",
                }

            path = self._save(
                image,
                article,
                output_format
            )

            public_url = self._public_url(path)

            return {
                "status": "IMAGE_READY",
                "generated": True,
                "source_type": "AI_GENERATED",
                "image_url": public_url,
                "local_path": str(path),
                "prompt": prompt,
                "story_type": story_type,
                "platform": platform,
                "width": width,
                "height": height,
                "alt_text": self.create_alt_text(article),
                "caption": self.create_caption(article),
                "credit": "AI-generated editorial illustration",
            }

        except requests.RequestException as exc:
            logger.exception("Image generation request failed.")

            return {
                "status": "FAILED",
                "generated": False,
                "source_type": "AI_GENERATED",
                "prompt": prompt,
                "error": str(exc),
            }

        except Exception as exc:
            logger.exception("Image generation failed.")

            return {
                "status": "FAILED",
                "generated": False,
                "source_type": "AI_GENERATED",
                "prompt": prompt,
                "error": str(exc),
            }

    def build_prompt(self, article: Dict[str, Any]) -> str:
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
                article.get("category", "general")
            )
        )

        location = self._text(
            article.get("location", "")
        )

        event = self._text(
            article.get(
                "event_type",
                article.get("story_type", "general")
            )
        )

        style = self.styles.get(
            self.story_type(article),
            self.styles["general"]
        )

        prompt = (
            f"{style}. "
            "Create an original editorial image illustrating the "
            "verified news topic. "
            f"Topic: {topic}. "
            f"Event: {event}. "
            f"Headline: {title}. "
            f"Context: {summary}. "
            f"Location: {location}. "
            "The image must be visually relevant, realistic, "
            "non-deceptive, and non-graphic unless the subject "
            "itself requires otherwise. "
            "Do not create fabricated logos, fake documents, "
            "fake evidence, misleading text, or deceptive visual proof."
        )

        return self._clean(prompt)

    def story_type(self, article: Dict[str, Any]) -> str:
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
            category: sum(
                1 for word in words
                if word in text
            )
            for category, words in mapping.items()
        }

        if not scores:
            return "general"

        best_score = max(scores.values())

        if best_score == 0:
            return "general"

        return max(
            scores,
            key=scores.get
        )

    def create_alt_text(self, article: Dict[str, Any]) -> str:
        title = self._text(
            article.get(
                "title",
                article.get("headline", "")
            )
        )

        return (
            title or "News image"
        )[:125]

    def create_caption(self, article: Dict[str, Any]) -> str:
        title = self._text(
            article.get(
                "title",
                article.get("headline", "")
            )
        )

        if title:
            return f"Editorial image illustrating: {title}"

        return "Editorial news image."

    def generate_prompt_only(
        self,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {
            "status": "PROMPT_READY",
            "prompt": self.build_prompt(article),
            "story_type": self.story_type(article),
            "alt_text": self.create_alt_text(article),
            "caption": self.create_caption(article),
        }

    def _payload(
        self,
        prompt: str,
        width: int,
        height: int,
        output_format: str
    ) -> Dict[str, Any]:

        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "format": output_format,
        }

        if self.model:
            payload["model"] = self.model

        return payload

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AI-News-Factory/1.1",
        }

    def _extract_image(self, data: Any) -> Optional[str]:
        if not isinstance(data, dict):
            return None

        for key in (
            "image_url",
            "url",
            "image",
            "b64_json",
            "data",
        ):
            value = data.get(key)

            if key == "data" and isinstance(value, list) and value:
                item = value[0]

                if isinstance(item, dict):
                    value = item.get(
                        "url",
                        item.get("b64_json")
                    )

            if value:
                if isinstance(value, str):
                    return value

        return None

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
                article.get("headline", "news")
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
            if output_format.lower() in {"jpg", "jpeg"}
            else "png"
        )

        path = (
            self.output_dir
            / f"{slug}_{abs(hash(title)) % 100000}.{ext}"
        )

        if isinstance(image, str) and image.startswith(
            ("http://", "https://")
        ):
            response = requests.get(
                image,
                timeout=self.timeout,
                headers={
                    "User-Agent": "AI-News-Factory/1.1"
                },
            )

            response.raise_for_status()
            path.write_bytes(response.content)

        elif isinstance(image, str):

            if image.startswith("data:image"):
                image = image.split(",", 1)[1]

            path.write_bytes(
                base64.b64decode(image)
            )

        elif isinstance(image, (bytes, bytearray)):
            path.write_bytes(
                bytes(image)
            )

        else:
            raise ValueError(
                "Unsupported image response."
            )

        return path

    def _public_url(self, path: Path) -> str:
        base = os.getenv(
            "MEDIA_PUBLIC_BASE_URL",
            ""
        ).rstrip("/")

        if base:
            return f"{base}/{path.name}"

        return str(path)

    def validate_result(
        self,
        result: Dict[str, Any]
    ) -> bool:

        return (
            isinstance(result, dict)
            and result.get("status") == "IMAGE_READY"
            and bool(result.get("image_url"))
        )

    def _text(self, value: Any) -> str:
        if value is None:
            return ""

        if isinstance(value, dict):
            return " ".join(
                str(v)
                for v in value.values()
                if v
            )

        if isinstance(value, list):
            return " ".join(
                str(v)
                for v in value
                if v
            )

        return str(value).strip()

    def _clean(self, text: str) -> str:
        return re.sub(
            r"\s+",
            " ",
            str(text or "")
        ).strip()

    def status(self) -> Dict[str, Any]:
        return {
            "engine": self.name,
            "version": self.version,
            "status": (
                "READY"
                if self.api_url and self.api_key
                else "NOT_CONFIGURED"
            ),
            "configured": bool(
                self.api_url and self.api_key
            ),
            "credential_source": (
                "CLOUDFLARE_API_TOKEN"
                if os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
                else (
                    "IMAGE_API_KEY"
                    if os.getenv("IMAGE_API_KEY", "").strip()
                    else "NONE"
                )
            ),
        }


image_generator = ImageGenerator()


def generate_news_image(
    article,
    platform="website",
    mode="auto",
    width=1280,
    height=720
):
    return image_generator.generate(
        article,
        platform,
        mode,
        "png",
        width,
        height
    )


def build_image_prompt(article):
    return image_generator.generate_prompt_only(
        article
    )


if __name__ == "__main__":
    test = {
        "title": "Officials announce a new development",
        "topic": "breaking news",
        "excerpt": "Officials announced a new development today.",
        "location": "Lagos",
    }

    print(build_image_prompt(test))
