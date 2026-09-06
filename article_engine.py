import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger("NewsFactory.ArticleEngine")


class ArticleEngine:
    """Generate structured, publication-ready article content from a story package."""

    def __init__(self) -> None:
        self.name = "News Article Production Engine"
        self.version = "1.0.0"
        self.max_facts = 12
        self.max_sections = 8

    def create(self, package: Dict[str, Any]) -> Dict[str, Any]:
        """Create a structured article from the supplied story package."""
        package = package if isinstance(package, dict) else {}
        story = package.get("story", {}) or {}
        synthesis = package.get("synthesis", package.get("story_model", {})) or {}
        verification = package.get("verification", {}) or {}
        significance = package.get("significance", {}) or {}
        angles = package.get("angles", {}) or {}
        headline = package.get("headline", {}) or {}

        topic = self._text(package.get("topic", story.get("topic", "")))
        title = self._title(story, headline, synthesis)
        facts = self._facts(package, synthesis, verification)
        lead = self._lead(title, facts, story, synthesis)
        context = self._context(package, synthesis)
        consequences = self._consequences(synthesis, significance)
        next_steps = self._next_steps(synthesis, story)
        questions = self._questions(synthesis, story)
        sections = self._sections(facts, context, consequences, next_steps)
        body = self._body(sections)
        excerpt = self._excerpt(lead)
        category = self._category(story, synthesis, topic)
        tags = self._tags(package, topic)
        source_links = self._source_links(package)
        publication_safe = self._publication_safe(package)

        return {
            "status": "ARTICLE_READY",
            "engine": self.name,
            "version": self.version,
            "title": title,
            "headline": title,
            "slug": self._slug(title),
            "topic": topic,
            "category": category,
            "tags": tags,
            "lead": lead,
            "excerpt": excerpt,
            "content": body,
            "body": body,
            "sections": sections,
            "key_facts": {"facts": facts},
            "context": context,
            "consequences": consequences,
            "next_steps": next_steps,
            "reader_questions": questions,
            "sources": source_links,
            "source_count": len(source_links),
            "significance": significance,
            "angle": angles.get("primary_angle", angles.get("recommended_angle", {})),
            "verification": verification,
            "publication_safe": publication_safe,
            "image_url": self._text(story.get("image_url", "")),
            "source_url": self._text(story.get("source_url", "")),
        }

    def create_article_plan(self, package: Dict[str, Any]) -> Dict[str, Any]:
        """Create an article plan containing the generated article and publication status."""
        article = self.create(package)
        return {
            "status": "ARTICLE_PLAN_READY",
            "engine": self.name,
            "version": self.version,
            "article": article,
            "publication_safe": article.get("publication_safe", False),
        }

    def _title(
        self,
        story: Dict[str, Any],
        headline: Dict[str, Any],
        synthesis: Dict[str, Any],
    ) -> str:
        """Select and normalize the most appropriate article title."""
        for value in (
            headline.get("recommended_headline"),
            headline.get("headline"),
            story.get("headline"),
            story.get("title"),
            synthesis.get("headline"),
        ):
            value = self._text(value)
            if value:
                return self._clean_title(value)

        return "Latest News Development"

    def _facts(
        self,
        package: Dict[str, Any],
        synthesis: Dict[str, Any],
        verification: Dict[str, Any],
    ) -> List[str]:
        """Collect unique, publishable facts from the available inputs."""
        raw = []
        raw.extend(synthesis.get("confirmed_facts", []) if isinstance(synthesis, dict) else [])
        raw.extend(package.get("fact_candidates", []) if isinstance(package, dict) else [])

        if isinstance(verification, dict):
            raw.extend(verification.get("claims", []))

        facts = []
        seen = set()

        for item in raw:
            text = ""
            status = ""

            if isinstance(item, dict):
                text = self._text(item.get("text", item.get("claim", "")))
                status = self._text(item.get("status", item.get("publication_status", "")))
            else:
                text = self._text(item)

            if not text:
                continue

            key = text.lower()
            if key in seen:
                continue

            if status in {"CONTRADICTED", "DISPUTED", "UNVERIFIED", "HOLD_FOR_REVIEW"}:
                continue

            seen.add(key)
            facts.append(text)

            if len(facts) >= self.max_facts:
                break

        return facts

    def _lead(
        self,
        title: str,
        facts: List[str],
        story: Dict[str, Any],
        synthesis: Dict[str, Any],
    ) -> str:
        """Select the strongest available lead for the article."""
        if facts:
            return facts[0]

        central_event = self._text(synthesis.get("central_event", ""))
        if central_event:
            return central_event

        summary = self._text(story.get("summary", story.get("description", "")))
        return summary or title

    def _context(self, package: Dict[str, Any], synthesis: Dict[str, Any]) -> List[str]:
        """Combine and normalize contextual information."""
        context = synthesis.get("context", []) if isinstance(synthesis, dict) else []
        if isinstance(context, str):
            context = [context]
        if not isinstance(context, list):
            context = []

        supplied = package.get("context", []) if isinstance(package, dict) else []
        if isinstance(supplied, str):
            supplied = [supplied]
        if isinstance(supplied, list):
            context += supplied

        return self._unique_text(context)[:6]

    def _consequences(
        self,
        synthesis: Dict[str, Any],
        significance: Dict[str, Any],
    ) -> List[str]:
        """Compile the potential implications and significance of the story."""
        values = synthesis.get("consequences", []) if isinstance(synthesis, dict) else []
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list):
            values = []

        reasons = significance.get("reasons", []) if isinstance(significance, dict) else []
        if isinstance(reasons, list):
            values += reasons

        return self._unique_text(values)[:6]

    def _next_steps(self, synthesis: Dict[str, Any], story: Dict[str, Any]) -> List[str]:
        """Collect reported or anticipated next steps."""
        values = []

        for key in ("next_steps", "what_happens_next", "future"):
            value = synthesis.get(key) if isinstance(synthesis, dict) else None
            if isinstance(value, list):
                values += value
            elif value:
                values.append(value)

        for key in ("next_steps", "what_happens_next"):
            value = story.get(key)
            if isinstance(value, list):
                values += value
            elif value:
                values.append(value)

        return self._unique_text(values)[:6]

    def _questions(self, synthesis: Dict[str, Any], story: Dict[str, Any]) -> List[str]:
        """Collect unresolved questions and known information gaps."""
        values = []

        for source, key in (
            (synthesis, "unknowns"),
            (synthesis, "questions"),
            (story, "reader_questions"),
        ):
            value = source.get(key) if isinstance(source, dict) else None
            if isinstance(value, list):
                values += value
            elif value:
                values.append(value)

        return self._unique_text(values)[:6]

    def _sections(
        self,
        facts: List[str],
        context: List[str],
        consequences: List[str],
        next_steps: List[str],
    ) -> List[Dict[str, Any]]:
        """Build the article's ordered content sections."""
        sections = []

        if facts:
            sections.append({"heading": "What happened", "content": facts})
        if context:
            sections.append({"heading": "Context", "content": context})
        if consequences:
            sections.append({"heading": "Why it matters", "content": consequences})
        if next_steps:
            sections.append({"heading": "What happens next", "content": next_steps})

        return sections[: self.max_sections]

    def _body(self, sections: List[Dict[str, Any]]) -> str:
        """Render article sections as Markdown."""
        paragraphs = []

        for section in sections:
            heading = self._text(section.get("heading"))
            content = section.get("content", [])

            if not isinstance(content, list):
                content = [content]

            paragraphs.append(f"## {heading}")

            for item in content:
                text = self._text(item)
                if text:
                    paragraphs.append(text)

        return "\n\n".join(paragraphs)

    def _excerpt(self, text: str) -> str:
        """Create a concise excerpt from the article lead."""
        text = self._clean_text(text)
        return text[:240].rsplit(" ", 1)[0] if len(text) > 240 else text

    def _category(
        self,
        story: Dict[str, Any],
        synthesis: Dict[str, Any],
        topic: str,
    ) -> str:
        """Determine and normalize the article category."""
        value = self._text(
            story.get(
                "category",
                story.get("story_type", synthesis.get("story_type", "general")),
            )
        )

        if value:
            return value.lower().replace(" ", "-")

        return "general"

    def _tags(self, package: Dict[str, Any], topic: str) -> List[str]:
        """Generate unique tags from the topic and story entities."""
        values = []

        if topic:
            values.extend(
                re.findall(r"\b[a-zA-Z][a-zA-Z0-9'-]{2,}\b", topic.lower())
            )

        story = package.get("story", {}) if isinstance(package, dict) else {}
        entities = story.get("entities", {}) if isinstance(story, dict) else {}

        if isinstance(entities, dict):
            for key in ("people", "organizations", "locations", "topics"):
                value = entities.get(key, [])
                if isinstance(value, list):
                    values += value

        return self._unique_text(values)[:10]

    def _source_links(self, package: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract valid source links from the story package."""
        sources = package.get("sources", []) if isinstance(package, dict) else {}
        output = []

        if not isinstance(sources, list):
            return output

        for source in sources:
            if not isinstance(source, dict):
                continue

            url = self._text(source.get("url", source.get("source_url", "")))
            if not url:
                continue

            output.append(
                {
                    "name": self._text(source.get("name", source.get("publisher", ""))),
                    "url": url,
                }
            )

        return output

    def _publication_safe(self, package: Dict[str, Any]) -> bool:
        """Evaluate verification and editorial controls before publication."""
        verification = package.get("verification", {}) if isinstance(package, dict) else {}
        editorial = package.get("editorial", {}) if isinstance(package, dict) else {}
        editorial_gate = (
            editorial.get("publication_gate") if isinstance(editorial, dict) else None
        )
        status = (
            self._text(verification.get("publication_status", ""))
            if isinstance(verification, dict)
            else ""
        )
        publication_ready = package.get("publication_ready")

        logger.info(
            "PUBLICATION GATE CHECK | verification=%s | editorial_gate=%s | publication_ready=%s",
            status,
            editorial_gate,
            publication_ready,
        )

        if isinstance(editorial, dict) and editorial_gate is False:
            logger.warning("PUBLICATION BLOCKED | reason=EDITORIAL_GATE_FALSE")
            return False

        if status in {"BLOCK_PUBLICATION", "HUMAN_REVIEW_REQUIRED"}:
            logger.warning("PUBLICATION BLOCKED | reason=VERIFICATION_%s", status)
            return False

        if publication_ready is False:
            logger.warning("PUBLICATION BLOCKED | reason=PUBLICATION_READY_FALSE")
            return False

        logger.info("PUBLICATION GATE PASSED")
        return True

    def _slug(self, title: str) -> str:
        """Convert a title into a URL-safe slug."""
        slug = self._text(title).lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s-]+", "-", slug).strip("-")
        return slug[:100]

    def _clean_title(self, text: str) -> str:
        """Normalize and limit a title."""
        return self._clean_text(text)[:140]

    def _clean_text(self, text: Any) -> str:
        """Normalize whitespace and trim surrounding spaces."""
        return re.sub(r"\s+", " ", self._text(text)).strip()

    def _text(self, value: Any) -> str:
        """Convert supported values to normalized text."""
        if value is None:
            return ""

        if isinstance(value, dict):
            return self._clean_text(
                value.get("text", value.get("content", value.get("title", "")))
            )

        if isinstance(value, list):
            return self._clean_text(" ".join(str(item) for item in value))

        return str(value).strip()

    def _unique_text(self, values: List[Any]) -> List[str]:
        """Return unique, normalized text values while preserving order."""
        output = []
        seen = set()

        for value in values:
            text = self._clean_text(value)
            if not text:
                continue

            key = text.lower()
            if key in seen:
                continue

            seen.add(key)
            output.append(text)

        return output

    def status(self) -> Dict[str, str]:
        """Return the current engine status."""
        return {"engine": self.name, "version": self.version, "status": "READY"}


article_engine = ArticleEngine()


def create_article(package: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an article using the shared article engine."""
    return article_engine.create(package)


def create_article_plan(package: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an article plan using the shared article engine."""
    return article_engine.create_article_plan(package)


if __name__ == "__main__":
    test = {
        "story": {
            "title": "Officials announce a new development",
            "summary": "Officials announced a new development.",
        },
        "synthesis": {
            "confirmed_facts": ["Officials announced a new development."]
        },
        "verification": {},
        "significance": {
            "reasons": ["The development may affect the public."]
        },
        "publication_ready": True,
    }

    print(create_article(test))
