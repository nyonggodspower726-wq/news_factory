"""
AI NEWS FACTORY
Story Analyzer

Purpose:
Turn raw news information into structured story intelligence.

The analyzer identifies:
- What happened
- Who is involved
- Where it happened
- When it happened
- What is confirmed
- What is uncertain
- Why it matters
- Potential reader impact
- Key questions
- Possible story angles
"""

import re
from datetime import datetime
from typing import Any, Dict, List


class StoryAnalyzer:

    def __init__(self):
        self.name = "Story Analyzer"
        self.version = "1.0.0"

    # -----------------------------------------------------
    # MAIN ANALYSIS
    # -----------------------------------------------------

    def analyze(self, story: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a raw story.

        Expected input:

        {
            "title": "...",
            "description": "...",
            "content": "...",
            "source": "...",
            "url": "...",
            "published_at": "..."
        }
        """

        title = self._clean_text(
            story.get("title", "")
        )

        description = self._clean_text(
            story.get("description", "")
        )

        content = self._clean_text(
            story.get("content", "")
        )

        source = story.get("source", "Unknown")

        url = story.get("url", "")

        combined_text = " ".join(
            [
                title,
                description,
                content
            ]
        ).strip()

        if not combined_text:
            return {
                "status": "rejected",
                "reason": "No usable story content."
            }

        # -------------------------------------------------
        # Extract basic information
        # -------------------------------------------------

        people = self._extract_people(combined_text)

        locations = self._extract_locations(
            combined_text
        )

        keywords = self._extract_keywords(
            combined_text
        )

        questions = self._generate_questions(
            title,
            combined_text
        )

        story_type = self._classify_story(
            combined_text
        )

        urgency = self._estimate_urgency(
            title,
            combined_text
        )

        impact = self._estimate_initial_impact(
            combined_text
        )

        return {
            "status": "analyzed",

            "analysis_timestamp":
                datetime.utcnow().isoformat(),

            "original": {
                "title": title,
                "description": description,
                "content": content,
                "source": source,
                "url": url
            },

            "story": {
                "summary": self._create_summary(
                    title,
                    description,
                    content
                ),

                "story_type": story_type,

                "urgency": urgency,

                "initial_impact": impact,

                "people": people,

                "locations": locations,

                "keywords": keywords,

                "reader_questions": questions
            },

            "editorial": {
                "needs_verification": True,
                "needs_context": True,
                "needs_multiple_sources": True,
                "recommended_action": "REVIEW"
            }
        }

    # -----------------------------------------------------
    # TEXT CLEANING
    # -----------------------------------------------------

    def _clean_text(self, text: str) -> str:

        if not text:
            return ""

        text = re.sub(
            r"<[^>]+>",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    def _create_summary(
        self,
        title: str,
        description: str,
        content: str
    ) -> str:

        if description:
            return description[:600]

        if content:
            sentences = re.split(
                r"(?<=[.!?])\s+",
                content
            )

            return " ".join(
                sentences[:3]
            )[:600]

        return title

    # -----------------------------------------------------
    # PEOPLE
    # -----------------------------------------------------

    def _extract_people(
        self,
        text: str
    ) -> List[str]:

        """
        Basic person detection.

        This is intentionally conservative.
        A future NLP/LLM entity engine will replace
        this with much stronger extraction.
        """

        matches = re.findall(
            r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
            text
        )

        results = []

        for item in matches:

            if item not in results:
                results.append(item)

        return results[:20]

    # -----------------------------------------------------
    # LOCATIONS
    # -----------------------------------------------------

    def _extract_locations(
        self,
        text: str
    ) -> List[str]:

        known_locations = [
            "Nigeria",
            "Lagos",
            "Abuja",
            "Port Harcourt",
            "Kano",
            "Rivers",
            "Akwa Ibom",
            "United States",
            "United Kingdom",
            "Ghana",
            "South Africa",
            "Kenya",
            "China",
            "India",
            "Russia",
            "Ukraine",
            "France",
            "Germany"
        ]

        found = []

        text_lower = text.lower()

        for location in known_locations:

            if location.lower() in text_lower:
                found.append(location)

        return found

    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    def _extract_keywords(
        self,
        text: str
    ) -> List[str]:

        words = re.findall(
            r"\b[a-zA-Z]{5,}\b",
            text.lower()
        )

        stop_words = {
            "about",
            "after",
            "before",
            "could",
            "their",
            "there",
            "which",
            "would",
            "these",
            "those",
            "where",
            "while",
            "being",
            "because",
            "people"
        }

        frequency = {}

        for word in words:

            if word in stop_words:
                continue

            frequency[word] = (
                frequency.get(word, 0) + 1
            )

        ranked = sorted(
            frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            word
            for word, count in ranked[:15]
        ]

    # -----------------------------------------------------
    # STORY TYPE
    # -----------------------------------------------------

    def _classify_story(
        self,
        text: str
    ) -> str:

        text_lower = text.lower()

        categories = {

            "politics": [
                "president",
                "government",
                "election",
                "senate",
                "minister",
                "political"
            ],

            "business": [
                "company",
                "market",
                "business",
                "economy",
                "investment",
                "bank"
            ],

            "technology": [
                "technology",
                "software",
                "artificial intelligence",
                "ai",
                "smartphone",
                "cyber"
            ],

            "sports": [
                "football",
                "match",
                "player",
                "league",
                "championship",
                "goal"
            ],

            "entertainment": [
                "movie",
                "music",
                "actor",
                "actress",
                "celebrity",
                "film"
            ],

            "world": [
                "war",
                "international",
                "country",
                "president",
                "global"
            ]
        }

        scores = {}

        for category, terms in categories.items():

            score = 0

            for term in terms:

                if term in text_lower:
                    score += 1

            scores[category] = score

        best_category = max(
            scores,
            key=scores.get
        )

        if scores[best_category] == 0:
            return "general"

        return best_category

    # -----------------------------------------------------
    # URGENCY
    # -----------------------------------------------------

    def _estimate_urgency(
        self,
        title: str,
        text: str
    ) -> str:

        combined = (
            title + " " + text
        ).lower()

        urgent_words = [
            "breaking",
            "just in",
            "urgent",
            "attack",
            "crash",
            "death",
            "explosion",
            "earthquake",
            "resigns",
            "arrested",
            "announced",
            "developing"
        ]

        score = sum(
            1
            for word in urgent_words
            if word in combined
        )

        if score >= 2:
            return "high"

        if score == 1:
            return "medium"

        return "normal"

    # -----------------------------------------------------
    # INITIAL IMPACT
    # -----------------------------------------------------

    def _estimate_initial_impact(
        self,
        text: str
    ) -> str:

        impact_terms = [
            "millions",
            "thousands",
            "government",
            "economy",
            "prices",
            "jobs",
            "security",
            "health",
            "education",
            "fuel",
            "electricity"
        ]

        text_lower = text.lower()

        score = sum(
            1
            for term in impact_terms
            if term in text_lower
        )

        if score >= 4:
            return "high"

        if score >= 2:
            return "medium"

        return "low"

    # -----------------------------------------------------
    # READER QUESTIONS
    # -----------------------------------------------------

    def _generate_questions(
        self,
        title: str,
        text: str
    ) -> List[str]:

        return [
            "What exactly happened?",
            "Why is this happening now?",
            "Who is affected?",
            "What does this mean for ordinary people?",
            "What happens next?",
            "What information is still unconfirmed?"
        ]


# ---------------------------------------------------------
# HELPER FUNCTION
# ---------------------------------------------------------

def analyze_story(
    story: Dict[str, Any]
) -> Dict[str, Any]:

    analyzer = StoryAnalyzer()

    return analyzer.analyze(story)
