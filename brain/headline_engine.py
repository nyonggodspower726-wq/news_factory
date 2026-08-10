"""
AI NEWS FACTORY
HEADLINE INTELLIGENCE ENGINE

Purpose
-------
Generate and score multiple headline candidates.

The engine evaluates:

    - clarity
    - curiosity
    - reader value
    - search intent
    - emotional pull
    - specificity
    - urgency
    - credibility
    - click-worthiness
    - misleading-clickbait risk

CORE PRINCIPLE
--------------
A powerful headline should make people WANT to read
without making them feel tricked after they click.

The engine therefore rewards:

    curiosity + information + specificity

and penalizes:

    deception + exaggeration + unsupported claims.

IMPORTANT
---------
This engine does not invent facts.

A headline must remain consistent with verified
story information.
"""

from typing import Any, Dict, List
import re


class HeadlineEngine:

    def __init__(self):

        self.name = "Headline Intelligence Engine"
        self.version = "1.0.0"

        self.max_candidates = 10

        self.clickbait_words = {
            "shocking",
            "insane",
            "unbelievable",
            "you won't believe",
            "secret",
            "destroyed",
            "exposed",
            "bombshell",
            "jaw-dropping",
            "mind-blowing",
            "crazy",
            "everyone is talking"
        }

        self.weak_words = {
            "things",
            "stuff",
            "interesting",
            "some",
            "many",
            "big",
            "huge",
            "major"
        }

        self.curiosity_patterns = [
            "why",
            "what",
            "how",
            "after",
            "before",
            "here's what",
            "what it means",
            "what happens next",
            "why it matters"
        ]

        self.urgency_words = {
            "breaking",
            "latest",
            "just",
            "now",
            "today",
            "update",
            "urgent"
        }

    # =====================================================
    # MAIN
    # =====================================================

    def analyze(
        self,
        story: Dict[str, Any],
        candidates: List[str] = None
    ) -> Dict[str, Any]:

        if candidates is None:

            candidates = self._generate_candidates(
                story
            )

        candidates = [
            self._clean(
                headline
            )
            for headline in candidates
            if headline
        ]

        candidates = self._unique(
            candidates
        )[:self.max_candidates]

        scored = []

        for headline in candidates:

            scored.append(
                self._score_headline(
                    headline,
                    story
                )
            )

        scored.sort(
            key=lambda item:
                item["total_score"],
            reverse=True
        )

        winner = (
            scored[0]
            if scored
            else None
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "ANALYZED",

            "candidate_count":
                len(scored),

            "candidates":
                scored,

            "recommended_headline":
                winner["headline"]
                if winner
                else None,

            "recommended_score":
                winner["total_score"]
                if winner
                else 0,

            "editorial_warning":
                self._editorial_warning(
                    winner
                )
        }

    # =====================================================
    # CANDIDATE GENERATION
    # =====================================================

    def _generate_candidates(
        self,
        story: Dict[str, Any]
    ) -> List[str]:

        candidates = []

        existing = story.get(
            "headline_candidates"
        )

        if isinstance(
            existing,
            list
        ):

            candidates.extend(
                str(item)
                for item in existing
                if item
            )

        title = story.get(
            "title",
            story.get(
                "headline",
                ""
            )
        )

        event = story.get(
            "event",
            story.get(
                "what_happened",
                ""
            )
        )

        subject = story.get(
            "subject",
            story.get(
                "person",
                story.get(
                    "organization",
                    ""
                )
            )
        )

        why = story.get(
            "why_it_matters",
            ""
        )

        next_step = story.get(
            "what_happens_next",
            ""
        )

        location = story.get(
            "location",
            ""
        )

        if title:

            candidates.append(
                str(title)
            )

        if event:

            candidates.append(
                self._combine(
                    subject,
                    event
                )
            )

        if subject and event:

            candidates.append(
                f"{subject}: {event}"
            )

        if why:

            candidates.append(
                f"{self._short(event)}: "
                f"What it means"
            )

        if next_step:

            candidates.append(
                f"{self._short(event)} — "
                f"what happens next"
            )

        if location and event:

            candidates.append(
                f"{event} in {location}: "
                f"What we know"
            )

        if subject:

            candidates.append(
                f"What to know about "
                f"{subject}"
            )

        return self._unique(
            candidates
        )

    # =====================================================
    # SCORING
    # =====================================================

    def _score_headline(
        self,
        headline: str,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        clarity = self._clarity_score(
            headline
        )

        curiosity = self._curiosity_score(
            headline
        )

        specificity = self._specificity_score(
            headline,
            story
        )

        search = self._search_score(
            headline,
            story
        )

        emotional = self._emotional_score(
            headline
        )

        urgency = self._urgency_score(
            headline,
            story
        )

        credibility = self._credibility_score(
            headline
        )

        clickability = self._clickability_score(
            curiosity,
            specificity,
            emotional,
            clarity
        )

        clickbait_risk = self._clickbait_risk(
            headline
        )

        unsupported_risk = (
            self._unsupported_claim_risk(
                headline,
                story
            )
        )

        total = (
            clarity * 0.15
            +
            curiosity * 0.18
            +
            specificity * 0.17
            +
            search * 0.12
            +
            emotional * 0.10
            +
            urgency * 0.08
            +
            credibility * 0.10
            +
            clickability * 0.10
            -
            clickbait_risk * 0.12
            -
            unsupported_risk * 0.15
        )

        total = int(
            max(
                0,
                min(
                    total,
                    100
                )
            )
        )

        return {

            "headline":
                headline,

            "total_score":
                total,

            "scores": {

                "clarity":
                    clarity,

                "curiosity":
                    curiosity,

                "specificity":
                    specificity,

                "search_intent":
                    search,

                "emotional_pull":
                    emotional,

                "urgency":
                    urgency,

                "credibility":
                    credibility,

                "clickability":
                    clickability,

                "clickbait_risk":
                    clickbait_risk,

                "unsupported_claim_risk":
                    unsupported_risk
            },

            "classification":
                self._classification(
                    total,
                    clickbait_risk,
                    unsupported_risk
                )
        }

    # =====================================================
    # CLARITY
    # =====================================================

    def _clarity_score(
        self,
        headline: str
    ) -> int:

        words = headline.split()

        if not words:
            return 0

        score = 100

        if len(words) < 4:
            score -= 25

        if len(words) > 18:
            score -= 20

        if "?" in headline:
            score -= 3

        if re.search(
            r"[!?]{2,}",
            headline
        ):
            score -= 25

        weak_count = sum(
            1
            for word in words
            if word.lower() in self.weak_words
        )

        score -= (
            weak_count * 8
        )

        return max(
            0,
            min(
                score,
                100
            )
        )

    # =====================================================
    # CURIOSITY
    # =====================================================

    def _curiosity_score(
        self,
        headline: str
    ) -> int:

        lowered = headline.lower()

        score = 40

        for pattern in self.curiosity_patterns:

            if pattern in lowered:

                score += 10

        if ":" in headline:
            score += 8

        if "?" in headline:
            score += 12

        if "what it means" in lowered:
            score += 10

        if "what happens next" in lowered:
            score += 10

        return min(
            score,
            100
        )

    # =====================================================
    # SPECIFICITY
    # =====================================================

    def _specificity_score(
        self,
        headline: str,
        story: Dict[str, Any]
    ) -> int:

        score = 30

        important_fields = [
            "subject",
            "person",
            "organization",
            "location",
            "country",
            "event",
            "date",
            "number"
        ]

        lowered = headline.lower()

        for field in important_fields:

            value = story.get(
                field
            )

            if not value:
                continue

            if isinstance(
                value,
                (str, int, float)
            ):

                value_text = str(
                    value
                ).lower()

                if (
                    value_text
                    and
                    value_text in lowered
                ):

                    score += 10

        numbers = re.findall(
            r"\b\d+(?:[.,]\d+)?%?\b",
            headline
        )

        score += min(
            len(numbers) * 8,
            20
        )

        return min(
            score,
            100
        )

    # =====================================================
    # SEARCH
    # =====================================================

    def _search_score(
        self,
        headline: str,
        story: Dict[str, Any]
    ) -> int:

        score = 40

        keywords = story.get(
            "keywords",
            story.get(
                "search_keywords",
                []
            )
        )

        if isinstance(
            keywords,
            str
        ):

            keywords = [
                keywords
            ]

        lowered = headline.lower()

        matches = 0

        for keyword in keywords:

            keyword = str(
                keyword
            ).lower().strip()

            if (
                keyword
                and
                keyword in lowered
            ):

                matches += 1

        score += min(
            matches * 15,
            45
        )

        # Search-friendly headlines usually communicate
        # the topic directly.

        if len(
            headline.split()
        ) >= 6:

            score += 10

        return min(
            score,
            100
        )

    # =====================================================
    # EMOTIONAL PULL
    # =====================================================

    def _emotional_score(
        self,
        headline: str
    ) -> int:

        emotional_words = {

            "warning",
            "crisis",
            "change",
            "surge",
            "fall",
            "rise",
            "risk",
            "impact",
            "pressure",
            "fear",
            "hope",
            "victory",
            "loss",
            "decision",
            "battle",
            "shift",
            "turning point"
        }

        words = set(
            self._tokens(
                headline
            )
        )

        matches = len(
            words
            &
            emotional_words
        )

        return min(
            35
            +
            matches * 15,
            100
        )

    # =====================================================
    # URGENCY
    # =====================================================

    def _urgency_score(
        self,
        headline: str,
        story: Dict[str, Any]
    ) -> int:

        lowered = headline.lower()

        score = 35

        for word in self.urgency_words:

            if word in lowered:

                score += 10

        if story.get(
            "breaking"
        ):

            score += 25

        if story.get(
            "published_recently"
        ):

            score += 15

        return min(
            score,
            100
        )

    # =====================================================
    # CREDIBILITY
    # =====================================================

    def _credibility_score(
        self,
        headline: str
    ) -> int:

        score = 90

        lowered = headline.lower()

        for word in self.clickbait_words:

            if word in lowered:

                score -= 18

        if headline.count(
            "!"
        ) > 1:

            score -= 25

        if headline.isupper():

            score -= 25

        if "??" in headline:

            score -= 15

        return max(
            0,
            min(
                score,
                100
            )
        )

    # =====================================================
    # CLICKABILITY
    # =====================================================

    def _clickability_score(
        self,
        curiosity: int,
        specificity: int,
        emotional: int,
        clarity: int
    ) -> int:

        return int(
            curiosity * 0.35
            +
            specificity * 0.30
            +
            emotional * 0.15
            +
            clarity * 0.20
        )

    # =====================================================
    # CLICKBAIT RISK
    # =====================================================

    def _clickbait_risk(
        self,
        headline: str
    ) -> int:

        lowered = headline.lower()

        risk = 0

        for word in self.clickbait_words:

            if word in lowered:

                risk += 20

        if headline.count(
            "!"
        ) >= 2:

            risk += 20

        if headline.count(
            "?"
        ) >= 2:

            risk += 15

        if "you won't believe" in lowered:

            risk += 35

        if "shocking" in lowered:

            risk += 20

        return min(
            risk,
            100
        )

    # =====================================================
    # UNSUPPORTED CLAIM RISK
    # =====================================================

    def _unsupported_claim_risk(
        self,
        headline: str,
        story: Dict[str, Any]
    ) -> int:

        verified_facts = story.get(
            "verified_facts",
            story.get(
                "facts",
                []
            )
        )

        if isinstance(
            verified_facts,
            str
        ):

            verified_facts = [
                verified_facts
            ]

        if not verified_facts:

            return 20

        headline_tokens = set(
            self._tokens(
                headline
            )
        )

        fact_text = " ".join(
            str(fact)
            for fact in verified_facts
        ).lower()

        fact_tokens = set(
            self._tokens(
                fact_text
            )
        )

        if not headline_tokens:

            return 0

        overlap = (
            headline_tokens
            &
            fact_tokens
        )

        ratio = (
            len(overlap)
            /
            len(headline_tokens)
        )

        if ratio >= 0.60:

            return 0

        if ratio >= 0.40:

            return 15

        return 35

    # =====================================================
    # CLASSIFICATION
    # =====================================================

    def _classification(
        self,
        score: int,
        clickbait_risk: int,
        unsupported_risk: int
    ) -> str:

        if clickbait_risk >= 70:

            return "CLICKBAIT_RISK"

        if unsupported_risk >= 60:

            return "UNSUPPORTED_CLAIM_RISK"

        if score >= 85:

            return "EXCELLENT"

        if score >= 75:

            return "STRONG"

        if score >= 60:

            return "ACCEPTABLE"

        return "WEAK"

    # =====================================================
    # EDITORIAL WARNING
    # =====================================================

    def _editorial_warning(
        self,
        winner: Dict[str, Any]
    ) -> str:

        if not winner:

            return (
                "No suitable headline candidate."
            )

        if winner["classification"] == "CLICKBAIT_RISK":

            return (
                "Top headline has excessive clickbait risk. "
                "Rewrite before publication."
            )

        if winner[
            "classification"
        ] == "UNSUPPORTED_CLAIM_RISK":

            return (
                "Top headline may contain a claim that "
                "is not adequately supported."
            )

        if winner[
            "total_score"
        ] < 60:

            return (
                "No headline reached the preferred quality threshold."
            )

        return (
            "Headline is suitable for editor review."
        )
    # =====================================================
    # TEXT HELPERS
    # =====================================================

    def _tokens(
        self,
        text: str
    ) -> List[str]:

        return re.findall(
            r"\b[a-zA-Z0-9]+(?:['-][a-zA-Z0-9]+)*\b",
            str(text).lower()
        )

    def _clean(
        self,
        headline: str
    ) -> str:

        headline = str(
            headline or ""
        ).strip()

        headline = re.sub(
            r"\s+",
            " ",
            headline
        )

        headline = headline.strip(
            " -–—"
        )

        return headline

    def _unique(
        self,
        items: List[str]
    ) -> List[str]:

        seen = set()
        result = []

        for item in items:

            cleaned = self._clean(
                item
            )

            if not cleaned:
                continue

            key = cleaned.lower()

            if key in seen:
                continue

            seen.add(key)

            result.append(
                cleaned
            )

        return result

    # =====================================================
    # COMBINE
    # =====================================================

    def _combine(
        self,
        subject: str,
        event: str
    ) -> str:

        subject = str(
            subject or ""
        ).strip()

        event = str(
            event or ""
        ).strip()

        if subject and event:

            return (
                f"{subject}: "
                f"{self._short(event)}"
            )

        return self._short(
            event
        )

    # =====================================================
    # SHORTEN TEXT
    # =====================================================

    def _short(
        self,
        text: Any,
        maximum: int = 90
    ) -> str:

        text = str(
            text or ""
        ).strip()

        if len(text) <= maximum:

            return text

        return (
            text[:maximum - 3].rstrip()
            + "..."
        )


# =========================================================
# MODULE-LEVEL HELPER
# =========================================================

def analyze_headline(
    story: Dict[str, Any],
    candidates: List[str] = None
) -> Dict[str, Any]:

    engine = HeadlineEngine()

    return engine.analyze(
        story,
        candidates
    )


# =========================================================
# BASIC TEST
# =========================================================

if __name__ == "__main__":

    sample_story = {

        "subject":
            "Example News Story",

        "event":
            "Officials announce a new development",

        "headline":
            "Officials announce a new development",

        "title":
            "Example News Story",

        "summary":
            "An example news story used to test the headline engine."
    }

    engine = HeadlineEngine()

    result = engine.analyze(
        sample_story
    )

    print(
        result
        )
