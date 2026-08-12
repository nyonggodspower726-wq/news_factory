import json,os
from datetime import datetime,timezone
from typing import Any,Dict,List,Optional

class PublicationHistory:
    def __init__(self,file_path:str="data/publication_history.json"):
        self.name="Publication History"
        self.version="1.0.0"
        self.file_path=file_path
        self._ensure()

    def record(self,article:Dict[str,Any],platform:str,result:Dict[str,Any]=None)->Dict[str,Any]:
        article=article if isinstance(article,dict) else {}
        result=result if isinstance(result,dict) else {}
        item={
            "history_id":self._id(article,platform),
            "article_id":str(article.get("id",article.get("article_id",""))),
            "title":str(article.get("title",article.get("headline",""))),
            "platform":str(platform or "website").lower(),
            "status":result.get("status","UNKNOWN"),
            "published":bool(result.get("published",False)),
            "url":result.get("url",result.get("publisher_result",{}).get("url","") if isinstance(result.get("publisher_result",{}),dict) else ""),
            "external_id":result.get("external_id",result.get("publisher_result",{}).get("external_id","") if isinstance(result.get("publisher_result",{}),dict) else ""),
            "slug":article.get("slug",""),
            "timestamp":datetime.now(timezone.utc).isoformat()
        }
        data=self._load()
        data.append(item)
        self._save(data)
        return item

    def has_published(self,article_id:str,platform:str)->bool:
        article_id=str(article_id or "")
        platform=str(platform or "").lower()
        return any(
            x.get("article_id")==article_id and
            str(x.get("platform","")).lower()==platform and
            x.get("published") is True
            for x in self._load()
        )

    def find_by_article(self,article_id:str)->List[Dict[str,Any]]:
        return [x for x in self._load() if x.get("article_id")==str(article_id)]

    def find_by_platform(self,platform:str)->List[Dict[str,Any]]:
        platform=str(platform or "").lower()
        return [x for x in self._load() if str(x.get("platform","")).lower()==platform]

    def get(self,history_id:str)->Optional[Dict[str,Any]]:
        for item in reversed(self._load()):
            if item.get("history_id")==history_id:
                return item
        return None

    def summary(self)->Dict[str,Any]:
        items=self._load()
        published=sum(1 for x in items if x.get("published"))
        failed=len(items)-published
        return {
            "engine":self.name,
            "version":self.version,
            "total":len(items),
            "published":published,
            "failed":failed,
            "success_rate":round(published/len(items)*100,2) if items else 0,
            "platforms":sorted({x.get("platform") for x in items if x.get("platform")})
        }

    def status(self)->Dict[str,Any]:
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "file_path":self.file_path,
            "summary":self.summary()
        }

    def _id(self,article,platform):
        import hashlib
        raw=f"{article.get('id',article.get('article_id',''))}|{article.get('title','')}|{platform}|{datetime.now(timezone.utc).isoformat()}"
        return "hist_"+hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _ensure(self):
        directory=os.path.dirname(self.file_path)
        if directory:
            os.makedirs(directory,exist_ok=True)
        if not os.path.exists(self.file_path):
            self._save([])

    def _load(self):
        try:
            with open(self.file_path,"r",encoding="utf-8") as f:
                data=json.load(f)
            return data if isinstance(data,list) else []
        except (FileNotFoundError,json.JSONDecodeError,OSError):
            return []

    def _save(self,data):
        temp=self.file_path+".tmp"
        with open(temp,"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
        os.replace(temp,self.file_path)

publication_history=PublicationHistory()

def record_publication_history(article,platform,result=None):
    return publication_history.record(article,platform,result)

def already_published(article_id,platform):
    return publication_history.has_published(article_id,platform)

def history_summary():
    return publication_history.summary()
