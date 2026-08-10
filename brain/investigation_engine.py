"""
AI NEWS FACTORY
INVESTIGATION ENGINE

Purpose
-------
Decide when a developing story requires deeper investigation.

The engine examines:
    - conflicting reports
    - missing primary evidence
    - important unsupported claims
    - unusual source behavior
    - rapidly changing stories
    - allegations
    - suspiciously repeated information
    - important unanswered questions

It does NOT invent facts.

It produces an investigation plan for the downstream
research, evidence, verification and editorial systems.

Possible investigation levels:

    NONE
    LIGHT
    STANDARD
    DEEP
    URGENT
"""

from typing import Any, Dict, List
from collections import Counter
import re


class InvestigationEngine:

    def __init__(self):

        self.name = "Investigation Intelligence Engine"
        self.version = "1.0.0"

        self.high_risk_terms = {
            "alleged",
            "allegedly",
            "accused",
            "accusation",
            "corruption",
            "fraud",
            "scam",
            "murder",
            "killed",
            "abuse",
            "assault",
            "terrorist",
            "terrorism",
            "criminal",
            "stolen",
            "bribery",
            "sexual",
            "exploit",
            "illegal",
            "ban",
            "banned",
            "arrested",
            "resigned",
            "impeached"
        }

        self.high_impact_terms = {
            "president",
            "government",
            "election",
            "minister",
            "court",
            "police",
            "military",
            "bank",
            "economy",
            "market",
            "currency",
            "crisis",
            "war",
            "attack",
            "earthquake",
            "flood",
            "explosion",
            "pandemic"
        }

        self.question_patterns = [
            "why",
            "how",
            "what happened",
            "who",
            "when",
            "where",
            "whether",
            "is it true",
            "did",
            "will"
        ]

    # =====================================================
    # MAIN
    # =====================================================

    def investigate(
        self,
        story: Dict[str, Any] = None,
        research: Dict[str, Any] = None,
        claims: List[Dict[str, Any]] = None,
        sources: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        story = (
            story
            if isinstance(story, dict)
            else {}
        )

        research = (
            research
            if isinstance(research, dict)
            else {}
        )

        claims = (
            claims
            if isinstance(claims, list)
            else research.get(
                "claim_candidates",
                []
            )
        )

        sources = (
            sources
            if isinstance(sources, list)
            else research.get(
                "sources",
                []
            )
        )

        signals = self._collect_signals(
            story,
            research,
            claims,
            sources
        )

        score = self._investigation_score(
            signals
        )

        level = self._level(
            score
        )

        questions = self._questions(
            story,
            research,
            claims,
            signals
        )

        actions = self._actions(
            level,
            signals,
            questions
        )

        priorities = self._priorities(
            claims,
            signals
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "INVESTIGATION_ASSESSMENT_COMPLETE",

            "investigation_score":
                score,

            "investigation_level":
                level,

            "signals":
                signals,

            "critical_questions":
                questions,

            "recommended_actions":
                actions,

            "claim_priorities":
                priorities,

            "publication_recommendation":
                self._publication_recommendation(
                    level
                )
        }

    # =====================================================
    # SIGNAL COLLECTION
    # =====================================================

    def _collect_signals(
        self,
        story: Dict[str, Any],
        research: Dict[str, Any],
        claims: List[Dict[str, Any]],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        contradictions = research.get(
            "contradictions",
            []
        )

        gaps = research.get(
            "research_gaps",
            []
        )

        duplicates = research.get(
            "duplicates",
            []
        )

        primary_sources = sum(
            1
            for source
            in sources
            if source.get(
                "primary"
            )
        )

        allegations = 0
        unsupported = 0

        for claim in claims:

            text = str(
                claim.get(
                    "text",
                    ""
                )
            ).lower()

            if any(
                term in text
                for term
                in {
                    "alleged",
                    "allegedly",
                    "accused",
                    "accusation"
                }
            ):

                allegations += 1

            if claim.get(
                "requires_verification",
                False
            ):

                unsupported += 1

        story_text = " ".join([

            str(
                story.get(
                    "title",
                    ""
                )
            ),

            str(
                story.get(
                    "topic",
                    ""
                )
            ),

            str(
                story.get(
                    "description",
                    ""
                )
            )
        ]).lower()

        high_risk = self._contains_terms(
            story_text,
            self.high_risk_terms
        )

        high_impact = self._contains_terms(
            story_text,
            self.high_impact_terms
        )

        breaking = bool(
            story.get(
                "breaking",
                False
            )
            or
            story.get(
                "is_breaking",
                False
            )
        )

        rapidly_changing = bool(
            story.get(
                "developing",
                False
            )
            or
            story.get(
                "rapidly_changing",
                False
            )
        )

        return {

            "source_count":
                len(
                    sources
                ),

            "primary_source_count":
                primary_sources,

            "contradiction_count":
                len(
                    contradictions
                ),

            "research_gap_count":
                len(
                    gaps
                ),

            "duplicate_group_count":
                len(
                    duplicates
                ),

            "allegation_count":
                allegations,

            "verification_required_count":
                unsupported,

            "high_risk_topic":
                high_risk,

            "high_impact_topic":
                high_impact,

            "breaking_story":
                breaking,

            "rapidly_changing":
                rapidly_changing
        }

    # =====================================================
    # SCORE
    # =====================================================

    def _investigation_score(
        self,
        signals: Dict[str, Any]
    ) -> int:

        score = 0

        contradictions = signals.get(
            "contradiction_count",
            0
        )

        gaps = signals.get(
            "research_gap_count",
            0
        )

        allegations = signals.get(
            "allegation_count",
            0
        )

        verification = signals.get(
            "verification_required_count",
            0
        )

        duplicates = signals.get(
            "duplicate_group_count",
            0
        )

        primary_sources = signals.get(
            "primary_source_count",
            0
        )

        if contradictions:

            score += min(
                contradictions * 15,
                35
            )

        if gaps:

            score += min(
                gaps * 5,
                20
            )

        if allegations:

            score += min(
                allegations * 10,
                25
            )

        if verification >= 5:

            score += 15

        elif verification >= 2:

            score += 8

        if duplicates:

            score += min(
                duplicates * 5,
                15
            )

        if primary_sources == 0:

            score += 15

        if signals.get(
            "high_risk_topic"
        ):

            score += 20

        if signals.get(
            "high_impact_topic"
        ):

            score += 15

        if signals.get(
            "breaking_story"
        ):

            score += 10

        if signals.get(
            "rapidly_changing"
        ):

            score += 15

        return min(
            100,
            score
        )

    # =====================================================
    # LEVEL
    # =====================================================

    def _level(
        self,
        score: int
    ) -> str:

        if score >= 80:

            return "URGENT"

        if score >= 60:

            return "DEEP"

        if score >= 35:

            return "STANDARD"

        if score >= 15:

            return "LIGHT"

        return "NONE"

    # =====================================================
    # QUESTIONS
    # =====================================================

    def _questions(
        self,
        story: Dict[str, Any],
        research: Dict[str, Any],
        claims: List[Dict[str, Any]],
        signals: Dict[str, Any]
    ) -> List[str]:

        questions = []

        gaps = research.get(
            "research_gaps",
            []
        )

        for gap in gaps:

            questions.append(
                str(
                    gap
                )
            )

        if signals.get(
            "primary_source_count",
            0
        ) == 0:

            questions.append(
                "Can the original or primary source of the information be located?"
            )

        if signals.get(
            "contradiction_count",
            0
        ) > 0:

            questions.append(
                "Which conflicting account is supported by stronger evidence?"
            )

            questions.append(
                "Are the conflicting reports actually independent?"
            )

        if signals.get(
            "duplicate_group_count",
            0
        ) > 0:

            questions.append(
                "Are multiple reports independently confirmed or merely repeating the same original report?"
            )

        if signals.get(
            "allegation_count",
            0
        ) > 0:

            questions.append(
                "What evidence exists for each allegation?"
            )

            questions.append(
                "Has the person or organization named in the allegation responded?"
            )

        if signals.get(
            "rapidly_changing",
            False
        ):

            questions.append(
                "What is confirmed now, and what remains developing?"
            )

        if not questions:

            questions.append(
                "No major unanswered research question was automatically detected."
            )

        return self._unique(
            questions
        )

    # =====================================================
    # ACTIONS
    # =====================================================

    def _actions(
        self,
        level: str,
        signals: Dict[str, Any],
        questions: List[str]
    ) -> List[Dict[str, Any]]:

        actions = []

        if level in {
            "DEEP",
            "URGENT"
        }:

            actions.append({

                "action":
                    "locate_primary_evidence",

                "priority":
                    "CRITICAL",

                "reason":
                    "High investigation score requires stronger evidence."
            })

            actions.append({

                "action":
                    "cross_check_independent_sources",

                "priority":
                    "CRITICAL",

                "reason":
                    "Do not treat repeated reporting as independent confirmation."
            })

        if signals.get(
            "contradiction_count",
            0
        ):

            actions.append({

                "action":
                    "resolve_conflicting_claims",

                "priority":
                    "HIGH",

                "reason":
                    "Conflicting claims were detected."
            })

        if signals.get(
            "allegation_count",
            0
        ):

            actions.append({

                "action":
                    "seek_response_from_subject",

                "priority":
                    "HIGH",

                "reason":
                    "The story contains allegations or accusations."
            })

        if signals.get(
            "rapidly_changing",
            False
        ):

            actions.append({

                "action":
                    "monitor_story_for_updates",

                "priority":
                    "HIGH",

                "reason":
                    "The story appears to be developing."
            })

        actions.append({

            "action":
                "run_claim_verification",

            "priority":
                "REQUIRED",

            "reason":
                "All material factual claims should pass verification."
        })

        actions.append({

            "action":
                "run_editorial_review",

            "priority":
                "REQUIRED",

            "reason":
                "Research findings must be evaluated before publication."
        })

        return actions

    # =====================================================
    # CLAIM PRIORITIES
    # =====================================================

    def _priorities(
        self,
        claims: List[Dict[str, Any]],
        signals: Dict[str, Any]
   
