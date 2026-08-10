"""
AI NEWS FACTORY
FACT CHECKING & CLAIM VERIFICATION ENGINE

Purpose
-------
Turn a news story into individual claims and evaluate each
claim against available evidence.

The engine separates:

    CONFIRMED
    STRONGLY_SUPPORTED
    PARTIALLY_SUPPORTED
    UNVERIFIED
    DISPUTED
    CONTRADICTED

IMPORTANT
---------
This engine never treats popularity as proof.

A claim repeated by 50 social-media accounts can still be
UNVERIFIED if those accounts all copied the same original
claim.

Independent source diversity matters.

The final publication pipeline should require this engine
to pass before automatic publication.
"""

import re
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Set


class FactChecker:

    def __init__(self):

        self.name = "Fact Verification Engine"
        self.version = "1.0.0"

        self.minimum_publish_score = 75

        self.high_risk_terms = {
            "allegedly",
            "rumor",
            "rumour",
            "unconfirmed",
            "reportedly",
            "claims",
            "supposedly",
            "possibly",
            "may have",
            "might have",
            "viral",
            "leaked"
        }

    # =====================================================
    # MAIN CHECK
    # =====================================================

    def verify_story(
        self,
        story: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        claims = self.extract_claims(
            story
        )

        verified_claims = []

        for claim in claims:

            result = self.verify_claim(
                claim,
                sources
            )

            verified_claims.append(
                result
            )

        summary = self._build_summary(
            verified_claims
        )

        publication_status = (
            self._publication_status(
                verified_claims
            )
        )

        return {
            "engine": self.name,
            "version": self.version,

            "story_id":
                self._story_id(
                    story
                ),

            "claims":
                verified_claims,

            "summary":
                summary,

            "publication_status":
                publication_status,

            "checked_at":
                datetime.utcnow().isoformat()
        }

    # =====================================================
    # CLAIM EXTRACTION
    # =====================================================

    def extract_claims(
        self,
        story: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        """
        Extract potentially factual statements.

        This is deliberately conservative. A production LLM
        can later replace/augment this method while keeping
        the same output structure.
        """

        content = (
            story.get(
                "content",
                ""
            )
            or
            story.get(
                "description",
                ""
            )
            or
            story.get(
                "title",
                ""
            )
        )

        sentences = re.split(
            r"(?<=[.!?])\s+",
            content.strip()
        )

        claims = []

        for sentence in sentences:

            sentence = sentence.strip()

            if len(sentence) < 20:
                continue

            # Skip obvious questions.
            if sentence.endswith("?"):
                continue

            claims.append({
                "claim_id":
                    self._claim_id(
                        sentence
                    ),

                "text":
                    sentence,

                "risk":
                    self._claim_risk(
                        sentence
                    )
            })

        return claims

    # =====================================================
    # VERIFY ONE CLAIM
    # =====================================================

    def verify_claim(
        self,
        claim: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        claim_text = claim[
            "text"
        ]

        supporting_sources = []
        contradicting_sources = []

        for source in sources:

            source_text = self._source_text(
                source
            )

            relationship = (
                self._compare_claim_to_source(
                    claim_text,
                    source_text
                )
            )

            if relationship == "SUPPORTS":

                supporting_sources.append(
                    source
                )

            elif relationship == "CONTRADICTS":

                contradicting_sources.append(
                    source
                )

        independent_support = (
            self._independent_sources(
                supporting_sources
            )
        )

        independent_contradiction = (
            self._independent_sources(
                contradicting_sources
            )
        )

        score = self._calculate_claim_score(
            claim,
            independent_support,
            independent_contradiction
        )

        status = self._classify_claim(
            score,
            independent_support,
            independent_contradiction
        )

        return {
            "claim_id":
                claim["claim_id"],

            "claim":
                claim_text,

            "risk":
                claim["risk"],

            "verification_score":
                score,

            "status":
                status,

            "supporting_sources":
                self._source_labels(
                    supporting_sources
                ),

            "contradicting_sources":
                self._source_labels(
                    contradicting_sources
                ),

            "independent_support_count":
                len(independent_support),

            "independent_contradiction_count":
                len(independent_contradiction),

            "publication_safe":
                status in {
                    "CONFIRMED",
                    "STRONGLY_SUPPORTED"
                }
        }

    # =====================================================
    # SOURCE TEXT
    # =====================================================

    def _source_text(
        self,
        source: Dict[str, Any]
    ) -> str:

        return " ".join([
            str(
                source.get(
                    "title",
                    ""
                )
            ),

            str(
                source.get(
                    "description",
                    ""
                )
            ),

            str(
                source.get(
                    "content",
                    ""
                )
            )
        ]).lower()

    # =====================================================
    # CLAIM / SOURCE COMPARISON
    # =====================================================

    def _compare_claim_to_source(
        self,
        claim: str,
        source_text: str
    ) -> str:

        claim_tokens = self._tokens(
            claim
        )

        source_tokens = self._tokens(
            source_text
        )

        if not claim_tokens:
            return "UNKNOWN"

        overlap = (
            len(
                claim_tokens
                &
                source_tokens
            )
            /
            len(
                claim_tokens
            )
        )

        # This deterministic layer is intentionally
        # conservative. It does not claim semantic certainty.

        if overlap >= 0.70:
            return "SUPPORTS"

        return "UNKNOWN"

    # =====================================================
    # INDEPENDENT SOURCES
    # =====================================================

    def _independent_sources(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        seen_domains: Set[str] = set()

        independent = []

        for source in sources:

            domain = (
                source.get(
                    "domain"
                )
                or
                source.get(
                    "source"
                )
                or
                "unknown"
            )

            domain = str(
                domain
            ).lower()

            if domain in seen_domains:
                continue

            seen_domains.add(
                domain
            )

            independent.append(
                source
            )

        return independent

    # =====================================================
    # CLAIM SCORE
    # =====================================================

    def _calculate_claim_score(
        self,
        claim: Dict[str, Any],
        supporting: List[Dict[str, Any]],
        contradicting: List[Dict[str, Any]]
    ) -> int:

        score = 20

        # Independent corroboration.
        score += min(
            len(supporting) * 20,
            60
        )

        # Contradictions are a serious penalty.
        score -= min(
            len(contradicting) * 30,
            60
        )

        # Risky wording lowers confidence.
        if claim.get(
            "risk"
        ) == "HIGH":

            score -= 15

        return max(
            0,
            min(
                score,
                100
            )
        )

    # =====================================================
    # CLAIM CLASSIFICATION
    # =====================================================

    def _classify_claim(
        self,
        score: int,
        supporting: List[Dict[str, Any]],
        contradicting: List[Dict[str, Any]]
    ) -> str:

        if contradicting and score < 50:
            return "CONTRADICTED"

        if (
            len(supporting) >= 3
            and score >= 80
        ):
            return "CONFIRMED"

        if (
            len(supporting) >= 2
            and score >= 60
        ):
            return "STRONGLY_SUPPORTED"

        if (
            len(supporting) >= 1
            and score >= 40
        ):
            return "PARTIALLY_SUPPORTED"

        if contradicting:
            return "DISPUTED"

        return "UNVERIFIED"
