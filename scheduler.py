"""
AI NEWS FACTORY
SCHEDULER - TEST MODE ONLY
Nigeria real-time clock
One controlled collection/brain test
"""

import asyncio,logging
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo

from main import NewsFactory
from collectors.source_manager import source_manager

logger=logging.getLogger("NewsFactory.Scheduler")
NIGERIA_TZ=ZoneInfo("Africa/Lagos")

# =========================================================
# TEST SETTINGS - EDIT THESE ONLY
# =========================================================
TEST_RUN_TIME="12:47:00"
NEWS_LIMIT=30
NEWS_TOPIC=""
RUN_IF_TIME_MISSED=True

class NewsScheduler:
    def __init__(self):
        self.running=False
        self.factory=NewsFactory()
        self.source_manager=source_manager
        self.test_completed=False

    async def start(self):
        self.running=True
        logger.info("="*70)
        logger.info("AI NEWS FACTORY - TEST MODE")
        logger.info("="*70)
        logger.info("Timezone: Africa/Lagos")
        logger.info("Test run time: %s",TEST_RUN_TIME)
        logger.info("News limit: %s",NEWS_LIMIT)
        logger.info("Automatic repeating run: DISABLED")
        logger.info("Live publishing automation: DISABLED")
        logger.info("="*70)

        await self.factory.start()
        logger.info("Factory initialized.")

        try:
            logger.info("Source manager: %s",self.source_manager.status())
        except Exception as exc:
            logger.warning("Source manager status unavailable: %s",exc)

        await self.wait_until_test_time()

        if not self.running:
            return

        result=await self.run_cycle()
        self.test_completed=True
        self.running=False

        logger.info("="*70)
        logger.info("SINGLE TEST RUN FINISHED")
        logger.info("No second automatic cycle will run.")
        logger.info("="*70)
        return result

    async def wait_until_test_time(self):
        try:
            parts=TEST_RUN_TIME.split(":")
            if len(parts)!=3:
                raise ValueError
            hour,minute,second=map(int,parts)
            if not (0<=hour<=23 and 0<=minute<=59 and 0<=second<=59):
                raise ValueError
        except ValueError:
            raise ValueError("TEST_RUN_TIME must use HH:MM:SS, e.g. 15:30:00")

        now=datetime.now(NIGERIA_TZ)
        target=now.replace(hour=hour,minute=minute,second=second,microsecond=0)

        if target<=now:
            if RUN_IF_TIME_MISSED:
                logger.info("Configured test time has passed today; running the single test now.")
                return
            target+=timedelta(days=1)

        while self.running:
            now=datetime.now(NIGERIA_TZ)
            remaining=max(0,int((target-now).total_seconds()))
            hours=remaining//3600
            minutes=(remaining%3600)//60
            seconds=remaining%60

            print(
                f"\rNigeria Time: {now.strftime('%H:%M:%S')} | "
                f"Scheduled: {TEST_RUN_TIME} | "
                f"Remaining: {hours:02d}:{minutes:02d}:{seconds:02d}",
                end="",
                flush=True
            )

            if remaining<=0:
                print()
                logger.info("TEST TIME REACHED.")
                return

            await asyncio.sleep(1)

    async def run_cycle(self):
        now=datetime.now(NIGERIA_TZ)
        logger.info("="*70)
        logger.info("FACTORY TEST CYCLE STARTED")
        logger.info("Nigeria time: %s",now.strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("="*70)

        # -------------------------------------------------
        # COLLECT FROM ALL CONFIGURED SOURCES
        # -------------------------------------------------
        logger.info("Collecting live news from configured sources...")

        try:
            collection=await self.source_manager.collect(
                topic=NEWS_TOPIC,
                limit=NEWS_LIMIT
            )
        except Exception as exc:
            logger.exception("Source collection failed: %s",exc)
            return {"status":"COLLECTION_FAILED","error":str(exc)}

        if not isinstance(collection,dict):
            logger.error("Source manager returned invalid data.")
            return {"status":"COLLECTION_FAILED","error":"Invalid collection response."}

        sources=collection.get("sources",[])
        if not isinstance(sources,list):
            sources=[]

        logger.info("Collection status: %s",collection.get("status","UNKNOWN"))
        logger.info("Total normalized sources: %s",len(sources))

        for item in collection.get("collector_status",[]):
            logger.info("SOURCE | %s | %s | count=%s",item.get("name","UNKNOWN"),item.get("status","UNKNOWN"),item.get("count","-"))

        errors=collection.get("errors",[])
        if errors:
            logger.warning("Source warnings: %s",errors)

        if not sources:
            logger.warning("ZERO usable news stories collected.")
            logger.warning("Brain will NOT be called.")
            return {"status":"NO_NEWS","collection":collection}

        # -------------------------------------------------
        # CHOOSE PRIMARY STORY
        # -------------------------------------------------
        primary=self._select_primary(sources)

        if not primary:
            logger.warning("Could not select a primary story.")
            return {"status":"NO_PRIMARY_STORY","collection":collection}

        story=self._build_story(primary)
        topic=NEWS_TOPIC or story.get("title","")

        logger.info("PRIMARY STORY")
        logger.info("Title: %s",story.get("title",""))
        logger.info("Source: %s",story.get("source",""))
        logger.info("URL: %s",story.get("source_url",""))
        logger.info("Additional sources: %s",max(len(sources)-1,0))

        # -------------------------------------------------
        # SEND TO MAIN / BRAIN
        # -------------------------------------------------
        logger.info("Sending %s collected sources to NewsFactory...",len(sources))

        try:
            result=await self.factory.process_story(
                sources=sources,
                story=story,
                topic=topic
            )
        except Exception as exc:
            logger.exception("Factory processing failed: %s",exc)
            return {"status":"FACTORY_FAILED","error":str(exc),"collection":collection}

        if not isinstance(result,dict):
            logger.warning("Factory returned non-dictionary result.")
            return {"status":"INVALID_FACTORY_RESULT","result":result}

        status=result.get("pipeline_status",result.get("status","UNKNOWN"))

        logger.info("="*70)
        logger.info("TEST RESULT")
        logger.info("Pipeline status: %s",status)
        logger.info("Brain completed: YES")
        logger.info("Automatic repeating cycle: NO")
        logger.info("================================================================")

        return result

    def _select_primary(self,sources):
        valid=[]
        for item in sources:
            if not isinstance(item,dict):
                continue
            title=str(item.get("title",item.get("headline","")) or "").strip()
            content=str(item.get("content",item.get("description",item.get("summary",""))) or "").strip()
            if not title:
                continue
            score=0
            if content: score+=30
            if len(content)>=200: score+=20
            if item.get("source_url") or item.get("url"): score+=15
            if item.get("published_at"): score+=10
            if item.get("source") or item.get("publisher"): score+=10
            if item.get("image_url"): score+=5
            valid.append((score,item))
        if not valid:
            return None
        valid.sort(key=lambda x:x[0],reverse=True)
        return valid[0][1]

    def _build_story(self,primary):
        title=str(primary.get("title",primary.get("headline","")) or "").strip()
        description=str(primary.get("description",primary.get("summary","")) or "").strip()
        content=str(primary.get("content",primary.get("text",primary.get("body",description))) or "").strip()
        url=str(primary.get("source_url",primary.get("url","")) or "").strip()
        source=primary.get("source",primary.get("publisher",primary.get("name","")))
        source=str(source or "").strip()
        return {
            "title":title,
            "headline":title,
            "description":description,
            "summary":description,
            "content":content,
            "body":content,
            "source":source,
            "source_name":source,
            "source_url":url,
            "url":url,
            "published_at":primary.get("published_at"),
            "image_url":str(primary.get("image_url","") or "")
        }

    async def stop(self):
        if not self.running:
            return
        self.running=False
        try:
            await self.factory.stop()
        except Exception as exc:
            logger.exception("Factory shutdown failed: %s",exc)
        logger.info("Scheduler stopped.")

async def start_scheduler():
    scheduler=NewsScheduler()
    try:
        return await scheduler.start()
    except KeyboardInterrupt:
        logger.info("Shutdown requested.")
    except Exception as exc:
        logger.exception("Scheduler failed: %s",exc)
    finally:
        await scheduler.stop()

if __name__=="__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    asyncio.run(start_scheduler())
