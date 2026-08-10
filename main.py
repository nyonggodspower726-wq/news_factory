"""
AI NEWS FACTORY
MAIN CONTROLLER

The main application talks to the central BrainPipeline.

Individual brain engines should NOT be called directly from here.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

from config import FACTORY_NAME, VERSION
from brain.pipeline import BrainPipeline


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("NewsFactory")


# =========================================================
# NEWS FACTORY
# =========================================================

class NewsFactory:

    def __init__(self):

        self.name = FACTORY_NAME
        self.version = VERSION

        self.running = False

        # ONE connection to the entire brain system.
        self.brain = BrainPipeline()

    # =====================================================
    # START
    # =====================================================

    async def start(self):

        self.running = True

        logger.info("=" * 60)
        logger.info(self.name)
        logger.info(f"Version: {self.version}")
        logger.info("=" * 60)

        logger.info("Starting News Factory...")
        logger.info(
            f"Startup time: "
            f"{datetime.now().isoformat()}"
        )

        # -------------------------------------------------
        # BRAIN STATUS
        # -------------------------------------------------

        status = self.brain.status()

        logger.info(
            "Brain system loaded: %s/%s",
            status["loaded_brains"],
            status["total_brains"]
        )

        for brain_name, state in status[
            "brains"
        ].items():

            logger.info(
                "BRAIN | %s | %s",
                brain_name,
                state
            )

        logger.info(
            "News Factory is online."
        )

    # =====================================================
    # PROCESS STORY
    # =====================================================

    async def process_story(
        self,
        sources: List[Dict[str, Any]],
        story: Dict[str, Any] = None,
        topic: str = ""
    ) -> Dict[str, Any]:

        if not self.running:

            raise RuntimeError(
                "News Factory is not running."
            )

        logger.info(
            "Starting intelligence pipeline..."
        )

        result = await asyncio.to_thread(
            self.brain.run,
            sources,
            story,
            topic
        )

        logger.info(
            "Brain pipeline completed."
        )

        logger.info(
            "Pipeline status: %s",
            result.get(
                "pipeline_status",
                "UNKNOWN"
            )
        )

        return result

    # =====================================================
    # STOP
    # =====================================================

    async def stop(self):

        if not self.running:
            return

        self.running = False

        logger.info(
            "News Factory stopped."
        )


# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

async def main():

    factory = NewsFactory()

    try:

        await factory.start()

        # -------------------------------------------------
        # KEEP FACTORY ALIVE
        # -------------------------------------------------

        while factory.running:

            await asyncio.sleep(5)

    except KeyboardInterrupt:

        logger.info(
            "Shutdown requested by user."
        )

    except Exception as error:

        logger.exception(
            "Factory error: %s",
            error
        )

    finally:

        await factory.stop()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())
