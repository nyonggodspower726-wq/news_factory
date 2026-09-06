import asyncio,logging,os,threading
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from main import NewsFactory
from collectors.source_manager import source_manager

logger=logging.getLogger("NewsFactory.Scheduler")
NIGERIA_TZ=ZoneInfo("Africa/Lagos")
RUN_TIME="20:37:00"
NEWS_LIMIT=30
NEWS_TOPIC=""
RUN_IF_TIME_MISSED=False
MEDIA_DIR=Path("media/generated")
HTTP_HOST="0.0.0.0"
HTTP_PORT=int(os.getenv("PORT","8088"))

class MediaHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=self.path.split("?",1)[0]
        if path in ("/","/health","/healthz"):
            body=b"AI News Factory is online."
            self.send_response(200)
            self.send_header("Content-Type","text/plain; charset=utf-8")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        filename=Path(path.lstrip("/")).name
        if filename and filename.lower().endswith((".png",".jpg",".jpeg",".webp")):
            file_path=MEDIA_DIR/filename
            if file_path.exists() and file_path.is_file():
                data=file_path.read_bytes()
                ext=file_path.suffix.lower()
                content_type={".png":"image/png",".jpg":"image/jpeg",".jpeg":"image/jpeg",".webp":"image/webp"}.get(ext,"application/octet-stream")
                self.send_response(200)
                self.send_header("Content-Type",content_type)
                self.send_header("Content-Length",str(len(data)))
                self.send_header("Cache-Control","public, max-age=86400")
                self.end_headers()
                self.wfile.write(data)
                return
        self.send_response(404)
        self.send_header("Content-Type","text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Not found.")
    def log_message(self,format,*args):
        logger.info("HTTP | %s",format%args)

