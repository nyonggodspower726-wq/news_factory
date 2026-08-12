import inspect,logging,os,asyncio
from typing import Any,Dict,List,Optional

logger=logging.getLogger("NewsFactory.SourceManager")

try:
    from collectors.api_collector import APICollector
except Exception:
    APICollector=None

try:
    from collectors.rss_collector import RSSCollector
except Exception:
    RSSCollector=None


class SourceManager:
    def __init__(self,api_collector=None,rss_collector=None):
        self.name="News Source Manager"
        self.version="2.0.0"
        self.api_collector=api_collector or (APICollector() if APICollector else None)
        self.rss_collector=rss_collector or (RSSCollector() if RSSCollector else None)
        self.max_sources=int(os.getenv("NEWS_MAX_SOURCES","30"))
        self.min_content_length=int(os.getenv("NEWS_MIN_CONTENT_LENGTH","80"))

    async def collect(self,topic:str="",limit:Optional[int]=None)->Dict[str,Any]:
        limit=max(1,int(limit or self.max_sources))
        raw=[]
        results=[]
        errors=[]

        for name,collector in (
            ("api",self.api_collector),
            ("rss",self.rss_collector)
        ):
            if collector is None:
                errors.append(f"{name}_collector_unavailable")
                continue
            try:
                value=await self._invoke(
                    collector,
                    topic,
                    limit
                )
                raw.extend(
                    self._extract_items(value)
                )
            except Exception as exc:
                logger.exception(
                    "%s collector failed.",
                    name
                )
                errors.append(
                    f"{name}:{exc}"
                )

        seen=set()

        for index,item in enumerate(raw):
            normalized=self._normalize(item,index)
            if not normalized:
                continue

            key=(
                normalized["url"]
                or
                (
                    normalized["title"].lower()
                    +"|"+
                    normalized["content"][:300].lower()
                )
            )

            if key in seen:
                continue

            seen.add(key)
            results.append(normalized)

            if len(results)>=limit:
                break

        return {
            "status":"COLLECTION_COMPLETE",
            "topic":topic,
            "source_count":len(results),
            "sources":results,
            "errors":errors
        }

    def collect_sync(self,topic:str="",limit:Optional[int]=None)->Dict[str,Any]:
        try:
            loop=asyncio.get_running_loop()
            if loop.is_running():
                raise RuntimeError(
                    "collect_sync() cannot run inside an active event loop."
                )
        except RuntimeError as exc:
            if "cannot run inside an active event loop" in str(exc):
                raise
        return asyncio.run(
            self.collect(topic,limit)
        )

    async def _invoke(self,collector,topic,limit):
        methods=[
            "collect",
            "fetch",
            "get_news",
            "get_sources",
            "run"
        ]

        method=None

        for name in methods:
            candidate=getattr(
                collector,
                name,
                None
            )
            if callable(candidate):
                method=candidate
                break

        if method is None:
            raise AttributeError(
                f"{collector.__class__.__name__} has no compatible collection method."
            )

        kwargs=self._arguments(
            method,
            topic,
            limit
        )

        result=method(
            **kwargs
        )

        if inspect.isawaitable(result):
            result=await result

        return result

    def _arguments(self,method,topic,limit):
        try:
            sig=inspect.signature(method)
        except (TypeError,ValueError):
            return {}

        values={
            "topic":topic,
            "query":topic,
            "keyword":topic,
            "keywords":topic,
            "limit":limit,
            "max_results":limit,
            "count":limit,
            "per_page":limit
        }

        kwargs={}

        for name,param in sig.parameters.items():
            if name=="self":
                continue
            if name in values:
                kwargs[name]=values[name]

        return kwargs

    def _extract_items(self,value):
        if value is None:
            return []

        if isinstance(value,list):
            return value

        if isinstance(value,dict):
            for key in (
                "sources",
                "articles",
                "items",
                "results",
                "data",
                "news"
            ):
                data=value.get(key)
                if isinstance(data,list):
                    return data
            return [value]

        if isinstance(value,str):
            return [{
                "content":value
            }]

        return []

    def _normalize(self,item,index):
        if isinstance(item,str):
            item={
                "content":item
            }

        if not isinstance(item,dict):
            return None

        title=str(
            item.get(
                "title",
                item.get(
                    "headline",
                    ""
                )
            ) or ""
        ).strip()

        description=str(
            item.get(
                "description",
                item.get(
                    "summary",
                    ""
                )
            ) or ""
        ).strip()

        content=str(
            item.get(
                "content",
                item.get(
                    "text",
                item.get(
                    "body",
                    description
                ))
            ) or ""
        ).strip()

        url=str(
            item.get(
                "url",
                item.get(
                    "link",
                    item.get(
                        "source_url",
                        ""
                    )
                )
            ) or ""
        ).strip()

        source_name=str(
            item.get(
                "source",
                item.get(
                    "publisher",
                    item.get(
                        "name",
                        ""
                    )
                )
            ) or ""
        ).strip()

        if not title and not content:
            return None

        if len(content)<self.min_content_length:
            content=(
                description
                if len(description)>=self.min_content_length
                else content
            )

        source_id=str(
            item.get(
                "source_id",
                item.get(
                    "id",
                    f"news_source_{index+1}"
                )
            )
        )

        source_type=str(
            item.get(
                "type",
                item.get(
                    "source_type",
                    "NEWS"
                )
            )
        ).upper()

        return {
            "source_id":source_id,
            "id":source_id,
            "name":source_name,
            "publisher":source_name,
            "title":title,
            "headline":title,
            "description":description,
            "summary":description,
            "content":content,
            "text":content,
            "body":content,
            "url":url,
            "source_url":url,
            "author":str(
                item.get(
                    "author",
                    ""
                ) or ""
            ),
            "published_at":item.get(
                "published_at",
                item.get(
                    "published",
                    item.get(
                        "pubDate"
                    )
                )
            ),
            "updated_at":item.get(
                "updated_at"
            ),
            "image_url":str(
                item.get(
                    "image_url",
                    item.get(
                        "image",
                        item.get(
                            "thumbnail",
                            ""
                        )
                    )
                ) or ""
            ),
            "type":source_type,
            "source_type":source_type,
            "primary":bool(
                item.get(
                    "primary",
                    False
                )
            ),
            "verified":bool(
                item.get(
                    "verified",
                    False
                )
            ),
            "original_source":str(
                item.get(
                    "original_source",
                    ""
                ) or ""
            )
        }

    def status(self)->Dict[str,Any]:
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "api_collector":self.api_collector is not None,
            "rss_collector":self.rss_collector is not None,
            "max_sources":self.max_sources,
            "min_content_length":self.min_content_length
        }


source_manager=SourceManager()


async def collect_news(
    topic="",
    limit=None
):
    return await source_manager.collect(
        topic,
        limit
    )


def collect_news_sync(
    topic="",
    limit=None
):
    return source_manager.collect_sync(
        topic,
        limit
    )


def source_manager_status():
    return source_manager.status()


if __name__=="__main__":
    import json
    print(
        json.dumps(
            source_manager.status(),
            indent=2,
            default=str
        )
        )
