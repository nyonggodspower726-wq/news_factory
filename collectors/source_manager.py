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
        self.name="News Source Manager";self.version="4.0.0"
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
            location=os.getenv(f"NEWS_API_KEY_LOCATION_{i}","").strip().lower()
            param=os.getenv(f"NEWS_API_KEY_PARAM_{i}","").strip()
            if not location:
                lname=name.lower()
                if "thenewsapi" in lname or "the news api" in lname:
                    location="query"
                else:
                    location="header"
            if not param:
                lname=name.lower()
                if "gnews" in lname:
                    param="apikey"
                elif "newsapi" in lname and "the" not in lname:
                    param="apiKey"
                else:
                    param="api_token"
            params_raw=os.getenv(f"NEWS_API_PARAMS_{i}","").strip()
            params={}
            if params_raw:
                try:
                    parsed=json.loads(params_raw)
                    if isinstance(parsed,dict):
                        params=parsed
                except json.JSONDecodeError as exc:
                    logger.warning("Invalid NEWS_API_PARAMS_%s JSON: %s",i,exc)
            try:
                collectors.append(APICollector(
                    url=url,
                    name=name,
                    api_key_env=key_env,
                    api_key_header=header,
                    api_key_location=location,
                    api_key_param=param,
                    params=params
                ))
            except Exception as exc:
                logger.error("Could not create API collector %s (%s): %s",i,name,exc)
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
        api_results=[]
        errors=[]
        collector_status=[]
        if self.api_collectors:
            tasks=[
                self._collect_one(collector,topic,limit)
                for collector in self.api_collectors
            ]
            api_results=await asyncio.gather(*tasks)
        for result in api_results:
            collector_status.append(result["status"])
            if result["items"]:
                results=result["items"]
            else:
                results=[]
            if result["error"]:
                errors.append(result["error"])
            result["items"]=None
            api_results[api_results.index(result)]=results
        raw=[]
        for result in api_results:
            if isinstance(result,list):
                raw.extend(result)
        if self.rss_collector is not None:
            rss_name=getattr(self.rss_collector,"name","RSS News Sources")
            try:
                value=await self._invoke(self.rss_collector,topic,limit)
                items=self._extract_items(value)
                raw.extend(items)
                collector_status.append({"name":rss_name,"status":"OK","count":len(items)})
            except Exception as exc:
                logger.exception("%s collection failed.",rss_name)
                errors.append(f"{rss_name}:{exc}")
                collector_status.append({"name":rss_name,"status":"ERROR","error":str(exc)})
        normalized=self._deduplicate_and_normalize(raw,limit)
        return {
            "status":"COLLECTION_COMPLETE",
            "topic":topic,
            "source_count":len(normalized),
            "sources":normalized,
            "errors":errors,
            "collector_status":collector_status,
            "api_collector_count":len(self.api_collectors),
            "rss_connected":self.rss_collector is not None,
            "successful_collectors":sum(1 for x in collector_status if x.get("status")=="OK"),
            "failed_collectors":sum(1 for x in collector_status if x.get("status")=="ERROR")
        }

    async def _collect_one(self,collector,topic,limit):
        name=getattr(collector,"name",collector.__class__.__name__)
        try:
            value=await self._invoke(collector,topic,limit)
            items=self._extract_items(value)
            return {
                "status":{"name":name,"status":"OK","count":len(items)},
                "items":items,
                "error":""
            }
        except Exception as exc:
            logger.exception("%s collection failed.",name)
            return {
                "status":{"name":name,"status":"ERROR","error":str(exc)},
                "items":[],
                "error":f"{name}:{exc}"
            }

    def _deduplicate_and_normalize(self,raw,limit):
        results=[];seen_urls=set();seen_titles=set()
        for index,item in enumerate(raw):
            normalized=self._normalize(item,index)
            if not normalized:
                continue
            url=normalized.get("url","").lower().strip()
            title=normalized.get("title","").lower().strip()
            fingerprint=title+"|"+normalized.get("content","")[:500].lower().strip()
            if url and url in seen_urls:
                continue
            if fingerprint in seen_titles:
                continue
            if url:
                seen_urls.add(url)
            seen_titles.add(fingerprint)
            results.append(normalized)
            if len(results)>=limit:
                break
        return results

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
        values={"topic":topic,"query":topic,"keyword":topic,"keywords":topic,"limit":limit,"max_results":limit,"count":limit,"per_page":limit}
        return {name:values[name] for name,param in sig.parameters.items() if name!="self" and name in values}

    def _extract_items(self,value):
        if value is None:
            return []
        if isinstance(value,list):
            return value
        if isinstance(value,dict):
            for key in ("sources","articles","items","results","data","news","stories"):
                data=value.get(key)
                if isinstance(data,list):
                    return data
            return [value]
        if isinstance(value,str):
            return [{"content":value}]
        return []

    def _normalize(self,item,index):
        if isinstance(item,str):
            item={"content":item}
        if not isinstance(item,dict):
            return None
        title=str(item.get("title",item.get("headline",item.get("name",""))) or "").strip()
        description=str(item.get("description",item.get("summary",item.get("excerpt",item.get("snippet","")))) or "").strip()
        content=str(item.get("content",item.get("text",item.get("body",item.get("snippet",description)))) or "").strip()
        url=str(item.get("url",item.get("link",item.get("source_url",item.get("web_url","")))) or "").strip()
        if not title and not content:
            return None
        if len(content)<self.min_content_length and len(description)>=self.min_content_length:
            content=description
        source=item.get("source",item.get("publisher",item.get("source_name",item.get("name",""))))
        if isinstance(source,dict):
            source=source.get("name",source.get("title",source.get("domain","")))
        source=str(source or "").strip()
        category=item.get("category",item.get("section",item.get("topic",item.get("categories","general"))))
        if isinstance(category,list):
            category=",".join(str(x) for x in category)
        source_id=str(item.get("source_id",item.get("uuid",item.get("id",f"news_source_{index+1}"))))
        source_type=str(item.get("type",item.get("source_type","NEWS")) or "NEWS").upper()
        return {
            "source_id":source_id,
            "id":source_id,
            "uuid":item.get("uuid"),
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
            "image_url":str(item.get("image_url",item.get("urlToImage",item.get("image",item.get("thumbnail",item.get("imageUrl",""))))) or ""),
            "type":source_type,
            "source_type":source_type,
            "category":category or "general",
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
        if self.rss_collector is not None:
            try:
                if hasattr(self.rss_collector,"health_check"):
                    results.append(self.rss_collector.health_check())
                else:
                    results.append({"source":getattr(self.rss_collector,"name","RSS"),"healthy":True})
            except Exception as exc:
                results.append({"source":getattr(self.rss_collector,"name","RSS"),"healthy":False,"error":str(exc)})
        return {"status":"HEALTH_CHECK_COMPLETE","sources":results}

    def status(self)->Dict[str,Any]:
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "api_collector_count":len(self.api_collectors),
            "api_collectors":[getattr(x,"name",x.__class__.__name__) for x in self.api_collectors],
            "rss_collector":getattr(self.rss_collector,"name",None) if self.rss_collector else None,
            "rss_connected":self.rss_collector is not None,
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
