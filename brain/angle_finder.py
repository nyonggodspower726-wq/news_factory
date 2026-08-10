"""
AI NEWS FACTORY
Editorial Angle Intelligence Engine

Purpose
-------
Find the strongest legitimate editorial angle for a news story.

The engine does not simply ask:
    "What headline sounds exciting?"

It asks:
    "What is the most useful, interesting, defensible and
     reader-relevant way to explain this story?"

Pipeline:

RAW STORY
    ↓
UNDERSTAND THE EVENT
    ↓
IDENTIFY INFORMATION GAPS
    ↓
IDENTIFY READER QUESTIONS
    ↓
GENERATE POSSIBLE ANGLES
    ↓
SCORE EACH ANGLE
    ↓
CHECK EVIDENCE SUPPORT
    ↓
CHECK MISLEADING POTENTIAL
    ↓
SELECT PRIMARY ANGLE
    ↓
CREATE BACKUP ANGLES

The AI/LLM layer can later use this structured output to
perform deeper reasoning.
"""

from typing import Any, Dict, List


class AngleFinder:

    def __init__(self):
        self.name = "Editorial Angle Intelligence Engine"
        self.version = "1.0.0"

        self.angle_types = [
            "WHAT_HAPPENED",
            "WHY_IT_MATTERS",
            "WHAT_IT_MEANS_FOR_PEOPLE",
            "WHAT_CHANGES_NOW",
            "WHAT_HAPPENS_NEXT",
            "EXPLAINER",
            "TIMELINE",
            "IMPACT",
            "CONTEXT",
            "KEY_QUESTIONS",
            "WHAT_IS_UNKNOWN",
            "LOCAL_ANGLE",
            "CONSEQUENCES",
            "DEVELOPING_STORY"
        ]

    # =====================================================
    # MAIN ENGINE
    # =====================================================

    def find_angles(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate, evaluate and rank editorial angles.
        """

        story_data = story.get(
            "story",
            {}
        )

        original = story.get(
            "original",
            {}
        )

        title = original.get(
            "title",
            ""
        )

        summary = story_data.get(
            "summary",
            ""
        )

        story_type = story_data.get(
            "story_type",
            "general"
        )

        urgency = story_data.get(
            "urgency",
            "normal"
        )

        impact = story_data.get(
            "initial_impact",
            "low"
        )

        locations = story_data.get(
            "locations",
            []
        )

        reader_questions = story_data.get(
            "reader_questions",
            []
        )

        keywords = story_data.get(
            "keywords",
            []
        )

        candidates = self._generate_candidates(
            title=title,
            summary=summary,
            story_type=story_type,
            urgency=urgency,
            impact=impact,
            locations=locations,
            reader_questions=reader_questions,
            keywords=keywords
        )

        scored_angles = []

        for candidate in candidates:

            scored = self._score_angle(
                candidate,
                story
            )

            scored_angles.append(
                scored
            )

        scored_angles.sort(
            key=lambda item: item["total_score"],
            reverse=True
        )

        selected = (
            scored_angles[0]
            if scored_angles
            else None
        )

        backup_angles = (
            scored_angles[1:4]
            if len(scored_angles) > 1
            else []
        )

        return {
            "engine": self.name,
            "version": self.version,

            "primary_angle": selected,

            "backup_angles": backup_angles,

            "all_angles": scored_angles,

            "editorial_instruction":
                self._build_editorial_instruction(
                    selected
                )
        }

    # =====================================================
    # GENERATE CANDIDATE ANGLES
    # =====================================================

    def _generate_candidates(
        self,
        title: str,
        summary: str,
        story_type: str,
        urgency: str,
        impact: str,
        locations: List[str],
        reader_questions: List[str],
        keywords: List[str]
    ) -> List[Dict[str, Any]]:

        candidates = []

        # -------------------------------------------------
        # Basic event angle
        # -------------------------------------------------

        candidates.append({
            "type": "WHAT_HAPPENED",
            "title": "What actually happened?",
            "purpose": (
                "Clearly establish the confirmed event."
            )
        })

        # -------------------------------------------------
        # Why it matters
        # -------------------------------------------------

        candidates.append({
            "type": "WHY_IT_MATTERS",
            "title": "Why this story matters",
            "purpose": (
                "Explain the significance beyond the announcement."
            )
        })

        # -------------------------------------------------
        # Reader impact
        # -------------------------------------------------

        candidates.append({
            "type": "WHAT_IT_MEANS_FOR_PEOPLE",
            "title": (
                "What this means for ordinary people"
            ),
            "purpose": (
                "Translate the event into practical reader impact."
            )
        })

        # -------------------------------------------------
        # Immediate change
        # -------------------------------------------------

        candidates.append({
            "type": "WHAT_CHANGES_NOW",
            "title": (
                "What changes now?"
            ),
            "purpose": (
                "Identify immediate consequences or changes."
            )
        })

        # -------------------------------------------------
        # Future development
        # -------------------------------------------------

        candidates.append({
            "type": "WHAT_HAPPENS_NEXT",
            "title": (
                "What happens next?"
            ),
            "purpose": (
                "Explain the likely next stages using confirmed information."
            )
        })

        # -------------------------------------------------
        # Explainer
        # -------------------------------------------------

        candidates.append({
            "type": "EXPLAINER",
            "title": (
                "The story explained"
            ),
            "purpose": (
                "Make a complicated event understandable."
            )
        })

        # -------------------------------------------------
        # Context
        # -------------------------------------------------

        candidates.append({
            "type": "CONTEXT",
            "title": (
                "The context behind the story"
            ),
            "purpose": (
                "Provide essential background needed to understand the event."
            )
        })

        # -------------------------------------------------
        # Timeline
        # -------------------------------------------------

        candidates.append({
            "type": "TIMELINE",
            "title": (
                "How we got here"
            ),
            "purpose": (
                "Reconstruct the important sequence of events."
            )
        })

        # -------------------------------------------------
        # Unknown information
        # -------------------------------------------------

        candidates.append({
            "type": "WHAT_IS_UNKNOWN",
            "title": (
                "What we still don't know"
            ),
            "purpose": (
                "Separate confirmed information from unresolved claims."
            )
        })

        # -------------------------------------------------
        # Consequences
        # -------------------------------------------------

        candidates.append({
            "type": "CONSEQUENCES",
            "title": (
                "What could happen as a result"
            ),
            "purpose": (
                "Explore supported consequences without presenting speculation as fact."
            )
        })

        # -------------------------------------------------
        # Local angle
        # -------------------------------------------------

        if locations:

            candidates.append({
                "type": "LOCAL_ANGLE",
                "title": (
                    "What this means locally"
                ),
                "purpose": (
                    "Connect the story to the affected geographic audience."
                )
            })

        # -------------------------------------------------
        # Developing
