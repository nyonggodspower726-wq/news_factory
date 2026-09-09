import json
import logging
import os
import re
from typing import Any, Dict, List

logger = logging.getLogger("brain.journalist_engine")


class JournalistEngine:
    """Generate long-form, publication-ready journalism from verified research."""

    def __init__(self, ai=None):
        self.ai = ai
        self.target_words = int(os.getenv("JOURNALIST_TARGET_WORDS", "1500"))
        self.min_words = int(os.getenv("JOURNALIST_MIN_WORDS", "1000"))
        self.max_words = int(os.getenv("JOURNALIST_MAX_WORDS", "2400"))
        self.temperature = float(os.getenv("JOURNALIST_TEMPERATURE", "0.4"))
        self.max_tokens = int(os.getenv("JOURNALIST_MAX_TOKENS", "6500"))
        self.max_retries = 1

    def write(
        self,
        story: Any = None,
        story_model: Any = None,
        verification: Any = None,
        sources: Any = None,
        narrative: Any = None,
        angles: Any = None,
        psychology: Any = None,
        reader_psychology: Any = None,
        engagement: Any = None,
        significance: Any = None,
        ai=None,
        **kwargs: Any,
    ) -> Dict[str, Any]:

        story = story or {}
        story_model = story_model or {}
        verification = verification or {}
        sources = sources or []
        narrative = narrative or {}
        angles = angles or {}
        psychology = psychology or {}
        reader_psychology = reader_psychology or {}
        engagement = engagement or {}
        significance = significance or {}

        client = ai or self.ai

        research = self._research(
            story=story,
            story_model=story_model,
            verification=verification,
            sources=sources,
            narrative=narrative,
            angles=angles,
            psychology=psychology,
            reader_psychology=reader_psychology,
            engagement=engagement,
            significance=significance,
        )

        if not research["publishable"]:
            return self._failure(
                "JOURNALISM_BLOCKED",
                research.get("reason", "Research is not publishable."),
            )

        if not client:
            return self._failure(
                "JOURNALISM_FAILED",
                "No journalism AI client is available.",
            )

        for attempt in range(self.max_retries + 1):
            try:
                result = self._call_ai(
                    client,
                    research,
                    expansion=attempt > 0,
                )

                article = self._clean_article(result, research)
                words = self._word_count(article.get("content", ""))

                logger.info(
                    "JOURNALIST OUTPUT | attempt=%s words=%s target=%s min=%s",
                    attempt + 1,
                    words,
                    self.target_words,
                    self.min_words,
                )

                if self._quality_ok(article, research):
                    article.update(
                        {
                            "status": "JOURNALISM_COMPLETE",
                            "publication_safe": True,
                            "publication_status": "READY",
                            "word_count": words,
                            "words": words,
                            "target_words": self.target_words,
                            "minimum_words": self.min_words,
                            "maximum_words": self.max_words,
                        }
                    )
                    return article

                if words < self.min_words and attempt < self.max_retries:
                    logger.warning(
                        "Journalist output too short | words=%s min=%s | automatic expansion retry",
                        words,
                        self.min_words,
                    )
                    continue

                logger.warning(
                    "Journalist quality gate rejected output | words=%s min=%s",
                    words,
                    self.min_words,
                )

                return self._failure(
                    "JOURNALISM_QUALITY_FAILED",
                    f"Generated article contains {words} words; minimum required is {self.min_words}.",
                    word_count=words,
                )

            except Exception as exc:
                logger.exception(
                    "Journalist AI generation failed: %s",
                    exc,
                )

                if attempt < self.max_retries:
                    logger.warning(
                        "Retrying journalism generation after failure."
                    )
                    continue

                return self._failure(
                    "JOURNALIST_FAILED",
                    str(exc),
                )

        return self._failure(
            "JOURNALISM_FAILED",
            "Journalism generation failed.",
        )

    def create(self, *args, **kwargs):
        return self.write(*args, **kwargs)

    def generate(self, *args, **kwargs):
        return self.write(*args, **kwargs)

    def produce(self, *args, **kwargs):
        return self.write(*args, **kwargs)

    def compose(self, *args, **kwargs):
        return self.write(*args, **kwargs)

    def _research(
        self,
        story,
        story_model,
        verification,
        sources,
        narrative,
        angles,
        psychology,
        reader_psychology,
        engagement,
        significance,
    ) -> Dict[str, Any]:

        title = self._text(
            story.get("title")
            or story.get("headline")
            or story_model.get("title")
            or story_model.get("headline")
        )

        summary = self._text(
            story.get("summary")
            or story.get("description")
            or story_model.get("summary")
            or story_model.get("central_event")
        )

        facts = []
        raw_facts = []

        if isinstance(story_model, dict):
            raw_facts += story_model.get("confirmed_facts", []) or []
            raw_facts += story_model.get("facts", []) or []

        if isinstance(verification, dict):
            raw_facts += verification.get("claims", []) or []
            raw_facts += verification.get("confirmed_facts", []) or []

        for item in raw_facts:
            text = self._claim_text(item)
            if text and text.lower() not in {x.lower() for x in facts}:
                facts.append(text)

        usable_sources = []

        if isinstance(sources, list):
            for source in sources[:10]:
                if not isinstance(source, dict):
                    continue

                name = self._text(
                    source.get("name")
                    or source.get("publisher")
                    or source.get("source")
                )

                url = self._text(
                    source.get("url")
                    or source.get("source_url")
                )

                text = self._text(
                    source.get("text")
                    or source.get("content")
                    or source.get("summary")
                )

                if name or url or text:
                    usable_sources.append(
                        {
                            "name": name,
                            "url": url,
                            "text": text[:5000],
                        }
                    )

        context = []

        for name, obj in (
            ("story_model", story_model),
            ("narrative", narrative),
            ("angles", angles),
            ("psychology", psychology),
            ("reader_psychology", reader_psychology),
            ("engagement", engagement),
            ("significance", significance),
        ):
            text = self._structured_text(obj)

            if text:
                context.append(f"{name}: {text[:3000]}")

        source_chars = sum(
            len(x.get("text", ""))
            for x in usable_sources
        )

        context_chars = sum(
            len(x)
            for x in context
        )

        logger.info(
            "JOURNALIST RESEARCH | sources=%s source_chars=%s facts=%s context_blocks=%s context_chars=%s",
            len(usable_sources),
            source_chars,
            len(facts),
            len(context),
            context_chars,
        )

        publishable = bool(
            title and (
                summary
                or facts
                or usable_sources
            )
        )

        return {
            "title": title,
            "summary": summary[:5000],
            "facts": facts[:40],
            "sources": usable_sources,
            "context": context[:10],
            "publishable": publishable,
            "story": story,
        }

    def _call_ai(self, client, research, expansion=False):
        facts = "\n".join(
            f"- {fact[:1000]}"
            for fact in research["facts"]
        )

        source_text = "\n\n".join(
            (
                f"SOURCE: {source.get('name', '')}\n"
                f"URL: {source.get('url', '')}\n"
                f"TEXT: {source.get('text', '')}"
            )
            for source in research["sources"]
        )

        context = "\n".join(
            research["context"]
        )

        if expansion:
            instruction = f"""
The previous draft was rejected because it was too short.

Rewrite the ENTIRE article from the supplied evidence.

The article MUST contain at least {self.min_words} words.
Aim for approximately {self.target_words} words.
Prefer roughly 1,200-1,700 words when the evidence supports it.

Do not stop after a few paragraphs.
Develop the verified facts fully.
Add useful context, chronology, consequences, reactions, and relevant background ONLY when supported by the supplied research.

Do NOT invent facts, statistics, names, quotations, dates, events, motives, or claims.

Do not mention that this is an expansion or rewrite.
"""
        else:
            instruction = f"""
Write a complete finished news article.

Target length: approximately {self.target_words} words.
Minimum acceptable length: {self.min_words} words.
Preferred range: 1,200-1,700 words when the evidence supports it.
Maximum: {self.max_words} words.

DO NOT intentionally produce a short article.
DO NOT stop after a few paragraphs.

Use the supplied evidence deeply and explain the development naturally.
Cover the important facts, chronology, context, significance, affected parties,
relevant background, consequences and developments supported by the research.

Do not invent facts, statistics, quotations, dates, names, motives or events.

Internal editorial questions may guide the article, but NEVER use generic
questions such as "What happens next?", "Why it matters?", "Who is affected?",
"What remains unclear?", "The bigger picture", or "The takeaway" as visible headings.

Use story-specific subheadings only when they genuinely improve readability.
The article should feel like professional human journalism, not an AI template.

Write substantial paragraphs with natural variation.
Do not repeat the same fact simply to increase word count.
"""

        system = f"""
You are the senior journalist for a serious digital newsroom.

You are writing publication-ready journalism from verified research.

{instruction}

Return ONLY valid JSON.

Required JSON structure:

{{
  "lead": "A strong factual opening paragraph.",
  "headline": "A clear factual headline.",
  "content": "The complete article.",
  "excerpt": "A concise factual excerpt.",
  "sections": []
}}

IMPORTANT:
- The "lead" field is REQUIRED.
- The lead must be a complete factual opening paragraph.
- "content" must contain the FULL article.
- Do not put the entire article only in "lead".
- "content" must be at least {self.min_words} words.
- Use valid JSON escaping.
- Never place raw line breaks, tabs or control characters inside JSON strings.
- Do not add Markdown fences.
- Do not add commentary outside the JSON.
"""

        user = f"""
HEADLINE/TOPIC:
{research["title"]}

SUMMARY:
{research["summary"]}

VERIFIED FACTS:
{facts}

SOURCES:
{source_text}

EDITORIAL CONTEXT:
{context}
"""

        messages = [
            {
                "role": "system",
                "content": system,
            },
            {
                "role": "user",
                "content": user,
            },
        ]

        logger.info(
            "JOURNALIST REQUEST | expansion=%s payload_chars=%s thinking=OFF max_tokens=%s",
            expansion,
            len(system) + len(user),
            self.max_tokens,
        )

        raw = client.chat(
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            enable_thinking=False,
        )

        if not raw:
            raise ValueError(
                "Journalist AI returned an empty response."
            )

        if isinstance(raw, dict):
            return raw

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            repaired = self._repair_json_controls(raw)

            try:
                return json.loads(repaired)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid journalist JSON: {exc}"
                ) from exc
    def _clean_article(self, result, research):
        if not isinstance(result, dict):
            raise ValueError(
                "Journalist AI response is not an object."
            )

        title = self._text(
            result.get("headline")
            or result.get("title")
            or research["title"]
        )

        content = self._clean_content(
            result.get("content")
            or result.get("body")
            or result.get("article")
            or ""
        )

        lead = self._clean_content(
            result.get("lead")
            or result.get("dek")
            or ""
        )

        if not lead:
            lead = self._derive_lead(content)

        excerpt = self._text(
            result.get("excerpt")
            or lead
        )

        sections = result.get("sections", [])

        if not isinstance(sections, list):
            sections = []

        return {
            "title": title,
            "headline": title,
            "lead": lead,
            "excerpt": excerpt[:400],
            "content": content,
            "body": content,
            "sections": sections,
        }

    def _quality_ok(self, article, research):
        content = self._clean_content(
            article.get("content", "")
        )

        lead = self._clean_content(
            article.get("lead", "")
        )

        words = self._word_count(content)

        if not lead:
            logger.warning(
                "Journalist quality gate rejected: lead missing"
            )
            return False

        if words < self.min_words:
            return False

        paragraphs = [
            p.strip()
            for p in re.split(
                r"\n\s*\n",
                content,
            )
            if p.strip()
        ]

        if len(paragraphs) < 8:
            logger.warning(
                "Journalist quality gate rejected: paragraphs=%s",
                len(paragraphs),
            )
            return False

        sentences = re.split(
            r"(?<=[.!?])\s+",
            content,
        )

        if len(
            [x for x in sentences if x.strip()]
        ) < 14:
            logger.warning(
                "Journalist quality gate rejected: insufficient sentences"
            )
            return False

        if self._template_score(content) > 3:
            logger.warning(
                "Journalist quality gate rejected: repetitive template language"
            )
            return False

        facts = research.get("facts", [])

        if facts:
            matches = 0
            lowered = content.lower()

            for fact in facts[:10]:
                terms = [
                    x.lower()
                    for x in re.findall(
                        r"[A-Za-z0-9]{5,}",
                        fact,
                    )
                ]

                if terms and sum(
                    term in lowered
                    for term in terms
                ) >= min(3, len(terms)):
                    matches += 1

            if matches == 0:
                logger.warning(
                    "Journalist quality gate rejected: weak evidence overlap"
                )
                return False

        return True

    def _derive_lead(self, content):
        if not content:
            return ""

        paragraphs = [
            p.strip()
            for p in re.split(
                r"\n\s*\n",
                content,
            )
            if p.strip()
        ]

        for paragraph in paragraphs:
            clean = re.sub(
                r"^#+\s*",
                "",
                paragraph,
            ).strip()

            if len(clean.split()) >= 20:
                return clean

        return paragraphs[0] if paragraphs else ""

    def _clean_content(self, value):
        text = self._text(value)
        text = re.sub(r"\r\n?", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _word_count(self, text):
        if isinstance(text, dict):
            text = text.get("content", "")

        if isinstance(text, list):
            text = " ".join(
                self._text(item)
                for item in text
            )

        text = self._text(text)

        return len(
            re.findall(
                r"\b[\w'-]+\b",
                text,
            )
        )

    def _template_score(self, text):
        forbidden = [
            "what happens next",
            "the bigger picture",
            "why it matters",
            "who is affected",
            "what remains unclear",
            "the takeaway",
            "what you need to know",
        ]

        lowered = (text or "").lower()

        return sum(
            lowered.count(item)
            for item in forbidden
        )

    def _repair_json_controls(self, raw):
        output = []
        inside_string = False
        escaped = False

        for char in raw:
            if escaped:
                output.append(char)
                escaped = False
                continue

            if char == "\\":
                output.append(char)
                escaped = True
                continue

            if char == '"':
                output.append(char)
                inside_string = not inside_string
                continue

            if inside_string:
                if char == "\n":
                    output.append("\\n")
                    continue

                if char == "\r":
                    output.append("\\r")
                    continue

                if char == "\t":
                    output.append("\\t")
                    continue

                if ord(char) < 32:
                    output.append(
                        f"\\u{ord(char):04x}"
                    )
                    continue

            output.append(char)

        return "".join(output)

    def _claim_text(self, value):
        if isinstance(value, dict):
            status = self._text(
                value.get("status")
                or value.get("verification_status")
            ).upper()

            if status in {
                "CONTRADICTED",
                "DISPUTED",
                "UNVERIFIED",
                "HOLD_FOR_REVIEW",
            }:
                return ""

            return self._text(
                value.get("text")
                or value.get("claim")
                or value.get("content")
            )

        return self._text(value)

    def _structured_text(self, value):
        if not value:
            return ""

        if isinstance(value, dict):
            parts = []

            for key, item in value.items():
                if item in (
                    None,
                    "",
                    [],
                    {},
                ):
                    continue

                if isinstance(
                    item,
                    (dict, list),
                ):
                    rendered = self._structured_text(item)
                else:
                    rendered = self._text(item)

                if rendered:
                    parts.append(
                        f"{key}: {rendered}"
                    )

            return " | ".join(parts)

        if isinstance(value, list):
            rendered_items = []

            for item in value:
                rendered = self._structured_text(item)

                if rendered:
                    rendered_items.append(rendered)

            return " | ".join(rendered_items)

        return self._text(value)

    def _text(self, value):
        if value is None:
            return ""

        if isinstance(value, dict):
            return str(
                value.get("text")
                or value.get("content")
                or value.get("title")
                or ""
            ).strip()

        if isinstance(value, list):
            return " ".join(
                self._text(item)
                for item in value
                if self._text(item)
            ).strip()

        return str(value).strip()

    def _failure(self, status, reason, **extra):
        word_count = extra.get("word_count", 0)

        result = {
            "status": status,
            "publication_safe": False,
            "publication_status": "BLOCKED",
            "reason": reason,
            "word_count": word_count,
            "words": word_count,
        }

        result.update(extra)

        return result


JournalistEngineV4 = JournalistEngine
JournalistEngineV3 = JournalistEngine
