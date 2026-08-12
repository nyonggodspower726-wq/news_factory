"""
AI NEWS FACTORY
SCHEDULER - TEST MODE
Nigeria real-time clock
"""

import asyncio
import logging
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo

from main import NewsFactory

logger=logging.getLogger("NewsFactory.Scheduler")

NIGERIA_TZ=ZoneInfo("Africa/Lagos")

# =========================================================
# EDIT ONLY THIS TIME
# FORMAT: HH:MM:SS
# =========================================================

TEST_RUN_TIME="14:16:00"


class NewsScheduler:

    def __init__(self):
        self.running=False
        self.factory=NewsFactory()

    async def start(self):

        self.running=True

        logger.info("="*60)
        logger.info("AI NEWS FACTORY TEST SCHEDULER")
        logger.info("="*60)
        logger.info("Timezone: Africa/Lagos")
        logger.info("Test time: %s",TEST_RUN_TIME)
        logger.info("="*60)

        await self.factory.start()

        logger.info("Factory initialized.")

        await self.wait_until_test_time()

        if self.running:
            await self.run_cycle()

        self.running=False

        logger.info("="*60)
        logger.info("TEST CYCLE FINISHED")
        logger.info("="*60)

    async def wait_until_test_time(self):

        try:
            hour,minute,second=map(
                int,
                TEST_RUN_TIME.split(":")
            )
        except ValueError:
            raise ValueError(
                "TEST_RUN_TIME must use HH:MM:SS format."
            )

        while self.running:

            now=datetime.now(NIGERIA_TZ)

            target=now.replace(
                hour=hour,
                minute=minute,
                second=second,
                microsecond=0
            )

            if target<=now:
                target+=timedelta(days=1)

            remaining=max(
                0,
                int(
                    (target-now).total_seconds()
                )
            )

            hours=remaining//3600
            minutes=(remaining%3600)//60
            seconds=remaining%60

            print(
                "\r"
                f"Nigeria Time: "
                f"{now.strftime('%H:%M:%S')}"
                f" | Scheduled: {TEST_RUN_TIME}"
                f" | Remaining: "
                f"{hours:02d}:"
                f"{minutes:02d}:"
                f"{seconds:02d}",
                end="",
                flush=True
            )

            if remaining<=0:
                print()
                logger.info(
                    "TEST TIME REACHED."
                )
                return

            await asyncio.sleep(1)

    async def run_cycle(self):

        logger.info("")
        logger.info("="*60)
        logger.info("FACTORY TEST CYCLE STARTED")
        logger.info("="*60)

        now=datetime.now(NIGERIA_TZ)

        logger.info(
            "Nigeria time: %s",
            now.strftime("%Y-%m-%d %H:%M:%S")
        )

        sources=[]
        story={}
        topic=""

        if not sources and not story:

            logger.info(
                "No news input available yet."
            )

            logger.info(
                "Scheduler is working."
            )

            logger.info(
                "News collector is not connected yet."
            )

            return

        logger.info(
            "Sending news to central factory..."
        )

        result=await self.factory.process_story(
            sources=sources,
            story=story,
            topic=topic
        )

        if isinstance(result,dict):

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

        else:

            logger.warning(
                "Factory returned invalid result."
            )

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


async def start_scheduler():

    scheduler=NewsScheduler()

    try:
        await scheduler.start()

    except KeyboardInterrupt:

        logger.info(
            "Shutdown requested."
        )

    except Exception as error:

        logger.exception(
            "Scheduler failed: %s",
            error
        )

    finally:

        await scheduler.stop()


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
