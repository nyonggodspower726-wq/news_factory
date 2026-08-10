"""
AI NEWS FACTORY
EDITOR ENGINE

Purpose
-------
Final editorial quality-control gate.

The Editor Engine does NOT create the story.

It evaluates the work produced by the upstream newsroom
engines and decides whether the article is:

    APPROVED
    NEEDS_REVISION
    BLOCKED

Checks include:

    - factual safety
    - unsupported claims
    - contradictions
    - headline quality
    - lead quality
    - reader value
    - structure
    - clarity
    - repetition
    - manipulation
    - attribution
    - uncertainty
    - publication readiness

IMPORTANT
---------
A high engagement score can never override a factual failure.

Priority:

    FACTS
      ↓
    SOURCES
      ↓
    CLARITY
      ↓
    READER VALUE
      ↓
    ENGAGEMENT

The editor is therefore a gatekeeper, not a cheerleader.
"""

import re
from typing import Any, Dict, List


class EditorEngine:

    def __init__(self):

        self.name = "AI Senior Editor"
        self.version = "1.0.0"

        self.minimum_approval_score = 80

        self.maximum_blocking_errors = 0

    # =====================================================
    # MAIN EDITORIAL REVIEW
    # =====================================================

    def review(
        self,
        article_plan: Dict[str, Any],
        psychology: Dict[str, Any],
        verification: Dict[str, Any],
        cluster: Dict[str, Any]
    ) -> Dict[str, Any]:

        checks = []

        checks.append(
            self._check_verification(
                verification
            )
        )

        checks.append(
            self._check_headline(
                article_plan
            )
        )

        checks.append(
            self._check_lead(
                article_plan
            )
        )

        checks.append(
            self._check_claims(
                article_plan,
                verification
            )
        )

        checks.append(
            self._check_structure(
                article_plan
            )
        )

        checks.append(
            self._check_reader_value(
                article_plan
            )
        )

        checks.append(
            self._check_psychology(
                psychology
            )
        )

        checks.append(
            self._check_source_diversity(
                cluster
            )
        )

        checks.append(
            self._check_repetition(
                article_plan
            )
        )

        errors = self._collect_errors(
            checks
        )

        warnings = self._collect_warnings(
            checks
        )

        score = self._calculate_score(
            checks,
            errors
        )

        decision = self._decision(
            score,
            errors,
            warnings
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "editorial_score":
                score,

            "decision":
                decision,

            "checks":
                checks,

            "errors":
                errors,

            "warnings":
                warnings,

            "publication_gate":
                decision == "APPROVED",

            "editor_note":
                self._editor_note(
                    decision,
                    errors,
                    warnings
                )
        }

    # =====================================================
    # VERIFICATION CHECK
    # =====================================================

    def _check_verification(
        self,
        verification: Dict[str, Any]
    ) -> Dict[str, Any]:

        status = verification.get(
            "publication_status",
            "UNKNOWN"
        )

        if status == "VERIFICATION_PASSED":

            return self._pass(
                "verification",
                "Verification passed."
            )

        if status == "REQUIRES_EDITORIAL_REVIEW":

            return self._warning(
                "verification",
                "Some claims remain unverified."
            )

        return self._error(
            "verification",
            "Verification failed or is incomplete."
        )

    # =====================================================
    # HEADLINE
    # =====================================================

    def _check_headline(
        self,
        article_plan: Dict[str, Any]
    ) -> Dict[str, Any]:

        headline = (
            article_plan
            .get("article", {})
            .get("headline", {})
        )

        if not headline:

            return self._error(
                "headline",
                "Headline structure is missing."
            )

        return self._pass(
            "headline",
            "Headline structure exists."
        )

    # =====================================================
    # LEAD
    # =====================================================

    def _check_lead(
        self,
        article_plan: Dict[str, Any]
    ) -> Dict[str, Any]:

        lead = (
            article_plan
            .get("article", {})
            .get("lead", {})
        )

        if not lead:

            return self._error(
                "lead",
                "Lead section is missing."
            )

        required = lead.get(
            "required_information",
            []
        )

        if len(required) < 3:

            return self._warning(
                "lead",
                "Lead may lack enough essential context."
            )

        return self._pass(
            "lead",
            "Lead contains the required editorial framework."
        )

    # =====================================================
    # CLAIM CHECK
    # =====================================================

    def _check_claims(
        self,
        article_plan: Dict[str, Any],
        verification: Dict[str, Any]
    ) -> Dict[str, Any]:

        safe_claims = article_plan.get(
            "safe_claims",
            []
        )

        excluded = article_plan.get(
            "excluded_claims",
            []
        )

        contradicted = [
            claim
            for claim in verification.get(
                "claims",
                []
            )
            if claim.get(
                "status"
            ) == "CONTRADICTED"
        ]

        if contradicted:

            return self._error(
                "claims",
                "Contradicted claims are present in the evidence set."
            )

        if excluded:

            return self._warning(
                "claims",
                f"{len(excluded)} claims require exclusion or attribution."
            )

        if not safe_claims:

            return self._error(
                "claims",
                "No sufficiently verified claims are available."
            )

        return self._pass(
            "claims",
            f"{len(safe_claims)} sufficiently verified claims available."
        )

    # =====================================================
    # STRUCTURE
    # =====================================================

    def _check_structure(
        self,
        article_plan: Dict[str, Any]
    ) -> Dict[str, Any]:

        article = article_plan.get(
            "article",
            {}
        )

        required = [
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

        missing = [
            section
            for section in required
            if section not in article
        ]

        if missing:

            return self._error(
                "structure",
                "Missing sections: "
                + ", ".join(
                    missing
                )
            )

        return self._pass(
            "structure",
            "Article structure is complete."
        )

    # =====================================================
    # READER VALUE
    # =====================================================

    def _check_reader_value(
        self,
        article_plan: Dict[str, Any]
    ) -> Dict[str, Any]:

        article = article_plan.get(
            "article",
            {}
        )

        required_sections = [
            "why_it_matters",
            "what_happens_next",
            "what_is_unknown"
        ]

        missing = [
            section
            for section in required_sections
            if not article.get(
                section
            )
        ]

        if missing:

            return self._warning(
                "reader_value",
                "Reader-value sections need strengthening."
            )

        return self._pass(
            "reader_value",
            "Article includes relevance and uncertainty sections."
        )

    # =====================================================
    # PSYCHOLOGY
    # =====================================================

    def _check_psychology(
        self,
        psychology: Dict[str, Any]
    ) -> Dict[str, Any]:

        risks = psychology.get(
            "manipulation_risks",
            []
        )

        if risks:

            return self._error(
                "psychology",
                "Manipulative engagement patterns detected."
            )

        scores = psychology.get(
            "scores",
            {}
        )

        retention = scores.get(
            "retention",
            0
        )

        if retention < 50:

            return self._warning(
                "psychology",
                "Reader retention structure is weak."
            )

        return self._pass(
            "psychology",
            "Engagement strategy passes editorial review."
        )

    # =====================================================
    # SOURCE DIVERSITY
    # =====================================================

    def _check_source_diversity(
        self,
        cluster: Dict[str, Any]
    ) -> Dict[str, Any]:

        domains = cluster.get(
            "independent_domain_count",
            0
        )

        if domains >= 3:

            return self._pass(
                "source_diversity",
                "Multiple independent domains available."
            )

        if domains == 2:

            return self._warning(
                "source_diversity",
                "Only two independent domains are available."
            )

        return self._warning(
            "source_diversity",
            "Story currently relies on limited independent coverage."
        )

    # =====================================================
    # REPETITION
    # =====================================================

    def _check_repetition(
        self,
        article_plan: Dict[str, Any]
    ) -> Dict[str, Any]:

        claims = article_plan.get(
            "safe_claims",
            []
        )

        texts = [
            claim.get(
                "claim",
                ""
            ).lower().strip()
            for claim in claims
        ]

        normalized = []

        for text in texts:

            text = re.sub(
                r"\s+",
                " ",
                text
            )

            normalized.append(
                text
            )

        duplicates = (
            len(normalized)
            -
            len(set(normalized))
        )

        if duplicates > 0:

            return self._warning(
                "repetition",
                "Repeated factual statements detected."
            )

        return self._pass(
            "repetition",
            "No obvious duplicate claims detected."
        )

    # =====================================================
    # SCORE
    # =====================================================

    def _calculate_score(
        self,
        checks: List[Dict[str, Any]],
        errors: List[Dict[str, Any]]
    ) -> int:

        score = 100

        for check in checks:

            status = check.get(
                "status"
            )

            if status == "WARNING":

                score -= 5

            elif status == "ERROR":

                score -= 30

        # Errors receive substantial penalties.
        score -= len(errors) * 10

        return max(
            0,
            min(
                score,
                100
            )
        )

    # =====================================================
    # DECISION
    # =====================================================

    def _decision(
        self,
        score: int,
        errors: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]]
    ) -> str:

        if errors:

            return "BLOCKED"

        if score < self.minimum_approval_score:

            return "NEEDS_REVISION"

        if warnings:

            return "APPROVED_WITH_WARNINGS"

        return "APPROVED"

    # =====================================================
    # ERROR COLLECTION
    # =====================================================

    def _collect_errors(
        self,
        checks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        return [
            check
            for check in checks
            if check.get(
                "status"
            ) == "ERROR"
        ]

    # =====================================================
    # WARNING COLLECTION
    # =====================================================

    def _collect_warnings(
        self,
        checks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        return [
            check
            for check in checks
            if check.get(
                "status"
            ) == "WARNING"
        ]

    # =====================================================
    # EDITOR NOTE
    # =====================================================

    def _editor_note(
        self,
        decision: str,
        errors: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]]
    ) -> str:

        if decision == "BLOCKED":

            return (
                "Publication blocked. Correct all critical "
                "editorial failures before the story proceeds."
            )

        if decision == "NEEDS_REVISION":

            return (
                "The article requires another editorial pass "
                "before publication."
            )

        if decision == "APPROVED_WITH_WARNINGS":

            return (
                "Article passes the main editorial gate but "
                "contains non-critical warnings."
            )

        return (
            "Article passed the editorial gate."
        )

    # =====================================================
    # CHECK BUILDERS
    # =====================================================

    def _pass(
        self,
        check: str,
        message: str
    ) -> Dict[str, Any]:

        return {
            "check": check,
            "status": "PASS",
            "message": message
        }

    def _warning(
        self,
        check: str,
        message: str
    ) -> Dict[str, Any]:

        return {
            "check": check,
            "status": "WARNING",
            "message": message
        }

    def _error(
        self,
        check: str,
        message: str
    ) -> Dict[str, Any]:

        return {
            "check": check,
            "status": "ERROR",
            "message": message
        }


# =========================================================
# HELPER
# =========================================================

def edit_article(
    article_plan: Dict[str, Any],
    psychology: Dict[str, Any],
    verification: Dict[str, Any],
    cluster: Dict[str, Any]
) -> Dict[str, Any]:

    editor = EditorEngine()

    return editor.review(
        article_plan,
        psychology,
        verification,
        cluster
    )
