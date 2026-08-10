"""
AI NEWS FACTORY
MISINFORMATION INTELLIGENCE ENGINE

Purpose
-------
Detect signals that a news claim may require additional
verification before publication.

This engine does NOT decide truth by itself.

It identifies risk patterns such as:

    - unsupported claims
    - extraordinary claims with weak evidence
    - conflicting reports
    - recycled old information
    - missing original source
    - anonymous claims
    - manipulated-context indicators
    - suspiciously identical reporting
    - excessive certainty
    - sensational framing
    - temporal inconsistencies

CORE RULE
---------
A viral claim is not automatically a true claim.

A large number of copies is not independent confirmation.

The engine produces a risk assessment that the
fact-checking and editor engines can use.
"""

from typing import Any, Dict, List
from datetime import datetime
from urllib.parse import urlparse
import hashlib
import re


class MisinformationEngine:

    def __init__(self):

        self.name = "Misinformation Intelligence Engine"
        self.version = "1.0.0"

        self.high_risk_words = {
            "shocking",
            "secret",
            "exposed",
            "confirmed",
            "guaranteed",
            "everyone",
            "nobody",
            "destroyed",
            "definitely",
            "undeniable",
            "miracle",
            "scam",
            "hoax",
            "breaking"
        }

        self.uncertainty_words = {
            "allegedly",
            "reportedly",
            "possibly",
            "apparently",
            "may",
            "might",
            "could",
            "unconfirmed",
            "rumor",
            "rumour"
        }

        self.attribution_patterns = [
            "according to",
            "officials said",
            "police said",
            "the company said",
            "the government said",
            "a spokesperson said",
            "court documents",
            "court filing",
            "statement",
            "document",
            "report"
        ]

        self.denial_patterns = [
            "denied",
            "disputed",
            "rejected",
            "called the claim false",
            "said the claim was false",
            "not true",
            "no evidence",
            "misleading",
            "incorrect"
        ]

        self.social_domains = {
            "x.com",
            "twitter.com",
            "facebook.com",
            "instagram.com",
            "tiktok.com",
            "reddit.com",
            "youtube.com"
        }

    # =====================================================
    # MAIN
    # =====================================================

    def analyze(
        self,
        claims: List[Any],
        sources: List[Dict[str, Any]] = None,
        story: Dict[str, Any] = None
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

        story = (
            story
            if isinstance(
                story,
                dict
            )
            else {}
        )

        claim_results = []

        for claim in claims:

            result = self._analyze_claim(
                claim,
                sources,
                story
            )

            claim_results.append(
                result
            )

        source_analysis = (
            self._analyze_sources(
                sources
            )
        )

        temporal_analysis = (
            self._analyze_temporal_consistency(
                sources,
                story
            )
        )

        duplication_analysis = (
            self._analyze_duplication(
                sources
            )
        )

        overall = self._overall_assessment(
            claim_results,
            source_analysis,
            temporal_analysis,
            duplication_analysis
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "ANALYZED",

            "overall":
                overall,

            "claims":
                claim_results,

            "source_analysis":
                source_analysis,

            "temporal_analysis":
                temporal_analysis,

            "duplication_analysis":
                duplication_analysis,

            "editorial_action":
                self._editorial_action(
                    overall
                )
        }

    # =====================================================
    # CLAIM NORMALIZATION
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

        normalized = []

        for index, claim in enumerate(
            claims
        ):

            if isinstance(
                claim,
                str
            ):

                normalized.append({

                    "id":
                        f"claim_{index + 1}",

                    "text":
                        claim,

                    "confidence":
                        0,

                    "sources":
                        []
                })

                continue

            if not isinstance(
                claim,
                dict
            ):

                continue

            normalized.append({

                "id":
                    claim.get(
                        "id",
                        f"claim_{index + 1}"
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

                "confidence":
                    claim.get(
                        "confidence",
                        0
                    ),

                "sources":
                    claim.get(
                        "sources",
                        []
                    )
            })

        return normalized

    # =====================================================
    # CLAIM ANALYSIS
    # =====================================================

    def _analyze_claim(
        self,
        claim: Dict[str, Any],
        sources: List[Dict[str, Any]],
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        text = str(
            claim.get(
                "text",
                ""
            )
        ).strip()

        lower = text.lower()

        risk = 0
        signals = []
        positives = []

        # -------------------------------------------------
        # ATTRIBUTION
        # -------------------------------------------------

        has_attribution = any(
            pattern in lower
            for pattern
            in self.attribution_patterns
        )

        if has_attribution:

            positives.append(
                "Claim contains attribution language."
            )

        else:

            risk += 10

            signals.append(
                "Claim has no obvious attribution."
            )

        # -------------------------------------------------
        # UNCERTAINTY
        # -------------------------------------------------

        if any(
            word in lower
            for word
            in self.uncertainty_words
        ):

            positives.append(
                "Claim contains uncertainty language."
            )

        # -------------------------------------------------
        # DENIAL
        # -------------------------------------------------

        if any(
            pattern in lower
            for pattern
            in self.denial_patterns
        ):

            risk += 20

            signals.append(
                "Claim appears to involve a denial or dispute."
            )

        # -------------------------------------------------
        # SENSATIONAL LANGUAGE
        # -------------------------------------------------

        sensational_hits = [

            word
            for word
            in self.high_risk_words
            if re.search(
                rf"\b{re.escape(word)}\b",
                lower
            )
        ]

        if sensational_hits:

            risk += min(
                len(
                    sensational_hits
                ) * 5,
                20
            )

            signals.append(
                "Sensational wording detected: "
                +
                ", ".join(
                    sensational_hits[:5]
                )
            )

        # -------------------------------------------------
        # ABSOLUTE LANGUAGE
        # -------------------------------------------------

        absolute_patterns = [
            r"\balways\b",
            r"\bnever\b",
            r"\beveryone\b",
            r"\bnobody\b",
            r"\b100%\b",
            r"\bcompletely\b",
            r"\bdefinitely\b"
        ]

        absolute_hits = sum(
            1
            for pattern
            in absolute_patterns
            if re.search(
                pattern,
                lower
            )
        )

        if absolute_hits:

            risk += min(
                absolute_hits * 6,
                18
            )

            signals.append(
                "Absolute language may indicate excessive certainty."
            )

        # -------------------------------------------------
        # NUMBERS
        # -------------------------------------------------

        numbers = re.findall(
            r"\b\d+(?:\.\d+)?%?\b",
            text
        )

        if numbers:

            if not has_attribution:

                risk += 8

                signals.append(
                    "Numerical claim requires identifiable evidence."
                )

            else:

                positives.append(
                    "Claim contains specific numerical information."
                )

        # -------------------------------------------------
        # EXCEPTIONAL CLAIM
        # -------------------------------------------------

        exceptional_terms = [
            "cure",
            "miracle",
            "secret technology",
            "government cover-up",
            "world-changing",
            "never before",
            "first ever",
            "impossible",
            "proof that"
        ]

        exceptional_hits = [

            term
            for term
            in exceptional_terms
            if term in lower
        ]

        if exceptional_hits:

            risk += min(
                len(
                    exceptional_hits
                ) * 8,
                25
            )

            signals.append(
                "Exceptional claim requires strong supporting evidence."
            )

        # -------------------------------------------------
        # SOURCE MATCH
        # -------------------------------------------------

        source_match = self._find_claim_sources(
            claim,
            sources
        )

        if not source_match:

            risk += 15

            signals.append(
                "No supplied source clearly supports the claim."
            )

        else:

            positives.append(
                "At least one supplied source appears relevant to the claim."
            )

        # -------------------------------------------------
        # CLAIM LENGTH
        # -------------------------------------------------

        if len(
            text.split()
        ) < 5:

            risk += 5

            signals.append(
                "Claim is too short to evaluate reliably."
            )

        # -------------------------------------------------
        # FINAL SCORE
        # -------------------------------------------------

        risk = min(
            risk,
            100
        )

        return {

            "claim_id":
                claim.get(
                    "id"
                ),

            "claim":
                text,

            "risk_score":
                risk,

            "risk_level":
                self._risk_level(
                    risk
                ),

            "signals":
                signals,

            "positive_signals":
                positives,

            "source_matches":
                source_match,

            "recommendation":
                self._claim_recommendation(
                    risk
                )
        }

    # =====================================================
    # FIND CLAIM SOURCES
    # =====================================================

    def _find_claim_sources(
        self,
        claim: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> List[str]:

        claim_text = str(
            claim.get(
                "text",
                ""
            )
        ).lower()

        claim_words = {
            word
            for word
            in re.findall(
                r"\b[a-zA-Z]{5,}\b",
                claim_text
            )
        }

        if not claim_words:

            return []

        matches = []

        for source in sources:

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
            ]).lower()

            source_words = {
                word
                for word
                in re.findall(
                    r"\b[a-zA-Z]{5,}\b",
                    source_text
                )
            }

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

            if overlap >= 0.20:

                matches.append(
                    str(
                        source.get(
                            "source_id",
                            source.get(
                                "id",
                                ""
                            )
                        )
                    )
                )

        return matches

    # =====================================================
    # SOURCE ANALYSIS
    # =====================================================

    def _analyze_sources(
        self,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not sources:

            return {

                "score":
                    0,

                "level":
                    "NO_DATA",

                "warnings":
                    [
                        "No source material supplied."
                    ]
            }

        primary = 0
        anonymous = 0
        social = 0
        named = 0

        for source in sources:

            source_type = str(
                source.get(
                    "type",
                    ""
                )
            ).lower()

            name = str(
                source.get(
                    "name",
                    ""
                )
            ).strip()

            if source.get(
                "primary"
            ):

                primary += 1

            if source_type in {
                "anonymous",
                "unknown"
            }:

                anonymous += 1

            if self._is_social_source(
                source
            ):

                social += 1

            if name:

                named += 1

        score = 40

        score += min(
            primary * 15,
            30
        )

        score += min(
            named * 5,
            20
        )

        score -= min(
            anonymous * 10,
            25
        )

        score -= min(
            social * 3,
            15
        )

        score = max(
            0,
            min(
                score,
                100
            )
        )

        warnings = []

        if primary == 0:

            warnings.append(
                "No clear primary source was identified."
            )

        if anonymous:

            warnings.append(
                "Anonymous or unidentified sources are present."
            )

        if social:

            warnings.append(
                "Social sources should be treated as leads unless independently verified."
            )

        return {

            "score":
                score,

            "level":
                self._risk_inverse_level(
                    score
                ),

            "primary_sources":
                primary,

            "named_sources":
                named,

            "anonymous_sources":
                anonymous,

            "social_sources":
                social,

            "warnings":
                warnings
        }

    # =====================================================
    # TEMPORAL ANALYSIS
    # =====================================================

    def _analyze_temporal_consistency(
        self,
        sources: List[Dict[str, Any]],
        story: Dict[str, Any]
    ) -> Dict[str, Any]:

        dates = []

        for source in sources:

            published = source.get(
                "published_at"
            )

            if not published:

                continue

            dates.append(
                str(
                    published
                )
            )

        warnings = []

        if len(
            dates
        ) >= 2:

            unique_dates = len(
                set(
                    dates
                )
            )

            if unique_dates == 1:

                warnings.append(
                    "All supplied sources share the same publication timestamp; "
                    "this may indicate syndicated material."
                )

        event_date = story.get(
            "event_date"
        )

        if event_date and dates:

            warnings.append(
                "Event date should be compared with publication dates before publication."
            )

        return {

            "source_dates":
                dates,

            "event_date":
                event_date,

            "warnings":
                warnings,

            "status":
                "REVIEW_REQUIRED"
                if warnings
                else
                "NO_MAJOR_SIGNAL"
        }

    # =====================================================
    # DUPLICATION
    # =====================================================

    def _analyze_duplication(
        self,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        fingerprints = {}

        duplicate_groups = []

        for source in sources:

            content = str(
    
