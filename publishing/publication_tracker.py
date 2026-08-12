import json,os
from datetime import datetime,timezone
from typing import Any,Dict,List,Optional

class PublicationTracker:
    def __init__(self,log_file:str="data/publications.json"):
        self.name="Publication Tracker"
        self.version="1.0.0"
        self.log_file=log_file
        self._ensure_storage()

    def record(self,article:Dict[str,Any],platform:str,publisher_result:Dict[str,Any]=None,status:str="",error:str="")->Dict[str,Any]:
        article=article if isinstance(article,dict) else {}
        publisher_result=publisher_result if isinstance(publisher_result,dict) else {}
        record={
            "publication_id":self._publication_id(article,platform),
            "article_id":article.get("id",article.get("article_id","")),
            "title":str(article.get("title",article.get("headline",""))),
            "platform":str(platform or "unknown"),
            "status":status or publisher_result.get("status","UNKNOWN"),
            "published":bool(publisher_result.get("published",False)),
            "external_id":publisher_result.get("external_id",""),
            "url":publisher_result.get("url",""),
            "error":error or publisher_result.get("error",""),
            "timestamp":datetime.now(timezone.utc).isoformat(),
            "slug":article.get("slug",""),
            "image_url":article.get("image_url","")
        }
        records=self._load()
        records.append(record)
        self._save(records)
        return record

    def get(self,publication_id:str)->Optional[Dict[str,Any]]:
        for item in reversed(self._load()):
            if item.get("publication_id")==publication_id:
                return item
        return None

    def list(self,platform:str=None,status:str=None,limit:int=100)->List[Dict[str,Any]]:
        records=self._load()
        if platform:
            records=[x for x in records if x.get("platform")==platform]
        if status:
            records=[x for x in records if x.get("status")==status]
        return records[-max(1,int(limit)):]

    def published(self,platform:str=None)->List[Dict[str,Any]]:
        return self.list(platform=platform,status="PUBLISHED")

    def failed(self,platform:str=None)->List[Dict[str,Any]]:
        records=self._load()
        if platform:
            records=[x for x in records if x.get("platform")==platform]
        return [x for x in records if not x.get("published",False)]

    def already_published(self,article_id:str,platform:str)->bool:
        if not article_id:
            return False
        return any(
            x.get("article_id")==article_id
            and x.get("platform")==platform
            and x.get("published") is True
            for x in self._load()
        )

    def summary(self)->Dict[str,Any]:
        records=self._load()
        total=len(records)
        success=sum(1 for x in records if x.get("published"))
        failed=sum(1 for x in records if not x.get("published"))
        platforms=sorted({x.get("platform") for x in records if x.get("platform")})
        return {
            "tracker":self.name,
            "version":self.version,
            "total_publications":total,
            "successful":success,
            "failed":failed,
            "success_rate":round(success/total*100,2) if total else 0,
            "platforms":platforms
        }

    def status(self)->Dict[str,Any]:
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "log_file":self.log_file,
            "summary":self.summary()
        }

    def _publication_id(self,article,platform):
        article_id=str(article.get("id",article.get("article_id","")))
        title=str(article.get("title",article.get("headline","")))
        stamp=datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        raw=f"{article_id}|{title}|{platform}|{stamp}"
        return "pub_"+__import__("hashlib").sha256(raw.encode()).hexdigest()[:16]

    def _ensure_storage(self):
        directory=os.path.dirname(self.log_file)
        if directory:
            os.makedirs(directory,exist_ok=True)
        if not os.path.exists(self.log_file):
            self._save([])

    def _load(self):
        try:
            with open(self.log_file,"r",encoding="utf-8") as f:
                data=json.load(f)
            return data if isinstance(data,list) else []
        except (FileNotFoundError,json.JSONDecodeError,OSError):
            return []

    def _save(self,records):
        temp=self.log_file+".tmp"
        with open(temp,"w",encoding="utf-8") as f:
            json.dump(records,f,ensure_ascii=False,indent=2)
        os.replace(temp,self.log_file)


publication_tracker=PublicationTracker()

def record_publication(article,platform,publisher_result=None,status="",error=""):
    return publication_tracker.record(article,platform,publisher_result,status,error)

def publication_summary():
    return publication_tracker.summary()

if __name__=="__main__":
    print(publication_tracker.status())
