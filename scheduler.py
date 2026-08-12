"""
AI NEWS FACTORY
SCHEDULER - TEST MODE
Nigeria real-time clock
Live source collection
"""

import asyncio
import logging
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo

from main import NewsFactory
from collectors.source_manager import source_manager

logger=logging.getLogger("NewsFactory.Scheduler")

NIGERIA_TZ=ZoneInfo("Africa/Lagos")

# =========================================================
# EDIT ONLY THIS TIME
# FORMAT: HH:MM:SS
# =========================================================

TEST_RUN_TIME="14:16:00"

# =========================================================
# COLLECTION SETTINGS
# =========================================================

NEWS_LIMIT=30
NEWS_TOPIC=""

class NewsScheduler:

    def __init__(self):

        self.running=False
        self.factory=NewsFactory()
        self.source_manager=source_manager

    # =====================================================
    # START
    # =====================================================

    async def start(self):

        self.running=True

        logger.info("")
        logger.info("="*70)
        logger.info("AI NEWS FACTORY - TEST SCHEDULER")
        logger.info("="*70)
        logger.info(
            "Timezone: Africa/Lagos"
        )
        logger.info(
            "Test time: %s",
            TEST_RUN_TIME
        )
        logger.info(
            "News source limit: %s",
            NEWS_LIMIT
        )
        logger.info("="*70)

        await self.factory.start()

        logger.info(
            "Factory initialized successfully."
        )

        try:

            source_status=self.source_manager.status()

            logger.info(
                "Source manager: %s",
                source_status
            )

        except Exception as error:

            logger.exception(
                "Source manager status failed: %s",
                error
            )

        await self.wait_until_test_time()

        if self.running:

            await self.run_cycle()

        self.running=False

        logger.info("")
        logger.info("="*70)
        logger.info(
            "TEST CYCLE FINISHED"
        )
        logger.info("="*70)

    # =====================================================
    # WAIT FOR TEST TIME
    # =====================================================

    async def wait_until_test_time(self):

        try:

            hour,minute,second=map(
                int,
                TEST_RUN_TIME.split(":")
            )

            if not (
                0<=hour<=23
                and
                0<=minute<=59
                and
                0<=second<=59
            ):
                raise ValueError

        except ValueError:

            raise ValueError(
                "TEST_RUN_TIME must use HH:MM:SS format."
            )

        while self.running:

            now=datetime.now(
                NIGERIA_TZ
            )

            target=now.replace(
                hour=hour,
                minute=minute,
                second=second,
                microsecond=0
            )

            if target<=now:

                target+=timedelta(
                    days=1
                )

            remaining=max(
                0,
                int(
                    (
                        target-now
                    ).total_seconds()
                )
            )

            hours=remaining//3600

            minutes=(remaining%3600)//60

            seconds=remaining%60

            print(
                "\r"
                f"Nigeria Time: "
                f"{now.strftime('%H:%M:%S')}"
                f" | Scheduled: "
                f"{TEST_RUN_TIME}"
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

    # =====================================================
    # ONE FACTORY CYCLE
    # =====================================================

    async def run_cycle(self):

        logger.info("")
        logger.info("="*70)
        logger.info(
            "FACTORY TEST CYCLE STARTED"
        )
        logger.info("="*70)

        now=datetime.now(
            NIGERIA_TZ
        )

        logger.info(
            "Nigeria time: %s",
            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        # =================================================
        # 1. COLLECT LIVE NEWS
        # =================================================

        logger.info(
            "Starting live source collection..."
        )

        try:

            collection=await self.source_manager.collect(
                topic=NEWS_TOPIC,
                limit=NEWS_LIMIT
            )

        except Exception as error:

            logger.exception(
                "Source collection failed: %s",
                error
            )

            return {
                "status":"COLLECTION_FAILED",
                "error":str(error)
            }

        if not isinstance(
            collection,
            dict
        ):

            logger.error(
                "Source manager returned invalid data."
            )

            return {
                "status":"COLLECTION_FAILED",
                "error":"Invalid source manager response."
            }

        sources=collection.get(
            "sources",
            []
        )

        if not isinstance(
            sources,
            list
        ):

            sources=[]

        logger.info(
            "Collection status: %s",
            collection.get(
                "status",
                "UNKNOWN"
            )
        )

        logger.info(
            "Sources collected: %s",
            len(sources)
        )

        errors=collection.get(
            "errors",
            []
        )

        if errors:

            logger.warning(
                "Source warnings/errors: %s",
                errors
            )

        # =================================================
        # 2. STOP IF NO NEWS
        # =================================================

        if not sources:

            logger.warning(
                "No usable news sources were collected."
            )

            logger.warning(
                "Brain will NOT be called with an empty package."
            )

            return {
                "status":"NO_NEWS",
                "collection":collection
            }

        # =================================================
        # 3. SELECT PRIMARY STORY
        # =================================================

        primary=sources[0]

        if not isinstance(
            primary,
            dict
        ):

            logger.error(
                "Primary source is invalid."
            )

            return {
                "status":"INVALID_PRIMARY_SOURCE"
            }

        title=str(
            primary.get(
                "title",
                primary.get(
                    "headline",
                    ""
                )
            )
            or ""
        ).strip()

        description=str(
            primary.get(
                "description",
                primary.get(
                    "summary",
                    ""
                )
            )
            or ""
        ).strip()

        content=str(
            primary.get(
                "content",
                primary.get(
                    "text",
                    primary.get(
                        "body",
                        description
                    )
                )
            )
            or ""
        ).strip()

        source_url=str(
            primary.get(
                "source_url",
                primary.get(
                    "url",
                    ""
                )
            )
            or ""
        ).strip()

        source_name=str(
            primary.get(
                "source",
                primary.get(
                    "publisher",
                    primary.get(
                        "name",
                        ""
                    )
                )
            )
            or ""
        ).strip()

        image_url=str(
            primary.get(
                "image_url",
                ""
            )
            or ""
        ).strip()

        published_at=primary.get(
            "published_at"
        )

        # =================================================
        # 4. BUILD STORY
        # =================================================

        story={

            "title":
                title,

            "headline":
                title,

            "description":
                description,

            "summary":
                description,

            "content":
                content,

            "body":
                content,

            "source":
                source_name,

            "source_name":
                source_name,

            "source_url":
                source_url,

            "url":
                source_url,

            "published_at":
                published_at,

            "image_url":
                image_url
        }

        topic=(
            NEWS_TOPIC
            or
            title
        )

        logger.info(
            "Primary story selected:"
        )

        logger.info(
            "TITLE: %s",
            title
        )

        logger.info(
            "SOURCE: %s",
            source_name
        )

        logger.info(
            "URL: %s",
            source_url
        )

        logger.info(
            "Additional sources available: %s",
            max(
                len(sources)-1,
                0
            )
        )

        # =================================================
        # 5. SEND TO CENTRAL FACTORY
        # =================================================

        logger.info("")
        logger.info(
            "Sending collected news to NewsFactory..."
        )

        try:

            result=await self.factory.process_story(
                sources=sources,
                story=story,
                topic=topic
            )

        except Exception as error:

            logger.exception(
                "Central factory processing failed: %s",
                error
            )

            return {
                "status":"FACTORY_FAILED",
                "error":str(error),
                "collection":collection
            }

        # =================================================
        # 6. REPORT RESULT
        # =================================================

        if not isinstance(
            result,
            dict
        ):

            logger.warning(
                "Factory returned non-dictionary result."
            )

            return {
                "status":"INVALID_FACTORY_RESULT",
                "result":result
            }

        pipeline_status=result.get(
            "pipeline_status",
            result.get(
                "status",
                "UNKNOWN"
            )
        )

        logger.info("")
        logger.info("="*70)
        logger.info(
            "BRAIN / FACTORY RESULT"
        )
        logger.info("="*70)

        logger.info(
            "Pipeline status: %s",
            pipeline_status
        )

        logger.info(
            "Factory test cycle completed."
        )

        return result

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
# START
# =========================================================

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


# =========================================================
# RUN DIRECTLY
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
