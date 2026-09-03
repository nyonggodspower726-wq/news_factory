import base64,json,os,logging
from datetime import datetime,timezone
from typing import Any,Dict,List,Optional
import requests
logger=logging.getLogger("NewsFactory.GitHubPublisher")
class GitHubPublisher:
    platform="github"
    def __init__(self,repository:Optional[str]=None,token:Optional[str]=None,branch:Optional[str]=None,articles_path:Optional[str]=None,site_url:Optional[str]=None,timeout:int=30):
        self.repository=(repository or os.getenv("GITHUB_REPOSITORY","")).strip()
        self.token=(token or os.getenv("GITHUB_TOKEN","")).strip()
        self.branch=(branch or os.getenv("GITHUB_BRANCH","main")).strip()
        self.articles_path=(articles_path or os.getenv("GITHUB_ARTICLES_PATH","data/articles.json")).strip().strip("/")
        self.site_url=(site_url or os.getenv("GITHUB_SITE_URL","")).strip().rstrip("/")
        self.timeout=timeout
        self.name="GitHub Website Publisher"
        self.version="2.0.0"
    def publish(self,article:Dict[str,Any])->Dict[str,Any]:
        if not isinstance(article,dict):
            return self._failure("Article must be a dictionary.")
        if not self._configured():
            return {"status":"NOT_CONFIGURED","published":False,"platform":self.platform,"message":"GitHub publishing credentials are not configured."}
        title=str(article.get("title",article.get("headline","")) or "").strip()
        slug=str(article.get("slug","") or "").strip()
        content=str(article.get("content",article.get("body","")) or "").strip()
        if not title:return self._failure("Article title is missing.")
        if not slug:return self._failure("Article slug is missing.")
        if not content:return self._failure("Article content is missing.")
        try:
            logger.info("Publishing article to GitHub: %s",title)
            current=self._get_articles_file()
            articles=current.get("articles",[])
            sha=current.get("sha","")
            if not isinstance(articles,list):articles=[]
            normalized=self._normalize_article(article)
            index=None
            for i,existing in enumerate(articles):
                if isinstance(existing,dict) and str(existing.get("slug","") or "").strip()==slug:
                    index=i
                    break
            action="updated" if index is not None else "created"
            if index is not None:articles[index]=normalized
            else:articles.insert(0,normalized)
            articles=self._sort_articles(articles)
            document=json.dumps(articles,ensure_ascii=False,indent=2)+"\n"
            payload={"message":f"{'Update' if action=='updated' else 'Publish'} news article: {title}","content":self._encode(document),"branch":self.branch}
            if sha:payload["sha"]=sha
            response=requests.put(self._contents_endpoint(self.articles_path),json=payload,headers=self._headers(),timeout=self.timeout)
            if not response.ok:
                return self._failure(self._github_error(response))
            data=response.json()
            commit=data.get("commit",{})
            content_data=data.get("content",{})
            commit_sha=str(commit.get("sha","") or "")
            file_sha=str(content_data.get("sha","") or "")
            return {"status":"PUBLISHED","published":True,"platform":self.platform,"action":action,"article_slug":slug,"external_id":file_sha or commit_sha,"commit_sha":commit_sha,"file_sha":file_sha,"path":self.articles_path,"url":self._article_url(normalized),"github_url":content_data.get("html_url",""),"commit":commit,"response":data}
        except requests.RequestException as exc:
            logger.exception("GitHub publishing request failed.")
            return self._failure(str(exc))
        except Exception as exc:
            logger.exception("Unexpected GitHub publishing error.")
            return self._failure(str(exc))
    def _normalize_article(self,article:Dict[str,Any])->Dict[str,Any]:
        title=str(article.get("title",article.get("headline","")) or "").strip()
        slug=str(article.get("slug","") or "").strip()
        category=str(article.get("category","World") or "World").strip()
        excerpt=str(article.get("excerpt",article.get("summary","")) or "").strip()
        content=str(article.get("content",article.get("body","")) or "").strip()
        author=str(article.get("author","AI News Factory") or "AI News Factory").strip()
        published_at=article.get("published_at") or article.get("date") or article.get("publishedAt")
        if not published_at:published_at=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        tags=article.get("tags",[])
        if not isinstance(tags,list):tags=[]
        tags=[str(x).strip() for x in tags if str(x).strip()]
        keywords=article.get("keywords",[])
        if not isinstance(keywords,list):keywords=[]
        keywords=[str(x).strip() for x in keywords if str(x).strip()]
        sources=article.get("sources",[])
        if not isinstance(sources,list):sources=[]
        normalized_sources=[]
        for source in sources:
            if isinstance(source,dict):normalized_sources.append(source)
            elif source:normalized_sources.append({"name":str(source)})
        image=article.get("image") or article.get("image_url") or ""
        seo=article.get("seo",{})
        if not isinstance(seo,dict):seo={}
        return {"id":article.get("id") or slug,"slug":slug,"title":title,"category":category,"excerpt":excerpt,"content":content,"author":author,"published_at":published_at,"read_time":article.get("read_time",article.get("reading_time","5 min read")),"featured":bool(article.get("featured",False)),"image":image,"image_url":image,"image_alt":article.get("image_alt",""),"image_caption":article.get("image_caption",""),"image_credit":article.get("image_credit",""),"tags":tags,"keywords":keywords,"sources":normalized_sources,"source_url":article.get("source_url",""),"seo":seo}
    def _sort_articles(self,articles:List[Dict[str,Any]])->List[Dict[str,Any]]:
        return sorted(articles,key=lambda x:str(x.get("published_at","") or "") if isinstance(x,dict) else "",reverse=True)
