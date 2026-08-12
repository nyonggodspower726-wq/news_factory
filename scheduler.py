"""
AI NEWS FACTORY
SCHEDULER - TEST MODE + LIVE NEWS COLLECTOR
Nigeria real-time clock
"""

import asyncio
import logging
import os
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo

import requests

from main import NewsFactory

logger=logging.getLogger("NewsFactory.Scheduler")

NIGERIA_TZ=ZoneInfo("Africa/Lagos")

# =========================================================
# EDIT ONLY THIS TIME
# FORMAT: HH:MM:SS
# =========================================================

TEST_RUN_TIME="14:38:00"

# =========================================================
# NEWS SETTINGS
# =========================================================

NEWS_API_KEY=os.getenv("NEWS_API_KEY","").strip()

NEWS_COUNTRY=os.getenv(
    "NEWS_COUNTRY",
    "ng"
).strip().lower()

NEWS_CATEGORY=os.getenv(
    "NEWS_CATEGORY",
    "general"
).strip().lower()

NEWS_PAGE_SIZE=int(
    os.getenv(
        "NEWS_PAGE_SIZE",
        "10"
    )
)

NEWS_QUERY=os.getenv(
    "NEWS_QUERY",
    ""
).strip()

NEWS_API_URL="https://newsapi.org/v2/top-headlines"


# =========================================================
# NEWS COLLECTOR
# =========================================================

