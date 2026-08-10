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

        primary_angle = angles.get(
            "primary_angle"
        ) or {}

        verified_claims = verification.get(
            "claims",
            []
        )

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

            "article": article_structure,

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
            if claim.get(
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
            if claim.get(
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
                        claim["claim"]
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
                        claim["claim"]
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
            }
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

            "WHAT_CHANGES_NOW":
