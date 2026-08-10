"""
AI NEWS FACTORY
SCHEDULER

The scheduler is responsible only for triggering the factory.

It does NOT call individual brain engines.
The brain pipeline is handled by:

main.py
    ↓
brain/pipeline.py
"""

import asyncio
import logging
from datetime import datetime

from main import NewsFactory


logger = logging.getLogger("NewsFactory.Scheduler")


# =========================================================
# SCHEDULER
# =========================================================

class NewsScheduler:

    def __init__(self, interval_seconds=300):

        self.interval_seconds = interval_seconds
        self.running = False

        self.factory = NewsFactory()

    # =====================================================
    # START
    # =====================================================

    async def start(self):

        self.running = True

        logger.info("=" * 60)
        logger.info("AI NEWS FACTORY SCHEDULER")
        logger.info("=" * 60)

        await self.factory.start()

        logger.info(
            "Scheduler started."
        )

        logger.info(
            "Interval: %s seconds",
            self.interval_seconds
        )

        while self.running:

            try:

                logger.info(
                    "Scheduler cycle started: %s",
                    datetime.now().isoformat()
                )

                await self.run_cycle()

            except Exception as error:

                logger.exception(
                    "Scheduler cycle failed: %s",
                    error
                )

            if self.running:

                logger.info(
                    "Next cycle in %s seconds.",
                    self.interval_seconds
                )

                await asyncio.sleep(
                    self.interval_seconds
                )

    # =====================================================
    # ONE CYCLE
    # =====================================================

    async def run_cycle(self):

        """
        One complete factory cycle.

        News collection will be connected here when the
        collection/body layer is ready.
        """

        logger.info(
            "Preparing intelligence cycle..."
        )

        # -------------------------------------------------
        # NEWS COLLECTION
        # -------------------------------------------------
        #
        # This will eventually become:
        #
        # sources = news_collector.collect()
        #
        # For now the brain remains idle until real sources
        # are supplied.
        #
        # -------------------------------------------------

        sources = []

        story = {}

        topic = ""

        if not sources and not story:

            logger.info(
                "No news input available yet."
            )

            logger.info(
                "Brain pipeline waiting for news collector."
            )

            return

        # -------------------------------------------------
        # SEND EVERYTHING TO CENTRAL BRAIN
        # -------------------------------------------------

        result = await self.factory.process_story(
            sources=sources,
            story=story,
            topic=topic
        )

        logger.info(
            "Pipeline result: %s",
            result.get(
                "pipeline_status",
                "UNKNOWN"
            )
        )

    # =====================================================
    # STOP
    # =====================================================

    async def stop(self):

        if not self.running:
            return

        self.running = False

        await self.factory.stop()

        logger.info(
            "Scheduler stopped."
        )


# =========================================================
# START FUNCTION
# =========================================================

async def start_scheduler(
    interval_seconds=300
):

    scheduler = NewsScheduler(
        interval_seconds=interval_seconds
    )

    try:

        await scheduler.start()

    except KeyboardInterrupt:

        logger.info(
            "Scheduler shutdown requested."
        )

    finally:

        await scheduler.stop()


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        )
    )

    asyncio.run(
        start_scheduler()
    )
