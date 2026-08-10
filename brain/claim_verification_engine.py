"""
AI NEWS FACTORY
CLAIM VERIFICATION ENGINE

Purpose
-------
Evaluate individual factual claims against the available
evidence collected by the news factory.

This engine is deliberately conservative.

It does not say:
    "This is true because many websites said it."

Instead it asks:
    - What exactly is being claimed?
    - Which sources support it?
    - Are those sources independent?
    - Is there direct evidence?
    - Does any source contradict it?
    - How strong is the evidence?
    - How should the journalist phrase the claim?

The final decision always belongs to the editorial layer.

DECISION LEVELS
---------------
VERIFIED
SUPPORTED
PARTIALLY_SUPPORTED
CONTESTED
UNVERIFIED
REJECTED

IMPORTANT
---------
A claim being "unverified" does NOT mean it is false.

It means the current evidence is insufficient for the
factory to confidently present it as established fact.
"""


from typing import Any, Dict, List
from urllib.parse import urlparse
import re


class ClaimVerificationEngine:

    def __init__(self):

        self.name = "Claim Verification Engine"
        self.version = "1.0.0"

        self.primary_types = {
            "official",
            "government",
            "court",
            "police",
            "company",
            "document",
            "transcript",
            "direct_statement",
            "original_video",
            "original_image"
        }

        self.secondary_types = {
            "news",
            "newspaper",
            "magazine",
            "broadcast",
            "analysis"
        }

        self.weak_types = {
            "social",
            "social_media",
            "forum",
            "anonymous",
            "unknown"
        }

        self.contradiction_words = {
            "denied",
            "disputed",
            "false",
            "incorrect",
            "misleading",
            "rejected",
            "not true",
            "no evidence"
        }

    # =====================================================
    # MAIN
    # =====================================================

    def verify(
        self,
        claims: List[Any],
        sources: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        claims = self._normalize_claims(
            claims
        )

        sources = (
            sources
            if isinstance(
                sources,
                list
            )
            else []
        )

        results = []

        for claim in claims:

            results.append(
                self._verify_claim(
                    claim,
                    sources
                )
            )

        summary = self._summary(
            results
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "VERIFICATION_COMPLETE",

            "results":
                results,

            "summary":
                summary,

            "publication_rules":
                self._publication_rules(
                    results
                )
        }

    # =====================================================
    # NORMALIZE CLAIMS
    # =====================================================

    def _normalize_claims(
        self,
        claims: List[Any]
    ) -> List[Dict[str, Any]]:

        if isinstance(
            claims,
            str
        ):

            claims = [
                claims
            ]

        elif isinstance(
            claims,
            dict
        ):

            claims = [
                claims
            ]

        if not isinstance(
            claims,
            list
        ):

            return []

        normalized = []

        for index, claim in enumerate(
            claims
        ):

            if isinstance(
                claim,
                str
            ):

                normalized.append({

                    "claim_id":
                        f"claim_{index + 1}",

                    "text":
                        claim
                })

            elif isinstance(
                claim,
                dict
            ):

                normalized.append({

                    "claim_id":
                        claim.get(
                            "claim_id",
                            claim.get(
                                "id",
                                f"claim_{index + 1}"
                            )
                        ),

                    "text":
                        str(
                            claim.get(
                                "text",
                                claim.get(
                                    "claim",
                                    ""
                                )
                            )
                        ),

                    "importance":
                        claim.get(
                            "importance",
                            "normal"
                        ),

                    "provided_sources":
                        claim.get(
                            "sources",
                            []
                        )
                })

        return normalized

    # =====================================================
    # VERIFY CLAIM
    # =====================================================

    def _verify_claim(
        self,
        claim: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        text = str(
            claim.get(
                "text",
                ""
            )
        ).strip()

        relevant_sources = self._find_relevant_sources(
            text,
            sources
        )

        support = []
        contradictions = []

        for source in relevant_sources:

            assessment = self._assess_source_against_claim(
                text,
                source
            )

            if assessment[
                "relationship"
            ] == "SUPPORTS":

                support.append(
                    assessment
                )

            elif assessment[
                "relationship"
            ] == "CONTRADICTS":

                contradictions.append(
                    assessment
                )

        independence = self._independence(
            support
        )

        evidence_score = self._evidence_score(
            support,
            contradictions,
            independence
        )

        status = self._status(
            evidence_score,
            support,
            contradictions
        )

        wording = self._safe_wording(
            status,
            text,
            support,
            contradictions
        )

        return {

            "claim_id":
                claim.get(
                    "claim_id"
                ),

            "claim":
                text,

            "status":
                status,

            "evidence_score":
                evidence_score,

            "supporting_sources":
                support,

            "contradicting_sources":
                contradictions,

            "independence":
                independence,

            "recommended_wording":
                wording,

            "publication_safe":
                status in {
                    "VERIFIED",
                    "SUPPORTED"
                }
        }

    # =====================================================
    # FIND RELEVANT SOURCES
    # =====================================================

    def _find_relevant_sources(
        self,
        claim_text: str,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        claim_words = self._keywords(
            claim_text
        )

        if not claim_words:

            return []

        matches = []

        for source in sources:

            content = " ".join([

                str(
                    source.get(
                        "title",
                        ""
                    )
                ),

                str(
                    source.get(
                        "content",
                        source.get(
                            "text",
                            ""
                        )
                    )
                )
            ])

            source_words = self._keywords(
                content
            )

            overlap = (
                len(
                    claim_words
                    &
                    source_words
                )
                /
                max(
                    len(
                        claim_words
                    ),
                    1
                )
            )

            # Direct claim/source IDs may be supplied by
            # the collection layer.

            explicit_claims = source.get(
                "claims",
                []
            )

            explicit_match = False

            if isinstance(
                explicit_claims,
                list
            ):

                for supplied_claim in explicit_claims:

                    if self._text_similarity(
                        claim_text,
                        str(
                            supplied_claim
                        )
                    ) >= 0.55:

                        explicit_match = True
                        break

            if overlap >= 0.18 or explicit_match:

                matches.append(
                    source
                )

        return matches

    # =====================================================
    # SOURCE VS CLAIM
    # =====================================================

    def _assess_source_against_claim(
        self,
        claim_text: str,
        source: Dict[str, Any]
    ) -> Dict[str, Any]:

        source_text = " ".join([

            str(
                source.get(
                    "title",
                    ""
                )
            ),

            str(
                source.get(
                    "content",
                    source.get(
                        "text",
                        ""
                    )
                )
            )
        ])

        lower = source_text.lower()

        similarity = self._text_similarity(
            claim_text,
            source_text
        )

        contradiction = any(
            phrase in lower
            for phrase
            in self.contradiction_words
        )

        if contradiction:

            relationship = "CONTRADICTS"

        elif similarity >= 0.35:

            relationship = "SUPPORTS"

        else:

            relationship = "RELATED"

        source_quality = self._source_quality(
            source
        )

        return {

            "source_id":
                source.get(
                    "source_id",
                    source.get(
                        "id",
                        ""
                    )
                ),

            "source_name":
                source.get(
                    "name",
                    source.get(
                        "publisher",
                        ""
                    )
                ),

            "relationship":
                relationship,

            "similarity":
                round(
                    similarity,
                    3
                ),

            "source_quality":
                source_quality
        }

    # =====================================================
    # SOURCE QUALITY
    # =====================================================

    def _source_quality(
        self,
        source: Dict[str, Any]
    ) -> int:

        score = 40

        source_type = str(
            source.get(
                "type",
                ""
            )
        ).lower()

        if source_type in self.primary_types:

            score += 30

        elif source_type in self.secondary_types:

            score += 15

        elif source_type in self.weak_types:

            score -= 15

        if source.get(
            "verified"
        ):

            score += 10

        if source.get(
            "primary"
        ):

            score += 10

        if source.get(
            "author"
        ):

            score += 5

        if source.get(
            "published_at"
        ):

            score += 5

        return self._clamp(
            score
        )

    # =====================================================
    # INDEPENDENCE
    # =====================================================

    def _independence(
        self,
        supporting_sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not supporting_sources:

            return {

                "score":
                    0,

                "independent_sources":
                    0,

                "assessment":
                    "No supporting evidence."
            }

        domains = set()
        publishers = set()

        for item in supporting_sources:

            source_id = item.get(
                "source_id"
            )

            # IDs are not assumed to be domains.
            # We use source metadata when available.

            source_name = str(
                item.get(
                    "source_name",
                    ""
                )
            ).lower()

            if source_name:

                publishers.add(
                    source_name
                )

            if source_id:

                domains.add(
                    str(
                        source_id
                    )
                )

        independent = max(
            len(
                publishers
            ),
            len(
                domains
            )
        )

        if independent >= 3:

            score = 90

        elif independent == 2:

            score = 70

        elif independent == 1:

            score = 40

        else:

            score = 0

        return {

            "score":
                score,

            "independent_sources":
                independent,

            "assessment":
                (
                    "Multiple apparently independent sources."
                    if independent >= 2
                    else
                    "Limited independent corroboration."
                )
        }

    # =====================================================
    # EVIDENCE SCORE
    # =====================================================

    def _evidence_score(
        self,
        support: List[Dict[str, Any]],
        contradictions: List[Dict[str, Any]],
        independence: Dict[str, Any]
    ) -> int:

        if not support:

            base = 0

        else:

            qualities = [

                self._number(
                    item.get(
                        "source_quality",
                        0
                    ),
                    0
                )

                for item
                in support
            ]

            base = sum(
                qualities
            ) / len(
                qualities
            )

        independence_score = self._number(
            independence.get(
                "score",
                0
            ),
            0
        )

        score = (
            base * 0.65
            +
            independence_score * 0.35
        )

        if contradictions:

            score -= min(
                len(
                    contradictions
                ) * 15,
                40
            )

        return self._clamp(
            score
        )

    # =====================================================
    # STATUS
    # =====================================================

    def _status(
        self,
        score: int,
        support: List[Dict[str, Any]],
        contradictions: List[Dict[str, Any]]
    ) -> str:

        if contradictions and score < 70:

            return "CONTESTED"

        if score >= 85 and support:

            return "VERIFIED"

        if score >= 65 and support:

            return "SUPPORTED"

        if score >= 40 and support:

            return "PARTIALLY_SUPPORTED"

        if not support:

            return "UNVERIFIED"

        return "UNVERIFIED"

    # =====================================================
    # SAFE WORDING
    # =====================================================

    def _safe_wording(
        self,
        status: str,
        claim: str,
        support: List[Dict[str, Any]],
        contradictions: List[Dict[str, Any]]
    ) -> str:

        if status == "VERIFIED":

            return (
                "The evidence supports stating the claim directly, "
                "while retaining the relevant attribution where appropriate."
            )

        if status == "SUPPORTED":

            return (
                "State the claim with attribution to the supporting source(s)."
            )

        if status == "PARTIALLY_SUPPORTED":

            return (
                "Use qualified language and state only the portion clearly supported by evidence."
            )

        if status == "CONTESTED":

            return (
                "Present the competing positions and clearly attribute each claim."
            )

        return (
            "Do not present this claim as established fact until stronger evidence is available."
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def _summary(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        counts = {

            "VERIFIED":
                0,

            "SUPPORTED":
                0,

            "PARTIALLY_SUPPORTED":
                0,

            "CONTESTED":
                0,

            "UNVERIFIED":
                0
        }

        for result in results:

            status = result.get(
                "status"
            )

            if status in counts:

                counts[
                    status
                ] += 1

        total = len(
            results
        )

        if total:

            verified_ratio = (
                (
                    counts[
                        "VERIFIED"
                    ]
                    +
                    counts[
                        "SUPPORTED"
                    ]
                )
                /
                total
            )

        else:

            verified_ratio = 0

        return {

            "total_claims":
                total,

            "counts":
                counts,

            "supported_ratio":
                round(
                    verified_ratio,
                    3
                ),

            "overall":
                self._summary_status(
                    counts,
                    total
                )
        }

    # =====================================================
    # SUMMARY STATUS
    # =====================================================

    def _summary_status(
        self,
        counts: Dict[str, int],
        total: int
    ) -> str:

        if total == 0:

            return "NO_CLAIMS"

        if counts[
            "CONTESTED"
        ] > 0:

            return "EDITORIAL_REVIEW_REQUIRED"

        if counts[
            "UNVERIFIED"
        ] > total / 2:

            return "INSUFFICIENT_EVIDENCE"

        if (
            counts[
                "VERIFIED"
            ]
            +
            counts[
                "SUPPORTED"
            ]
        ) == total:

            return "STRONG_EVIDENCE_BASE"

        return "MIXED_EVIDENCE"

    # =====================================================
    # PUBLICATION RULES
    # ==========
