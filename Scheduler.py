"""
AI NEWS FACTORY
SCHEDULER

TEST MODE:
Runs the factory once at the configured Nigerian time.

PRODUCTION MODE:
Replace TEST_RUN_TIME with the production schedule when ready.
"""

import asyncio
import logging
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo

from main import NewsFactory

logger=logging.getLogger("NewsFactory.Scheduler")

NIGERIA_TZ=ZoneInfo("Africa/Lagos")

# =========================================================
# TEST SCHEDULE
# =========================================================

TEST_RUN_TIME="13:54"


class NewsScheduler:

    def __init__(self):

        self.running=False
        self.factory=NewsFactory()

    # =====================================================
    # START
    # =====================================================

    async def start(self):

        self.running=True

        logger.info("="*60)
        logger.info("AI NEWS FACTORY SCHEDULER")
        logger.info("="*60)

        logger.info(
            "Timezone: Africa/Lagos"
        )

        logger.info(
            "TEST RUN TIME: %s",
            TEST_RUN_TIME
        )

        await self.factory.start()

        logger.info(
            "Scheduler started."
        )

        # Wait for the configured Nigerian time.
        await self.wait_until_test_time()

        if self.running:

            try:

                await self.run_cycle()

            except Exception as error:

                logger.exception(
                    "Scheduler cycle failed: %s",
                    error
                )

        logger.info(
            "Test run completed."
        )

        self.running=False

    # =====================================================
    # WAIT FOR TEST TIME
    # =====================================================

    async def wait_until_test_time(self):

        now=datetime.now(
            NIGERIA_TZ
        )

        hour,minute=map(
            int,
            TEST_RUN_TIME.split(":")
        )

        target=now.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0
        )

        # If today's time has already passed,
        # schedule it for tomorrow.
        if target<=now:

            target+=timedelta(
                days=1
            )

        seconds=(
            target-now
        ).total_seconds()

        logger.info(
            "Nigeria time now: %s",
            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        logger.info(
            "Next test run: %s",
            target.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        logger.info(
            "Waiting %.0f seconds.",
            seconds
        )

        await asyncio.sleep(
            seconds
        )

    # =====================================================
    # ONE FACTORY CYCLE
    # =====================================================

    async def run_cycle(self):

        logger.info("="*60)

        logger.info(
            "FACTORY TEST CYCLE STARTED"
        )

        logger.info(
            "Nigeria time: %s",
            datetime.now(
                NIGERIA_TZ
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        logger.info("="*60)

        # -------------------------------------------------
        # NEWS COLLECTION
        # -------------------------------------------------

        sources=[]

        story={}

        topic=""

        # -------------------------------------------------
        # CURRENT TEST STATE
        # -------------------------------------------------

        if not sources and not story:

            logger.info(
                "No news input available yet."
            )

            logger.info(
                "Brain pipeline is waiting for "
                "the news collector."
            )

            return

        # -------------------------------------------------
        # CENTRAL FACTORY
        # -------------------------------------------------

        result=await self.factory.process_story(
            sources=sources,
            story=story,
            topic=topic
        )

        if not isinstance(
            result,
            dict
        ):

            logger.warning(
                "Factory returned invalid result."
            )

            return

        logger.info(
            "Pipeline result: %s",
            result.get(
                "pipeline_status",
                result.get(
                    "status",
                    "UNKNOWN"
                )
            )
        )

    # =====================================================
    # STOP
    # =====================================================

    async def stop(self):

        if not self.running:

            return

        self.running=False

        try:

            await self.factory.stop()

        except Exception as error:

            logger.exception(
                "Factory shutdown failed: %s",
                error
            )

        logger.info(
            "Scheduler stopped."
        )


# =========================================================
# START SCHEDULER
# =========================================================

async def start_scheduler():

    scheduler=NewsScheduler()

    try:

        await scheduler.start()

    except KeyboardInterrupt:

        logger.info(
            "Scheduler shutdown requested."
        )

    except Exception as error:

        logger.exception(
            "Scheduler failed: %s",
            error
        )

    finally:

        await scheduler.stop()


# =========================================================
# DIRECT RUN
# =========================================================

if __name__=="__main__":

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
