import base64,json,os,logging
from datetime import datetime,timezone
from typing import Any,Dict,List,Optional
import requests
from xml.sax.saxutils import escape
logger=logging.getLogger("NewsFactory.GitHubPublisher")

class GitHubPublisher:
    platform="github"
    def __init__(self,repository:Optional[str]=None,token:Optional[str]=None,branch:Optional[str]=None,articles_path:Optional[str]=None,site_url:Optional[str]=None,sitemap_path:Optional[str]=None,timeout:int=30):
        self.repository=(repository or os.getenv("GITHUB_REPOSITORY","")).strip()
        self.token=(token or os.getenv("GITHUB_TOKEN","")).strip()
        self.branch=(branch or os.getenv("GITHUB_BRANCH","main")).strip()
        self.articles_path=(articles_path or os.getenv("GITHUB_ARTICLES_PATH","data/articles.json")).strip().strip("/")
        self.site_url=(site_url or os.getenv("GITHUB_SITE_URL","")).strip().rstrip("/")
        self.sitemap_path=(sitemap_path or os.getenv("GITHUB_SITEMAP_PATH","sitemap.xml")).strip().strip("/")
        self.timeout=timeout
        self.name="GitHub Website Publisher"
        self.version="2.1.0"

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
            sitemap_result=self._update_sitemap(articles)
            result={
                "status":"PUBLISHED",
                "published":True,
                "platform":self.platform,
                "action":action,
                "article_slug":slug,
                "external_id":file_sha or commit_sha,
                "commit_sha":commit_sha,
                "file_sha":file_sha,
                "path":self.articles_path,
                "url":self._article_url(normalized),
                "github_url":content_data.get("html_url",""),
                "commit":commit,
                "response":data,
                "sitemap":sitemap_result,
            }
            if not sitemap_result.get("updated",False):
                result["status"]="PUBLISHED_WITH_WARNING"
                result["sitemap_warning"]=sitemap_result.get("error","Sitemap update failed.")
                logger.warning("ARTICLE PUBLISHED | sitemap update failed: %s",result["sitemap_warning"])
            return result
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

    def _get_articles_file(self)->Dict[str,Any]:
        response=requests.get(self._contents_endpoint(self.articles_path),params={"ref":self.branch},headers=self._headers(),timeout=self.timeout)
        if response.status_code==404:return {"articles":[],"sha":""}
        if not response.ok:raise requests.RequestException(self._github_error(response))
        data=response.json()
        encoded=data.get("content","")
        if not encoded:return {"articles":[],"sha":data.get("sha","")}
        try:
            decoded=base64.b64decode(encoded.replace("\n","").strip()).decode("utf-8")
            articles=json.loads(decoded)
            if not isinstance(articles,list):articles=[]
        except Exception as exc:
            raise ValueError(f"Could not decode or parse {self.articles_path}: {exc}")
        return {"articles":articles,"sha":data.get("sha","")}

    def _update_sitemap(self,articles:List[Dict[str,Any]])->Dict[str,Any]:
        if not self.site_url:
            return {"updated":False,"error":"GITHUB_SITE_URL is not configured."}
        try:
            sitemap=self._build_sitemap(articles)
            current=self._get_file(self.sitemap_path)
            payload={"message":"Update newsroom sitemap","content":self._encode(sitemap),"branch":self.branch}
            if current.get("sha"):payload["sha"]=current["sha"]
            response=requests.put(self._contents_endpoint(self.sitemap_path),json=payload,headers=self._headers(),timeout=self.timeout)
            if not response.ok:
                return {"updated":False,"error":self._github_error(response)}
            data=response.json()
            content_data=data.get("content",{})
            commit=data.get("commit",{})
            return {"updated":True,"path":self.sitemap_path,"file_sha":content_data.get("sha",""),"commit_sha":commit.get("sha",""),"url":f"{self.site_url}/sitemap.xml"}
        except requests.RequestException as exc:
            return {"updated":False,"error":str(exc)}
        except Exception as exc:
            logger.exception("Sitemap generation failed.")
            return {"updated":False,"error":str(exc)}

    def _build_sitemap(self,articles:List[Dict[str,Any]])->str:
        urls=[]
        seen=set()
        static_urls=[
            (self.site_url,""),
            (f"{self.site_url}/article.html",""),
            (f"{self.site_url}/category.html",""),
            (f"{self.site_url}/search.html",""),
        ]
        for url,lastmod in static_urls:
            urls.append(self._sitemap_entry(url,lastmod))
        for article in articles:
            if not isinstance(article,dict):continue
            slug=str(article.get("slug","") or "").strip()
            if not slug or slug in seen or not self.site_url:continue
            seen.add(slug)
            url=self._article_url(article)
            lastmod=self._sitemap_date(article.get("published_at",""))
            urls.append(self._sitemap_entry(url,lastmod))
        return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"\n".join(urls)+"\n</urlset>\n"

    def _sitemap_entry(self,url:str,lastmod:str="")->str:
        entry=f"  <url><loc>{escape(url)}</loc>"
        if lastmod:entry+=f"<lastmod>{escape(lastmod)}</lastmod>"
        return entry+"</url>"

    def _sitemap_date(self,value:Any)->str:
        text=str(value or "").strip()
        if not text:return ""
        try:
            normalized=text.replace("Z","+00:00")
            return datetime.fromisoformat(normalized).date().isoformat()
        except Exception:
            return text[:10] if len(text)>=10 else ""

    def _get_file(self,path:str)->Dict[str,Any]:
        response=requests.get(self._contents_endpoint(path),params={"ref":self.branch},headers=self._headers(),timeout=self.timeout)
        if response.status_code==404:return {"sha":""}
        if not response.ok:raise requests.RequestException(self._github_error(response))
        data=response.json()
        return {"sha":data.get("sha","")}

    def _article_url(self,article:Dict[str,Any])->str:
        if not self.site_url:return ""
        slug=str(article.get("slug","") or "").strip()
        return f"{self.site_url}/article.html?slug={slug}" if slug else self.site_url

    def _github_error(self,response)->str:
        try:
            data=response.json()
            message=data.get("message")
            if message:return f"GitHub API {response.status_code}: {message}"
        except Exception:
            pass
        return f"GitHub API {response.status_code}: {response.text[:500]}"

    def _contents_endpoint(self,path:str)->str:
        return f"https://api.github.com/repos/{self.repository}/contents/{path}"

    def _headers(self)->Dict[str,str]:
        return {"Accept":"application/vnd.github+json","Authorization":f"Bearer {self.token}","X-GitHub-Api-Version":"2022-11-28","User-Agent":"AI-News-Factory/2.1"}

    def _encode(self,text:str)->str:
        return base64.b64encode(text.encode("utf-8")).decode("ascii")

    def _configured(self)->bool:
        return bool(self.repository and self.token)

    def status(self)->Dict[str,Any]:
        configured=self._configured()
        return {"engine":self.name,"version":self.version,"status":"READY" if configured else "NOT_CONFIGURED","configured":configured,"repository":self.repository,"branch":self.branch,"articles_path":self.articles_path,"sitemap_path":self.sitemap_path,"site_url":self.site_url}

    def _failure(self,error:str)->Dict[str,Any]:
        return {"status":"FAILED","published":False,"platform":self.platform,"error":str(error)}

def create_github_publisher(repository:Optional[str]=None,token:Optional[str]=None,branch:Optional[str]=None)->GitHubPublisher:
    return GitHubPublisher(repository=repository,token=token,branch=branch)
