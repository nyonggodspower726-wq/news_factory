import asyncio,inspect,json,logging,os
from typing import Any,Dict,List,Optional
from collectors.api_collector import APICollector
try:
    from collectors.rss_collector import RSSCollector
except Exception:
    RSSCollector=None

logger=logging.getLogger("NewsFactory.SourceManager")

class SourceManager:
    def __init__(self,api_collectors=None,rss_collector=None):
        self.name="News Source Manager";self.version="3.0.0"
        self.max_sources=max(1,int(os.getenv("NEWS_MAX_SOURCES","30")))
        self.min_content_length=max(0,int(os.getenv("NEWS_MIN_CONTENT_LENGTH","80")))
        self.api_collectors=api_collectors if isinstance(api_collectors,list) else self._build_api_collectors()
        self.rss_collector=rss_collector or self._build_rss_collector()

    def _build_api_collectors(self):
        collectors=[]
        for i in range(1,11):
            url=os.getenv(f"NEWS_API_URL_{i}","").strip()
            if not url:
                continue
            name=os.getenv(f"NEWS_API_NAME_{i}",f"News API {i}").strip()
            key_env=os.getenv(f"NEWS_API_KEY_ENV_{i}","").strip() or None
            header=os.getenv(f"NEWS_API_HEADER_{i}","X-API-Key").strip()
            params_raw=os.getenv(f"NEWS_API_PARAMS_{i}","").strip()
            params={}
            if params_raw:
                try:
                    parsed=json.loads(params_raw)
                    if isinstance(parsed,dict):
                        params=parsed
                except json.JSONDecodeError:
                    logger.warning("Invalid NEWS_API_PARAMS_%s JSON.",i)
            try:
                collectors.append(APICollector(
                    url=url,
                    name=name,
                    api_key_env=key_env,
                    api_key_header=header,
                    params=params
                ))
            except Exception as exc:
                logger.error("Could not create API collector %s: %s",i,exc)
        return collectors

    def _build_rss_collector(self):
        if RSSCollector is None:
            return None
        try:
            return RSSCollector()
        except Exception as exc:
            logger.warning("RSS collector initialization failed: %s",exc)
            return None

    async def collect(self,topic:str="",limit:Optional[int]=None)->Dict[str,Any]:
        limit=max(1,int(limit or self.max_sources))
        raw=[];errors=[];collector_status=[]
        for collector in self.api_collectors:
            name=getattr(collector,"name",collector.__class__.__name__)
            try:
                value=await self._invoke(collector,topic,limit)
                items=self._extract_items(value)
                raw.extend(items)
                collector_status.append({"name":name,"status":"OK","count":len(items)})
            except Exception as exc:
                logger.exception("%s collection failed.",name)
                errors.append(f"{name}:{exc}")
                collector_status.append({"name":name,"status":"ERROR","error":str(exc)})
        if self.rss_collector is not None:
            name=getattr(self.rss_collector,"name","RSS")
            try:
                value=await self._invoke(self.rss_collector,topic,limit)
                items=self._extract_items(value)
                raw.extend(items)
                collector_status.append({"name":name,"status":"OK","count":len(items)})
            except Exception as exc:
                logger.exception("%s collection failed.",name)
                errors.append(f"{name}:{exc}")
                collector_status.append({"name":name,"status":"ERROR","error":str(exc)})
        results=[];seen=set()
        for index,item in enumerate(raw):
            normalized=self._normalize(item,index)
            if not normalized:
                continue
            key=(
                normalized.get("url","").lower().strip()
                or (
                    normalized.get("title","").lower().strip()
                    +"|"+
                    normalized.get("content","")[:400].lower().strip()
                )
            )
            if not key or key in seen:
                continue
            seen.add(key);results.append(normalized)
            if len(results)>=limit:
                break
        return {
            "status":"COLLECTION_COMPLETE",
            "topic":topic,
            "source_count":len(results),
            "sources":results,
            "errors":errors,
            "collector_status":collector_status,
            "api_collector_count":len(self.api_collectors),
            "rss_connected":self.rss_collector is not None
        }

    def collect_sync(self,topic:str="",limit:Optional[int]=None):
        try:
            asyncio.get_running_loop()
            raise RuntimeError("collect_sync() cannot run inside an active event loop.")
        except RuntimeError as exc:
            if "cannot run inside an active event loop" in str(exc):
                raise
        return asyncio.run(self.collect(topic,limit))

    async def _invoke(self,collector,topic,limit):
        methods=["collect","fetch","get_news","get_sources","run"]
        method=None
        for name in methods:
            candidate=getattr(collector,name,None)
            if callable(candidate):
                method=candidate
                break
        if method is None:
            raise AttributeError(f"{collector.__class__.__name__} has no compatible collection method.")
        kwargs=self._arguments(method,topic,limit)
        result=method(**kwargs)
        if inspect.isawaitable(result):
            result=await result
        return result

    def _arguments(self,method,topic,limit):
        try:
            sig=inspect.signature(method)
        except (TypeError,ValueError):
            return {}
        values={
            "topic":topic,"query":topic,"keyword":topic,"keywords":topic,
            "limit":limit,"max_results":limit,"count":limit,"per_page":limit
        }
        return {
            name:values[name]
            for name,param in sig.parameters.items()
            if name!="self" and name in values
        }

    def _extract_items(self,value):
        if value is None:return []
        if isinstance(value,list):return value
        if isinstance(value,dict):
            for key in ("sources","articles","items","results","data","news","stories"):
                data=value.get(key)
                if isinstance(data,list):return data
            return [value]
        if isinstance(value,str):return [{"content":value}]
        return []

    def _normalize(self,item,index):
        if isinstance(item,str):item={"content":item}
        if not isinstance(item,dict):return None
        title=str(item.get("title",item.get("headline",item.get("name",""))) or "").strip()
        description=str(item.get("description",item.get("summary",item.get("excerpt",""))) or "").strip()
        content=str(item.get("content",item.get("text",item.get("body",description))) or "").strip()
        url=str(item.get("url",item.get("link",item.get("source_url",item.get("web_url","")))) or "").strip()
        if not title and not content:return None
        if len(content)<self.min_content_length and len(description)>=self.min_content_length:
            content=description
        source=item.get("source",item.get("publisher",item.get("source_name",item.get("name",""))))
        if isinstance(source,dict):source=source.get("name","")
        source=str(source or "").strip()
        source_id=str(item.get("source_id",item.get("id",f"news_source_{index+1}")))
        source_type=str(item.get("type",item.get("source_type","NEWS")) or "NEWS").upper()
        return {
            "source_id":source_id,
            "id":source_id,
            "name":source,
            "publisher":source,
            "title":title,
            "headline":title,
            "description":description,
            "summary":description,
            "content":content,
            "text":content,
            "body":content,
            "url":url,
            "source_url":url,
            "author":str(item.get("author",item.get("creator",item.get("byline",""))) or ""),
            "published_at":item.get("published_at",item.get("publishedAt",item.get("published",item.get("pubDate",item.get("date",item.get("created_at")))))),
            "updated_at":item.get("updated_at"),
            "image_url":str(item.get("image_url",item.get("urlToImage",item.get("image",item.get("thumbnail","")))) or ""),
            "type":source_type,
            "source_type":source_type,
            "primary":bool(item.get("primary",False)),
            "verified":bool(item.get("verified",False)),
            "original_source":str(item.get("original_source","") or ""),
            "collector":str(item.get("collector",source) or source),
            "raw":item.get("raw",item)
        }

    def health_check(self)->Dict[str,Any]:
        results=[]
        for collector in self.api_collectors:
            try:
                if hasattr(collector,"health_check"):
                    results.append(collector.health_check())
                else:
                    results.append({"source":getattr(collector,"name","API"),"healthy":True})
            except Exception as exc:
                results.append({"source":getattr(collector,"name","API"),"healthy":False,"error":str(exc)})
        return {
            "status":"HEALTH_CHECK_COMPLETE",
            "api_collectors":results,
            "rss_connected":self.rss_collector is not None
        }

    def status(self)->Dict[str,Any]:
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "api_collector_count":len(self.api_collectors),
            "api_collectors":[getattr(x,"name",x.__class__.__name__) for x in self.api_collectors],
            "rss_collector":self.rss_collector is not None,
            "max_sources":self.max_sources,
            "min_content_length":self.min_content_length
        }

source_manager=SourceManager()

async def collect_news(topic="",limit=None):
    return await source_manager.collect(topic,limit)

def collect_news_sync(topic="",limit=None):
    return source_manager.collect_sync(topic,limit)

def source_manager_status():
    return source_manager.status()

if __name__=="__main__":
    import json
    print(json.dumps(source_manager.status(),indent=2,default=str))
    print(json.dumps(source_manager.health_check(),indent=2,default=str))