class NewsCollector:

    def __init__(self):

        self.name="News Collector"
        self.version="1.0.0"

        self.api_key=NEWS_API_KEY
        self.country=NEWS_COUNTRY
        self.category=NEWS_CATEGORY
        self.page_size=NEWS_PAGE_SIZE
        self.query=NEWS_QUERY

    # =====================================================
    # STATUS
    # =====================================================

    def status(self):

        return {
            "status":
                "READY"
                if self.api_key
                else "NOT_CONFIGURED",

            "provider":
                "NewsAPI",

            "country":
                self.country,

            "category":
                self.category,

            "page_size":
                self.page_size,

            "query":
                self.query
                or None
        }

    # =====================================================
    # COLLECT
    # =====================================================

    def collect(self):

        if not self.api_key:

            raise RuntimeError(
                "NEWS_API_KEY is not configured in Railway Variables."
            )

        params={
            "country":
                self.country,

            "category":
                self.category,

            "pageSize":
                self.page_size,

            "apiKey":
                self.api_key
        }

        if self.query:

            params["q"]=self.query

        logger.info(
            "Collecting live news..."
        )

        response=requests.get(
            NEWS_API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data=response.json()

        if data.get("status")!="ok":

            raise RuntimeError(
                "NewsAPI error: "
                + str(
                    data.get(
                        "message",
                        "Unknown NewsAPI error"
                    )
                )
            )

        articles=data.get(
            "articles",
            []
        )

        if not isinstance(
            articles,
            list
        ):

            articles=[]

        sources=[]

        for article in articles:

            if not isinstance(
                article,
                dict
            ):
                continue

            title=str(
                article.get(
                    "title",
                    ""
                )
                or ""
            ).strip()

            description=str(
                article.get(
                    "description",
                    ""
                )
                or ""
            ).strip()

            url=str(
                article.get(
                    "url",
                    ""
                )
                or ""
            ).strip()

            if not title or not url:
                continue

            source_data=article.get(
                "source",
                {}
            )

            if not isinstance(
                source_data,
                dict
            ):
                source_data={}

            source_name=str(
                source_data.get(
                    "name",
                    ""
                )
                or ""
            ).strip()

            published_at=str(
                article.get(
                    "publishedAt",
                    ""
                )
                or ""
            ).strip()

            image_url=str(
                article.get(
                    "urlToImage",
                    ""
                )
                or ""
            ).strip()

            sources.append({

                "title":
                    title,

                "headline":
                    title,

                "description":
                    description,

                "content":
                    description,

                "url":
                    url,

                "source_url":
                    url,

                "source":
                    source_name,

                "source_name":
                    source_name,

                "published_at":
                    published_at,

                "publishedAt":
                    published_at,

                "image":
                    image_url,

                "image_url":
                    image_url
            })

        logger.info(
            "News collector found %s usable article(s).",
            len(sources)
        )

        return sources


# =========================================================
# SCHEDULER
# =========================================================

class NewsScheduler:

    def __init__(self):

        self.running=False

        self.factory=NewsFactory()

        self.news_collector=NewsCollector()

    # =====================================================
    # START
    # =====================================================

    async def start(self):

        self.running=True

        logger.info("="*60)
        logger.info(
            "AI NEWS FACTORY TEST SCHEDULER"
        )
        logger.info("="*60)

        logger.info(
            "Timezone: Africa/Lagos"
        )

        logger.info(
            "Test time: %s",
            TEST_RUN_TIME
        )

        logger.info("="*60)

        await self.factory.start()

        logger.info(
            "Factory initialized."
        )

        collector_status=(
            self.news_collector.status()
        )

        logger.info(
            "News collector status: %s",
            collector_status
        )

        await self.wait_until_test_time()

        if self.running:

            await self.run_cycle()

        self.running=False

        logger.info("="*60)
        logger.info(
            "TEST CYCLE FINISHED"
        )
        logger.info("="*60)

    # =====================================================
    # WAIT UNTIL TEST TIME
    # =====================================================

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

            minutes=(
                remaining%3600
            )//60

            seconds=(
                remaining%60
            )

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
        logger.info("="*60)
        logger.info(
            "FACTORY TEST CYCLE STARTED"
        )
        logger.info("="*60)

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
        # COLLECT LIVE NEWS
        # =================================================

        logger.info(
            "Starting live news collection..."
        )

        try:

            sources=await asyncio.to_thread(
                self.news_collector.collect
            )

        except Exception as error:

            logger.exception(
                "News collection failed: %s",
                error
            )

            return

        if not sources:

            logger.warning(
                "News collector returned zero articles."
            )

            return

        logger.info(
            "Collected %s live article(s).",
            len(sources)
        )

        # =================================================
        # BUILD STORY INPUT
        # =================================================

        primary=sources[0]

        story={

            "title":
                primary.get(
                    "title",
                    ""
                ),

            "headline":
                primary.get(
                    "headline",
                    primary.get(
                        "title",
                        ""
                    )
                ),

            "description":
                primary.get(
                    "description",
                    ""
                ),

            "content":
                primary.get(
                    "content",
                    primary.get(
                        "description",
                        ""
                    )
                ),

            "source_url":
                primary.get(
                    "source_url",
                    primary.get(
                        "url",
                        ""
                    )
                ),

            "source":
                primary.get(
                    "source_name",
                    primary.get(
                        "source",
                        ""
                    )
                ),

            "published_at":
                primary.get(
                    "published_at",
                    ""
                ),

            "image_url":
                primary.get(
                    "image_url",
                    ""
                )
        }

        topic=(
            primary.get(
                "title",
                ""
            )
        )

        logger.info(
            "Primary story: %s",
            story.get(
                "title",
                ""
            )
        )

        logger.info(
            "Sending live news to central factory..."
        )

        # =================================================
        # CENTRAL BRAIN
        # =================================================

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

            return

        # =================================================
        # RESULT
        # =================================================

        if isinstance(
            result,
            dict
        ):

            pipeline_status=result.get(
                "pipeline_status",
                result.get(
                    "status",
                    "UNKNOWN"
                )
            )

            logger.info(
                "Pipeline result: %s",
                pipeline_status
            )

            logger.info(
                "Factory intelligence cycle completed."
            )

        else:

            logger.warning(
                "Factory returned invalid result."
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
# START FUNCTION
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
# RUN
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
