"""
AI NEWS FACTORY
SOCIAL PUBLISHER

Central interface for publishing approved news to social
platform adapters.

Each platform should have its own adapter later.

The factory never publishes unverified stories.
"""

import logging
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class SocialPublisher:

    def __init__(
        self,
        adapters: Optional[List[Any]] = None
    ):

        self.adapters = []

        if adapters:

            for adapter in adapters:

                self.register(
                    adapter
                )

        self.name = "Social Publisher"
        self.version = "1.0.0"

    # =====================================================
    # REGISTER
    # =====================================================

    def register(
        self,
        adapter: Any
    ) -> None:

        if adapter is None:

            return

        if not hasattr(
            adapter,
            "publish"
        ):

            raise ValueError(
                "Social adapter must provide publish()."
            )

        self.adapters.append(
            adapter
        )

    # =====================================================
    # PUBLISH ALL
    # =====================================================

    def publish_all(
        self,
        article: Dict[str, Any],
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:

        results = []

        for adapter in self.adapters:

            platform = self._platform_name(
                adapter
            )

            if platforms:

                if platform not in platforms:

                    continue

            try:

                result = adapter.publish(
                    article
                )

                results.append({

                    "platform":
                        platform,

                    "result":
                        result
                })

            except Exception as exc:

                logger.exception(
                    "Social publishing failed: %s",
                    platform
                )

                results.append({

                    "platform":
                        platform,

                    "result": {

                        "status":
                            "FAILED",

                        "published":
                            False,

                        "error":
                            str(exc)
                    }
                })

        successful = sum(

            1

            for item in results

            if item["result"].get(
                "published"
            ) is True
        )

        return {

            "status":
                "SOCIAL_PUBLISH_COMPLETE",

            "total":
                len(results),

            "successful":
                successful,

            "failed":
                len(results) - successful,

            "results":
                results
        }

    # =====================================================
    # SINGLE PLATFORM
    # =====================================================

    def publish_to(
        self,
        platform: str,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:

        for adapter in self.adapters:

            name = self._platform_name(
                adapter
            )

            if name.lower() != platform.lower():

                continue

            try:

                return adapter.publish(
                    article
                )

            except Exception as exc:

                logger.exception(
                    "Publishing failed."
                )

                return {

                    "status":
                        "FAILED",

                    "published":
                        False,

                    "platform":
                        name,

                    "error":
                        str(exc)
                }

        return {

            "status":
                "NOT_CONFIGURED",

            "published":
                False,

            "platform":
                platform,

            "error":
                "No adapter configured."
        }

    # =====================================================
    # PLATFORM NAME
    # =====================================================

    def _platform_name(
        self,
        adapter: Any
    ) -> str:

        name = getattr(
            adapter,
            "platform",
            None
        )

        if name:

            return str(
                name
            )

        name = getattr(
            adapter,
            "name",
            None
        )

        if name:

            return str(
                name
            )

        return adapter.__class__.__name__


# =========================================================
# HELPER
# =========================================================

def create_social_publisher(
    adapters: Optional[List[Any]] = None
) -> SocialPublisher:

    return SocialPublisher(
        adapters=adapters
      )
