"""
AI NEWS FACTORY
RUNTIME LAYER

Responsible for:
- starting the factory
- running collection cycles
- processing queued stories
- handling controlled continuous operation
- exposing factory status

The intelligence engines remain separate from runtime.
"""

import logging
import time
from typing import Any, Dict, Optional

from core.factory_orchestrator import FactoryOrchestrator


logger = logging.getLogger(__name__)


class FactoryRuntime:

    def __init__(
        self,
        factory: FactoryOrchestrator,
        interval: int = 900
    ):

        self.factory = factory
        self.interval = max(
            30,
            int(interval)
        )

        self.running = False

        self.stats = {

            "cycles":
                0,

            "stories_collected":
                0,

            "stories_processed":
                0,

            "successful":
                0,

            "failed":
                0,

            "started_at":
                None,

            "last_cycle":
                None
        }

        self.name = "AI News Factory Runtime"
        self.version = "1.0.0"

    # =====================================================
    # SINGLE CYCLE
    # =====================================================

    def run_cycle(
        self
    ) -> Dict[str, Any]:

        started = time.time()

        self.stats["cycles"] += 1

        try:

            collection = self.factory.collect()

            collected = collection.get(
                "count",
                0
            )

            self.stats[
                "stories_collected"
            ] += collected

            results = self.factory.process(
                maximum=10
            )

            processed = len(
                results
            )

            self.stats[
                "stories_processed"
            ] += processed

            successful = sum(

                1

                for result in results

                if result.get(
                    "status"
                ) == "COMPLETED"
            )

            failed = sum(

                1

                for result in results

                if result.get(
                    "status"
                ) == "FAILED"
            )

            self.stats[
                "successful"
            ] += successful

            self.stats[
                "failed"
            ] += failed

            self.stats[
                "last_cycle"
            ] = time.time()

            return {

                "status":
                    "CYCLE_COMPLETE",

                "collection":
                    collection,

                "processed":
                    processed,

                "successful":
                    successful,

                "failed":
                    failed,

                "duration":
                    round(
                        time.time() - started,
                        3
                    )
            }

        except Exception as exc:

            logger.exception(
                "Factory cycle failed."
            )

            self.stats[
                "failed"
            ] += 1

            return {

                "status":
                    "CYCLE_FAILED",

                "error":
                    str(exc),

                "duration":
                    round(
                        time.time() - started,
                        3
                    )
            }

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
        once: bool = False
    ) -> None:

        if self.running:

            logger.warning(
                "Factory is already running."
            )

            return

        self.running = True

        self.stats[
            "started_at"
        ] = time.time()

        logger.info(
            "AI News Factory started."
        )

        try:

            if once:

                self.run_cycle()

                return

            while self.running:

                self.run_cycle()

                if not self.running:

                    break

                time.sleep(
                    self.interval
                )

        except KeyboardInterrupt:

            logger.info(
                "Factory stopped by user."
            )

        except Exception:

            logger.exception(
                "Runtime stopped unexpectedly."
            )

        finally:

            self.running = False

            logger.info(
                "AI News Factory stopped."
            )

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self
    ) -> None:

        self.running = False

        logger.info(
            "Stop signal received."
        )

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self
    ) -> Dict[str, Any]:

        queue_size = 0

        try:

            queue_size = self.factory.queue.size()

        except Exception:

            pass

        return {

            "name":
                self.name,

            "version":
                self.version,

            "running":
                self.running,

            "interval":
                self.interval,

            "queue_size":
                queue_size,

            "stats":
                dict(
                    self.stats
                )
        }


# =========================================================
# HELPER
# =========================================================

def create_runtime(
    factory: FactoryOrchestrator,
    interval: int = 900
) -> FactoryRuntime:

    return FactoryRuntime(
        factory=factory,
        interval=interval
              )
