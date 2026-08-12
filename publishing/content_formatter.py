from typing import Any,Dict,List
import re

class ContentFormatter:
    def __init__(self):
        self.name="Platform Content Formatter"
        self.version="1.0.0"
        self.platform_limits={
            "website":100000,
            "wordpress":100000,
            "reddit":40000,
            "social":5000,
            "facebook":5000,
            "x":280,
            "twitter":280,
            "punch":100000
        }

    def format(self,article:Dict[str,Any],platform:str="website")->Dict[str,Any]:
        if not isinstance(article,dict):
            raise TypeError("Article must be a dictionary.")
        platform=self._normalize(platform)
        title=self._title(article,platform)
        content=self._content(article,platform)
        excerpt=self._excerpt(article,platform)
        tags=self._tags(article,platform)
        return {
            "status":"FORMATTED",
            "platform":platform,
            "title":title,
            "content":content,
            "excerpt":excerpt,
            "tags":tags,
            "category":article.get("category","news"),
            "slug":article.get("slug",""),
            "image_url":article.get("image_url",""),
            "image_alt":article.get("image_alt",""),
            "image_caption":article.get("image_caption",""),
            "image_credit":article.get("image_credit",""),
            "source_url":article.get("source_url",""),
            "seo":article.get("seo",{})
        }

    def _normalize(self,platform:Any)->str:
        value=str(platform or "website").strip().lower()
        aliases={
            "site":"website",
            "web":"website",
            "blog":"wordpress",
            "wp":"wordpress",
            "fb":"facebook",
            "tweet":"x",
            "twitter":"x"
        }
        return aliases.get(value,value)

    def _title(self,article,platform):
        seo=article.get("seo",{})
        if isinstance(seo,dict):
            titles=seo.get("platform_titles",{})
            if isinstance(titles,dict) and titles.get(platform):
                return str(titles[platform]).strip()
        return str(
            article.get(
                "platform_title",
                article.get(
                    "seo_title",
                    article.get(
                        "title",
                        article.get("headline","")
                    )
                )
            )
        ).strip()

    def _content(self,article,platform):
        content=str(
            article.get(
                "content",
                article.get("body","")
            ) or ""
        ).strip()
        if platform in {"x","twitter"}:
            return self._shorten(content,260)
        if platform in {"social","facebook"}:
            return self._shorten(content,4500)
        return content

    def _excerpt(self,article,platform):
        excerpt=str(
            article.get(
                "excerpt",
                article.get("summary","")
            ) or ""
        ).strip()
        if platform=="x":
            return self._shorten(excerpt,200)
        if platform in {"social","facebook"}:
            return self._shorten(excerpt,500)
        return self._shorten(excerpt,320)

    def _tags(self,article,platform)->List[str]:
        tags=article.get("tags",[])
        if not isinstance(tags,list):
            tags=[]
        result=[]
        for tag in tags:
            value=str(tag).strip()
            if value and value.lower() not in {x.lower() for x in result}:
                result.append(value)
        return result[:10] if platform in {"social","facebook","reddit","x"} else result[:30]

    def _shorten(self,text,limit):
        text=str(text or "").strip()
        if len(text)<=limit:
            return text
        shortened=text[:max(1,limit-3)].rstrip()
        shortened=re.sub(r"\s+\S*$","",shortened)
        return shortened+"..."

    def status(self):
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "platforms":sorted(self.platform_limits)
        }

content_formatter=ContentFormatter()

def format_content(article,platform="website"):
    return content_formatter.format(article,platform)

if __name__=="__main__":
    print(content_formatter.status())
