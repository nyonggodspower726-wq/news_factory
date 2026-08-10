"""
AI NEWS FACTORY
TREND DETECTION & STORY MOMENTUM ENGINE

Purpose
-------
Detect emerging news trends from incoming stories and
cross-platform signals.

The engine looks for:

    - story acceleration
    - source growth
    - cross-platform spread
    - source diversity
    - geographic spread
    - topic momentum
    - novelty
    - saturation
    - persistence
    - recency

IMPORTANT
---------
Popularity is NOT proof.

A viral claim can be:

    TRENDING
but still:
    UNVERIFIED

Therefore this engine determines PRIORITY, not truth.

Its output feeds:

    News Brain
    Story Cluster
    Significance Engine
    Editorial Scheduler
"""

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List


class TrendEngine:

    def __init__(self):

        self.name = "Trend & Momentum Engine"
        self.version = "1.0.0"

        self.acceleration_threshold = 1.5
        self.high_momentum_threshold = 70
        self.saturation_threshold = 80

    # =====================================================
    # MAIN ANALYSIS
    # =====================================================

    def analyze(
        self,
        stories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if not stories:

            return {
                "status": "NO_DATA",
                "trends": []
            }

        grouped = (
            self._group_story_signals(
                stories
            )
        )

        trends = []

        for key, signals in grouped.items():

            trend = self._analyze_group(
                key,
                signals
            )

            trends.append(
                trend
            )

        trends.sort(
            key=lambda item:
                item["momentum_score"],
            reverse=True
        )

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "ANALYZED",

            "generated_at":
                datetime.utcnow().isoformat(),

            "trend_count":
                len(trends),

            "trends":
                trends
        }

    # =====================================================
    # GROUP SIGNALS
    # =====================================================

    def _group_story_signals(
        self,
        stories: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:

        groups = defaultdict(list)

        for story in stories:

            cluster_id = (
                story.get(
                    "cluster_id"
                )
                or
                story.get(
                    "story_id"
                )
                or
                self._fallback_key(
                    story
                )
            )

            groups[
                cluster_id
            ].append(
                story
            )

        return groups

    # =====================================================
    # ANALYZE GROUP
    # =====================================================

    def _analyze_group(
        self,
        key: str,
        signals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        source_count = self._unique_count(
            signals,
            "source"
        )

        platform_count = self._unique_count(
            signals,
            "platform"
        )

        domain_count = self._unique_domains(
            signals
        )

        total_mentions = sum(
            max(
                int(
                    item.get(
                        "mentions",
                        1
                    )
                ),
                0
            )
            for item in signals
        )

        current_velocity = self._velocity(
            signals
        )

        previous_velocity = self._previous_velocity(
            signals
        )

        acceleration = (
            self._acceleration(
                current_velocity,
                previous_velocity
            )
        )

        novelty = self._novelty(
            signals
        )

        persistence = self._persistence(
            signals
        )

        saturation = self._saturation(
            signals,
            source_count
        )

        cross_platform = (
            self._cross_platform_score(
                platform_count
            )
        )

        source_diversity = (
            self._source_diversity_score(
                domain_count
            )
        )

        momentum = (
            self._momentum_score(
                current_velocity,
                acceleration,
                novelty,
                persistence,
                cross_platform,
                source_diversity,
                saturation
            )
        )

        classification = (
            self._classify(
                momentum,
                acceleration,
                saturation
            )
        )

        return {

            "trend_id":
                key,

            "topic":
                self._best_topic(
                    signals
                ),

            "momentum_score":
                momentum,

            "classification":
                classification,

            "signals": {

                "total_mentions":
                    total_mentions,

                "source_count":
                    source_count,

                "independent_domains":
                    domain_count,

                "platform_count":
                    platform_count,

                "current_velocity":
                    current_velocity,

                "previous_velocity":
                    previous_velocity,

                "acceleration":
                    acceleration,

                "novelty":
                    novelty,

                "persistence":
                    persistence,

                "cross_platform":
                    cross_platform,

                "source_diversity":
                    source_diversity,

                "saturation":
                    saturation
            },

            "editorial_priority":
                self._editorial_priority(
                    momentum,
                    novelty,
                    saturation
                ),

            "warning":
                self._warning(
                    saturation
                )
        }

    # =====================================================
    # VELOCITY
    # =====================================================

    def _velocity(
        self,
        signals: List[Dict[str, Any]]
    ) -> float:

        """
        Estimate current mention velocity.

        If upstream collectors provide an explicit
        velocity field, use it.

        Otherwise fall back to recent mention volume.
        """

        explicit = [
            float(
                item.get(
                    "velocity",
                    0
                )
            )
            for item in signals
            if item.get(
                "velocity"
            ) is not None
        ]

        if explicit:

            return round(
                sum(explicit)
                /
                len(explicit),
                2
            )

        recent_mentions = sum(
            max(
                int(
                    item.get(
                        "mentions",
                        1
                    )
                ),
                0
            )
            for item in signals
        )

        return float(
            recent_mentions
        )

    # =====================================================
    # PREVIOUS VELOCITY
    # =====================================================

    def _previous_velocity(
        self,
        signals: List[Dict[str, Any]]
    ) -> float:

        values = [
            float(
                item.get(
                    "previous_velocity",
                    0
                )
            )
            for item in signals
            if item.get(
                "previous_velocity"
            ) is not None
        ]

        if not values:
            return 0.0

        return (
            sum(values)
            /
            len(values)
        )

    # =====================================================
    # ACCELERATION
    # =====================================================

    def _acceleration(
        self,
        current: float,
        previous: float
    ) -> float:

        if previous <= 0:

            if current > 0:
                return 2.0

            return 0.0

        return round(
            current
            /
            previous,
            3
        )

    # =====================================================
    # NOVELTY
    # =====================================================

    def _novelty(
        self,
        signals: List[Dict[str, Any]]
    ) -> int:

        new_story_count = sum(
            1
            for item in signals
            if item.get(
                "is_new",
                False
            )
        )

        total = max(
            len(signals),
            1
        )

        score = (
            new_story_count
            /
            total
            *
            100
        )

        return int(
            min(
                score,
                100
            )
        )

    # =====================================================
    # PERSISTENCE
    # =====================================================

    def _persistence(
        self,
        signals: List[Dict[str, Any]]
    ) -> int:

        periods = set()

        for signal in signals:

            period = signal.get(
                "time_bucket"
            )

            if period is not None:

                periods.add(
                    str(period)
                )

        if not periods:

            return min(
                len(signals) * 10,
                100
            )

        return min(
            len(periods) * 15,
            100
        )

    # =====================================================
    # CROSS PLATFORM
    # =====================================================

    def _cross_platform_score(
        self,
        platform_count: int
    ) -> int:

        return min(
            platform_count * 20,
            100
        )

    # =====================================================
    # SOURCE DIVERSITY
    # =====================================================

    def _source_diversity_score(
        self,
        domain_count: int
    ) -> int:

        return min(
            domain_count * 20,
            100
        )

    # =====================================================
    # SATURATION
    # =====================================================

    def _saturation(
        self,
        signals: List[Dict[str, Any]],
        source_count: int
    ) -> int:

        mentions = sum(
            max(
                int(
                    item.get(
                        "mentions",
                        1
                    )
                ),
                0
            )
            for item in signals
        )

        if mentions <= 0:
            return 0

        # A high number of mentions per source suggests
        # that the story may already be saturated.

        ratio = (
            mentions
            /
            max(
                source_count,
                1
            )
        )

        return int(
            min(
                ratio * 10,
                100
            )
        )

    # =====================================================
    # MOMENTUM SCORE
    # =====================================================

    def _momentum_score(
        self,
        velocity: float,
        acceleration: float,
        novelty: int,
        persistence: int,
        cross_platform: int,
        source_diversity: int,
        saturation: int
    ) -> int:

        velocity_score = min(
            velocity * 5,
            100
        )

        acceleration_score = min(
            acceleration * 30,
            100
        )

        score = (
            velocity_score * 0.20
            +
            acceleration_score * 0.20
            +
            novelty * 0.15
            +
            persistence * 0.10
            +
            cross_platform * 0.15
            +
            source_diversity * 0.15
            +
            (100 - saturation) * 0.05
        )

        return int(
            max(
                0,
                min(
                    score,
                    100
                )
            )
        )

    # =====================================================
    # CLASSIFICATION
    # =====================================================

    def _classify(
        self,
        momentum: int,
        acceleration: float,
        saturation: int
    ) -> str:

        if (
            momentum >= 80
            and acceleration >= self.acceleration_threshold
            and saturation < self.saturation_threshold
        ):

            return "BREAKING_OR_EMERGING"

        if momentum >= 70:

            return "RISING"

        if momentum >= 50:

            return "DEVELOPING"

        if saturation >= self.saturation_threshold:

            return "SATURATED"

        return "LOW_MOMENTUM"

    # =====================================================
    # EDITORIAL PRIORITY
    # =====================================================

    def _editorial_priority(
        self,
        momentum: int,
        novelty: int,
        saturation: int
    ) -> str:

        if (
            momentum >= 80
            and novelty >= 50
            and saturation < 80
        ):

            return "IMMEDIATE_REVIEW"

        if momentum >= 65:

            return "HIGH"

        if momentum >= 45:

            return "NORMAL"

        return "LOW"

    # =====================================================
    # WARNING
    # =====================================================

    def _warning(
        self,
        saturation: int
    ) -> str:

        if saturation >= 90:

            return (
                "Story may already be highly saturated. "
                "Look for a genuinely new angle rather than "
                "another duplicate article."
            )

        if saturation >= 70:

            return (
                "Coverage is becoming crowded. "
                "Differentiate through verified new information."
            )

        return ""

    # =====================================================
    # BEST TOPIC
    # =====================================================

    def _best_topic(
        self,
        signals: List[Dict[str, Any]]
    ) -> str:

        topics = defaultdict(int)

        for signal in signals:

            topic = signal.get(
                "topic",
                "unknown"
            )

            topics[
                str(topic)
            ] += max(
                int(
                    signal.get(
                        "mentions",
                        1
                    )
                ),
                1
            )

        if not topics:
            return "unknown"

        return max(
            topics,
            key=topics.get
        )

    # =====================================================
    # UNIQUE COUNT
    # =====================================================

    def _unique_count(
        self,
        signals: List[Dict[str, Any]],
        field: str
    ) -> int:

        values = {
            str(
                signal.get(
                    field
                )
            )
            for signal in signals
            if signal.get(
                field
            )
        }

        return len(values)

    # =====================================================
    # UNIQUE DOMAINS
    # =====================================================

    def _unique_domains(
        self,
        signals: List[Dict[str, Any]]
    ) -> int:

        domains = {
            str(
                signal.get(
                    "domain"
                )
            ).lower()
            for signal in signals
            if signal.get(
                "domain"
            )
        }

        return len(domains)

    # =====================================================
    # FALLBACK GROUP KEY
    # =====================================================

    def _fallback_key(
        self,
        story: Dict[str, Any]
    ) -> str:

        title = str(
            story.get(
                "title",
                ""
            )
        ).lower()

        words = [
            word
            for word in title.split()
            if len(word) > 4
        ]

        return "_".join(
            words[:6]
        ) or "unknown_story"


# =========================================================
# HELPER
# =========================================================

def detect_trends(
    stories: List[Dict[str, Any]]
) -> Dict[str, Any]:

    engine = TrendEngine()

    return engine.analyze(
        stories
    )
