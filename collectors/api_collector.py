"""
AI NEWS FACTORY
GENERIC API COLLECTOR
Supports header and query-parameter authentication.
"""

from typing import Any,Dict,List,Optional
import logging,os,time
import requests

logger=logging.getLogger(__name__)

class APICollector:
    def __init__(self,url:str,name:str="News API",api_key_env:Optional[str]=None,api_key_header:str="X-API-Key",api_key_location:str="header",api_key_param:str="api_token",params:Optional[Dict[str,Any]]=None,timeout:int=20):
        self.url=url
        self.name=name
        self.api_key_env=api_key_env
        self.api_key_header=api_key_header or "X-API-Key"
        self.api_key_location=(api_key_location or "header").strip().lower()
        self.api_key_param=api_key_param or "api_token"
        self.params=params or {}
        self.timeout=timeout
        self.version="2.0.0"

    def collect(self,limit:int=20)->List[Dict[str,Any]]:
        headers={"User-Agent":"AI-News-Factory/2.0"}
        params=dict(self.params)
        self._apply_credentials(headers,params)
        response=requests.get(self.url,headers=headers,params=params,timeout=self.timeout)
        response.raise_for_status()
        data=response.json()
        items=self._extract_items(data)
        results=[]
        for item in items[:limit]:
            parsed=self._parse_item(item)
            if parsed:
                results.append(parsed)
        return results

    def _apply_credentials(self,headers:Dict[str,str],params:Dict[str,Any])->None:
        if not self.api_key_env:
            return
        api_key=os.getenv(self.api_key_env,"").strip()
        if not api_key:
            logger.warning("%s API key variable %s is missing.",self.name,self.api_key_env)
            return
        if self.api_key_location in {"query","param","params","parameter"}:
            params[self.api_key_param]=api_key
        elif self.api_key_location=="bearer":
            headers["Authorization"]=f"Bearer {api_key}"
        else:
            headers[self.api_key_header]=api_key

    def _extract_items(self,data:Any)->List[Any]:
        if isinstance(data,list):
            return data
        if not isinstance(data,dict):
            return []
        for key in ("articles","results","data","items","stories","news"):
            value=data.get(key)
            if isinstance(value,list):
                return value
        return []

    def _parse_item(self,item:Any)->Optional[Dict[str,Any]]:
        if not isinstance(item,dict):
            return None
        title=self._first(item,["title","headline","name"])
        if not title:
            return None
        description=self._first(item,["description","summary","excerpt","content","snippet","text"])
        content=self._first(item,["content","body","description","summary","snippet","text"])
        url=self._first(item,["url","link","source_url","web_url","urlToArticle"])
        published=self._first(item,["published_at","publishedAt","published","pubDate","date","created_at","published"])
        author=self._first(item,["author","creator","byline"])
        image=self._first(item,["urlToImage","image_url","image","thumbnail","imageUrl"])
        source=self._extract_source(item)
        category=self._first(item,["category","section","topic","categories"])
        return {
            "title":str(title).strip(),
            "description":str(description or "").strip(),
            "content":str(content or description or "").strip(),
            "source_url":str(url or "").strip(),
            "published_at":published,
            "author":author or "",
            "image_url":image or "",
            "source":source or self.name,
            "category":category or "general",
            "collector":self.name,
            "collected_at":time.time(),
            "raw":item
        }

    def _extract_source(self,item:Dict[str,Any])->str:
        source=item.get("source")
        if isinstance(source,dict):
            return str(source.get("name",source.get("title","")) or "")
        if source:
            return str(source)
        publisher=item.get("publisher")
        if isinstance(publisher,dict):
            return str(publisher.get("name",publisher.get("title","")) or "")
        return str(publisher or "")

    def _first(self,item:Dict[str,Any],keys:List[str])->Any:
        for key in keys:
            value=item.get(key)
            if value not in (None,"",[]):
                return value
        return ""

    def health_check(self)->Dict[str,Any]:
        try:
            headers={"User-Agent":"AI-News-Factory/2.0"}
            params=dict(self.params)
            self._apply_credentials(headers,params)
            response=requests.get(self.url,headers=headers,params=params,timeout=self.timeout)
            return {
                "source":self.name,
                "healthy":response.ok,
                "status_code":response.status_code
            }
        except Exception as exc:
            logger.exception("API health check failed for %s.",self.name)
            return {
                "source":self.name,
                "healthy":False,
                "error":str(exc)
            }

    def status(self)->Dict[str,Any]:
        configured=True
        if self.api_key_env:
            configured=bool(os.getenv(self.api_key_env,"").strip())
        return {
            "engine":"APICollector",
            "version":self.version,
            "name":self.name,
            "url":self.url,
            "configured":configured,
            "api_key_env":self.api_key_env,
            "api_key_location":self.api_key_location,
            "api_key_param":self.api_key_param if self.api_key_location in {"query","param","params","parameter"} else None
        }

def create_api_collector(url:str,name:str="News API",api_key_env:Optional[str]=None,api_key_header:str="X-API-Key",api_key_location:str="header",api_key_param:str="api_token",params:Optional[Dict[str,Any]]=None,timeout:int=20)->APICollector:
    return APICollector(
        url=url,
        name=name,
        api_key_env=api_key_env,
        api_key_header=api_key_header,
        api_key_location=api_key_location,
        api_key_param=api_key_param,
        params=params,
        timeout=timeout
                )
