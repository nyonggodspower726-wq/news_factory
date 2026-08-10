"""
AI NEWS FACTORY
EVIDENCE INTELLIGENCE ENGINE

Purpose
-------
Evaluate the evidence supporting individual news claims.

The engine asks:

    - What exactly is being claimed?
    - Which sources support it?
    - Are those sources independent?
    - Is there a primary source?
    - Does the evidence directly support the claim?
    - Is the evidence fresh enough?
    - Are there contradictions?
    - Is the claim fact, allegation, analysis, prediction,
      or opinion?

CORE PRINCIPLE
--------------
A source can be credible while a particular claim from
that source is still poorly supported.

Therefore:

    SOURCE QUALITY != CLAIM EVIDENCE

The engine evaluates evidence at the claim level.

IMPORTANT
---------
This engine does not independently establish truth.

It creates an evidence assessment for downstream systems
such as:

    claim_engine
    fact_checker
    journalist_engine
    editor_engine
"""


from typing import Any, Dict, List
import re


class EvidenceEngine:

    def __init__(self):

        self.name = "Evidence Intelligence Engine"
        self.version = "1.0.0"

        self.claim_types = {
            "FACT",
            "ALLEGATION",
            "OPINION",
            "ANALYSIS",
            "PREDICTION",
            "UNCONFIRMED"
        }

        self.strong_source_types = {
            "PRIMARY",
            "OFFICIAL",
            "GOVERNMENT",
            "COURT",
            "REGULATORY",
            "ACADEMIC",
            "WIRE"
        }

        self.weak_source_types = {
            "SOCIAL",
            "USER_GENERATED",
            "UNKNOWN"
        }

        self.uncertainty_words = {
            "may",
            "might",
            "could",
            "possibly",
            "reportedly",
            "allegedly",
            "apparently",
            "unconfirmed",
            "rumored",
            "rumour",
            "rumor",
            "expected",
            "likely"
        }

        self.attribution_words = {
            "according",
            "said",
            "says",
            "reported",
            "confirmed",
            "stated",
            "announced",
            "claimed",
            "told"
        }

    # =====================================================
    # MAIN
    # =====================================================

    def analyze(
        self,
        claims: List[Dict[str, Any]],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        claims = self._normalize_claims(
            claims
        )

        sources = self._normalize_sources(
            sources
        )

        assessments = []

        for claim in claims:

            assessment = (
                self._assess_claim(
                    claim,
                    sources
                )
            )

            assessments.append(
                assessment
            )

        summary = self._summary(
            assessments
        )

        publication = (
            self._publication_readiness(
                assessments
            )
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "ANALYZED",

            "claim_count":
                len(assessments),

            "claims":
                assessments,

            "summary":
                summary,

            "publication_readiness":
                publication
        }

    # =====================================================
    # CLAIM NORMALIZATION
    # =====================================================

    def _normalize_claims(
        self,
        claims: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        if isinstance(
            claims,
            str
        ):

            claims = [
                {
                    "text":
                        claims
                }
            ]

        if isinstance(
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

        output = []

        for index, claim in enumerate(
            claims
        ):

            if isinstance(
                claim,
                str
            ):

                claim = {
                    "text":
                        claim
                }

            if not isinstance(
                claim,
                dict
            ):

                continue

            text = str(
                claim.get(
                    "text",
                    claim.get(
                        "claim",
                        ""
                    )
                )
            ).strip()

            if not text:
                continue

            output.append({

                "id":
                    claim.get(
                        "id",
                        f"claim_{index + 1}"
                    ),

                "text":
                    text,

                "type":
                    str(
                        claim.get(
                            "type",
                            ""
                        )
                    ).upper(),

                "importance":
                    str(
                        claim.get(
                            "importance",
                            "MEDIUM"
                        )
                    ).upper(),

                "source_ids":
                    claim.get(
                        "source_ids",
                        []
                    ),

                "entities":
                    claim.get(
                        "entities",
                        []
                    )
            })

        return output

    # =====================================================
    # SOURCE NORMALIZATION
    # =====================================================

    def _normalize_sources(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        if isinstance(
            sources,
            dict
        ):

            sources = list(
                sources.values()
            )

        if not isinstance(
            sources,
            list
        ):

            return []

        output = []

        for index, source in enumerate(
            sources
        ):

            if isinstance(
                source,
                str
            ):

                source = {
                    "url":
                        source
                }

            if not isinstance(
                source,
                dict
            ):

                continue

            output.append({

                "id":
                    source.get(
                        "id",
                        f"source_{index + 1}"
                    ),

                "name":
                    source.get(
                        "name",
                        source.get(
                            "publisher",
                            "Unknown"
                        )
                    ),

                "url":
                    source.get(
                        "url",
                        ""
                    ),

                "title":
                    source.get(
                        "title",
                        ""
                    ),

                "text":
                    source.get(
                        "text",
                        source.get(
                            "excerpt",
                            ""
                        )
                    ),

                "type":
                    str(
                        source.get(
                            "type",
                            source.get(
                                "source_type",
                                "UNKNOWN"
                            )
                        )
                    ).upper(),

                "domain":
                    source.get(
                        "domain",
                        ""
                    ),

                "primary":
                    bool(
                        source.get(
                            "primary",
                            False
                        )
                    ),

                "official":
                    bool(
                        source.get(
                            "official",
                            False
                        )
                    ),

                "independent":
                    bool(
                        source.get(
                            "independent",
                            False
                        )
                    ),

                "quality_score":
                    self._number(
                        source.get(
                            "quality_score",
                            source.get(
                                "reliability",
                                50
                            )
                        ),
                        50
                    ),

                "published_at":
                    source.get(
                        "published_at"
                    )
            })

        return output

    # =====================================================
    # CLAIM ASSESSMENT
    # =====================================================

    def _assess_claim(
        self,
        claim: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        claim_type = self._classify_claim(
            claim
        )

        supporting = []
        opposing = []

        for source in sources:

            relationship = (
                self._source_relationship(
                    claim,
                    source
                )
            )

            if relationship == "SUPPORTS":

                supporting.append(
                    source
                )

            elif relationship == "OPPOSES":

                opposing.append(
                    source
                )

        directness = self._directness_score(
            claim,
            supporting
        )

        source_strength = (
            self._source_strength(
                supporting
            )
        )

        independence = (
            self._independence_score(
                supporting
            )
        )

        primary = (
            self._primary_score(
                supporting
            )
        )

        freshness = (
            self._freshness_score(
                supporting
            )
        )

        contradiction = (
            self._contradiction_score(
                supporting,
                opposing
            )
        )

        attribution = (
            self._attribution_score(
                claim
            )
        )

        uncertainty = (
            self._uncertainty_score(
                claim
            )
        )

        evidence_score = (
            directness * 0.25
            +
            source_strength * 0.20
            +
            independence * 0.15
            +
            primary * 0.15
            +
            freshness * 0.10
            +
            attribution * 0.05
            +
            (100 - contradiction) * 0.10
        )

        evidence_score = int(
            max(
                0,
                min(
                    evidence_score,
                    100
                )
            )
        )

        if claim_type in {
            "ALLEGATION",
            "PREDICTION",
            "OPINION",
            "ANALYSIS"
        }:

            publication_status = (
                "ATTRIBUTE_OR_LABEL"
            )

        elif contradiction >= 60:

            publication_status = (
                "HOLD_FOR_REVIEW"
            )

        elif evidence_score >= 80:

            publication_status = (
                "STRONG_SUPPORT"
            )

        elif evidence_score >= 60:

            publication_status = (
                "MODERATE_SUPPORT"
            )

        elif evidence_score >= 40:

            publication_status = (
                "WEAK_SUPPORT"
            )

        else:

            publication_status = (
                "INSUFFICIENT_SUPPORT"
            )

        return {

            "claim_id":
                claim["id"],

            "claim":
                claim["text"],

            "claim_type":
                claim_type,

            "importance":
                claim["importance"],

            "supporting_sources":
                self._source_names(
                    supporting
                ),

            "opposing_sources":
                self._source_names(
                    opposing
                ),

            "supporting_source_count":
                len(supporting),

            "opposing_source_count":
                len(opposing),

            "evidence_score":
                evidence_score,

            "evidence_dimensions": {

                "directness":
                    directness,

                "source_strength":
                    source_strength,

                "independence":
                    independence,

                "primary_source":
                    primary,

                "freshness":
                    freshness,

                "attribution":
                    attribution,

                "contradiction":
                    contradiction,

                "uncertainty":
                    uncertainty
            },

            "publication_status":
                publication_status,

            "recommended_treatment":
                self._recommended_treatment(
                    claim_type,
                    evidence_score,
                    contradiction
                )
        }

    # =====================================================
    # SOURCE RELATIONSHIP
    # =====================================================

    def _source_relationship(
        self,
        claim: Dict[str, Any],
        source: Dict[str, Any]
    ) -> str:

        claim_text = (
            claim[
                "text"
            ].lower()
        )

        source_text = (
            (
                str(
                    source.get(
                        "title",
                        ""
                    )
                )
                +
                " "
                +
                str(
                    source.get(
                        "text",
                        ""
                    )
                )
            ).lower()
        )

        if not source_text:

            return "NEUTRAL"

        claim_tokens = set(
            self._tokens(
                claim_text
            )
        )

        source_tokens = set(
            self._tokens(
                source_text
            )
        )

        if not claim_tokens:

            return "NEUTRAL"

        overlap = (
            claim_tokens
            &
            source_tokens
        )

        ratio = (
            len(overlap)
            /
            len(claim_tokens)
        )

        if ratio < 0.20:

            return "NEUTRAL"

        opposition = [
            (
                "denied",
                "confirmed"
            ),
            (
                "false",
                "true"
            ),
            (
                "rejected",
                "approved"
            ),
            (
                "disputed",
                "confirmed"
            ),
            (
                "not",
                ""
            )
        ]

        for negative, positive in opposition:

            if (
                negative
                and
                negative in source_text
                and
                positive
                and
                positive in claim_text
            ):

                return "OPPOSES"

        return "SUPPORTS"

    # =====================================================
    # DIRECTNESS
    # =====================================================

    def _directness_score(
        self,
        claim: Dict[str, Any],
        supporting: List[Dict[str, Any]]
    ) -> int:

        if not supporting:

            return 0

        claim_tokens = set(
            self._tokens(
                claim["text"]
            )
        )

        best = 0

        for source in supporting:

            text = (
                str(
                    source.get(
                        "title",
                        ""
                    )
                )
                +
                " "
                +
                str(
                    source.get(
                        "text",
                        ""
                    )
                )
            )

            source_tokens = set(
                self._tokens(
                    text
                )
            )

            if not source_tokens:
                continue

            overlap = (
                claim_tokens
                &
                source_tokens
            )

            ratio = (
                len(overlap)
                /
                max(
                    len(claim_tokens),
                    1
                )
            )

            score = int(
                ratio * 100
            )

            if source.get(
                "primary"
            ):

                score += 15

            best = max(
                best,
                min(
                    score,
                    100
                )
            )

        return best

    # =====================================================
    # SOURCE STRENGTH
    # =====================================================

    def _source_strength(
        self,
        sources: List[Dict[str, Any]]
    ) -> int:

        if not sources:

            return 0

        scores = []

        for source in sources:

            explicit = source.get(
                "quality_score"
            )

            try:

                value = float(
                    explicit
                )

            except (
                TypeError,
                ValueError
            ):

                value = 50

            source_type = source.get(
                "type",
                "UNKNOWN"
            )

            if source_type in self.strong_source_types:

                value += 10

            if source_type in self.weak_source_types:

                value -= 20

            if source.get(
                "primary"
            ):

                value += 20

            scores.append(
                max(
                    0,
                    min(
                        value,
                        100
                    )
                )
            )

        return int(
            sum(scores)
            /
            len(scores)
        )

    # =====================================================
    # INDEPENDENCE
    # =====================================================

    def _independence_score(
        self,
        sources: List[Dict[str, Any]]
    ) -> int:

        if not sources:

            return 0

        domains = set()

        independent_count = 0

        for source in sources:

            domain = str(
                source.get(
                    "domain",
                    ""
                )
            ).lower().strip()

            if domain:

                domains.add(
                    domain
                )

            if source.get(
                "independent"
            ):

                independent_count += 1

        score = min(
            len(domains) * 20,
            60
     
