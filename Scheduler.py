"""
AI NEWS FACTORY
SCHEDULER

Controls the recurring News Factory workflow.

main.py
   ↓
scheduler.py
   ↓
NewsFactory
   ↓
Collect → Analyze → Verify → Write
→ Psychology → Quality Control
→ Website → Social
"""

import asyncio
import logging
import os
from datetime import datetime

from main import NewsFactory


logger = logging.getLogger("NewsFactoryScheduler")


# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------

INTERVAL_MINUTES = int(
    os.getenv(
        "FACTORY_INTERVAL_MINUTES",
        "15"
    )
)

INTERVAL_SECONDS = max(
    60,
    INTERVAL_MINUTES * 60
)


# ---------------------------------------------------------
# SCHEDULER
# ---------------------------------------------------------

class NewsScheduler:

    def __init__(
        self,
        factory=None
    ):

        self.factory = (
            factory
            or NewsFactory()
        )

        self.running = False

        self.cycle_number = 0

    # -----------------------------------------------------
    # RUN ONE CYCLE
    # -----------------------------------------------------

    async def run_cycle(self):

        self.cycle_number += 1

        logger.info(
            "=" * 60
        )

        logger.info(
            "NEWS FACTORY CYCLE #%s",
            self.cycle_number
        )

        logger.info(
            "Cycle started: %s",
            datetime.now().isoformat()
        )

        try:

            # The NewsFactory will eventually perform the
            # complete intelligence pipeline here.

            await self.factory.start()

            logger.info(
                "Factory cycle completed successfully."
            )

        except Exception as error:

            logger.exception(
                "Factory cycle failed: %s",
                error
            )

    # -----------------------------------------------------
    # START
    # -----------------------------------------------------

    async def start(self):

        self.running = True

        logger.info(
            "News Scheduler started."
        )

        logger.info(
            "Interval: %s minutes",
            INTERVAL_MINUTES
        )

        while self.running:

            try:

                await self.run_cycle()

            except Exception as error:

                logger.exception(
                    "Scheduler error: %s",
                    error
                )

            if not self.running:

                break

            logger.info(
                "Next factory cycle in %s minutes.",
                INTERVAL_MINUTES
            )

            await asyncio.sleep(
                INTERVAL_SECONDS
            )

    # -----------------------------------------------------
    # STOP
    # -----------------------------------------------------

    async def stop(self):

        self.running = False

        try:

            await self.factory.stop()

        except Exception:

            logger.exception(
                "Error while stopping factory."
            )

        logger.info(
            "News Scheduler stopped."
        )


# ---------------------------------------------------------
# APPLICATION
# ---------------------------------------------------------

async def main():

    scheduler = NewsScheduler()

    try:

        await scheduler.start()

    except KeyboardInterrupt:

        logger.info(
            "Shutdown requested."
        )

    except Exception as error:

        logger.exception(
            "Fatal scheduler error: %s",
            error
        )

    finally:

        await scheduler.stop()


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":

    asyncio.run(
        main()
)
