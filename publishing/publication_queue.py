import json,os,uuid
from datetime import datetime,timezone
from typing import Any,Dict,List,Optional

class PublicationQueue:
    def __init__(self,queue_file:str="data/publication_queue.json"):
        self.name="Publication Queue"
        self.version="1.0.0"
        self.queue_file=queue_file
        self._ensure_storage()

    def enqueue(self,article:Dict[str,Any],platform:str="website",priority:str="NORMAL",scheduled_at:Optional[str]=None)->Dict[str,Any]:
        if not isinstance(article,dict):
            raise TypeError("Article must be a dictionary.")
        item={
            "queue_id":"queue_"+uuid.uuid4().hex[:16],
            "article_id":str(article.get("id",article.get("article_id",""))),
            "title":str(article.get("title",article.get("headline",""))),
            "platform":str(platform or "website").lower(),
            "priority":str(priority or "NORMAL").upper(),
            "scheduled_at":scheduled_at,
            "status":"QUEUED",
            "attempts":0,
            "created_at":datetime.now(timezone.utc).isoformat(),
            "article":article
        }
        items=self._load()
        items.append(item)
        self._save(items)
        return item

    def next(self,platform:Optional[str]=None)->Optional[Dict[str,Any]]:
        items=self._load()
        ready=[x for x in items if x.get("status")=="QUEUED" and (not platform or x.get("platform")==platform)]
        if not ready:return None
        order={"CRITICAL":0,"HIGH":1,"NORMAL":2,"LOW":3}
        ready.sort(key=lambda x:(order.get(x.get("priority","NORMAL"),2),x.get("created_at","")))
        return ready[0]

    def reserve(self,queue_id:str)->Optional[Dict[str,Any]]:
        items=self._load()
        for item in items:
            if item.get("queue_id")==queue_id and item.get("status")=="QUEUED":
                item["status"]="PROCESSING"
                item["attempts"]=int(item.get("attempts",0))+1
                item["processing_at"]=datetime.now(timezone.utc).isoformat()
                self._save(items)
                return item
        return None

    def complete(self,queue_id:str,result:Dict[str,Any]=None)->Optional[Dict[str,Any]]:
        return self._finish(queue_id,"PUBLISHED",result)

    def fail(self,queue_id:str,error:str="",result:Dict[str,Any]=None)->Optional[Dict[str,Any]]:
        items=self._load()
        for item in items:
            if item.get("queue_id")==queue_id:
                item["status"]="FAILED"
                item["failed_at"]=datetime.now(timezone.utc).isoformat()
                item["error"]=str(error or "")
                item["result"]=result if isinstance(result,dict) else {}
                self._save(items)
                return item
        return None

    def retry(self,queue_id:str)->Optional[Dict[str,Any]]:
        items=self._load()
        for item in items:
            if item.get("queue_id")==queue_id and item.get("status") in {"FAILED","PROCESSING"}:
                item["status"]="QUEUED"
                item["retry_at"]=datetime.now(timezone.utc).isoformat()
                self._save(items)
                return item
        return None

    def cancel(self,queue_id:str)->Optional[Dict[str,Any]]:
        return self._finish(queue_id,"CANCELLED")

    def remove(self,queue_id:str)->bool:
        items=self._load()
        new=[x for x in items if x.get("queue_id")!=queue_id]
        changed=len(new)!=len(items)
        if changed:self._save(new)
        return changed

    def get(self,queue_id:str)->Optional[Dict[str,Any]]:
        for item in self._load():
            if item.get("queue_id")==queue_id:return item
        return None

    def list(self,status:Optional[str]=None,platform:Optional[str]=None,limit:int=100)->List[Dict[str,Any]]:
        items=self._load()
        if status:items=[x for x in items if x.get("status")==status]
        if platform:items=[x for x in items if x.get("platform")==platform]
        return items[-max(1,int(limit)):]

    def clear_completed(self)->int:
        items=self._load()
        remaining=[x for x in items if x.get("status") not in {"PUBLISHED","CANCELLED"}]
        removed=len(items)-len(remaining)
        self._save(remaining)
        return removed

    def summary(self)->Dict[str,Any]:
        items=self._load()
        counts={}
        for item in items:
            status=item.get("status","UNKNOWN")
            counts[status]=counts.get(status,0)+1
        return {"engine":self.name,"version":self.version,"total":len(items),"counts":counts}

    def status(self)->Dict[str,Any]:
        return {"engine":self.name,"version":self.version,"status":"READY","queue_file":self.queue_file,"summary":self.summary()}

    def _finish(self,queue_id,status,result=None):
        items=self._load()
        for item in items:
            if item.get("queue_id")==queue_id:
                item["status"]=status
                item["completed_at"]=datetime.now(timezone.utc).isoformat()
                item["result"]=result if isinstance(result,dict) else {}
                self._save(items)
                return item
        return None

    def _ensure_storage(self):
        directory=os.path.dirname(self.queue_file)
        if directory:os.makedirs(directory,exist_ok=True)
        if not os.path.exists(self.queue_file):self._save([])

    def _load(self):
        try:
            with open(self.queue_file,"r",encoding="utf-8") as f:
                data=json.load(f)
            return data if isinstance(data,list) else []
        except (FileNotFoundError,json.JSONDecodeError,OSError):
            return []

    def _save(self,items):
        temp=self.queue_file+".tmp"
        with open(temp,"w",encoding="utf-8") as f:
            json.dump(items,f,ensure_ascii=False,indent=2)
        os.replace(temp,self.queue_file)

publication_queue=PublicationQueue()

def enqueue_publication(article,platform="website",priority="NORMAL",scheduled_at=None):
    return publication_queue.enqueue(article,platform,priority,scheduled_at)

def get_next_publication(platform=None):
    return publication_queue.next(platform)

def publication_queue_status():
    return publication_queue.status()
