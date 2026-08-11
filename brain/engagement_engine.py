"""
AI NEWS FACTORY
ENGAGEMENT INTELLIGENCE ENGINE

Purpose
-------
Design the reading experience of a news article so that
the reader can quickly understand the story while having
good reasons to continue reading.

The engine analyzes:

    - opening strength
    - information density
    - curiosity gaps
    - paragraph pacing
    - section sequencing
    - reader questions
    - practical relevance
    - consequence depth
    - continuation signals
    - fatigue risk
    - clickbait risk

CORE PRINCIPLE
--------------
The goal is NOT to manipulate readers.

The goal is:

    VALUE -> CURIOSITY -> CONTEXT -> CONSEQUENCE
    -> ANSWERS -> NEXT DEVELOPMENT

A reader should continue because every section provides
useful information.

The engine must never intentionally hide critical facts,
fabricate suspense, or create false urgency.

IMPORTANT
---------
This engine is an editorial planning layer.

It does not write the final article by itself.
"""

from typing import Any, Dict, List
import re


class EngagementEngine:

    def __init__(self):

        self.name = "Engagement Intelligence Engine"
        self.version = "1.0.0"

        self.max_sections = 12

        self.high_value_sections = [
            "WHAT_HAPPENED",
            "WHY_IT_MATTERS",
            "WHO_IS_AFFECTED",
            "BACKGROUND",
            "WHAT_HAPPENS_NEXT",
            "WHAT_WE_KNOW",
            "WHAT_WE_DONT_KNOW"
        ]

        self.fatigue_words = {
            "however",
            "therefore",
            "additionally",
            "furthermore",
            "moreover",
            "consequently"
        }

        self.question_patterns = [
            "why",
            "how",
            "what",
            "when",
            "where",
            "who"
        ]

    # =====================================================
    # MAIN
    # =====================================================

    def analyze(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        opening = self._opening_strategy(
            story
        )

        questions = self._reader_questions(
            story
        )

        sections = self._build_sections(
            story,
            questions
        )

        pacing = self._pacing_strategy(
            story,
            sections
        )

        curiosity = self._curiosity_map(
            story,
            questions,
            sections
        )

        relevance = self._relevance_signals(
            story
        )

        fatigue = self._fatigue_risk(
            story
        )

        continuation = (
            self._continuation_strategy(
                story,
                sections
            )
        )

        score = self._engagement_score(
            opening,
            sections,
            curiosity,
            relevance,
            fatigue
        )

        return {
            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "ANALYZED",

            "engagement_score":
                score,

            "opening_strategy":
                opening,

            "reader_questions":
                questions,

            "section_plan":
                sections,

            "pacing_strategy":
                pacing,

            "curiosity_map":
                curiosity,

            "relevance_signals":
                relevance,

            "fatigue_risk":
                fatigue,

            "continuation_strategy":
                continuation,

            "editorial_rule":
                self._editorial_rule(
                    score
                )
        }

    # =====================================================
    # OPENING
    # =====================================================

    def _opening_strategy(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        event = str(
            story.get(
                "event",
                story.get(
                    "what_happened",
                    ""
                )
            )
        )

        subject = str(
            story.get(
                "subject",
                story.get(
                    "person",
                    story.get(
                        "organization",
                        ""
                    )
                )
            )
        )

        impact = str(
            story.get(
                "why_it_matters",
                story.get(
                    "impact",
                    ""
                )
            )
        )

        if event and impact:

            style = "EVENT_PLUS_IMPACT"

        elif event and subject:

            style = "DIRECT_NEWS_LEAD"

        elif event:

            style = "DIRECT_EVENT_LEAD"

        else:

            style = "CONTEXT_FIRST"

        return {
            "style":
                style,

            "lead_priority":
                [
                    "confirmed_fact",
                    "most_relevant_consequence",
                    "reader_context"
                ],

            "avoid":
                [
                    "generic_intro",
                    "long_background_before_event",
                    "unsupported_drama"
                ]
        }

    # =====================================================
    # READER QUESTIONS
    # =====================================================

    def _reader_questions(
        self,
        story: Dict[str, Any]
    ) -> List[str]:

        questions = []

        raw = story.get(
            "reader_questions",
            story.get(
                "questions",
                []
            )
        )

        if isinstance(
            raw,
            str
        ):

            raw = [
                raw
            ]

        if isinstance(
            raw,
            list
        ):

            questions.extend(
                str(item)
                for item in raw
                if item
            )

        defaults = [
            "What happened?",
            "Why does it matter?",
            "Who is affected?",
            "What do we know so far?",
            "What happens next?"
        ]

        for question in defaults:

            if question not in questions:

                questions.append(
                    question
                )

        if story.get(
            "timeline"
        ):

            questions.append(
                "How did we get here?"
            )

        if story.get(
            "controversy"
        ):

            questions.append(
                "What is disputed?"
            )

        if story.get(
            "economic_impact"
        ):

            questions.append(
                "What could this mean economically?"
            )

        return self._unique(
            questions
        )[:10]

    # =====================================================
    # SECTION PLAN
    # =====================================================

    def _build_sections(
        self,
        story: Dict[str, Any],
        questions: List[str]
    ) -> List[Dict[str, Any]]:

        sections = []

        sections.append({
            "id":
                "WHAT_HAPPENED",

            "purpose":
                "Give the confirmed core event quickly.",

            "reader_question":
                "What happened?",

            "priority":
                "CRITICAL"
        })

        if story.get(
            "why_it_matters"
        ) or story.get(
            "consequences"
        ):

            sections.append({
                "id":
                    "WHY_IT_MATTERS",

                "purpose":
                    "Explain the significance and immediate impact.",

                "reader_question":
                    "Why does it matter?",

                "priority":
                    "HIGH"
            })

        if story.get(
            "affected_groups"
        ):

            sections.append({
                "id":
                    "WHO_IS_AFFECTED",

                "purpose":
                    "Identify people, organizations or communities affected.",

                "reader_question":
                    "Who is affected?",

                "priority":
                    "HIGH"
            })

        if story.get(
            "timeline"
        ):

            sections.append({
                "id":
                    "TIMELINE",

                "purpose":
                    "Explain the sequence of important developments.",

                "reader_question":
                    "How did we get here?",

                "priority":
                    "MEDIUM"
            })

        if story.get(
            "historical_context"
        ) or story.get(
            "background"
        ):

            sections.append({
                "id":
                    "BACKGROUND",

                "purpose":
                    "Provide only the background necessary to understand the story.",

                "reader_question":
                    "What led to this?",

                "priority":
                    "MEDIUM"
            })

        if story.get(
            "consequences"
        ):

            sections.append({
                "id":
                    "CONSEQUENCES",

                "purpose":
                    "Explain confirmed and clearly labeled potential consequences.",

                "reader_question":
                    "What could change because of this?",

                "priority":
                    "HIGH"
            })

        if story.get(
            "what_happens_next"
        ):

            sections.append({
                "id":
                    "WHAT_HAPPENS_NEXT",

                "purpose":
                    "Explain confirmed upcoming developments and clearly labeled possibilities.",

                "reader_question":
                    "What happens next?",

                "priority":
                    "HIGH"
            })

        sections.append({
            "id":
                "WHAT_WE_DONT_KNOW",

            "purpose":
                "Clearly identify unanswered or unverified questions.",

            "reader_question":
                "What remains unknown?",

            "priority":
                "MEDIUM"
        })

        return sections[
            :self.max_sections
        ]

    # =====================================================
    # PACING
    # =====================================================

    def _pacing_strategy(
        self,
        story: Dict[str, Any],
        sections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        article_length = story.get(
            "target_word_count",
            800
        )

        try:

            article_length = int(
                article_length
            )

        except (
            TypeError,
            ValueError
        ):

            article_length = 800

        if article_length < 500:

            paragraph_target = "2-3 sentences"

        elif article_length < 1200:

            paragraph_target = "2-4 sentences"

        else:

            paragraph_target = "2-5 sentences"

        return {
            "target_word_count":
                article_length,

            "paragraph_target":
                paragraph_target,

            "section_transition":
                "Every section should answer a new reader question.",

            "pacing_rule":
                "Alternate facts, context and consequences instead of repeating the same information.",

            "avoid":
                [
                    "repeating_the_lead",
                    "long_unbroken_paragraphs",
                    "excessive_subheadings",
                    "empty_transition_sentences"
                ]
        }

    # =====================================================
    # CURIOSITY MAP
    # =====================================================

    def _curiosity_map(
        self,
        story: Dict[str, Any],
        questions: List[str],
        sections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        curiosity_points = []

        for index, section in enumerate(
            sections
        ):

            section_id = section[
                "id"
            ]

            if section_id == "WHAT_HAPPENED":

                trigger = (
                    "Give the confirmed event "
                    "and immediately establish why "
                    "the reader should care."
                )

            elif section_id == "WHY_IT_MATTERS":

                trigger = (
                    "Connect the event to its "
                    "real-world consequences."
                )

            elif section_id == "WHO_IS_AFFECTED":

                trigger = (
                    "Make the story personally or "
                    "practically relevant."
                )

            elif section_id == "TIMELINE":

                trigger = (
                    "Reveal the sequence that explains "
                    "how the situation developed."
                )

            elif section_id == "BACKGROUND":

                trigger = (
                    "Answer the context question "
                    "without delaying the main news."
                )

            elif section_id == "CONSEQUENCES":

                trigger = (
                    "Explain what could change "
                    "and distinguish fact from possibility."
                )

            elif section_id == "WHAT_HAPPENS_NEXT":

                trigger = (
                    "Give readers the next confirmed "
                    "development to watch."
                )

            else:

                trigger = (
                    "Clarify what remains uncertain "
                    "instead of pretending certainty."
                )

            curiosity_points.append({
                "order":
                    index + 1,

                "section":
                    section_id,

                "reader_reason_to_continue":
                    trigger
            })

        return curiosity_points

    # =====================================================
    # RELEVANCE
    # =====================================================

    def _relevance_signals(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        signals = []

        if story.get(
            "affected_groups"
        ):

            signals.append(
                "PEOPLE_AFFECTED"
            )

        if story.get(
            "economic_impact"
        ):

            signals.append(
                "ECONOMIC_IMPACT"
            )

        if story.get(
            "political_impact"
        ):

            signals.append(
                "POLICY_IMPACT"
            )

        if story.get(
            "practical_impact"
        ):

            signals.append(
                "PRACTICAL_IMPACT"
            )

        if story.get(
            "location"
        ):

            signals.append(
                "GEOGRAPHIC_RELEVANCE"
            )

        if story.get(
            "what_happens_next"
        ):

            signals.append(
                "FUTURE_DEVELOPMENT"
            )

        return {
            "signals":
                signals,

            "signal_count":
                len(signals),

            "reader_value":
                self._reader_value(
                    len(signals)
                )
        }

    # =====================================================
    # FATIGUE RISK
    # =====================================================

    def _fatigue_risk(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        body = str(
            story.get(
                "body",
                ""
            )
        )

        if not body:

            return {
                "score":
                    0,

                "level":
                    "UNKNOWN",

                "reasons":
                    []
            }

        paragraphs = [
            paragraph.strip()
            for paragraph in body.split(
                "\n\n"
            )
            if paragraph.strip()
        ]

        reasons = []

        score = 0

        if len(
            paragraphs
        ) > 15:

            score += 15

            reasons.append(
                "Many paragraphs"
            )

        average_length = (
            len(body.split())
            /
            max(
                len(paragraphs),
                1
            )
        )

        if average_length > 130:

            score += 25

            reasons.append(
                "Paragraphs may be too dense"
            )

        if average_length < 20:

            score += 15

            reasons.append(
                "Paragraphs may be too fragmented"
            )

        repeated_transition_count = 0

        lowered = body.lower()

        for word in self.fatigue_words:

            repeated_transition_count += (
                lowered.count(
                    word
                )
            )

        if repeated_transition_count >= 8:

            score += 20

            reasons.append(
                "Too many formal transitions"
            )

        if body.count(
            "!"
        ) >= 8:

            score += 20

            reasons.append(
                "Excessive emotional punctuation"
            )

        score = min(
            score,
            100
        )

        if score >= 60:

            level = "HIGH"

        elif score >= 30:

            level = "MEDIUM"

        else:

            level = "LOW"

        return {
            "score":
                score,

            "level":
                level,

            "reasons":
                reasons
        }

    # =====================================================
    # CONTINUATION
    # =====================================================

    def _continuation_strategy(
        self,
        story: Dict[str, Any],
        sections: List[Dict[str, Any]]
    ) -> List[str]:

        strategy = []

        if story.get(
            "timeline"
        ):

            strategy.append(
                "Use timeline progression to maintain narrative clarity."
            )

        if story.get(
            "consequences"
        ):

            strategy.append(
                "Move from event to consequence so each section adds value."
            )

        if story.get(
            "what_happens_next"
        ):

            strategy.append(
                "End with confirmed next developments and watch points."
            )

        strategy.append(
            "Use descriptive subheadings that answer real reader questions."
        )

        strategy.append(
            "Introduce new information instead of repeating previous paragraphs."
        )

        strategy.append(
            "Never withhold a critical fact merely to create suspense."
        )

        return strategy

    # =====================================================
    # SCORE
    # =====================================================

    def _engagement_score(
        self,
        opening: Dict[str, Any],
        sections: List[Dict[str, Any]],
        curiosity: List[Dict[str, Any]],
        relevance: Dict[str, Any],
        fatigue: Dict[str, Any]
    ) -> int:

        score = 45

        if opening.get(
            "style"
        ) == "EVENT_PLUS_IMPACT":

            score += 15

        elif opening.get(
            "style"
        ) == "DIRECT_NEWS_LEAD":

            score += 10
        score += min(
            len(curiosity) * 2,
            14
        )

        score += min(
            relevance.get(
                "signal_count",
                0
            ) * 3,
            12
        )

        score -= min(
            fatigue.get(
                "score",
                0
            ) * 0.20,
            20
        )

        return int(
            max(
                0,
                min(
                    score,
                    100
                )
            )
        )

    # =====================================================
    # READER VALUE
    # =====================================================

    def _reader_value(
        self,
        signal_count: int
    ) -> str:

        if signal_count >= 4:

            return "VERY_HIGH"

        if signal_count >= 3:

            return "HIGH"

        if signal_count >= 2:

            return "MODERATE"

        if signal_count == 1:

            return "LOW"

        return "LIMITED"

    # =====================================================
    # EDITORIAL RULE
    # =====================================================

    def _editorial_rule(
        self,
        score: int
    ) -> str:

        if score >= 80:

            return (
                "Strong reading structure. "
                "Maintain factual clarity while "
                "continuing to add useful information."
            )

        if score >= 60:

            return (
                "Good reading structure. "
                "Strengthen relevance, context and "
                "section-to-section information value."
            )

        if score >= 40:

            return (
                "Moderate engagement potential. "
                "Improve the opening, practical relevance "
                "and information density."
            )

        return (
            "Weak engagement structure. "
            "Lead with confirmed facts and make each "
            "section provide clear reader value."
        )

    # =====================================================
    # UNIQUE VALUES
    # =====================================================

    def _unique(
        self,
        items: List[Any]
    ) -> List[Any]:

        seen = set()
        result = []

        for item in items:

            key = str(
                item
            ).strip().lower()

            if not key:
                continue

            if key in seen:
                continue

            seen.add(
                key
            )

            result.append(
                item
            )

        return result


# =========================================================
# SAFE MODULE TEST
# =========================================================

if __name__ == "__main__":

    engine = EngagementEngine()

    test_story = {

        "event":
            "A new policy was announced.",

        "subject":
            "Government",

        "why_it_matters":
            "The policy may affect consumers.",

        "affected_groups":
            [
                "consumers",
                "businesses"
            ],

        "timeline":
            True,

        "consequences":
            "The policy could change operating costs.",

        "what_happens_next":
            "Officials are expected to provide further details.",

        "target_word_count":
            800,

        "body":
            (
                "Officials announced the new policy today.\n\n"
                "The announcement could affect consumers "
                "and businesses.\n\n"
                "More details are expected as implementation "
                "plans are released."
            )
    }

    result = engine.analyze(
        test_story
    )

    print(
        "Engagement Engine Test"
    )

    print(
        "Status:",
        result.get(
            "status"
        )
    )

    print(
        "Score:",
        result.get(
            "engagement_score"
        )
    )
