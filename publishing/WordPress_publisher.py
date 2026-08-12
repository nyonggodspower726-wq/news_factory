import os,logging
from typing import Any,Dict,Optional
import requests

logger=logging.getLogger("NewsFactory.WordPressPublisher")

class WordPressPublisher:
    def __init__(self,api_url:Optional[str]=None,username:Optional[str]=None,password:Optional[str]=None,api_key:Optional[str]=None,timeout:int=30):
        self.name="WordPress Publisher";self.version="1.0.0";self.timeout=timeout
        self.api_url=(api_url or os.getenv("WORDPRESS_API_URL","")).strip().rstrip("/")
        self.username=username or os.getenv("WORDPRESS_USERNAME","")
        self.password=password or os.getenv("WORDPRESS_PASSWORD","")
        self.api_key=api_key or os.getenv("WORDPRESS_API_KEY","")

    def publish(self,article:Dict[str,Any])->Dict[str,Any]:
        if not isinstance(article,dict):
            return {"status":"FAILED","published":False,"platform":"wordpress","error":"Article must be a dictionary."}
        endpoint=self.api_url
        if not endpoint:
            return {"status":"NOT_CONFIGURED","published":False,"platform":"wordpress","message":"WORDPRESS_API_URL is not configured."}
        if not endpoint.endswith("/posts"):
            endpoint=endpoint.rstrip("/")+"/posts"
        payload=self._payload(article)
        headers={"Content-Type":"application/json","User-Agent":"AI-News-Factory/1.0"}
        auth=None
        if self.api_key:headers["Authorization"]=f"Bearer {self.api_key}"
        elif self.username and self.password:auth=(self.username,self.password)
        try:
            response=requests.post(endpoint,json=payload,headers=headers,auth=auth,timeout=self.timeout)
            response.raise_for_status()
            data=self._data(response)
            return {"status":"PUBLISHED","published":True,"platform":"wordpress","external_id":self._extract(data,"id"),"url":self._extract(data,"link"),"response":data}
        except requests.RequestException as exc:
            logger.exception("WordPress publishing failed.")
            return {"status":"FAILED","published":False,"platform":"wordpress","error":str(exc)}

    def _payload(self,article):
        return {
            "title":article.get("title",article.get("headline","")),
            "content":article.get("content",article.get("body","")),
            "excerpt":article.get("excerpt",article.get("summary","")),
            "slug":article.get("slug",""),
            "status":article.get("wordpress_status","draft"),
            "featured_media":article.get("featured_media_id",0) or 0
        }

    def _data(self,response):
        try:return response.json()
        except ValueError:return {"text":response.text,"status_code":response.status_code}

    def _extract(self,data,key):
        if not isinstance(data,dict):return ""
        value=data.get(key,"")
        return "" if value is None else str(value)

    def status(self):
        configured=bool(self.api_url and ((self.api_key) or (self.username and self.password)))
        return {"engine":self.name,"version":self.version,"status":"READY" if configured else "NOT_CONFIGURED","configured":configured}

def create_wordpress_publisher(api_url=None,username=None,password=None,api_key=None):
    return WordPressPublisher(api_url,username,password,api_key)
