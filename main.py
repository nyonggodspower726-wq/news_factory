"""
AI NEWS FACTORY
Main Controller

This is the central entry point for the News Factory.
It coordinates:
- News collection
- Story analysis
- Editorial intelligence
- Journalist engine
- Psychology engine
- Quality control
- Publishing

We are building the system in stages, so some engines
will be connected as we develop them.
"""

import asyncio
import logging
from datetime import datetime

from config import FACTORY_NAME, VERSION


# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("NewsFactory")


# ---------------------------------------------------------
# FACTORY
# ---------------------------------------------------------

class NewsFactory:

    def __init__(self):
        self.name = FACTORY_NAME
        self.version = VERSION
        self.running = False

    async def start(self):
        """Start the News Factory."""

        self.running = True

        logger.info("=" * 60)
        logger.info(f"{self.name}")
        logger.info(f"Version: {self.version}")
        logger.info("=" * 60)

        logger.info("Starting News Factory...")
        logger.info(f"Startup time: {datetime.now().isoformat()}")

        # -------------------------------------------------
        # Future pipeline
        # -------------------------------------------------
        #
        # 1. Collect news
        # 2. Detect duplicate stories
        # 3. Analyze sources
        # 4. Verify important claims
        # 5. Determine story significance
        # 6. Find the strongest editorial angle
        # 7. Generate article
        # 8. Analyze reader psychology
        # 9. Quality-control article
        # 10. Publish to website
        # 11. Distribute to social platforms
        #
        # -------------------------------------------------

        logger.info("News Factory is online.")
        logger.info("Waiting for the first intelligence pipeline...")

    async def stop(self):
        """Stop the News Factory."""

        self.running = False
        logger.info("News Factory stopped.")


# ---------------------------------------------------------
# APPLICATION ENTRY POINT
# ---------------------------------------------------------

async def main():

    factory = NewsFactory()

    try:
        await factory.start()

        # Keep the application alive.
        while factory.running:
            await asyncio.sleep(5)

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user.")

    except Exception as error:
        logger.exception(f"Factory error: {error}")

    finally:
        await factory.stop()


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())
