"""
AI NEWS FACTORY
CLAIM ANALYSIS & EVIDENCE ENGINE

Purpose
-------
Break a proposed news story into individual claims and
track the evidence supporting each claim.

The engine distinguishes:

    VERIFIED
    WELL_SUPPORTED
    PARTIALLY_SUPPORTED
    UNVERIFIED
    CONTRADICTED
    OPINION
    PREDICTION
    ATTRIBUTED_CLAIM

CORE PRINCIPLE
--------------
A story is not one giant fact.

Each factual assertion should be evaluated independently.

IMPORTANT
---------
This engine organizes evidence.
It does not invent evidence.
It does not convert predictions into facts.
It does not treat repeated social posts as independent proof.
"""

from typing import Any, Dict, List
from collections import defaultdict
import re


class ClaimEngine:

    def __init__(self):
        self.name = "Claim & Evidence Engine"
        self.version = "1.0.0"

        self.status_weights = {
            "VERIFIED": 100,
            "WELL_SUPPORTED": 85,
            "PARTIALLY_SUPPORTED": 60,
            "UNVERIFIED": 25,
            "CONTRADICTED": 0,
            "OPINION": 50,
            "PREDICTION": 40,
            "ATTRIBUTED_CLAIM": 65
        }

    def analyze(self, story: Dict[str, Any]) -> Dict[str, Any]:
        claims = self._extract_claims(story)
        evidence = self._extract_evidence(story)
        analyzed_claims = []

        for claim in claims:
            matched_evidence = self._match_evidence(
                claim, evidence
            )
            analyzed_claims.append(
                self._assess_claim(
                    claim,
                    matched_evidence
                )
            )

        summary = self._build_summary(analyzed_claims)
        publication_status = self._publication_status(
            analyzed_claims
        )

        return {
            "engine": self.name,
            "version": self.version,
            "status": "ANALYZED",
            "claim_count": len(analyzed_claims),
            "claims": analyzed_claims,
            "summary": summary,
            "publication_status": publication_status
        }

    def _extract_claims(
        self,
        story: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        raw_claims = story.get("claims")
        claims = []

        if isinstance(raw_claims, list):
            for item in raw_claims:
                if isinstance(item, str):
                    claims.append({
                        "text": item,
                        "type": "FACT"
                    })
                elif isinstance(item, dict):
                    claims.append({
                        "id": item.get("id"),
                        "text": item.get(
                            "text",
                            item.get("claim", "")
                        ),
                        "type": item.get(
                            "type",
                            "FACT"
                        ),
                        "importance": item.get(
                            "importance",
                            "NORMAL"
                        ),
                        "attribution": item.get(
                            "attribution"
                        )
                    })

        if claims:
            return [
                claim
                for claim in claims
                if claim["text"]
            ]

        body = str(
            story.get(
                "body",
                story.get("summary", "")
            )
        )

        sentences = re.split(
            r"(?<=[.!?])\s+",
            body
        )

        for sentence in sentences:
            sentence = sentence.strip()

            if len(sentence) < 15:
                continue

            claims.append({
                "text": sentence,
                "type": self._infer_claim_type(sentence),
                "importance": "NORMAL",
                "attribution": None
            })

        return claims

    def _extract_evidence(
        self,
        story: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        raw = story.get(
            "evidence",
            story.get("sources", [])
        )

        evidence = []

        if isinstance(raw, dict):
            raw = list(raw.values())

        if not isinstance(raw, list):
            return []

        for item in raw:
            if isinstance(item, str):
                evidence.append({
                    "text": item,
                    "source": None,
                    "type": "UNKNOWN"
                })

            elif isinstance(item, dict):
                evidence.append({
                    "id": item.get("id"),
                    "text": item.get(
                        "text",
                        item.get(
                            "excerpt",
                            item.get(
                                "description",
                                ""
                            )
                        )
                    ),
                    "source": item.get(
                        "source",
                        item.get("url")
                    ),
                    "type": item.get(
                        "type",
                        "UNKNOWN"
                    ),
                    "authority": item.get(
                        "authority",
                        0
                    ),
                    "independent": item.get(
                        "independent",
                        False
                    ),
                    "primary": item.get(
                        "primary",
                        False
                    ),
                    "supports": item.get(
                        "supports",
                        []
                    ),
                    "contradicts": item.get(
                        "contradicts",
                        []
                    )
                })

        return evidence

    def _match_evidence(
        self,
        claim: Dict[str, Any],
        evidence: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        claim_id = claim.get("id")
        claim_text = claim["text"].lower()
        matched = []

        for item in evidence:
            supports = item.get("supports", [])
            contradicts = item.get("contradicts", [])

            if claim_id and claim_id in supports:
                matched.append(item)
                continue

            if claim_id and claim_id in contradicts:
                matched.append(item)
                continue

            evidence_text = str(
                item.get("text", "")
            ).lower()

            similarity = self._text_similarity(
                claim_text,
                evidence_text
            )

            if similarity >= 0.20:
                matched.append(item)

        return matched

    def _assess_claim(
        self,
        claim: Dict[str, Any],
        evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        claim_type = str(
            claim.get("type", "FACT")
        ).upper()

        if claim_type in {"OPINION", "COMMENTARY"}:
            status = "OPINION"

        elif claim_type in {"PREDICTION", "FORECAST"}:
            status = "PREDICTION"

        else:
            status = self._evidence_status(evidence)

        support_score = self._support_score(evidence)

        contradictions = [
            item
            for item in evidence
            if self._evidence_contradicts(
                item,
                claim
            )
        ]

        if contradictions:
            status = "CONTRADICTED"

        return {
            "claim": claim["text"],
            "type": claim_type,
            "importance": claim.get(
                "importance",
                "NORMAL"
            ),
            "attribution": claim.get(
                "attribution"
            ),
            "status": status,
            "support_score": support_score,
            "evidence_count": len(evidence),
            "independent_evidence_count":
                self._independent_count(evidence),
            "primary_evidence_count": sum(
                1
                for item in evidence
                if item.get("primary", False)
            ),
            "contradiction_count": len(
                contradictions
            ),
            "evidence": [
                {
                    "source": item.get("source"),
                    "type": item.get("type"),
                    "primary": item.get(
                        "primary",
                        False
                    ),
                    "independent": item.get(
                        "independent",
                        False
                    )
                }
                for item in evidence
            ]
        }

    def _evidence_status(
        self,
        evidence: List[Dict[str, Any]]
    ) -> str:

        if not evidence:
            return "UNVERIFIED"

        contradictions = [
            item
            for item in evidence
            if item.get("contradicts")
        ]

        if contradictions:
            return "CONTRADICTED"

        independent = self._independent_count(
            evidence
        )

        primary = sum(
            1
            for item in evidence
            if item.get("primary", False)
        )

        support_score = self._support_score(
            evidence
        )

        if primary >= 1 and support_score >= 75:
            return "VERIFIED"

        if independent >= 2 and support_score >= 70:
            return "WELL_SUPPORTED"

        if support_score >= 45:
            return "PARTIALLY_SUPPORTED"

        return "UNVERIFIED"

    def _support_score(
        self,
        evidence: List[Dict[str, Any]]
    ) -> int:

        if not evidence:
            return 0

        scores = []

        for item in evidence:
            authority = float(
                item.get("authority", 0)
            )

            if authority <= 0:
                if item.get("primary", False):
                    authority = 100
                elif item.get("independent", False):
                    authority = 70
                else:
                    authority = 30

            scores.append(authority)

        strongest = max(scores)

        independent_bonus = min(
            self._independent_count(evidence) * 10,
            30
        )

        return int(
            min(
                strongest + independent_bonus,
                100
            )
        )

    def _evidence_contradicts(
        self,
        evidence: Dict[str, Any],
        claim: Dict[str, Any]
    ) -> bool:

        contradictions = evidence.get(
            "contradicts",
            []
        )

        claim_id = claim.get("id")

        if claim_id and claim_id in contradictions:
            return True

        return bool(
            evidence.get(
                "contradiction",
                False
            )
        )

    def _independent_count(
        self,
        evidence: List[Dict[str, Any]]
    ) -> int:

        sources = set()

        for item in evidence:
            if not item.get(
                "independent",
                False
            ):
                continue

            source = (
                item.get("source")
                or item.get("id")
            )

            if source:
                sources.add(str(source))

        return len(sources)

    def _build_summary(
        self,
        claims: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        counts = defaultdict(int)

        for claim in claims:
            counts[claim["status"]] += 1

        total = len(claims)

        supported = (
            counts["VERIFIED"]
            +
            counts["WELL_SUPPORTED"]
        )

        return {
            "total_claims": total,
            "verified": counts["VERIFIED"],
            "well_supported":
                counts["WELL_SUPPORTED"],
            "partially_supported":
                counts["PARTIALLY_SUPPORTED"],
            "unverified": counts["UNVERIFIED"],
            "contradicted": counts["CONTRADICTED"],
            "opinions": counts["OPINION"],
            "predictions": counts["PREDICTION"],
            "support_rate": round(
                supported
                / max(total, 1)
                * 100,
                2
            )
        }

    def _publication_status(
        self,
        claims: List[Dict[str, Any]]
    ) -> str:

        if not claims:
            return "NO_CLAIMS"

        critical_unverified = 0
        contradicted = 0

        for claim in claims:
            if claim["status"] == "CONTRADICTED":
                contradicted += 1

            if (
                claim["status"] == "UNVERIFIED"
                and str(
                    claim.get(
                        "importance",
                        ""
                    )
                ).upper()
                in {"HIGH", "CRITICAL"}
            ):
                critical_unverified += 1

        if contradicted > 0:
            return "HOLD_FOR_REVIEW"

        if critical_unverified > 0:
            return "HOLD_FOR_VERIFICATION"

        return "READY_FOR_EDITOR_REVIEW"

    def _infer_claim_type(
        self,
        sentence: str
    ) -> str:

        lowered = sentence.lower()

        opinion_markers = [
            "i think",
            "in my view",
            "arguably",
            "should",
            "must",
            "best"
        ]

        prediction_markers = [
            "could",
            "may",
            "might",
            "expected to",
            "likely",
            "forecast"
        ]

        if any(
            marker in lowered
            for marker in opinion_markers
        ):
            return "OPINION"

        if any(
            marker in lowered
            for marker in prediction_markers
        ):
            return "PREDICTION"

        return "FACT"

    def _text_similarity(
        self,
        text_a: str,
        text_b: str
    ) -> float:

        words_a = set(
            self._tokens(text_a)
        )

        words_b = set(
            self._tokens(text_b)
        )

        if not words_a or not words_b:
            return 0.0

        intersection = words_a & words_b
        union = words_a | words_b

        return (
            len(intersection)
            / max(len(union), 1)
        )

    def _tokens(
        self,
        text: str
    ) -> List[str]:

        return re.findall(
            r"\b[a-z0-9]{3,}\b",
            text.lower()
        )


def analyze_claims(
    story: Dict[str, Any]
) -> Dict[str, Any]:

    engine = ClaimEngine()
    return engine.analyze(story)
