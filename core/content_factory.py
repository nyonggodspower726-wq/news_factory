"""
AI NEWS FACTORY
CONTENT FACTORY

Turns the intelligence pipeline output into a clean
website-ready news package.

Responsibilities:
- article packaging
- SEO metadata
- slug generation
- excerpts
- tags
- categories
- social captions
- Open Graph metadata
- structured publishing payload
"""

import re
import unicodedata
from typing import Any, Dict, List


class ContentFactory:

    def __init__(self):
        self.name = "AI News Content Factory"
        self.version = "1.0.0"

    # =====================================================
    # MAIN
    # =====================================================

    def build(
        self,
        pipeline_result: Dict[str, Any]
    ) -> Dict[str, Any]:

        if not isinstance(
            pipeline_result,
            dict
        ):
            raise TypeError(
                "pipeline_result must be a dictionary."
            )

        package = pipeline_result.get(
            "package",
            {}
        )

        if not isinstance(
            package,
            dict
        ):
            package = {}

        title = self._clean(
            package.get(
                "title",
                ""
            )
        )

        content = self._clean(
            package.get(
                "content",
                ""
            )
        )

        category = self._clean(
            package.get(
                "category",
                "general"
            )
        )

        source = self._clean(
            package.get(
                "source",
                ""
            )
        )

        source_url = self._clean(
            package.get(
                "source_url",
                ""
            )
        )

        slug = self.create_slug(
            title
        )

        excerpt = self.create_excerpt(
            content
        )

        tags = self.generate_tags(
            title,
            content,
            category
        )

        seo = self.generate_seo(
            title,
            content,
            category,
            slug
        )

        social = self.generate_social(
            title,
            excerpt,
            category
        )

        return {

            "status":
                "CONTENT_PACKAGE_READY",

            "factory":
                self.name,

            "version":
                self.version,

            "article": {

                "title":
                    title,

                "slug":
                    slug,

                "content":
                    content,

                "excerpt":
                    excerpt,

                "category":
                    category,

                "tags":
                    tags,

                "source":
                    source,

                "source_url":
                    source_url
            },

            "seo":
                seo,

            "social":
                social,

            "publishing": {

                "website_ready":
                    True,

                "social_ready":
                    True,

                "slug":
                    slug
            }
        }

    # =====================================================
    # SLUG
    # =====================================================

    def create_slug(
        self,
        title: str
    ) -> str:

        title = unicodedata.normalize(
            "NFKD",
            str(title)
        )

        title = title.encode(
            "ascii",
            "ignore"
        ).decode(
            "ascii"
        )

        title = title.lower()

        title = re.sub(
            r"[^a-z0-9\s-]",
            "",
            title
        )

        title = re.sub(
            r"[\s-]+",
            "-",
            title
        )

        return title.strip(
            "-"
        )[:120]

    # =====================================================
    # EXCERPT
    # =====================================================

    def create_excerpt(
        self,
        content: str,
        length: int = 180
    ) -> str:

        text = re.sub(
            r"\s+",
            " ",
            str(content)
        ).strip()

        if len(text) <= length:

            return text

        excerpt = text[
            :length
        ]

        last_space = excerpt.rfind(
            " "
        )

        if last_space > 80:

            excerpt = excerpt[
                :last_space
            ]

        return excerpt.rstrip(
            " .,;:"
        ) + "..."

    # =====================================================
    # TAGS
    # =====================================================

    def generate_tags(
        self,
        title: str,
        content: str,
        category: str
    ) -> List[str]:

        text = (
            str(title)
            + " "
            + str(content)
        )

        words = re.findall(
            r"\b[a-zA-Z]{4,}\b",
            text.lower()
        )

        stop_words = {
            "about",
            "after",
            "before",
            "could",
            "would",
            "their",
            "there",
            "which",
            "while",
            "where",
            "these",
            "those",
            "being",
            "because",
            "through",
            "reported",
            "according",
            "officials"
        }

        frequency = {}

        for word in words:

            if word in stop_words:
                continue

            frequency[word] = (
                frequency.get(
                    word,
                    0
                ) + 1
            )

        ranked = sorted(
            frequency.items(),
            key=lambda item: item[1],
            reverse=True
        )

        tags = []

        if category:

            tags.append(
                category.lower()
            )

        for word, _ in ranked:

            if word not in tags:

                tags.append(
                    word
                )

            if len(tags) >= 8:

                break

        return tags

    # =====================================================
    # SEO
    # =====================================================

    def generate_seo(
        self,
        title: str,
        content: str,
        category: str,
        slug: str
    ) -> Dict[str, Any]:

        description = self.create_excerpt(
            content,
            155
        )

        keywords = self.generate_tags(
            title,
            content,
            category
        )

        return {

            "meta_title":
                self._limit(
                    title,
                    60
                ),

            "meta_description":
                self._limit(
                    description,
                    160
                ),

            "focus_keyword":
                self._focus_keyword(
                    title,
                    category
                ),

            "keywords":
                keywords,

            "slug":
                slug,

            "robots":
                "index,follow",

            "canonical_ready":
                True,

            "open_graph_ready":
                True
        }

    # =====================================================
    # SOCIAL
    # =====================================================

    def generate_social(
        self,
        title: str,
        excerpt: str,
        category: str
    ) -> Dict[str, Any]:

        clean_title = title.strip()

        return {

            "facebook": {

                "text":
                    f"{clean_title}\n\n"
                    f"{excerpt}",

                "format":
                    "LINK_POST"
            },

            "x": {

                "text":
                    self._limit(
                        clean_title
                        + " — "
                        + excerpt,
                        270
                    ),

                "format":
                    "LINK_POST"
            },

            "linkedin": {

                "text":
                    clean_title
                    + "\n\n"
                    + excerpt,

                "format":
                    "LINK_POST"
            },

            "reddit": {

                "title":
                    clean_title,

                "text":
                    excerpt,

                "format":
                    "LINK_POST"
            },

            "generic": {

                "text":
                    clean_title
                    + "\n\n"
                    + excerpt
            }
        }

    # =====================================================
    # FOCUS KEYWORD
    # =====================================================

    def _focus_keyword(
        self,
        title: str,
        category: str
    ) -> str:

        words = re.findall(
            r"\b[a-zA-Z]{4,}\b",
            title.lower()
        )

        if words:

            return " ".join(
                words[:3]
            )

        return category.lower()

    # =====================================================
    # LIMIT
    # =====================================================

    def _limit(
        self,
        text: str,
        maximum: int
    ) -> str:

        text = str(
            text
        ).strip()

        if len(text) <= maximum:

            return text

        shortened = text[
            :maximum
        ]

        position = shortened.rfind(
            " "
        )

        if position > 0:

            shortened = shortened[
                :position
            ]

        return shortened.rstrip(
            " .,;:"
        ) + "..."

    # =====================================================
    # CLEAN
    # =====================================================

    def _clean(
        self,
        value: Any
    ) -> str:

        if value is None:

            return ""

        return re.sub(
            r"\s+",
            " ",
            str(value)
        ).strip()


# =========================================================
# HELPER
# =========================================================

def create_content_package(
    pipeline_result: Dict[str, Any]
) -> Dict[str, Any]:

    factory = ContentFactory()

    return factory.build(
        pipeline_result
  )
