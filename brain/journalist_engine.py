"""
AI NEWS FACTORY
JOURNALIST ENGINE

Purpose
-------
Convert verified newsroom intelligence into a structured
news article.

The Journalist Engine receives:

    - verified claims
    - source intelligence
    - story significance
    - editorial angle
    - story cluster
    - reader questions

It produces a newsroom-ready article plan.

IMPORTANT
---------
This engine must not invent facts.

Anything unsupported by the evidence should be marked as:
    UNKNOWN
    UNVERIFIED
    DISPUTED

The actual prose-generation model can consume this structured
plan later.

Editorial priorities:
    1. Accuracy
    2. Clarity
    3. Relevance
    4. Context
    5. Reader engagement
    6. Concision
    7. Transparency
"""

from typing import Any, Dict, List


# =========================================================
# JOURNALIST ENGINE
# =========================================================

class JournalistEngine:

    def __init__(self):

        self.name = "AI Journalist Engine"

        self.version = "1.0.0"

        self.required_sections = [
            "headline",
            "dek",
            "lead",
            "key_facts",
            "context",
            "why_it_matters",
            "what_happens_next",
            "what_is_unknown",
            "sources"
        ]

    # =====================================================
    # MAIN ARTICLE PLAN
    # =====================================================

    def create_article_plan(
        self,
        newsroom_package: Dict[str, Any]
    ) -> Dict[str, Any]:

        newsroom_package = (
            newsroom_package
            if isinstance(
                newsroom_package,
                dict
            )
            else {}
        )

        story = newsroom_package.get(
            "story",
            {}
        )

        significance = newsroom_package.get(
            "significance",
            {}
        )

        angles = newsroom_package.get(
            "angles",
            {}
        )

        verification = newsroom_package.get(
            "verification",
            {}
        )

        cluster = newsroom_package.get(
            "cluster",
            {}
        )

        if not isinstance(story, dict):
            story = {}

        if not isinstance(significance, dict):
            significance = {}

        if not isinstance(angles, dict):
            angles = {}

        if not isinstance(verification, dict):
            verification = {}

        if not isinstance(cluster, dict):
            cluster = {}

        primary_angle = angles.get(
            "primary_angle"
        ) or {}

        if not isinstance(
            primary_angle,
            dict
        ):
            primary_angle = {}

        verified_claims = verification.get(
            "claims",
            []
        )

        if not isinstance(
            verified_claims,
            list
        ):
            verified_claims = []

        safe_claims = self._safe_claims(
            verified_claims
        )

        unsupported_claims = self._unsafe_claims(
            verified_claims
        )

        article_structure = (
            self._build_structure(
                primary_angle,
                story,
                safe_claims,
                unsupported_claims
            )
        )

        editorial_notes = (
            self._editorial_notes(
                verification,
                significance,
                cluster
            )
        )

        return {
            "engine": self.name,

            "version": self.version,

            "status":
                self._article_status(
                    verification
                ),

            "article":
                article_structure,

            "editorial_notes":
                editorial_notes,

            "safe_claims":
                safe_claims,

            "excluded_claims":
                unsupported_claims,

            "writing_rules":
                self._writing_rules()
        }

    # =====================================================
    # SAFE CLAIMS
    # =====================================================

    def _safe_claims(
        self,
        claims: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        safe_statuses = {
            "CONFIRMED",
            "STRONGLY_SUPPORTED"
        }

        return [
            claim
            for claim in claims
            if isinstance(
                claim,
                dict
            )
            and claim.get(
                "status"
            ) in safe_statuses
        ]

    # =====================================================
    # UNSAFE CLAIMS
    # =====================================================

    def _unsafe_claims(
        self,
        claims: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        safe_statuses = {
            "CONFIRMED",
            "STRONGLY_SUPPORTED"
        }

        return [
            claim
            for claim in claims
            if isinstance(
                claim,
                dict
            )
            and claim.get(
                "status"
            ) not in safe_statuses
        ]

    # =====================================================
    # ARTICLE STRUCTURE
    # =====================================================

    def _build_structure(
        self,
        angle: Dict[str, Any],
        story: Dict[str, Any],
        safe_claims: List[Dict[str, Any]],
        unsafe_claims: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        angle_type = angle.get(
            "type",
            "WHAT_HAPPENED"
        )

        original = story.get(
            "original",
            {}
        )

        if not isinstance(
            original,
            dict
        ):
            original = {}

        title = original.get(
            "title",
            ""
        )

        source = original.get(
            "source",
            ""
        )

        return {

            "headline": {

                "purpose":
                    "Accurately communicate the most important development.",

                "must_include":
                    self._headline_requirements(
                        angle_type
                    ),

                "avoid": [
                    "false urgency",
                    "unsupported claims",
                    "manufactured controversy",
                    "clickbait that changes meaning",
                    "all-caps sensationalism"
                ]
            },

            "dek": {

                "purpose":
                    "Give the reader enough context to understand why the story matters."
            },

            "lead": {

                "purpose":
                    self._lead_instruction(
                        angle_type
                    ),

                "required_information":
                    self._lead_information(
                        safe_claims
                    )
            },

            "key_facts": {

                "purpose":
                    "Present the strongest verified facts first.",

                "facts":
                    [
                        claim.get(
                            "claim",
                            claim.get(
                                "text",
                                ""
                            )
                        )
                        for claim in safe_claims
                    ]
            },

            "context": {

                "purpose":
                    "Explain the background needed to understand the event."
            },

            "why_it_matters": {

                "purpose":
                    "Connect the confirmed development to reader relevance."
            },

            "what_happens_next": {

                "purpose":
                    "Explain confirmed next steps without presenting predictions as facts."
            },

            "what_is_unknown": {

                "purpose":
                    "Explicitly identify unresolved or unverified information.",

                "items":
                    [
                        claim.get(
                            "claim",
                            claim.get(
                                "text",
                                ""
                            )
                        )
                        for claim in unsafe_claims
                    ]
            },

            "sources": {

                "primary_source":
                    source,

                "source_count":
                    len(
                        safe_claims
                    )
            },

            "source_title":
                title
        }

    # =====================================================
    # HEADLINE REQUIREMENTS
    # =====================================================

    def _headline_requirements(
        self,
        angle_type: str
    ) -> List[str]:

        requirements = {

            "WHAT_HAPPENED": [

                "state the main event",

                "identify the relevant actor",

                "avoid unnecessary adjectives"
            ],

            "WHY_IT_MATTERS": [

                "state the important development",

                "signal its significance",

                "avoid exaggeration"
            ],

            "WHAT_IT_MEANS_FOR_PEOPLE": [

                "identify the affected audience",

                "make the practical consequence clear"
            ],

            "WHAT_CHANGES_NOW": [

                "identify the immediate change",

                "explain who or what is affected",

                "avoid unsupported predictions"
            ],

            "WHAT_HAPPENS_NEXT": [

                "identify the confirmed next step",

                "avoid presenting speculation as fact"
            ]
        }

        return requirements.get(
            angle_type,
            requirements[
                "WHAT_HAPPENED"
            ]
        )

    # =====================================================
    # LEAD INSTRUCTION
    # =====================================================

    def _lead_instruction(
        self,
        angle_type: str
    ) -> str:

        instructions = {

            "WHAT_HAPPENED":
                "Open with the most important confirmed development.",

            "WHY_IT_MATTERS":
                "Open with the confirmed development and immediately establish why it matters.",

            "WHAT_IT_MEANS_FOR_PEOPLE":
                "Open with the confirmed development and its practical relevance to affected people.",

            "WHAT_CHANGES_NOW":
                "Open with what has changed and identify the confirmed immediate effect.",

            "WHAT_HAPPENS_NEXT":
                "Open with the confirmed development and explain the next verified step."
        }

        return instructions.get(
            angle_type,
            instructions[
                "WHAT_HAPPENED"
            ]
        )

    # =====================================================
    # LEAD INFORMATION
    # =====================================================

    def _lead_information(
        self,
        claims: List[Dict[str, Any]]
    ) -> List[str]:

        information = []

        for claim in claims[:5]:

            if not isinstance(
                claim,
                dict
            ):
                continue

            text = claim.get(
                "claim",
                claim.get(
                    "text",
                    ""
                )
            )

            if text:

                information.append(
                    str(text)
                )

        return information

    # =====================================================
    # ARTICLE STATUS
    # =====================================================

    def _article_status(
        self,
        verification: Dict[str, Any]
    ) -> str:

        status = verification.get(
            "status"
        )

        if status:

            return str(
                status
            )

        claims = verification.get(
            "claims",
            []
        )

        if not claims:

            return "NEEDS_VERIFICATION"

        safe_claims = self._safe_claims(
            claims
        )

        if len(
            safe_claims
        ) == len(
            claims
        ):

            return "READY_FOR_EDITORIAL_REVIEW"

        if safe_claims:

            return "PARTIALLY_VERIFIED"

        return "NEEDS_VERIFICATION"

    # =====================================================
    # EDITORIAL NOTES
    # =====================================================

    def _editorial_notes(
        self,
        verification: Dict[str, Any],
        significance: Dict[str, Any],
        cluster: Dict[str, Any]
    ) -> List[str]:

        notes = []

        verification_status = verification.get(
            "status"
        )

        if verification_status:

            notes.append(
                "Verification status: "
                + str(
                    verification_status
                )
            )

        significance_level = significance.get(
            "level"
        )

        if significance_level:

            notes.append(
                "Story significance: "
                + str(
                    significance_level
                )
            )

        if verification.get(
            "disputed_claims"
        ):

            notes.append(
                "Review disputed claims before publication."
            )

        if verification.get(
            "unknowns"
        ):

            notes.append(
                "Review unresolved information before publication."
            )

        if cluster.get(
            "duplicate"
        ):

            notes.append(
                "Check whether this story duplicates an existing story cluster."
            )

        if not notes:

            notes.append(
                "Editorial review required before publication."
            )

        return notes

    # =====================================================
    # WRITING RULES
    # =====================================================

    def _writing_rules(
        self
    ) -> List[str]:

        return [

            "Do not invent facts.",

            "Use only information supported by the newsroom package.",

            "Clearly distinguish confirmed information from unverified information.",

            "Attribute claims when attribution is required.",

            "Avoid sensationalism.",

            "Avoid false certainty.",

            "Prefer clear and direct language.",

            "Preserve important context.",

            "Do not manufacture conflict.",

            "Do not turn speculation into fact.",

            "Do not hide important uncertainty.",

            "Prioritize accuracy over engagement."
        ]