class NewsScheduler:
    def __init__(self):
        self.running=False
        self.factory=NewsFactory()
        self.source_manager=source_manager
        self.http_server=None
        self.http_thread=None

    def start_http_server(self):
        MEDIA_DIR.mkdir(parents=True,exist_ok=True)
        self.http_server=ThreadingHTTPServer((HTTP_HOST,HTTP_PORT),MediaHandler)
        self.http_thread=threading.Thread(target=self.http_server.serve_forever,daemon=True)
        self.http_thread.start()
        logger.info("HTTP server started on %s:%s",HTTP_HOST,HTTP_PORT)
        logger.info("Media directory: %s",MEDIA_DIR.resolve())

    def stop_http_server(self):
        if self.http_server:
            try:
                self.http_server.shutdown()
                self.http_server.server_close()
            except Exception as exc:
                logger.warning("HTTP server shutdown warning: %s",exc)
            self.http_server=None
            self.http_thread=None
            logger.info("HTTP server stopped.")

    async def start(self):
        self.running=True
        logger.info("="*70)
        logger.info("AI NEWS FACTORY - SINGLE TIME SCHEDULER")
        logger.info("="*70)
        logger.info("Timezone: Africa/Lagos")
        logger.info("Daily run time: %s",RUN_TIME)
        logger.info("News limit: %s",NEWS_LIMIT)
        logger.info("Persistent scheduler: ENABLED")
        logger.info("Automatic publishing: ENABLED")
        logger.info("Automatic publication failover: ENABLED")
        logger.info("="*70)
        try:
            self.start_http_server()
        except Exception as exc:
            logger.exception("HTTP server failed to start: %s",exc)
        await self.factory.start()
        try:
            logger.info("Source manager: %s",self.source_manager.status())
        except Exception as exc:
            logger.warning("Source manager status unavailable: %s",exc)
        while self.running:
            try:
                target=self._next_run_time()
                await self._wait_until(target)
                if not self.running:
                    break
                logger.info("="*70)
                logger.info("SCHEDULED TIME REACHED")
                logger.info("Nigeria time: %s",datetime.now(NIGERIA_TZ).strftime("%Y-%m-%d %H:%M:%S"))
                logger.info("="*70)
                result=await self.run_cycle()
                status="UNKNOWN"
                if isinstance(result,dict):
                    status=result.get("pipeline_status",result.get("status","UNKNOWN"))
                logger.info("="*70)
                logger.info("FACTORY CYCLE COMPLETE")
                logger.info("Pipeline status: %s",status)
                logger.info("Scheduler remains ACTIVE.")
                logger.info("Next daily run: %s",RUN_TIME)
                logger.info("="*70)
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                logger.info("Scheduler cancelled.")
                raise
            except Exception as exc:
                logger.exception("Scheduler cycle failed: %s",exc)
                await asyncio.sleep(10)
        logger.info("Scheduler stopped.")

    def _parse_run_time(self):
        try:
            parts=RUN_TIME.split(":")
            if len(parts)!=3:
                raise ValueError
            hour,minute,second=map(int,parts)
            if not(0<=hour<=23 and 0<=minute<=59 and 0<=second<=59):
                raise ValueError
            return hour,minute,second
        except ValueError:
            raise ValueError("RUN_TIME must use HH:MM:SS format, e.g. 13:30:00")

    def _next_run_time(self):
        hour,minute,second=self._parse_run_time()
        now=datetime.now(NIGERIA_TZ)
        target=now.replace(hour=hour,minute=minute,second=second,microsecond=0)
        if target>now:
            return target
        if RUN_IF_TIME_MISSED:
            logger.info("Today's scheduled time has passed. Running now.")
            return now
        return target+timedelta(days=1)

    async def _wait_until(self,target):
        logger.info("="*70)
        logger.info("NEXT RUN: %s",target.strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("="*70)
        while self.running:
            now=datetime.now(NIGERIA_TZ)
            remaining=int((target-now).total_seconds())
            if remaining<=0:
                print()
                return
            hours=remaining//3600
            minutes=(remaining%3600)//60
            seconds=remaining%60
            print(f"\rNigeria Time: {now.strftime('%H:%M:%S')} | Scheduled: {RUN_TIME} | Remaining: {hours:02d}:{minutes:02d}:{seconds:02d}",end="",flush=True)
            await asyncio.sleep(1)

    async def run_cycle(self):
        now=datetime.now(NIGERIA_TZ)
        logger.info("="*70)
        logger.info("FACTORY CYCLE STARTED")
        logger.info("Nigeria time: %s",now.strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("="*70)
        logger.info("Collecting live news from configured sources...")
        try:
            collection=await self.source_manager.collect(topic=NEWS_TOPIC,limit=NEWS_LIMIT)
        except Exception as exc:
            logger.exception("Source collection failed: %s",exc)
            return {"status":"COLLECTION_FAILED","error":str(exc)}
        if not isinstance(collection,dict):
            return {"status":"COLLECTION_FAILED","error":"Invalid collection response."}
        sources=collection.get("sources",[])
        if not isinstance(sources,list):
            sources=[]
        logger.info("Collection status: %s",collection.get("status","UNKNOWN"))
        logger.info("Total normalized sources: %s",len(sources))
        collector_status=collection.get("collector_status",[])
        if isinstance(collector_status,list):
            for item in collector_status:
                if isinstance(item,dict):
                    logger.info("SOURCE | %s | %s | count=%s",item.get("name","UNKNOWN"),item.get("status","UNKNOWN"),item.get("count","-"))
        errors=collection.get("errors",[])
        if errors:
            logger.warning("Source warnings: %s",errors)
        if not sources:
            logger.warning("ZERO usable news stories collected.")
            return {"status":"NO_NEWS","collection":collection}
        candidates=self._rank_candidates(sources)
        if not candidates:
            logger.warning("Could not find usable news stories.")
            return {"status":"NO_PRIMARY_STORY","collection":collection}
        logger.info("="*70)
        logger.info("PUBLICATION FAILOVER ENGINE")
        logger.info("Candidate stories available: %s",len(candidates))
        logger.info("="*70)
        if not self.factory.running:
            logger.info("News Factory is not running. Starting factory for this cycle...")
            await self.factory.start()
        attempts=[]
        for index,primary in enumerate(candidates,1):
            story=self._build_story(primary)
            topic=NEWS_TOPIC or story.get("title","")
            logger.info("="*70)
            logger.info("PUBLICATION ATTEMPT %s/%s",index,len(candidates))
            logger.info("Title: %s",story.get("title",""))
            logger.info("Source: %s",story.get("source",""))
            logger.info("URL: %s",story.get("source_url",""))
            logger.info("Remaining candidates: %s",max(len(candidates)-index,0))
            logger.info("="*70)
            try:
                result=await self.factory.process_story(sources=sources,story=story,topic=topic)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.exception("Factory processing failed for candidate %s: %s",index,exc)
                attempts.append({"attempt":index,"title":story.get("title",""),"status":"FACTORY_FAILED","error":str(exc)})
                continue
            if not isinstance(result,dict):
                attempts.append({"attempt":index,"title":story.get("title",""),"status":"INVALID_RESULT"})
                continue
            publication=result.get("publication",{})
            published=bool(result.get("published",False))
            if not published and isinstance(publication,dict):
                published=bool(publication.get("published",False))
            publication_status=""
            if isinstance(publication,dict):
                publication_status=str(publication.get("status",""))
            if not publication_status:
                publication_status=str(result.get("publication_status",result.get("status","UNKNOWN")))
            pipeline_status=str(result.get("pipeline_status",result.get("status","UNKNOWN")))
            logger.info("Attempt %s result: pipeline=%s publication=%s published=%s",index,pipeline_status,publication_status or "UNKNOWN",published)
            if published:
                logger.info("="*70)
                logger.info("NEWS SUCCESSFULLY PUBLISHED")
                logger.info("Title: %s",story.get("title",""))
                logger.info("Source: %s",story.get("source",""))
                logger.info("Publication status: %s",publication_status or "PUBLISHED")
                logger.info("Published: YES")
                logger.info("Attempts used: %s",index)
                logger.info("="*70)
                return {**result,"status":"PUBLISHED","published":True,"publication_status":"PUBLISHED","selected_story":story,"attempts":attempts+[{"attempt":index,"title":story.get("title",""),"status":"PUBLISHED"}]}
            reason=""
            if isinstance(publication,dict):
                reason=str(publication.get("reason",publication.get("error","")))
            if not reason:
                reason=str(result.get("reason",result.get("error","")))
            attempts.append({"attempt":index,"title":story.get("title",""),"status":publication_status or pipeline_status,"reason":reason})
            logger.warning("Candidate %s was not publishable. Trying next candidate.",index)
        logger.warning("="*70)
        logger.warning("NO STORY PASSED THE PUBLICATION GATES")
        logger.warning("Candidates attempted: %s",len(candidates))
        logger.warning("Nothing was published this cycle.")
        logger.warning("="*70)
        return {"status":"NO_PUBLISHABLE_STORY","pipeline_status":"NO_PUBLISHABLE_STORY","published":False,"attempts":attempts,"collection":collection}

    def _rank_candidates(self,sources):
        valid=[]
        seen=set()
        for item in sources:
            if not isinstance(item,dict):
                continue
            title=str(item.get("title",item.get("headline","")) or "").strip()
            content=str(item.get("content",item.get("description",item.get("summary",""))) or "").strip()
            url=str(item.get("source_url",item.get("url","")) or "").strip()
            if not title or not url:
                continue
            key=(title.lower(),url.lower())
            if key in seen:
                continue
            seen.add(key)
            score=0
            if content:score+=30
            if len(content)>=200:score+=20
            if url:score+=15
            if item.get("published_at"):score+=10
            if item.get("source") or item.get("publisher"):score+=10
            if item.get("image_url"):score+=5
            valid.append((score,item))
        valid.sort(key=lambda x:x[0],reverse=True)
        return [item for _,item in valid]

    def _select_primary(self,sources):
        candidates=self._rank_candidates(sources)
        return candidates[0] if candidates else None

    def _build_story(self,primary):
        title=str(primary.get("title",primary.get("headline","")) or "").strip()
        description=str(primary.get("description",primary.get("summary","")) or "").strip()
        content=str(primary.get("content",primary.get("text",primary.get("body",description))) or "").strip()
        url=str(primary.get("source_url",primary.get("url","")) or "").strip()
        source=primary.get("source",primary.get("publisher",primary.get("name","")))
        source=str(source or "").strip()
        return {"title":title,"headline":title,"description":description,"summary":description,"content":content,"body":content,"source":source,"source_name":source,"source_url":url,"url":url,"published_at":primary.get("published_at"),"image_url":str(primary.get("image_url","") or "")}

    async def stop(self):
        if not self.running:
            self.stop_http_server()
            return
        self.running=False
        try:
            await self.factory.stop()
        except Exception as exc:
            logger.exception("Factory shutdown failed: %s",exc)
        self.stop_http_server()
        logger.info("Scheduler stopped.")

async def start_scheduler():
    scheduler=NewsScheduler()
    try:
        await scheduler.start()
    except KeyboardInterrupt:
        logger.info("Shutdown requested.")
    except Exception as exc:
        logger.exception("Scheduler failed: %s",exc)
    finally:
        await scheduler.stop()

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")
    asyncio.run(start_scheduler())
