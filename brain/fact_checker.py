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
    # =====================================================
    # SUMMARY
    # =====================================================

    def _build_summary(
        self,
        claims: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        counts = {
            "CONFIRMED": 0,
            "STRONGLY_SUPPORTED": 0,
            "PARTIALLY_SUPPORTED": 0,
            "UNVERIFIED": 0,
            "DISPUTED": 0,
            "CONTRADICTED": 0
        }

        for claim in claims:

            status = claim.get(
                "status",
                "UNVERIFIED"
            )

            if status not in counts:
                status = "UNVERIFIED"

            counts[
                status
            ] += 1

        total = len(
            claims
        )

        if total:

            average_score = round(
                sum(
                    claim.get(
                        "verification_score",
                        0
                    )
                    for claim
                    in claims
                )
                /
                total,
                2
            )

        else:

            average_score = 0

        return {
            "total_claims":
                total,

            "confirmed":
                counts[
                    "CONFIRMED"
                ],

            "strongly_supported":
                counts[
                    "STRONGLY_SUPPORTED"
                ],

            "partially_supported":
                counts[
                    "PARTIALLY_SUPPORTED"
                ],

            "unverified":
                counts[
                    "UNVERIFIED"
                ],

            "disputed":
                counts[
                    "DISPUTED"
                ],

            "contradicted":
                counts[
                    "CONTRADICTED"
                ],

            "average_verification_score":
                average_score,

            "all_claims_safe":
                (
                    total > 0
                    and
                    counts["CONTRADICTED"] == 0
                    and
                    counts["DISPUTED"] == 0
                    and
                    counts["UNVERIFIED"] == 0
                )
        }

    # =====================================================
    # PUBLICATION STATUS
    # =====================================================

    def _publication_status(
        self,
        claims: List[Dict[str, Any]]
    ) -> str:

        if not claims:
            return "NO_CLAIMS_TO_VERIFY"

        statuses = {
            claim.get(
                "status",
                "UNVERIFIED"
            )
            for claim
            in claims
        }

        if "CONTRADICTED" in statuses:
            return "BLOCK_PUBLICATION"

        if "DISPUTED" in statuses:
            return "HUMAN_REVIEW_REQUIRED"

        if "UNVERIFIED" in statuses:
            return "HUMAN_REVIEW_REQUIRED"

        scores = [
            claim.get(
                "verification_score",
                0
            )
            for claim
            in claims
        ]

        average_score = (
            sum(scores)
            /
            len(scores)
        )

        if average_score < self.minimum_publish_score:
            return "HUMAN_REVIEW_REQUIRED"

        if any(
            claim.get(
                "risk"
            ) == "HIGH"
            for claim
            in claims
        ):

            return "HUMAN_REVIEW_REQUIRED"

        return "SAFE_FOR_EDITORIAL_PIPELINE"

    # =====================================================
    # CLAIM RISK
    # =====================================================

    def _claim_risk(
        self,
        text: str
    ) -> str:

        lowered = str(
            text
        ).lower()

        for term in self.high_risk_terms:

            if term in lowered:
                return "HIGH"

        # Claims containing numbers, percentages,
        # money, dates or named organizations deserve
        # additional attention.
        if re.search(
            r"\d+%|\$[\d,]+|\b\d{4}\b",
            lowered
        ):

            return "MEDIUM"

        return "NORMAL"

    # =====================================================
    # SOURCE LABELS
    # =====================================================

    def _source_labels(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        labels = []

        for source in sources:

            labels.append({

                "source_id":
                    source.get(
                        "source_id",
                        source.get(
                            "id"
                        )
                    ),

                "publisher":
                    source.get(
                        "publisher",
                        source.get(
                            "name",
                            ""
                        )
                    ),

                "domain":
                    source.get(
                        "domain",
                        source.get(
                            "url",
                            ""
                        )
                    ),

                "url":
                    source.get(
                        "url",
                        ""
                    )
            })

        return labels

    # =====================================================
    # TOKENIZER
    # =====================================================

    def _tokens(
        self,
        text: str
    ) -> Set[str]:

        text = str(
            text
            or
            ""
        ).lower()

        words = re.findall(
            r"\b[a-z0-9]{3,}\b",
            text
        )

        stop_words = {
            "the",
            "and",
            "for",
            "that",
            "this",
            "with",
            "from",
            "have",
            "has",
            "had",
            "were",
            "was",
            "are",
            "been",
            "will",
            "would",
            "could",
            "should",
            "about",
            "after",
            "before",
            "into",
            "their",
            "there",
            "they",
            "them",
            "than",
            "then",
            "when",
            "where",
            "which",
            "while",
            "what",
            "said",
            "says",
            "also",
            "more",
            "most",
            "some",
            "such"
        }

        return {
            word
            for word
            in words
            if word
            not in stop_words
        }

    # =====================================================
    # CLAIM ID
    # =====================================================

    def _claim_id(
        self,
        text: str
    ) -> str:

        digest = hashlib.sha256(
            text.encode(
                "utf-8"
            )
        ).hexdigest()[:12]

        return (
            "claim_"
            + digest
        )

    # =====================================================
    # STORY ID
    # =====================================================

    def _story_id(
        self,
        story: Dict[str, Any]
    ) -> str:

        existing_id = story.get(
            "story_id",
            story.get(
                "id"
            )
        )

        if existing_id:
            return str(
                existing_id
            )

        source_text = " ".join([

            str(
                story.get(
                    "title",
                    ""
                )
            ),

            str(
                story.get(
                    "content",
                    ""
                )
            )
        ])

        digest = hashlib.sha256(
            source_text.encode(
                "utf-8"
            )
        ).hexdigest()[:12]

        return (
            "story_"
            + digest
        )


# =========================================================
# SIMPLE FUNCTION API
# =========================================================

def verify_story(
    story: Dict[str, Any],
    sources: List[Dict[str, Any]]
) -> Dict[str, Any]:

    checker = FactChecker()

    return checker.verify_story(
        story=story,
        sources=sources
    )


def verify_claim(
    claim: Dict[str, Any],
    sources: List[Dict[str, Any]]
) -> Dict[str, Any]:

    checker = FactChecker()

    return checker.verify_claim(
        claim=claim,
        sources=sources
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    example_story = {

        "title":
            "Officials announce a new development",

        "content":
            (
                "Officials announced a new development "
                "in the investigation. "
                "The investigation will continue."
            )
    }

    example_sources = [

        {
            "source_id":
                "source_1",

            "publisher":
                "Example News",

            "domain":
                "example.com",

            "url":
                "https://example.com/story",

            "title":
                "Officials announce a new development",

            "content":
                (
                    "Officials announced a new development "
                    "in the investigation."
                )
        },

        {
            "source_id":
                "source_2",

            "publisher":
                "Example Wire",

            "domain":
                "wire.example.com",

            "url":
                "https://wire.example.com/story",

            "title":
                "Officials announce development",

            "content":
                (
                    "Officials announced a new development "
                    "in the investigation."
                )
        }
    ]

    checker = FactChecker()

    result = checker.verify_story(
        story=example_story,
        sources=example_sources
    )

    print(
        result
        )
