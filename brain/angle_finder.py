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
        # Developing story
        # -------------------------------------------------

        if urgency == "high":

            candidates.append({
                "type": "DEVELOPING_STORY",
                "title": (
                    "The latest confirmed developments"
                ),
                "purpose": (
                    "Focus on what has changed and what is confirmed now."
                )
            })

        # -------------------------------------------------
        # Impact angle
        # -------------------------------------------------

        if impact in {
            "high",
            "medium"
        }:

            candidates.append({
                "type": "IMPACT",
                "title": (
                    "Who is affected and how?"
                ),
                "purpose": (
                    "Identify the people, organizations or communities affected."
                )
            })

        return candidates

    # =====================================================
    # SCORE ANGLE
    # =====================================================

    def _score_angle(
        self,
        candidate: Dict[str, Any],
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        story_data = story.get(
            "story",
            {}
        )

        angle_type = candidate[
            "type"
        ]

        score = 0.0

        factors = {}

        # -------------------------------------------------
        # Reader usefulness
        # -------------------------------------------------

        usefulness = self._usefulness_score(
            angle_type,
            story_data
        )

        factors["reader_usefulness"] = usefulness

        # -------------------------------------------------
        # Information value
        # -------------------------------------------------

        information_value = (
            self._information_value(
                angle_type,
                story_data
            )
        )

        factors["information_value"] = (
            information_value
        )

        # -------------------------------------------------
        # Reader curiosity
        # -------------------------------------------------

        curiosity = (
            self._curiosity_score(
                angle_type,
                story_data
            )
        )

        factors["curiosity"] = curiosity

        # -------------------------------------------------
        # Evidence support
        # -------------------------------------------------

        evidence = (
            self._evidence_score(
                angle_type,
                story
            )
        )

        factors["evidence_support"] = evidence

        # -------------------------------------------------
        # Local relevance
        # -------------------------------------------------

        local_relevance = (
            self._local_relevance(
                angle_type,
                story_data
            )
        )

        factors["local_relevance"] = (
            local_relevance
        )

        # -------------------------------------------------
        # Misinformation risk
        # -------------------------------------------------

        risk = (
            self._risk_score(
                angle_type,
                story
            )
        )

        factors["misinformation_risk"] = risk

        # -------------------------------------------------
        # Final weighted score
        # -------------------------------------------------

        score += usefulness * 0.25
        score += information_value * 0.20
        score += curiosity * 0.15
        score += evidence * 0.25
        score += local_relevance * 0.05

        # Risk is a penalty.

        score -= risk * 0.10

        score = max(
            0,
            min(
                round(score, 2),
                100
            )
        )

        return {
            **candidate,

            "total_score": score,

            "factors": factors,

            "decision":
                self._angle_decision(
                    score
                )
        }

    # =====================================================
    # USEFULNESS
    # =====================================================

    def _usefulness_score(
        self,
        angle_type: str,
        story_data: Dict[str, Any]
    ) -> float:

        high_value = {
            "WHY_IT_MATTERS": 95,
            "WHAT_IT_MEANS_FOR_PEOPLE": 98,
            "WHAT_CHANGES_NOW": 96,
            "WHAT_HAPPENS_NEXT": 90,
            "EXPLAINER": 94,
            "IMPACT": 93,
            "WHAT_IS_UNKNOWN": 91
        }

        return high_value.get(
            angle_type,
            75
        )

    # =====================================================
    # INFORMATION VALUE
    # =====================================================

    def _information_value(
        self,
        angle_type: str,
        story_data: Dict[str, Any]
    ) -> float:

        values = {
            "WHAT_HAPPENED": 85,
            "WHY_IT_MATTERS": 95,
            "WHAT_IT_MEANS_FOR_PEOPLE": 98,
            "WHAT_CHANGES_NOW": 96,
            "WHAT_HAPPENS_NEXT": 88,
            "EXPLAINER": 95,
            "CONTEXT": 92,
            "TIMELINE": 87,
            "WHAT_IS_UNKNOWN": 90,
            "IMPACT": 94
        }

        return values.get(
            angle_type,
            70
        )

    # =====================================================
    # CURIOSITY
    # =====================================================

    def _curiosity_score(
        self,
        angle_type: str,
        story_data: Dict[str, Any]
    ) -> float:

        scores = {
            "WHY_IT_MATTERS": 95,
            "WHAT_HAPPENS_NEXT": 97,
            "WHAT_CHANGES_NOW": 94,
            "WHAT_IT_MEANS_FOR_PEOPLE": 92,
            "WHAT_IS_UNKNOWN": 96,
            "CONSEQUENCES": 94,
            "TIMELINE": 82,
            "EXPLAINER": 86,
            "WHAT_HAPPENED": 70
        }

        return scores.get(
            angle_type,
            70
        )

    # =====================================================
    # EVIDENCE SUPPORT
    # =====================================================

    def _evidence_score(
        self,
        angle_type: str,
        story: Dict[str, Any]
    ) -> float:

        source_intelligence = story.get(
            "source_intelligence"
        )

        if not source_intelligence:
            return 45

        source_score = source_intelligence.get(
            "score",
            45
        )

        # Angles that require speculation receive less
        # evidence confidence.

        if angle_type in {
            "CONSEQUENCES",
            "WHAT_HAPPENS_NEXT"
        }:
            return max(
                20,
                source_score - 15
            )

        return source_score

    # =====================================================
    # LOCAL RELEVANCE
    # =====================================================

    def _local_relevance(
        self,
        angle_type: str,
        story_data: Dict[str, Any]
    ) -> float:

        locations = story_data.get(
            "locations",
            []
        )

        if angle_type != "LOCAL_ANGLE":
            return 60

        if not locations:
            return 20

        nigeria_locations = {
            "Nigeria",
            "Lagos",
            "Abuja",
            "Port Harcourt",
            "Kano",
            "Rivers",
            "Akwa Ibom"
        }

        if any(
            location in nigeria_locations
            for location in locations
        ):
            return 100

        return 70

    # =====================================================
    # MISINFORMATION RISK
    # =====================================================

    def _risk_score(
        self,
        angle_type: str,
        story: Dict[str, Any]
    ) -> float:

        risk = 20

        story_data = story.get(
            "story",
            {}
        )

        if story_data.get(
            "urgency"
        ) == "high":

            risk += 10

        if angle_type in {
            "CONSEQUENCES",
            "WHAT_HAPPENS_NEXT"
        }:

            risk += 15

        source_intelligence = story.get(
            "source_intelligence"
        )

        if source_intelligence:

            source_score = source_intelligence.get(
                "score",
                40
            )

            if source_score < 50:
                risk += 25

        return min(
            risk,
            100
        )

    # =====================================================
    # DECISION
    # =====================================================

    def _angle_decision(
        self,
        score: float
    ) -> str:

        if score >= 85:
            return "STRONG_PRIMARY_ANGLE"

        if score >= 70:
            return "GOOD_ANGLE"

        if score >= 55:
            return "SECONDARY_ANGLE"

        return "WEAK_ANGLE"

    # =====================================================
    # EDITORIAL INSTRUCTION
    # =====================================================

    def _build_editorial_instruction(
        self,
        selected: Dict[str, Any]
    ) -> str:

        if not selected:
            return (
                "No reliable editorial angle was identified. "
                "Do not proceed to publication."
            )

        angle_type = selected[
            "type"
        ]

        instructions = {

            "WHAT_HAPPENED":
                "Lead with the confirmed event and establish the essential facts.",

            "WHY_IT_MATTERS":
                "Lead with the significance of the development and explain its consequences.",

            "WHAT_IT_MEANS_FOR_PEOPLE":
                "Translate the development into practical consequences for readers.",

            "WHAT_CHANGES_NOW":
                "Clearly explain what changes immediately and who is affected.",

            "WHAT_HAPPENS_NEXT":
                "Explain the confirmed next steps while clearly separating facts from forecasts.",

            "EXPLAINER":
                "Make the complicated parts simple without removing important nuance.",

            "CONTEXT":
                "Give readers the background they need to understand the current development.",

            "TIMELINE":
                "Build a clear chronological sequence showing how the story developed.",

            "WHAT_IS_UNKNOWN":
                "Clearly separate verified facts from unresolved claims and unknowns.",

            "IMPACT":
                "Focus on the people, organizations or communities most affected.",

            "LOCAL_ANGLE":
                "Explain the local relevance without forcing a geographic connection.",

            "CONSEQUENCES":
                "Discuss supported consequences while labeling uncertainty clearly.",

            "DEVELOPING_STORY":
                "Prioritize the newest confirmed development and identify what remains
