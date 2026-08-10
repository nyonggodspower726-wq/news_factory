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

from typing import Any, Dict, List, Optional


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
    # =====================================================
    # EVIDENCE SUPPORT
    # =====================================================

    def _evidence_score(
        self,
        angle_type: str,
        story: Dict[str, Any]
    ) -> float:

        story_data = story.get(
            "story",
            {}
        )

        evidence_items = story_data.get(
            "evidence",
            []
        )

        claims = story_data.get(
            "claims",
            []
        )

        # Angles that normally require less
        # interpretation receive stronger baseline support.

        baseline = {
            "WHAT_HAPPENED": 92,
            "TIMELINE": 88,
            "WHAT_IS_UNKNOWN": 90,
            "EXPLAINER": 84,
            "CONTEXT": 82,
            "WHY_IT_MATTERS": 78,
            "WHAT_IT_MEANS_FOR_PEOPLE": 76,
            "WHAT_CHANGES_NOW": 80,
            "WHAT_HAPPENS_NEXT": 68,
            "CONSEQUENCES": 65,
            "LOCAL_ANGLE": 72,
            "IMPACT": 80,
            "DEVELOPING_STORY": 88
        }

        score = baseline.get(
            angle_type,
            70
        )

        if evidence_items:
            score += min(
                len(evidence_items) * 2,
                10
            )

        if claims:
            score += min(
                len(claims),
                5
            )

        return min(
            score,
            100
        )

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

        if angle_type == "LOCAL_ANGLE":

            if locations:
                return 100

            return 20

        if locations:
            return 75

        return 50

    # =====================================================
    # MISINFORMATION RISK
    # =====================================================

    def _risk_score(
        self,
        angle_type: str,
        story: Dict[str, Any]
    ) -> float:

        story_data = story.get(
            "story",
            {}
        )

        uncertainty = story_data.get(
            "uncertainty",
            "normal"
        )

        risk = {
            "WHAT_HAPPENED": 15,
            "WHY_IT_MATTERS": 25,
            "WHAT_IT_MEANS_FOR_PEOPLE": 30,
            "WHAT_CHANGES_NOW": 25,
            "WHAT_HAPPENS_NEXT": 40,
            "EXPLAINER": 20,
            "TIMELINE": 15,
            "CONTEXT": 20,
            "WHAT_IS_UNKNOWN": 10,
            "CONSEQUENCES": 45,
            "LOCAL_ANGLE": 25,
            "IMPACT": 30,
            "DEVELOPING_STORY": 20
        }

        value = risk.get(
            angle_type,
            30
        )

        if uncertainty in {
            "high",
            "very_high"
        }:

            value += 15

        return min(
            value,
            100
        )

    # =====================================================
    # ANGLE DECISION
    # =====================================================

    def _angle_decision(
        self,
        score: float
    ) -> str:

        if score >= 85:
            return "STRONG_PRIMARY"

        if score >= 75:
            return "STRONG_BACKUP"

        if score >= 65:
            return "USABLE"

        if score >= 50:
            return "WEAK"

        return "REJECT"

    # =====================================================
    # EDITORIAL INSTRUCTION
    # =====================================================

    def _build_editorial_instruction(
        self,
        selected: Any
    ) -> str:

        if not selected:
            return (
                "No sufficiently supported editorial angle "
                "was identified. Return to evidence gathering."
            )

        angle_type = selected.get(
            "type",
            "WHAT_HAPPENED"
        )

        instructions = {

            "WHAT_HAPPENED":
                "Lead with the confirmed facts. "
                "Do not add unsupported interpretation.",

            "WHY_IT_MATTERS":
                "Explain the significance of the event "
                "and why readers should care.",

            "WHAT_IT_MEANS_FOR_PEOPLE":
                "Translate the confirmed development "
                "into practical reader consequences.",

            "WHAT_CHANGES_NOW":
                "Focus on confirmed immediate changes "
                "rather than speculation.",

            "WHAT_HAPPENS_NEXT":
                "Explain confirmed next steps and clearly "
                "label anything that remains uncertain.",

            "EXPLAINER":
                "Explain the underlying issue in simple "
                "language and provide the necessary context.",

            "TIMELINE":
                "Organize the story chronologically and "
                "separate confirmed events from disputed claims.",

            "IMPACT":
                "Identify who is affected, how they are "
                "affected, and what evidence supports that assessment.",

            "CONTEXT":
                "Provide only background information that "
                "helps readers understand the current development.",

            "WHAT_IS_UNKNOWN":
                "Clearly identify unresolved questions "
                "and avoid filling information gaps with assumptions.",

            "LOCAL_ANGLE":
                "Connect the confirmed development to the "
                "affected location or local audience.",

            "CONSEQUENCES":
                "Discuss supported consequences while "
                "clearly separating possibilities from confirmed outcomes.",

            "DEVELOPING_STORY":
                "Prioritize the newest confirmed development "
                "and identify what remains unresolved."
        }

        return instructions.get(
            angle_type,
            instructions["WHAT_HAPPENED"]
        )

    # =====================================================
    # PRIMARY ANGLE
    # =====================================================

    def get_primary_angle(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        result = self.find_angles(
            story
        )

        return result.get(
            "primary_angle"
        )

    # =====================================================
    # BACKUP ANGLES
    # =====================================================

    def get_backup_angles(
        self,
        story: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        result = self.find_angles(
            story
        )

        return result.get(
            "backup_angles",
            []
        )

    # =====================================================
    # ANGLE TYPES
    # =====================================================

    def get_angle_types(
        self
    ) -> List[str]:

        return list(
            self.angle_types
        )

    # =====================================================
    # ANGLE VALIDATION
    # =====================================================

    def validate_angle(
        self,
        angle: Dict[str, Any]
    ) -> Dict[str, Any]:

        if not isinstance(
            angle,
            dict
        ):

            return {
                "valid": False,
                "reason": "Angle must be a dictionary."
            }

        required_fields = [
            "type",
            "title",
            "purpose",
            "total_score"
        ]

        missing = [
            field
            for field in required_fields
            if field not in angle
        ]

        if missing:

            return {
                "valid": False,
                "reason": (
                    "Missing required fields: "
                    + ", ".join(missing)
                )
            }

        if angle["type"] not in self.angle_types:

            return {
                "valid": False,
                "reason": (
                    "Unknown angle type: "
                    + str(angle["type"])
                )
            }

        return {
            "valid": True,
            "reason": "Angle is valid."
        }

    # =====================================================
    # FILTER ACCEPTABLE ANGLES
    # =====================================================

    def filter_acceptable_angles(
        self,
        angles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        acceptable = []

        for angle in angles:

            validation = self.validate_angle(
                angle
            )

            if not validation["valid"]:
                continue

            if angle.get(
                "decision"
            ) == "REJECT":

                continue

            acceptable.append(
                angle
            )

        acceptable.sort(
            key=lambda item: item.get(
                "total_score",
                0
            ),
            reverse=True
        )

        return acceptable

    # =====================================================
    # SELECT SAFEST PRIMARY ANGLE
    # =====================================================

    def select_safest_angle(
        self,
        angles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        acceptable = (
            self.filter_acceptable_angles(
                angles
            )
        )

        if not acceptable:

            return {
                "type": "WHAT_HAPPENED",
                "title": "What actually happened?",
                "purpose": (
                    "Focus only on confirmed information."
                ),
                "total_score": 0,
                "decision": "FALLBACK"
            }

        # Prefer a high-scoring angle with
        # strong evidence support.

        acceptable.sort(
            key=lambda item: (
                item.get(
                    "factors",
                    {}
                ).get(
                    "evidence_support",
                    0
                ),
                item.get(
                    "total_score",
                    0
                )
            ),
            reverse=True
        )

        return acceptable[0]

    # =====================================================
    # CREATE ANGLE SUMMARY
    # =====================================================

    def create_summary(
        self,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:

        primary = result.get(
            "primary_angle"
        )

        if not primary:

            return {
                "primary_type": None,
                "primary_title": None,
                "score": 0,
                "editorial_instruction":
                    result.get(
                        "editorial_instruction",
                        ""
                    )
            }

        return {
            "primary_type":
                primary.get(
                    "type"
                ),

            "primary_title":
                primary.get(
                    "title"
                ),

            "score":
                primary.get(
                    "total_score",
                    0
                ),

            "decision":
                primary.get(
                    "decision"
                ),

            "editorial_instruction":
                result.get(
                    "editorial_instruction",
                    ""
                )
        }

    # =====================================================
    # PIPELINE INTERFACE
    # =====================================================

    def analyze(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        result = self.find_angles(
            story
        )

        result["summary"] = (
            self.create_summary(
                result
            )
        )

        return result

    # =====================================================
    # SIMPLE CALL INTERFACE
    # =====================================================

    def run(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        return self.analyze(
            story
        )
    # =====================================================
    # BATCH ANALYSIS
    # =====================================================

    def analyze_many(
        self,
        stories: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        results = []

        for story in stories:

            try:
                result = self.analyze(
                    story
                )

                results.append(
                    result
                )

            except Exception as exc:

                results.append(
                    {
                        "success": False,
                        "error": str(exc),
                        "story": story
                    }
                )

        return results

    # =====================================================
    # BEST ANGLE FROM MULTIPLE STORIES
    # =====================================================

    def best_angle_from_stories(
        self,
        stories: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:

        results = self.analyze_many(
            stories
        )

        candidates = []

        for result in results:

            primary = result.get(
                "primary_angle"
            )

            if primary:
                candidates.append(
                    primary
                )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: item.get(
                "total_score",
                0
            ),
            reverse=True
        )

        return candidates[0]

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(
        self
    ) -> Dict[str, Any]:

        return {
            "engine": "AngleFinder",
            "status": "ready",
            "angle_types": len(
                self.angle_types
            ),
            "minimum_score":
                self.minimum_score
        }


# =========================================================
# DEFAULT ENGINE INSTANCE
# =========================================================

angle_finder = AngleFinder()


# =========================================================
# MODULE-LEVEL HELPERS
# =========================================================

def find_angles(
    story: Dict[str, Any]
) -> Dict[str, Any]:

    return angle_finder.find_angles(
        story
    )


def analyze(
    story: Dict[str, Any]
) -> Dict[str, Any]:

    return angle_finder.analyze(
        story
    )


def run(
    story: Dict[str, Any]
) -> Dict[str, Any]:

    return angle_finder.run(
        story
    )


def get_primary_angle(
    story: Dict[str, Any]
) -> Optional[Dict[str, Any]]:

    return angle_finder.get_primary_angle(
        story
    )


def get_backup_angles(
    story: Dict[str, Any]
) -> List[Dict[str, Any]]:

    return angle_finder.get_backup_angles(
        story
    )


# =========================================================
# PUBLIC EXPORTS
# =========================================================

__all__ = [
    "AngleFinder",
    "angle_finder",
    "find_angles",
    "analyze",
    "run",
    "get_primary_angle",
    "get_backup_angles",
]


# =========================================================
# DIRECT TEST
# =========================================================

if __name__ == "__main__":

    test_story = {
        "story": {
            "title": "Example News Story",
            "summary": (
                "An example confirmed development "
                "has occurred."
            ),
            "evidence": [
                "Confirmed source A",
                "Confirmed source B"
            ],
            "claims": [
                "Example confirmed claim"
            ],
            "locations": [],
            "uncertainty": "normal"
        }
    }

    try:

        result = angle_finder.analyze(
            test_story
        )

        print(
            "\nANGLE FINDER TEST"
        )

        print(
            "Status:",
            result.get(
                "status",
                "unknown"
            )
        )

        primary = result.get(
            "primary_angle"
        )

        if primary:

            print(
                "Primary angle:",
                primary.get(
                    "type"
                )
            )

            print(
                "Title:",
                primary.get(
                    "title"
                )
            )

            print(
                "Score:",
                primary.get(
                    "total_score"
                )
            )

        print(
            "Health:",
            angle_finder.health_check()
        )

    except Exception as exc:

        print(
            "AngleFinder test failed:",
            str(exc)
        )
