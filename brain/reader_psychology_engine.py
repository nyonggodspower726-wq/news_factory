"""
AI NEWS FACTORY
READER PSYCHOLOGY ENGINE

Purpose
-------
Optimize news for human attention WITHOUT using deception.

It evaluates:

- curiosity
- relevance
- emotional weight
- clarity
- information gaps
- urgency
- reader payoff
- cognitive load
- headline strength
- opening strength
- retention opportunities

IMPORTANT
---------
This engine must NEVER manufacture fear, outrage, facts,
quotes, statistics, victims, or uncertainty.

Psychology is used to improve communication, not manipulate
the reader.
"""

from typing import Any, Dict, List
import re


class ReaderPsychologyEngine:

    def __init__(self):

        self.name = "Reader Psychology Intelligence Engine"
        self.version = "1.0.0"

        self.curiosity_words = {
            "why",
            "how",
            "behind",
            "reveals",
            "explained",
            "means",
            "next",
            "changed",
            "unexpected",
            "reason",
            "what"
        }

        self.urgency_words = {
            "breaking",
            "latest",
            "just",
            "now",
            "today",
            "urgent",
            "warning",
            "deadline",
            "immediately"
        }

        self.impact_words = {
            "people",
            "families",
            "workers",
            "students",
            "businesses",
            "consumers",
            "markets",
            "prices",
            "jobs",
            "money",
            "cost",
            "risk",
            "benefit"
        }

        self.strong_emotion_words = {
            "shock",
            "fear",
            "anger",
            "crisis",
            "death",
            "loss",
            "danger",
            "conflict",
            "controversy",
            "scandal"
        }

        self.banned_manipulation_patterns = [
            r"you won't believe",
            r"shocking truth",
            r"they don't want you to know",
            r"this will change everything",
            r"guaranteed",
            r"100% proof",
            r"secret exposed",
            r"everyone is furious"
        ]

    # =====================================================
    # MAIN
    # =====================================================

    def analyze(
        self,
        story: Dict[str, Any],
        article: Dict[str, Any] = None,
        angle: Dict[str, Any] = None
    ) -> Dict[str, Any]:

        story = story if isinstance(
            story,
            dict
        ) else {}

        article = article if isinstance(
            article,
            dict
        ) else {}

        angle = angle if isinstance(
            angle,
            dict
        ) else {}

        text = self._get_text(
            story,
            article
        )

        headline = self._get_headline(
            story,
            article
        )

        signals = self._signals(
            text,
            headline,
            story,
            angle
        )

        headline_score = self._headline_score(
            headline,
            signals
        )

        opening_score = self._opening_score(
            text,
            signals
        )

        retention_score = self._retention_score(
            text,
            signals
        )

        readability_score = self._readability_score(
            text
        )

        manipulation_flags = (
            self._detect_manipulation(
                headline,
                text
            )
        )

        overall = (
            headline_score * 0.25
            +
            opening_score * 0.20
            +
            retention_score * 0.25
            +
            readability_score * 0.20
            +
            signals["relevance"] * 0.10
        )

        if manipulation_flags:
            overall *= 0.70

        overall = min(
            100,
            max(
                0,
                overall
            )
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "PSYCHOLOGY_ANALYSIS_COMPLETE",

            "overall_reader_score":
                round(
                    overall,
                    2
                ),

            "headline_score":
                round(
                    headline_score,
                    2
                ),

            "opening_score":
                round(
                    opening_score,
                    2
                ),

            "retention_score":
                round(
                    retention_score,
                    2
                ),

            "readability_score":
                round(
                    readability_score,
                    2
                ),

            "signals":
                signals,

            "manipulation_flags":
                manipulation_flags,

            "reader_profile":
                self._reader_profile(
                    signals
                ),

            "improvements":
                self._improvements(
                    signals,
                    headline,
                    text
                ),

            "retention_plan":
                self._retention_plan(
                    signals
                ),

            "editorial_rule":
                (
                    "Create curiosity through useful "
                    "information gaps, not deception."
                )
        }

    # =====================================================
    # SIGNALS
    # =====================================================

    def _signals(
        self,
        text: str,
        headline: str,
        story: Dict[str, Any],
        angle: Dict[str, Any]
    ) -> Dict[str, float]:

        words = self._words(
            text
        )

        headline_words = self._words(
            headline
        )

        curiosity = self._signal(
            words,
            self.curiosity_words
        )

        urgency = self._signal(
            words,
            self.urgency_words
        )

        impact = self._signal(
            words,
            self.impact_words
        )

        emotion = self._signal(
            words,
            self.strong_emotion_words
        )

        relevance = min(
            1.0,
            (
                impact * 0.55
                +
                urgency * 0.20
                +
                emotion * 0.10
                +
                curiosity * 0.15
            )
        )

        information_gap = self._information_gap(
            text
        )

        specificity = self._specificity(
            text
        )

        novelty = self._novelty(
            story,
            angle
        )

        complexity = self._complexity(
            text
        )

        headline_curiosity = self._signal(
            headline_words,
            self.curiosity_words
        )

        headline_urgency = self._signal(
            headline_words,
            self.urgency_words
        )

        return {

            "curiosity":
                round(
                    curiosity,
                    3
                ),

            "urgency":
                round(
                    urgency,
                    3
                ),

            "impact":
                round(
                    impact,
                    3
                ),

            "emotional_weight":
                round(
                    emotion,
                    3
                ),

            "relevance":
                round(
                    relevance,
                    3
                ),

            "information_gap":
                round(
                    information_gap,
                    3
                ),

            "specificity":
                round(
                    specificity,
                    3
                ),

            "novelty":
                round(
                    novelty,
                    3
                ),

            "complexity":
                round(
                    complexity,
                    3
                ),

            "headline_curiosity":
                round(
                    headline_curiosity,
                    3
                ),

            "headline_urgency":
                round(
                    headline_urgency,
                    3
                )
        }

    # =====================================================
    # HEADLINE
    # =====================================================

    def _headline_score(
        self,
        headline: str,
        signals: Dict[str, float]
    ) -> float:

        if not headline.strip():
            return 0.0

        words = self._words(
            headline
        )

        if not words:
            return 0.0

        length_score = self._headline_length(
            headline
        )

        specificity = self._specificity(
            headline
        )

        score = (
            signals["headline_curiosity"] * 25
            +
            signals["headline_urgency"] * 10
            +
            specificity * 30
            +
            length_score * 25
            +
            signals["relevance"] * 10
        )

        if self._detect_manipulation(
            headline,
            ""
        ):
            score *= 0.55

        return min(
            100,
            score
        )

    # =====================================================
    # OPENING
    # =====================================================

    def _opening_score(
        self,
        text: str,
        signals: Dict[str, float]
    ) -> float:

        paragraphs = [
            p.strip()
            for p in re.split(
                r"\n\s*\n",
                text
            )
            if p.strip()
        ]

        if not paragraphs:
            return 0.0

        opening = paragraphs[0]

        opening_words = self._words(
            opening
        )

        if not opening_words:
            return 0.0

        specificity = self._specificity(
            opening
        )

        relevance = self._signal(
            opening_words,
            self.impact_words
        )

        curiosity = self._signal(
            opening_words,
            self.curiosity_words
        )

        length = min(
            1.0,
            len(
                opening_words
            ) / 35
        )

        return min(
            100,
            (
                specificity * 30
                +
                relevance * 30
                +
                curiosity * 20
                +
                length * 20
            )
        )

    # =====================================================
    # RETENTION
    # =====================================================

    def _retention_score(
        self,
        text: str,
        signals: Dict[str, float]
    ) -> float:

        words = self._words(
            text
        )

        if not words:
            return 0.0

        structure = self._structure_score(
            text
        )

        information_value = (
            signals["specificity"] * 0.25
            +
            signals["novelty"] * 0.25
            +
            signals["impact"] * 0.25
            +
            signals["information_gap"] * 0.25
        )

        cognitive_penalty = (
            signals["complexity"]
            * 0.25
        )

        score = (
            structure * 35
            +
            information_value * 50
            +
            15
            -
            cognitive_penalty * 20
        )

        return min(
            100,
            max(
                0,
                score
            )
        )

    # =====================================================
    # READABILITY
    # =====================================================

    def _readability_score(
        self,
        text: str
    ) -> float:

        words = self._words(
            text
        )

        if not words:
            return 0.0

        sentences = re.split(
            r"[.!?]+",
            text
        )

        sentences = [
            s.strip()
            for s in sentences
            if s.strip()
        ]

        if not sentences:
            return 50.0

        avg_words = (
            len(words)
            /
            len(sentences)
        )

        if avg_words <= 16:
            sentence_score = 1.0

        elif avg_words <= 24:
            sentence_score = 0.8

        elif avg_words <= 32:
            sentence_score = 0.55

        else:
            sentence_score = 0.30

        long_words = sum(
            1
            for word in words
            if len(
                word
            ) >= 10
        )

        complexity = (
            long_words
            /
            max(
                len(words),
                1
            )
        )

        vocabulary_score = max(
            0,
            1 - complexity
        )

        return min(
            100,
            (
                sentence_score * 60
                +
                vocabulary_score * 40
            )
        )

    # =====================================================
    # INFORMATION GAP
    # =====================================================

    def _information_gap(
        self,
        text: str
    ) -> float:

        question_mark = "?" in text

        unknown_words = {
            "why",
            "how",
            "what",
            "whether",
            "unknown",
            "unclear",
            "remains",
            "yet",
            "still",
            "pending"
        }

        signal = self._signal(
            self._words(
                text
            ),
            unknown_words
        )

        if question_mark:
            signal += 0.15

        return min(
            1.0,
            signal
        )

    # =====================================================
    # NOVELTY
    # =====================================================

    def _novelty(
        self,
        story: Dict[str, Any],
        angle: Dict[str, Any]
    ) -> float:

        if angle:

            score = angle.get(
                "angle_score",
                0
            )

            try:

                score = float(
                    score
                )

                if score > 1:
                    score /= 100

                return min(
                    1.0,
                    max(
                        0.0,
                        score
                    )
                )

            except Exception:
                pass

        if story.get(
            "is_new"
        ) is True:

            return 1.0

        return 0.50

    # =====================================================
    # SPECIFICITY
    # =====================================================

    def _specificity(
        self,
        text: str
    ) -> float:

        numbers = len(
            re.findall(
                r"\b\d+(?:\.\d+)?%?\b",
                text
            )
        )

        named_entities = len(
            re.findall(
                r"\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*\b",
                text
            )
        )

        concrete_terms = len(
            re.findall(
                r"\b(?:today|yesterday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|January|February|March|April|May|June|July|August|September|October|November|December)\b",
                text,
                re.IGNORECASE
            )
        )

        return min(
            1.0,
            (
                numbers * 0.10
                +
                named_entities * 0.05
                +
                concrete_terms * 0.08
            )
        )

    # =====================================================
    # COMPLEXITY
    # =====================================================

    def _complexity(
        self,
        text: str
    ) -> float:

        words = self._words(
            text
        )

        if not words:
            return 0.0

        long_words = sum(
            1
            for word
            in words
            if len(
                word
            ) >= 10
        )

        return min(
            1.0,
            (
                long_words
                /
                len(
                    words
                )
            )
            * 4
        )

    # =====================================================
    # STRUCTURE
    # =====================================================

    def _structure_score(
        self,
        text: str
    ) -> float:

        paragraphs = [
            p.strip()
            for p in re.split(
                r"\n\s*\n",
                text
            )
            if p.strip()
        ]

        if len(
            paragraphs
        ) >= 4:

            return 1.0

        if len(
            paragraphs
        ) == 3:

            return 0.85

        if len(
            paragraphs
        ) == 2:

            return 0.70

        return 0.45

    # =====================================================
    # HEADLINE LENGTH
    # =====================================================

    def _headline_length(
        self,
        headline: str
    ) -> float:

        length = len(
            self._words(
                headline
            )
        )

        if 7 <= length <= 14:
            return 1.0

        if 5 <= length <= 18:
            return 0.80

        if 3 <= length <= 22:
            return 0.60

        return 0.35
