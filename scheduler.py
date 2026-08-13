"""
AI NEWS FACTORY
SCHEDULER
Persistent automatic scheduler
Nigeria real-time clock
"""

import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from main import NewsFactory
from collectors.source_manager import source_manager


logger = logging.getLogger("NewsFactory.Scheduler")

NIGERIA_TZ = ZoneInfo("Africa/Lagos")


# =========================================================
# PRODUCTION SETTINGS
# =========================================================

# Automatic daily run times in Nigeria time.
RUN_TIMES = [
    "08:00:00",
    "14:00:00",
    "20:00:00",
]

NEWS_LIMIT = 30
NEWS_TOPIC = ""

# If Railway starts after one of today's scheduled times,
# wait for the NEXT scheduled time instead of immediately
# running a duplicate cycle.
RUN_IF_TIME_MISSED = False


class NewsScheduler:

    def __init__(self):
        self.running = False
        self.factory = NewsFactory()
        self.source_manager = source_manager

    # =====================================================
    # MAIN SCHEDULER
    # =====================================================

    async def start(self):

        self.running = True

        logger.info("=" * 70)
        logger.info("AI NEWS FACTORY - AUTOMATIC SCHEDULER")
        logger.info("=" * 70)
        logger.info("Timezone: Africa/Lagos")
        logger.info("Scheduled runs: %s", ", ".join(RUN_TIMES))
        logger.info("News limit: %s", NEWS_LIMIT)
        logger.info("Automatic repeating run: ENABLED")
        logger.info("Live publishing automation: ENABLED")
        logger.info("=" * 70)

        # Initialize factory once.
        try:
            await self.factory.start()
            logger.info("Factory initialized successfully.")
        except Exception as exc:
            logger.exception("Factory initialization failed: %s", exc)
            self.running = False
            raise

        try:
            logger.info(
                "Source manager: %s",
                self.source_manager.status()
            )
        except Exception as exc:
            logger.warning(
                "Source manager status unavailable: %s",
                exc
            )

        # =================================================
        # PERMANENT LOOP
        # =================================================

        while self.running:

            try:

                target = self._next_run_time()

                await self._wait_until(target)

                if not self.running:
                    break

                logger.info("=" * 70)
                logger.info("SCHEDULED TIME REACHED")
                logger.info(
                    "Nigeria time: %s",
                    datetime.now(NIGERIA_TZ).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
                logger.info("=" * 70)

                result = await self.run_cycle()

                status = "UNKNOWN"

                if isinstance(result, dict):
                    status = result.get(
                        "pipeline_status",
                        result.get("status", "UNKNOWN")
                    )

                logger.info("=" * 70)
                logger.info("FACTORY CYCLE COMPLETE")
                logger.info("Pipeline status: %s", status)
                logger.info("Scheduler remains ACTIVE.")
                logger.info("Next scheduled run will be calculated automatically.")
                logger.info("=" * 70)

                # Small pause prevents an accidental immediate
                # duplicate execution.
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                logger.info("Scheduler task cancelled.")
                break

            except Exception as exc:
                logger.exception(
                    "Scheduler cycle failed: %s",
                    exc
                )

                # IMPORTANT:
                # Do NOT terminate the scheduler because one cycle failed.
                # Wait briefly and continue with the next scheduled run.
                await asyncio.sleep(10)

        logger.info("Scheduler main loop exited.")

    # =====================================================
    # FIND NEXT SCHEDULED TIME
    # =====================================================

    def _next_run_time(self):

        now = datetime.now(NIGERIA_TZ)

        candidates = []

        for time_string in RUN_TIMES:

            try:
                hour, minute, second = map(
                    int,
                    time_string.split(":")
                )

            except ValueError:
                raise ValueError(
                    f"Invalid RUN_TIMES value: {time_string}. "
                    "Use HH:MM:SS."
                )

            if not (
                0 <= hour <= 23
                and 0 <= minute <= 59
                and 0 <= second <= 59
            ):
                raise ValueError(
                    f"Invalid scheduled time: {time_string}"
                )

            candidate = now.replace(
                hour=hour,
                minute=minute,
                second=second,
                microsecond=0
            )

            if candidate > now:
                candidates.append(candidate)

        # There is no remaining run today.
        # Schedule the first run tomorrow.
        if not candidates:

            first_time = sorted(RUN_TIMES)[0]

            hour, minute, second = map(
                int,
                first_time.split(":")
            )

            tomorrow = now + timedelta(days=1)

            return tomorrow.replace(
                hour=hour,
                minute=minute,
                second=second,
                microsecond=0
            )

        return min(candidates)

    # =====================================================
    # WAIT FOR NEXT RUN
    # =====================================================

    async def _wait_until(self, target):

        logger.info("=" * 70)
        logger.info("NEXT AUTOMATIC RUN")
        logger.info(
            "Scheduled: %s",
            target.strftime("%Y-%m-%d %H:%M:%S")
        )
        logger.info("=" * 70)

        while self.running:

            now = datetime.now(NIGERIA_TZ)

            remaining = int(
                (target - now).total_seconds()
            )

            if remaining <= 0:
                print()
                return

            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            seconds = remaining % 60

            print(
                f"\rNigeria Time: {now.strftime('%H:%M:%S')} | "
                f"Next Run: {target.strftime('%H:%M:%S')} | "
                f"Remaining: "
                f"{hours:02d}:{minutes:02d}:{seconds:02d}",
                end="",
                flush=True
            )

            await asyncio.sleep(1)

    # =====================================================
    # RUN ONE FACTORY CYCLE
    # =====================================================

    async def run_cycle(self):

        now = datetime.now(NIGERIA_TZ)

        logger.info("=" * 70)
        logger.info("FACTORY AUTOMATIC CYCLE STARTED")
        logger.info(
            "Nigeria time: %s",
            now.strftime("%Y-%m-%d %H:%M:%S")
        )
        logger.info("=" * 70)

        # -------------------------------------------------
        # COLLECT NEWS
        # -------------------------------------------------

        logger.info(
            "Collecting live news from configured sources..."
        )

        try:

            collection = await self.source_manager.collect(
                topic=NEWS_TOPIC,
                limit=NEWS_LIMIT
            )

        except Exception as exc:

            logger.exception(
                "Source collection failed: %s",
                exc
            )

            return {
                "status": "COLLECTION_FAILED",
                "error": str(exc)
            }

        if not isinstance(collection, dict):

            logger.error(
                "Source manager returned invalid data."
            )

            return {
                "status": "COLLECTION_FAILED",
                "error": "Invalid collection response."
            }

        sources = collection.get("sources", [])

        if not isinstance(sources, list):
            sources = []

        logger.info(
            "Collection status: %s",
            collection.get("status", "UNKNOWN")
        )

        logger.info(
            "Total normalized sources: %s",
            len(sources)
        )

        # -------------------------------------------------
        # SOURCE STATUS
        # -------------------------------------------------

        collector_status = collection.get(
            "collector_status",
            []
        )

        if isinstance(collector_status, list):

            for item in collector_status:

                if not isinstance(item, dict):
                    continue

                logger.info(
                    "SOURCE | %s | %s | count=%s",
                    item.get("name", "UNKNOWN"),
                    item.get("status", "UNKNOWN"),
                    item.get("count", "-")
                )

        errors = collection.get("errors", [])

        if errors:
            logger.warning(
                "Source warnings: %s",
                errors
            )

        # -------------------------------------------------
        # NO NEWS
        # -------------------------------------------------

        if not sources:

            logger.warning(
                "ZERO usable news stories collected."
            )

            logger.warning(
                "Brain will NOT be called."
            )

            return {
                "status": "NO_NEWS",
                "collection": collection
            }

        # -------------------------------------------------
        # PRIMARY STORY
        # -------------------------------------------------

        primary = self._select_primary(sources)

        if not primary:

            logger.warning(
                "Could not select a primary story."
            )

            return {
                "status": "NO_PRIMARY_STORY",
                "collection": collection
            }

        story = self._build_story(primary)

        topic = NEWS_TOPIC or story.get(
            "title",
            ""
        )

        logger.info("=" * 70)
        logger.info("PRIMARY STORY")
        logger.info(
            "Title: %s",
            story.get("title", "")
        )
        logger.info(
            "Source: %s",
            story.get("source", "")
        )
        logger.info(
            "URL: %s",
            story.get("source_url", "")
        )
        logger.info(
            "Additional sources: %s",
            max(len(sources) - 1, 0)
        )
        logger.info("=" * 70)

        # -------------------------------------------------
        # SEND TO BRAIN
        # -------------------------------------------------

        logger.info(
            "Sending %s collected sources to NewsFactory...",
            len(sources)
        )

        try:

            result = await self.factory.process_story(
                sources=sources,
                story=story,
                topic=topic
            )

        except Exception as exc:

            logger.exception(
                "Factory processing failed: %s",
                exc
            )

            return {
                "status": "FACTORY_FAILED",
                "error": str(exc),
                "collection": collection
            }

        if not isinstance(result, dict):

            logger.warning(
                "Factory returned non-dictionary result."
            )

            return {
                "status": "INVALID_FACTORY_RESULT",
                "result": result
            }

        status = result.get(
            "pipeline_status",
            result.get("status", "UNKNOWN")
        )

        logger.info("=" * 70)
        logger.info("FACTORY RESULT")
        logger.info(
            "Pipeline status: %s",
            status
        )
        logger.info(
            "Brain completed: YES"
        )
        logger.info(
            "Automatic repeating cycle: YES"
        )
        logger.info(
            "Scheduler remains ACTIVE: YES"
        )
        logger.info("=" * 70)

        return result

    # =====================================================
    # PRIMARY STORY SELECTION
    # =====================================================

    def _select_primary(self, sources):

        valid = []

        for item in sources:

            if not isinstance(item, dict):
                continue

            title = str(
                item.get(
                    "title",
                    item.get("headline", "")
                ) or ""
            ).strip()

            content = str(
                item.get(
                    "content",
                    item.get(
                        "description",
                        item.get("summary", "")
                    )
                ) or ""
            ).strip()

            if not title:
                continue

            score = 0

            if content:
                score += 30

            if len(content) >= 200:
                score += 20

            if item.get("source_url") or item.get("url"):
                score += 15

            if item.get("published_at"):
                score += 10

            if item.get("source") or item.get("publisher"):
                score += 10

            if item.get("image_url"):
                score += 5

            valid.append(
                (score, item)
            )

        if not valid:
            return None

        valid.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return valid[0][1]

    # =====================================================
    # STORY NORMALIZATION
    # =====================================================

    def _build_story(self, primary):

        title = str(
            primary.get(
                "title",
                primary.get("headline", "")
            ) or ""
        ).strip()

        description = str(
            primary.get(
                "description",
                primary.get("summary", "")
            ) or ""
        ).strip()

        content = str(
            primary.get(
                "content",
                primary.get(
                    "text",
                    primary.get(
                        "body",
                        description
                    )
                )
            ) or ""
        ).strip()

        url = str(
            primary.get(
                "source_url",
                primary.get("url", "")
            ) or ""
        ).strip()

        source = primary.get(
            "source",
            primary.get(
                "publisher",
                primary.get("name", "")
            )
        )

        source = str(source or "").strip()

        return {
            "title": title,
            "headline": title,
            "description": description,
            "summary": description,
            "content": content,
            "body": content,
            "source": source,
            "source_name": source,
            "source_url": url,
            "url": url,
            "published_at": primary.get(
                "published_at"
            ),
            "image_url": str(
                primary.get(
                    "image_url",
                    ""
                ) or ""
            )
        }

    # =====================================================
    # STOP
    # =====================================================

    async def stop(self):

        if not self.running:
            return

        self.running = False

        try:

            await self.factory.stop()

        except Exception as exc:

            logger.exception(
                "Factory shutdown failed: %s",
                exc
            )

        logger.info(
            "Scheduler stopped."
        )


# =========================================================
# ENTRY POINT
# =========================================================

async def start_scheduler():

    scheduler = NewsScheduler()

    try:

        await scheduler.start()

    except KeyboardInterrupt:

        logger.info(
            "Shutdown requested."
        )

    except Exception as exc:

        logger.exception(
            "Scheduler failed: %s",
            exc
        )

    finally:

        await scheduler.stop()


# =========================================================
# DIRECT EXECUTION
# =========================================================

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    asyncio.run(
        start_scheduler()
        )
