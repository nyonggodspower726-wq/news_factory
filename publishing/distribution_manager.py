import logging
from typing import Any,Dict,List,Optional

logger=logging.getLogger("NewsFactory.DistributionManager")

class DistributionManager:
    def __init__(self,router=None,queue=None,tracker=None,history=None,guard=None):
        self.name="Publication Distribution Manager"
        self.version="1.0.0"
        self.router=router
        self.queue=queue
        self.tracker=tracker
        self.history=history
        self.guard=guard
        self.default_platforms=["website"]

    def configure(self,router=None,queue=None,tracker=None,history=None,guard=None):
        if router is not None:self.router=router
        if queue is not None:self.queue=queue
        if tracker is not None:self.tracker=tracker
        if history is not None:self.history=history
        if guard is not None:self.guard=guard
        return self.status()

    def prepare(self,article:Dict[str,Any],platforms:Optional[List[str]]=None)->Dict[str,Any]:
        if not isinstance(article,dict):
            return {"status":"FAILED","error":"Article must be a dictionary.","packages":{}}
        platforms=self._platforms(platforms)
        packages={}
        for platform in platforms:
            if self.router and hasattr(self.router,"prepare"):
                try:
                    result=self.router.prepare(article,platform)
                except Exception as exc:
                    result={"status":"FAILED","platform":platform,"error":str(exc)}
            else:
                result={"status":"READY","platform":platform,"article":dict(article),"payload":dict(article)}
            packages[platform]=result
        return {"status":"READY","article_id":article.get("id",article.get("article_id","")),"platforms":platforms,"packages":packages}

    def distribute(self,article:Dict[str,Any],platforms:Optional[List[str]]=None,queue_first:bool=False)->Dict[str,Any]:
        if not isinstance(article,dict):
            return {"status":"FAILED","published_count":0,"results":{}}
        platforms=self._platforms(platforms)
        results={}
        published=0
        queued=0
        for platform in platforms:
            if self.guard:
                try:
                    package={"article":article,"publication_ready":article.get("publication_safe",True),"publication_history":[]}
                    gate=self.guard.check(package,platform)
                    if not gate.get("publication_allowed",False):
                        results[platform]={"status":"BLOCKED","published":False,"guard":gate}
                        continue
                except Exception as exc:
                    results[platform]={"status":"GUARD_FAILED","published":False,"error":str(exc)}
                    continue

            if self.history and self.history.has_published(
                str(article.get("id",article.get("article_id",""))),
                platform
            ):
                results[platform]={"status":"ALREADY_PUBLISHED","published":False}
                continue

            if queue_first and self.queue:
                try:
                    item=self.queue.enqueue(article,platform)
                    results[platform]={"status":"QUEUED","published":False,"queue":item}
                    queued+=1
                    continue
                except Exception as exc:
                    results[platform]={"status":"QUEUE_FAILED","published":False,"error":str(exc)}
                    continue

            if not self.router:
                results[platform]={"status":"NO_ROUTER","published":False}
                continue

            try:
                result=self.router.publish(article,platform)
            except Exception as exc:
                logger.exception("Distribution failed for %s.",platform)
                result={"status":"PUBLISH_FAILED","published":False,"error":str(exc)}

            if not isinstance(result,dict):
                result={"status":"UNKNOWN","published":False,"response":result}

            if result.get("published"):
                published+=1

            results[platform]=result

            self._record(article,platform,result)

        return {
            "status":"COMPLETE",
            "article_id":article.get("id",article.get("article_id","")),
            "platforms":platforms,
            "published_count":published,
            "queued_count":queued,
            "results":results
        }

    def distribute_prepared(self,prepared:Dict[str,Any],platforms:Optional[List[str]]=None)->Dict[str,Any]:
        if not isinstance(prepared,dict):
            return {"status":"FAILED","published_count":0}
        article=prepared.get("article",prepared)
        return self.distribute(article,platforms)

    def queue(self,article:Dict[str,Any],platforms:Optional[List[str]]=None,priority:str="NORMAL")->Dict[str,Any]:
        if not self.queue:
            return {"status":"NO_QUEUE","queued_count":0,"results":{}}
        if not isinstance(article,dict):
            return {"status":"FAILED","queued_count":0,"results":{}}
        results={}
        count=0
        for platform in self._platforms(platforms):
            try:
                results[platform]=self.queue.enqueue(article,platform,priority)
                count+=1
            except Exception as exc:
                results[platform]={"status":"FAILED","error":str(exc)}
        return {"status":"QUEUED","queued_count":count,"results":results}

    def process_queue(self,platform:Optional[str]=None,limit:int=10)->Dict[str,Any]:
        if not self.queue or not self.router:
            return {"status":"NOT_CONFIGURED","processed":0,"results":[]}
        results=[]
        processed=0
        for _ in range(max(1,int(limit))):
            item=self.queue.next(platform)
            if not item:break
            reserved=self.queue.reserve(item.get("queue_id"))
            if not reserved:continue
            target_platform=reserved.get("platform","website")
            article=reserved.get("article",{})
            try:
                result=self.router.publish(article,target_platform)
            except Exception as exc:
                result={"status":"PUBLISH_FAILED","published":False,"error":str(exc)}
            if isinstance(result,dict) and result.get("published"):
                self.queue.complete(reserved["queue_id"],result)
            else:
                self.queue.fail(
                    reserved["queue_id"],
                    str(result.get("error","Publication failed.")) if isinstance(result,dict) else "Publication failed.",
                    result if isinstance(result,dict) else {}
                )
            self._record(article,target_platform,result if isinstance(result,dict) else {})
            results.append({"queue_id":reserved.get("queue_id"),"platform":target_platform,"result":result})
            processed+=1
        return {"status":"COMPLETE","processed":processed,"results":results}

    def _record(self,article,platform,result):
        if self.tracker:
            try:self.tracker.record(article,platform,result)
            except Exception:logger.exception("Publication tracker failed.")
        if self.history:
            try:self.history.record(article,platform,result)
            except Exception:logger.exception("Publication history failed.")

    def _platforms(self,platforms):
        if isinstance(platforms,str):platforms=[platforms]
        if not isinstance(platforms,list) or not platforms:
            platforms=list(self.default_platforms)
        aliases={"site":"website","web":"website","wp":"wordpress","blog":"wordpress","fb":"social","twitter":"social"}
        output=[]
        for platform in platforms:
            value=str(platform or "").strip().lower()
            value=aliases.get(value,value)
            if value and value not in output:output.append(value)
        return output or ["website"]

    def status(self):
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "router_connected":self.router is not None,
            "queue_connected":self.queue is not None,
            "tracker_connected":self.tracker is not None,
            "history_connected":self.history is not None,
            "guard_connected":self.guard is not None
        }

distribution_manager=DistributionManager()

def distribute_article(article,platforms=None):
    return distribution_manager.distribute(article,platforms)

def prepare_distribution(article,platforms=None):
    return distribution_manager.prepare(article,platforms)

def queue_article(article,platforms=None,priority="NORMAL"):
    return distribution_manager.queue(article,platforms,priority)
