import os,logging
from typing import Any,Dict,Optional
import requests

logger=logging.getLogger("NewsFactory.WebsitePublisher")

class WebsitePublisher:
    def __init__(self,api_url:Optional[str]=None,api_key:Optional[str]=None,timeout:int=30):
        self.name="Website Publisher";self.version="1.1.0";self.timeout=timeout
        self.api_url=(api_url or os.getenv("NEWS_SITE_API_URL","")).strip()
        self.api_key=(api_key or os.getenv("NEWS_SITE_API_KEY","")).strip()

    def publish(self,article:Dict[str,Any])->Dict[str,Any]:
        if not isinstance(article,dict):
            return {"status":"FAILED","published":False,"platform":"website","error":"Article must be a dictionary."}
        if not self.api_url:
            return {"status":"NOT_CONFIGURED","published":False,"platform":"website","message":"NEWS_SITE_API_URL is not configured."}
        try:
            response=requests.post(self.api_url,json=self._payload(article),headers=self._headers(),timeout=self.timeout)
            response.raise_for_status()
            data=self._data(response)
            return {"status":"PUBLISHED","published":True,"platform":"website","external_id":self._extract(data,"id"),"url":self._extract(data,"url"),"response":data}
        except requests.RequestException as exc:
            logger.exception("Website publishing failed.")
            return {"status":"FAILED","published":False,"platform":"website","error":str(exc)}

    def _payload(self,article):
        seo=article.get("seo",{}) if isinstance(article.get("seo",{}),dict) else {}
        return {
            "title":article.get("title",article.get("headline","")),
            "slug":article.get("slug",""),
            "content":article.get("content",article.get("body","")),
            "excerpt":article.get("excerpt",article.get("summary","")),
            "category":article.get("category","news"),
            "tags":article.get("tags",[]),
            "image_url":article.get("image_url",""),
            "image_alt":article.get("image_alt",""),
            "image_caption":article.get("image_caption",""),
            "image_credit":article.get("image_credit",""),
            "source_url":article.get("source_url",""),
            "seo":seo
        }

    def _headers(self):
        headers={"Content-Type":"application/json","User-Agent":"AI-News-Factory/1.1"}
        if self.api_key:headers["Authorization"]=f"Bearer {self.api_key}"
        return headers

    def _data(self,response):
        try:return response.json()
        except ValueError:return {"text":response.text,"status_code":response.status_code}

    def _extract(self,data,key):
        if not isinstance(data,dict):return ""
        value=data.get(key,"")
        return "" if value is None else str(value)

    def status(self):
        return {"engine":self.name,"version":self.version,"status":"READY" if self.api_url else "NOT_CONFIGURED","configured":bool(self.api_url)}

def create_website_publisher(api_url=None,api_key=None):
    return WebsitePublisher(api_url,api_key)
