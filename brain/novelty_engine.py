"""
AI NEWS FACTORY
NOVELTY & ORIGINALITY ENGINE

Purpose
-------
Determine whether a proposed story adds something genuinely
useful beyond existing coverage.

The engine looks for:

    - new facts
    - new developments
    - new primary evidence
    - new context
    - new timeline information
    - new comparisons
    - unanswered questions
    - geographic relevance
    - audience-specific usefulness
    - duplicate / near-duplicate coverage

IMPORTANT
---------
"Original" does NOT mean inventing information.

A story can be original because it:

    explains something better
    connects verified facts
    adds new context
    reports a new development
    answers an unanswered question
    provides a useful timeline
    compares verified information

The engine NEVER approves unsupported claims merely because
they are novel.
"""

from typing import Any, Dict, List
from collections import Counter
import re


class NoveltyEngine:

    def __init__(self):

        self.name = "Novelty & Originality Engine"
        self.version = "1.0.0"

        self.duplicate_threshold = 0.85
        self.high_novelty_threshold = 75
        self.minimum_useful_novelty = 50

    # =====================================================
    # MAIN
    # =====================================================

    def analyze(
        self,
        proposed_story: Dict[str, Any],
        existing_stories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        proposed_text = self._story_text(
            proposed_story
        )

        if not proposed_text:

            return {
                "status": "INSUFFICIENT_DATA",
                "novelty_score": 0,
                "publication_recommendation":
                    "NEEDS_MORE_INFORMATION"
            }

        comparisons = []

        for existing in existing_stories:

            existing_text = self._story_text(
                existing
            )

            if not existing_text:
                continue

            similarity = self._similarity(
                proposed_text,
                existing_text
            )

            comparisons.append({

                "story_id":
                    existing.get(
                        "id"
                    ),

                "similarity":
                    round(
                        similarity,
                        3
                    ),

                "duplicate":
                    similarity
                    >=
                    self.duplicate_threshold
            })

        highest_similarity = max(
            [
                item["similarity"]
                for item in comparisons
            ],
            default=0
        )

        new_facts = self._detect_new_facts(
            proposed_story
        )

        new_context = self._detect_new_context(
            proposed_story
        )

        new_questions = self._detect_new_questions(
            proposed_story
        )

        new_analysis = self._detect_analysis(
            proposed_story
        )

        new_evidence = self._detect_new_evidence(
            proposed_story
        )

        usefulness = self._usefulness_score(
            proposed_story
        )

        originality = self._originality_score(
            new_facts,
            new_context,
            new_questions,
            new_analysis,
            new_evidence,
            usefulness,
            highest_similarity
        )

        classification = self._classification(
            originality,
            highest_similarity
        )

        recommendations = self._recommendations(
            originality,
            highest_similarity,
            new_facts,
            new_context,
            new_questions,
            new_analysis
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "ANALYZED",

            "novelty_score":
                originality,

            "classification":
                classification,

            "highest_existing_similarity":
                highest_similarity,

            "new_elements": {

                "new_facts":
                    new_facts,

                "new_context":
                    new_context,

                "new_questions":
                    new_questions,

                "new_analysis":
                    new_analysis,

                "new_evidence":
                    new_evidence
            },

            "usefulness_score":
                usefulness,

            "comparisons":
                comparisons,

            "recommendations":
                recommendations,

            "publication_recommendation":
                self._publication_recommendation(
                    originality,
                    highest_similarity,
                    new_facts,
                    new_context,
                    new_analysis
                )
        }

    # =====================================================
    # STORY TEXT
    # =====================================================

    def _story_text(
        self,
        story: Dict[str, Any]
    ) -> str:

        fields = [
            "title",
            "headline",
            "summary",
            "description",
            "body",
            "angle",
            "context"
        ]

        parts = []

        for field in fields:

            value = story.get(
                field
            )

            if isinstance(
                value,
                dict
            ):

                value = " ".join(
                    str(v)
                    for v in value.values()
                    if isinstance(
                        v,
                        (str, int, float)
                    )
                )

            if value:

                parts.append(
                    str(value)
                )

        return " ".join(
            parts
        ).strip()

    # =====================================================
    # SIMILARITY
    # =====================================================

    def _similarity(
        self,
        text_a: str,
        text_b: str
    ) -> float:

        words_a = set(
            self._tokens(
                text_a
            )
        )

        words_b = set(
            self._tokens(
                text_b
            )
        )

        if not words_a or not words_b:

            return 0.0

        intersection = (
            words_a
            &
            words_b
        )

        union = (
            words_a
            |
            words_b
        )

        return (
            len(intersection)
            /
            max(
                len(union),
                1
            )
        )

    # =====================================================
    # NEW FACTS
    # =====================================================

    def _detect_new_facts(
        self,
        story: Dict[str, Any]
    ) -> List[str]:

        candidates = []

        fields = [
            "new_facts",
            "new_claims",
            "developments",
            "key_facts"
        ]

        for field in fields:

            value = story.get(
                field
            )

            if isinstance(
                value,
                list
            ):

                candidates.extend(
                    [
                        str(item)
                        for item in value
                        if item
                    ]
                )

            elif isinstance(
                value,
                dict
            ):

                candidates.extend(
                    [
                        str(item)
                        for item in value.values()
                        if item
                    ]
                )

        return self._unique(
            candidates
        )

    # =====================================================
    # NEW CONTEXT
    # =====================================================

    def _detect_new_context(
        self,
        story: Dict[str, Any]
    ) -> List[str]:

        context = story.get(
            "new_context",
            story.get(
                "context",
                []
            )
        )

        if isinstance(
            context,
            str
        ):

            return [
                context
            ] if context else []

        if isinstance(
            context,
            list
        ):

            return self._unique(
                [
                    str(item)
                    for item in context
                    if item
                ]
            )

        if isinstance(
            context,
            dict
        ):

            return self._unique(
                [
                    str(item)
                    for item in context.values()
                    if item
                ]
            )

        return []

    # =====================================================
    # NEW QUESTIONS
    # =====================================================

    def _detect_new_questions(
        self,
        story: Dict[str, Any]
    ) -> List[str]:

        questions = story.get(
            "new_questions",
            story.get(
                "unanswered_questions",
                []
            )
        )

        if isinstance(
            questions,
            str
        ):

            questions = [
                questions
            ]

        if not isinstance(
            questions,
            list
        ):

            return []

        return self._unique(
            [
                str(question)
                for question in questions
                if question
            ]
        )

    # =====================================================
    # NEW ANALYSIS
    # =====================================================

    def _detect_analysis(
        self,
        story: Dict[str, Any]
    ) -> List[str]:

        analysis = story.get(
            "analysis",
            story.get(
                "angle",
                []
            )
        )

        if isinstance(
            analysis,
            str
        ):

            return [
                analysis
            ]

        if isinstance(
            analysis,
            dict
        ):

            return [
                str(value)
                for value in analysis.values()
                if value
            ]

        if isinstance(
            analysis,
            list
        ):

            return [
                str(value)
                for value in analysis
                if value
            ]

        return []

    # =====================================================
    # NEW EVIDENCE
    # =====================================================

    def _detect_new_evidence(
        self,
        story: Dict[str, Any]
    ) -> List[str]:

        evidence = story.get(
            "new_evidence",
            story.get(
                "primary_evidence",
                []
            )
        )

        if isinstance(
            evidence,
            str
        ):

            return [
                evidence
            ]

        if isinstance(
            evidence,
            dict
        ):

            return [
                str(value)
                for value in evidence.values()
                if value
            ]

        if isinstance(
            evidence,
            list
        ):

            return [
                str(value)
                for value in evidence
                if value
            ]

        return []

    # =====================================================
    # USEFULNESS
    # =====================================================

    def _usefulness_score(
        self,
        story: Dict[str, Any]
    ) -> int:

        score = 0

        if story.get(
            "why_it_matters"
        ):

            score += 25

        if story.get(
            "what_happens_next"
        ):

            score += 20

        if story.get(
            "timeline"
        ):

            score += 15

        if story.get(
            "comparison"
        ):

            score += 15

        if story.get(
            "explainer"
        ):

            score += 15

        if story.get(
            "reader_questions"
        ):

            score += 10

        return min(
            score,
            100
        )

    # =====================================================
    # ORIGINALITY SCORE
    # =====================================================

    def _originality_score(
        self,
        new_facts: List[str],
        new_context: List[str],
        new_questions: List[str],
        new_analysis: List[str],
        new_evidence: List[str],
        usefulness: int,
        similarity: float
    ) -> int:

        new_fact_score = min(
            len(new_facts) * 15,
            100
        )

        context_score = min(
            len(new_context) * 10,
            100
        )

        question_score = min(
            len(new_questions) * 8,
            100
        )

        analysis_score = min(
            len(new_analysis) * 12,
            100
        )

        evidence_score = min(
            len(new_evidence) * 20,
            100
        )

        duplication_penalty = (
            similarity * 40
        )

        score = (
            new_fact_score * 0.25
            +
            context_score * 0.15
            +
            question_score * 0.10
            +
            analysis_score * 0.15
            +
            evidence_score * 0.20
            +
            usefulness * 0.15
            -
            duplication_penalty
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
    # CLASSIFICATION
    # =====================================================

    def _classification(
        self,
        score: int,
        similarity: float
    ) -> str:

        if (
            similarity
            >=
            self.duplicate_threshold
        ):

            return "NEAR_DUPLICATE"

        if score >= 80:

            return "HIGHLY_ORIGINAL"

        if score >= self.high_novelty_threshold:

            return "MEANINGFULLY_DIFFERENT"

        if score >= self.minimum_useful_novelty:

            return "USEFUL_REPACKAGING"

        return "LOW_NOVELTY"

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    def _recommendations(
        self,
        score: int,
        similarity: float,
        new_facts: List[str],
        new_context: List[str],
        new_questions: List[str],
        new_analysis: List[str]
    ) -> List[str]:

        recommendations = []

        if similarity >= self.duplicate_threshold:

            recommendations.append(
                "Do not publish as another generic rewrite."
            )

            recommendations.append(
                "Find a genuinely new development, source, "
                "context, or unanswered question."
            )

        if not new_facts:

            recommendations.append(
                "Look for verified developments that are not "
                "already present in existing coverage."
            )

        if not new_context:

            recommendations.append(
                "Add useful historical, geographic, financial, "
                "legal, technical, or timeline context where relevant."
            )

        if not new_questions:

            recommendations.append(
                "Identify important questions existing coverage "
                "has not adequately answered."
            )

        if not new_analysis:

            recommendations.append(
                "Find a legitimate explanatory angle rather than "
                "simply changing the wording."
            )

        if score >= 75:

            recommendations.append(
                "Preserve the original information contribution "
                "and clearly attribute source material."
            )

        return recommendations

    # =====================================================
    # PUBLICATION RECOMMENDATION
    # =====================================================

    def _publication_recommendation(
        self,
        score: int,
        similarity: float,
        new_facts: List[str],
        new_context: List[str],
        new_analysis: List[str]
    ) -> str:

        if similarity >= self.duplicate_threshold:

            return "DO_NOT_PUBLISH_DUPLICATE"

        if score >= 80:

            return "STRONG_ORIGINAL_VALUE"

        if score >= 65:

            return "PUBLISH_IF_EDITOR_APPROVES"

        if (
            new_facts
            or
            new_context
            or
            new_analysis
        ):

            return "STRENGTHEN_AND_REVIEW"

        return "INSUFFICIENT_NEW_VALUE"

    # =====================================================
    # TOKENIZER
    # =====================================================

    def _tokens(
        self,
        text: str
    ) -> List[str]:

        text = text.lower()

        return re.findall(
            r"\b[a-z0-9]{3,}\b",
            text
        )

    # =====================================================
    # UNIQUE
    # =====================================================

    def _unique(
        self,
        items: List[str]
    ) -> List[str]:

        seen = set()
        output = []

        for item in items:

            normalized = (
                str(item)
                .strip()
                .lower()
            )

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(
                normalized
            )

            output.append(
                str(item).strip()
            )

        return output


# =========================================================
# HELPER
# =========================================================

def analyze_novelty(
    proposed_story: Dict[str, Any],
    existing_stories: List[Dict[str, Any]]
) -> Dict[str, Any]:

    engine = NoveltyEngine()

    return engine.analyze(
        proposed_story,
        existing_stories
              )
