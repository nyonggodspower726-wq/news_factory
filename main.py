import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List
from config import FACTORY_NAME, VERSION
from brain.pipeline import BrainPipeline
from factory_pipeline import FactoryPipeline
logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")
logger=logging.getLogger("NewsFactory.FactoryPipeline")
class NewsFactory:
    def __init__(self):
        self.name=FACTORY_NAME
        self.version=VERSION
        self.running=False
        self.brain=BrainPipeline()
        self.factory_pipeline=FactoryPipeline()
    async def start(self):
        self.running=True
        logger.info("="*70)
        logger.info("NEWS FACTORY STARTING")
        logger.info("="*70)
        logger.info("Factory: %s",self.name)
        logger.info("Version: %s",self.version)
        logger.info("Startup time: %s",datetime.utcnow().isoformat())
        status=self.brain.status()
        logger.info("Brain system loaded: %s/%s",status.get("loaded_brains",0),status.get("total_brains",0))
        for brain_name,state in status.get("brains",{}).items():
            logger.info("BRAIN | %s | %s",brain_name,state)
        logger.info("AI intelligence pipeline: READY")
        try:
            factory_status=self.factory_pipeline.status()
            logger.info("Publication pipeline: %s",factory_status.get("status","READY"))
        except Exception as exc:
            logger.warning("Publication pipeline status check warning: %s",exc)
        logger.info("Automatic publishing pipeline: ENABLED")
        logger.info("News Factory is online.")
        logger.info("="*70)
    async def process_story(self,sources:List[Dict[str,Any]],story:Dict[str,Any]=None,topic:str="")->Dict[str,Any]:
        if not self.running:
            raise RuntimeError("News Factory is not running.")
        logger.info("="*70)
        logger.info("STARTING NEWS PROCESSING")
        logger.info("="*70)
        logger.info("Sources received: %s",len(sources or []))
        logger.info("Topic: %s",topic or "General News")
        logger.info("Starting intelligence pipeline...")
        try:
            brain_result=await asyncio.to_thread(self.brain.run,sources,story,topic)
        except Exception as exc:
            logger.exception("Brain pipeline failed: %s",exc)
            return {"pipeline_status":"BRAIN_FAILED","publication_ready":False,"published":False,"error":str(exc)}
        if not isinstance(brain_result,dict):
            logger.error("Brain pipeline returned invalid result type: %s",type(brain_result).__name__)
            return {"pipeline_status":"BRAIN_INVALID_RESULT","publication_ready":False,"published":False,"error":"Brain pipeline returned a non-dictionary result."}
        logger.info("Brain pipeline completed.")
        logger.info("Pipeline status: %s",brain_result.get("pipeline_status","UNKNOWN"))
        publication_ready=bool(brain_result.get("publication_ready",False))
        logger.info("Editorial publication gate: %s","PASSED" if publication_ready else "NOT PASSED")
        if not publication_ready:
            logger.warning("Story was NOT approved for publication.")
            logger.warning("Publication pipeline will not publish this story.")
            return {**brain_result,"publication_status":"NOT_READY","published":False}
        logger.info("Story passed the central editorial publication gate.")
        logger.info("Sending approved story to FactoryPipeline...")
        try:
            publication_result=await asyncio.to_thread(self.factory_pipeline.publish,brain_result,"website",False)
        except Exception as exc:
            logger.exception("Publication pipeline failed: %s",exc)
            return {**brain_result,"publication_status":"PUBLISH_FAILED","published":False,"publication_error":str(exc)}
        if not isinstance(publication_result,dict):
            logger.error("Publication pipeline returned invalid result type: %s",type(publication_result).__name__)
            return {**brain_result,"publication_status":"PUBLISH_FAILED","published":False,"publication_error":"Publication pipeline returned a non-dictionary result."}
        publication_status=publication_result.get("status","UNKNOWN")
        published=publication_status=="PUBLISHED"
        logger.info("Publication pipeline status: %s",publication_status)
        logger.info("Published: %s","YES" if published else "NO")
        return {**brain_result,"publication":publication_result,"publication_status":publication_status,"published":published}
