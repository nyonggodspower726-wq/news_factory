"""
AI NEWS FACTORY
READER INTELLIGENCE ENGINE

Purpose
-------
Learn from aggregate reader behavior and convert that data
into editorial insights.

Signals may include:

    - page views
    - engaged sessions
    - average reading time
    - scroll depth
    - article completion
    - internal clicks
    - returning readers
    - shares
    - comments
    - topic performance
    - angle performance
    - headline performance

IMPORTANT
---------
Reader behavior is feedback, NOT truth.

This engine can influence:

    topic selection
    presentation
    article structure
    headline testing
    internal linking
    publishing priorities

It must NEVER influence:

    factual verification
    whether false information becomes true
    source credibility
    removal of uncertainty
    publication of contradicted claims

The engine is designed around aggregate metrics rather than
individual profiling.
"""

from typing import Any, Dict, List
from collections import defaultdict


class ReaderIntelligence:

    def __init__(self):

        self.name = "Reader Intelligence Engine"
        self.version = "1.0.0"

        self.minimum_sample_size = 20

    # =====================================================
    # MAIN ANALYSIS
    # =====================================================

    def analyze(
        self,
        articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not articles:

            return {
                "status": "NO_DATA",
                "message":
                    "No reader data available."
            }

        normalized = [
            self._normalize_article(
                article
            )
            for article in articles
        ]

        topic_insights = (
            self._analyze_topics(
                normalized
            )
        )

        angle_insights = (
            self._analyze_angles(
                normalized
            )
        )

        headline_insights = (
            self._analyze_headlines(
                normalized
            )
        )

        retention_insights = (
            self._analyze_retention(
                normalized
            )
        )

        engagement_insights = (
            self._analyze_engagement(
                normalized
            )
        )

        recommendations = (
            self._generate_recommendations(
                topic_insights,
                angle_insights,
                headline_insights,
                retention_insights,
                engagement_insights
            )
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "ANALYZED",

            "sample_size":
                len(normalized),

            "topics":
                topic_insights,

            "angles":
                angle_insights,

            "headlines":
                headline_insights,

            "retention":
                retention_insights,

            "engagement":
                engagement_insights,

            "recommendations":
                recommendations
        }

    # =====================================================
    # NORMALIZATION
    # =====================================================

    def _normalize_article(
        self,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        views = max(
            int(
                article.get(
                    "views",
                    0
                )
            ),
            0
        )

        reading_time = max(
            float(
                article.get(
                    "avg_reading_time",
                    0
                )
            ),
            0
        )

        scroll_depth = max(
            min(
                float(
                    article.get(
                        "scroll_depth",
                        0
                    )
                ),
                100
            ),
            0
        )

        completion = max(
            min(
                float(
                    article.get(
                        "completion_rate",
                        0
                    )
                ),
                100
            ),
            0
        )

        shares = max(
            int(
                article.get(
                    "shares",
                    0
                )
            ),
            0
        )

        internal_clicks = max(
            int(
                article.get(
                    "internal_clicks",
                    0
                )
            ),
            0
        )

        return {

            "id":
                article.get(
                    "id"
                ),

            "topic":
                article.get(
                    "topic",
                    "unknown"
                ),

            "angle":
                article.get(
                    "angle",
                    "unknown"
                ),

            "headline_type":
                article.get(
                    "headline_type",
                    "unknown"
                ),

            "views":
                views,

            "avg_reading_time":
                reading_time,

            "scroll_depth":
                scroll_depth,

            "completion_rate":
                completion,

            "shares":
                shares,

            "internal_clicks":
                internal_clicks,

            "returning_readers":
                max(
                    int(
                        article.get(
                            "returning_readers",
                            0
                        )
                    ),
                    0
                )
        }

    # =====================================================
    # TOPIC ANALYSIS
    # =====================================================

    def _analyze_topics(
        self,
        articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        groups = defaultdict(list)

        for article in articles:

            groups[
                article["topic"]
            ].append(
                article
            )

        results = []

        for topic, items in groups.items():

            metrics = (
                self._aggregate(
                    items
                )
            )

            results.append({
                "topic":
                    topic,

                "article_count":
                    len(items),

                "metrics":
                    metrics,

                "performance":
                    self._performance_label(
                        metrics
                    )
            })

        results.sort(
            key=lambda x:
                x["metrics"]["engagement_score"],
            reverse=True
        )

        return results

    # =====================================================
    # ANGLE ANALYSIS
    # =====================================================

    def _analyze_angles(
        self,
        articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        groups = defaultdict(list)

        for article in articles:

            groups[
                article["angle"]
            ].append(
                article
            )

        results = []

        for angle, items in groups.items():

            metrics = (
                self._aggregate(
                    items
                )
            )

            results.append({
                "angle":
                    angle,

                "article_count":
                    len(items),

                "metrics":
                    metrics,

                "performance":
                    self._performance_label(
                        metrics
                    )
            })

        results.sort(
            key=lambda x:
                x["metrics"]["engagement_score"],
            reverse=True
        )

        return results

    # =====================================================
    # HEADLINE ANALYSIS
    # =====================================================

    def _analyze_headlines(
        self,
        articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        groups = defaultdict(list)

        for article in articles:

            groups[
                article["headline_type"]
            ].append(
                article
            )

        results = []

        for headline_type, items in groups.items():

            metrics = (
                self._aggregate(
                    items
                )
            )

            results.append({
                "headline_type":
                    headline_type,

                "article_count":
                    len(items),

                "metrics":
                    metrics
            })

        return sorted(
            results,
            key=lambda x:
                x["metrics"]["engagement_score"],
            reverse=True
        )

    # =====================================================
    # RETENTION ANALYSIS
    # =====================================================

    def _analyze_retention(
        self,
        articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not articles:

            return {}

        avg_scroll = (
            sum(
                item["scroll_depth"]
                for item in articles
            )
            /
            len(articles)
        )

        avg_completion = (
            sum(
                item["completion_rate"]
                for item in articles
            )
            /
            len(articles)
        )

        avg_time = (
            sum(
                item["avg_reading_time"]
                for item in articles
            )
            /
            len(articles)
        )

        return {

            "average_scroll_depth":
                round(
                    avg_scroll,
                    2
                ),

            "average_completion_rate":
                round(
                    avg_completion,
                    2
                ),

            "average_reading_time":
                round(
                    avg_time,
                    2
                ),

            "retention_health":
                self._retention_health(
                    avg_scroll,
                    avg_completion
                )
        }

    # =====================================================
    # ENGAGEMENT
    # =====================================================

    def _analyze_engagement(
        self,
        articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not articles:

            return {}

        total_views = sum(
            item["views"]
            for item in articles
        )

        total_shares = sum(
            item["shares"]
            for item in articles
        )

        total_internal_clicks = sum(
            item["internal_clicks"]
            for item in articles
        )

        total_returning = sum(
            item["returning_readers"]
            for item in articles
        )

        share_rate = self._rate(
            total_shares,
            total_views
        )

        internal_rate = self._rate(
            total_internal_clicks,
            total_views
        )

        return {

            "total_views":
                total_views,

            "total_shares":
                total_shares,

            "total_internal_clicks":
                total_internal_clicks,

            "returning_readers":
                total_returning,

            "share_rate":
                round(
                    share_rate,
                    4
                ),

            "internal_click_rate":
                round(
                    internal_rate,
                    4
                )
        }

    # =====================================================
    # AGGREGATE
    # =====================================================

    def _aggregate(
        self,
        items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not items:

            return {
                "views": 0,
                "reading_time": 0,
                "scroll_depth": 0,
                "completion": 0,
                "shares": 0,
                "engagement_score": 0
            }

        views = sum(
            item["views"]
            for item in items
        )

        reading_time = (
            sum(
                item["avg_reading_time"]
                for item in items
            )
            /
            len(items)
        )

        scroll_depth = (
            sum(
                item["scroll_depth"]
                for item in items
            )
            /
            len(items)
        )

        completion = (
            sum(
                item["completion_rate"]
                for item in items
            )
            /
            len(items)
        )

        shares = sum(
            item["shares"]
            for item in items
        )

        share_rate = self._rate(
            shares,
            views
        )

        engagement_score = (
            scroll_depth * 0.30
            +
            completion * 0.35
            +
            min(
                reading_time,
                600
            )
            / 600
            * 20
            +
            min(
                share_rate * 10000,
                15
            )
        )

        return {

            "views":
                views,

            "reading_time":
                round(
                    reading_time,
                    2
                ),

            "scroll_depth":
                round(
                    scroll_depth,
                    2
                ),

            "completion":
                round(
                    completion,
                    2
                ),

            "shares":
                shares,

            "share_rate":
                round(
                    share_rate,
                    5
                ),

            "engagement_score":
                round(
                    min(
                        engagement_score,
                        100
                    ),
                    2
                )
        }

    # =====================================================
    # PERFORMANCE LABEL
    # =====================================================

    def _performance_label(
        self,
        metrics: Dict[str, Any]
    ) -> str:

        if (
            metrics["views"]
            <
            self.minimum_sample_size
        ):

            return "INSUFFICIENT_DATA"

        score = metrics[
            "engagement_score"
        ]

        if score >= 80:
            return "EXCEPTIONAL"

        if score >= 65:
            return "STRONG"

        if score >= 50:
            return "AVERAGE"

        return "WEAK"

    # =====================================================
    # RETENTION HEALTH
    # =====================================================

    def _retention_health(
        self,
        scroll: float,
        completion: float
    ) -> str:

        score = (
            scroll * 0.45
            +
            completion * 0.55
        )

        if score >= 80:
            return "EXCELLENT"

        if score >= 65:
            return "HEALTHY"

        if score >= 50:
            return "MODERATE"

        return "WEAK"

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    def _generate_recommendations(
        self,
        topics: List[Dict[str, Any]],
        angles: List[Dict[str, Any]],
        headlines: List[Dict[str, Any]],
        retention: Dict[str, Any],
        engagement: Dict[str, Any]
    ) -> List[str]:

        recommendations = []

        strong_topics = [
            item["topic"]
            for item in topics
            if item["performance"]
            in {
                "STRONG",
                "EXCEPTIONAL"
            }
        ]

        strong_angles = [
            item["angle"]
            for item in angles
            if item["performance"]
            in {
                "STRONG",
                "EXCEPTIONAL"
            }
        ]

        if strong_topics:

            recommendations.append(
                "Prioritize verified stories within historically strong topics."
            )

        if strong_angles:

            recommendations.append(
                "Test more stories using high-performing editorial angles."
            )

        if retention.get(
            "retention_health"
        ) == "WEAK":

            recommendations.extend([
                "Improve article structure.",
                "Strengthen the opening with verified relevance.",
                "Reduce unnecessary complexity."
            ])

        if engagement.get(
            "internal_click_rate",
            0
        ) < 0.01:

            recommendations.append(
                "Improve contextual internal linking between related stories."
            )

        if engagement.get(
            "share_rate",
            0
        ) < 0.001:

            recommendations.append(
                "Test clearer, more useful presentation of highly relevant stories."
            )

        recommendations.append(
            "Use performance data to improve presentation, never to weaken verification."
        )

        return recommendations

    # =====================================================
    # RATE
    # =====================================================

    def _rate(
        self,
        numerator: float,
        denominator: float
    ) -> float:

        if denominator <= 0:
            return 0.0

        return (
            numerator
            /
            denominator
        )


# =========================================================
# HELPER
# =========================================================

def analyze_reader_data(
    articles: List[Dict[str, Any]]
) -> Dict[str, Any]:

    engine = ReaderIntelligence()

    return engine.analyze(
        articles
    )
