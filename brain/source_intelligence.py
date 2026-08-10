"""
AI NEWS FACTORY
Source Intelligence Engine

Purpose:
Evaluate the quality and usefulness of sources.

The engine does NOT decide that a source is "true" simply
because it has a high score. It produces an intelligence
assessment for the verification pipeline.

Source levels:

1. PRIMARY
   Official statements, government releases, company
   announcements, court documents, direct records, etc.

2. PROFESSIONAL
   Established news organizations and specialist publications.

3. SECONDARY
   Blogs, aggregators and other publications.

4. SOCIAL
   Social-media posts and community discussions.

5. UNKNOWN
   Sources that cannot yet be classified.

The system also looks for:
- corroboration
- source independence
- freshness
- attribution
- direct evidence
- potential conflict
- uncertainty
"""

from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urlparse


class SourceIntelligence:

    def __init__(self):
        self.name = "Source Intelligence Engine"
        self.version = "1.0.0"

        # Known source classifications.
        # This is deliberately conservative.
        self.primary_domains = {
            "gov.ng",
            "gov.uk",
            "gov",
            "who.int",
            "un.org",
            "courtlistener.com"
        }

        self.professional_domains = {
            "reuters.com",
            "apnews.com",
            "bbc.com",
            "bbc.co.uk",
            "aljazeera.com",
            "theguardian.com",
            "nytimes.com",
            "washingtonpost.com",
            "cnn.com",
            "npr.org"
        }

        self.aggregator_domains = {
            "news.google.com",
            "news.yahoo.com"
        }

    # =====================================================
    # MAIN ANALYSIS
    # =====================================================

    def analyze_source(
        self,
        source: Dict[str, Any]
    ) -> Dict[str, Any]:

        name = source.get(
            "name",
            "Unknown"
        )

        url = source.get(
            "url",
            ""
        )

        title = source.get(
            "title",
            ""
        )

        content = source.get(
            "content",
            ""
        )

        published_at = source.get(
            "published_at"
        )

        source_type = self.classify_source(
            name=name,
            url=url,
            content=content
        )

        domain = self._extract_domain(url)

        attribution = self._detect_attribution(
            content
        )

        direct_evidence = self._detect_direct_evidence(
            content
        )

        uncertainty = self._detect_uncertainty(
            content
        )

        freshness = self._calculate_freshness(
            published_at
        )

        score = self._calculate_source_score(
            source_type=source_type,
            attribution=attribution,
            direct_evidence=direct_evidence,
            uncertainty=uncertainty,
            freshness=freshness
        )

        return {
            "source": {
                "name": name,
                "domain": domain,
                "url": url,
                "type": source_type
            },

            "intelligence": {
                "score": score,
                "attribution": attribution,
                "direct_evidence": direct_evidence,
                "uncertainty": uncertainty,
                "freshness": freshness
            },

            "recommendation":
                self._recommendation(score),

            "analyzed_at":
                datetime.utcnow().isoformat()
        }

    # =====================================================
    # SOURCE CLASSIFICATION
    # =====================================================

    def classify_source(
        self,
        name: str,
        url: str,
        content: str = ""
    ) -> str:

        domain = self._extract_domain(url)

        if self._matches_domain(
            domain,
            self.primary_domains
        ):
            return "PRIMARY"

        if self._matches_domain(
            domain,
            self.professional_domains
        ):
            return "PROFESSIONAL"

        if self._matches_domain(
            domain,
            self.aggregator_domains
        ):
            return "AGGREGATOR"

        # Basic social-media detection.
        social_domains = {
            "x.com",
            "twitter.com",
            "facebook.com",
            "instagram.com",
            "tiktok.com",
            "reddit.com",
            "youtube.com"
        }

        if self._matches_domain(
            domain,
            social_domains
        ):
            return "SOCIAL"

        if domain:
            return "SECONDARY"

        return "UNKNOWN"

    # =====================================================
    # DOMAIN
    # =====================================================

    def _extract_domain(
        self,
        url: str
    ) -> str:

        if not url:
            return ""

        try:
            parsed = urlparse(url)

            domain = parsed.netloc.lower()

            if domain.startswith("www."):
                domain = domain[4:]

            return domain

        except Exception:
            return ""

    # =====================================================
    # DOMAIN MATCHING
    # =====================================================

    def _matches_domain(
        self,
        domain: str,
        domains: set
    ) -> bool:

        if not domain:
            return False

        for known in domains:

            if domain == known:
                return True

            if domain.endswith(
                "." + known
            ):
                return True

        return False

    # =====================================================
    # ATTRIBUTION
    # =====================================================

    def _detect_attribution(
        self,
        content: str
    ) -> bool:

        if not content:
            return False

        attribution_terms = [
            "according to",
            "said",
            "told reporters",
            "statement",
            "officials said",
            "the report said",
            "court documents",
            "police said",
            "the ministry said",
            "the company said"
        ]

        text = content.lower()

        return any(
            term in text
            for term in attribution_terms
        )

    # =====================================================
    # DIRECT EVIDENCE
    # =====================================================

    def _detect_direct_evidence(
        self,
        content: str
    ) -> bool:

        if not content:
            return False

        evidence_terms = [
            "official statement",
            "official document",
            "court filing",
            "court documents",
            "report",
            "data",
            "records",
            "filing",
            "press release",
            "announcement"
        ]

        text = content.lower()

        return any(
            term in text
            for term in evidence_terms
        )

    # =====================================================
    # UNCERTAINTY
    # =====================================================

    def _detect_uncertainty(
        self,
        content: str
    ) -> bool:

        if not content:
            return True

        uncertainty_terms = [
            "allegedly",
            "reportedly",
            "unconfirmed",
            "could not be independently verified",
            "claims",
            "appears to",
            "may have",
            "possibly",
            "sources say",
            "it is unclear"
        ]

        text = content.lower()

        return any(
            term in text
            for term in uncertainty_terms
        )

    # =====================================================
    # FRESHNESS
    # =====================================================

    def _calculate_freshness(
        self,
        published_at: Any
    ) -> str:

        if not published_at:
            return "unknown"

        try:

            if isinstance(
                published_at,
                datetime
            ):
                published = published_at

            else:
                published = datetime.fromisoformat(
                    str(published_at)
                    .replace("Z", "+00:00")
                )

            now = datetime.now(
                published.tzinfo
            )

            age_hours = (
                now - published
            ).total_seconds() / 3600

            if age_hours <= 6:
                return "very_fresh"

            if age_hours <= 24:
                return "fresh"

            if age_hours <= 72:
                return "recent"

            return "old"

        except Exception:
            return "unknown"

    # =====================================================
    # SOURCE SCORE
    # =====================================================

    def _calculate_source_score(
        self,
        source_type: str,
        attribution: bool,
        direct_evidence: bool,
        uncertainty: bool,
        freshness: str
    ) -> int:

        base_scores = {
            "PRIMARY": 90,
            "PROFESSIONAL": 80,
            "SECONDARY": 60,
            "AGGREGATOR": 50,
            "SOCIAL": 35,
            "UNKNOWN": 20
        }

        score = base_scores.get(
            source_type,
            20
        )

        if attribution:
            score += 5

        if direct_evidence:
            score += 5

        if uncertainty:
            score -= 10

        freshness_bonus = {
            "very_fresh": 5,
            "fresh": 4,
            "recent": 2,
            "old": 0,
            "unknown": 0
        }

        score += freshness_bonus.get(
            freshness,
            0
        )

        return max(
            0,
            min(score, 100)
        )

    # =====================================================
    # RECOMMENDATION
    # =====================================================

    def _recommendation(
        self,
        score: int
    ) -> str:

        if score >= 90:
            return "STRONG_PRIMARY_SOURCE"

        if score >= 75:
            return "GOOD_SUPPORTING_SOURCE"

        if score >= 55:
            return "USE_WITH_CORROBORATION"

        if score >= 35:
            return "SIGNAL_ONLY"

        return "DO_NOT_RELY_ON_ALONE"

    # =====================================================
    # COMPARE SOURCES
    # =====================================================

    def compare_sources(
        self,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        analyzed = []

        for source in sources:

            result = self.analyze_source(
                source
            )

            analyzed.append(result)

        analyzed.sort(
            key=lambda item:
                item["intelligence"]["score"],
            reverse=True
        )

        return {
            "total_sources": len(analyzed),
            "sources": analyzed,
            "strongest_source":
                analyzed[0]
                if analyzed
                else None
        }


# =========================================================
# HELPER FUNCTION
# =========================================================

def analyze_source(
    source: Dict[str, Any]
) -> Dict[str, Any]:

    engine = SourceIntelligence()

    return engine.analyze_source(
        source
      )
