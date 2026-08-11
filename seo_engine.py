import re,html
from typing import Any,Dict,List

class SEOEngine:
    def __init__(self):
        self.name="News SEO Intelligence Engine";self.version="1.0.0"
        self.stop_words={"a","an","and","are","as","at","be","by","for","from","in","into","is","it","of","on","or","that","the","this","to","was","were","with"}
    def optimize(self,article:Dict[str,Any],platform:str="website")->Dict[str,Any]:
        if not isinstance(article,dict):raise TypeError("Article must be a dictionary.")
        title=self._clean(article.get("title",article.get("headline","")))
        content=self._clean(article.get("content",article.get("body","")))
        excerpt=self._clean(article.get("excerpt",article.get("summary","")))
        topic=self._clean(article.get("topic",title))
        seo_title=self.create_title(title,platform)
        description=self.create_description(excerpt or content,seo_title)
        keywords=self.extract_keywords(title+" "+content,topic)
        slug=self.create_slug(seo_title)
        tags=self.create_tags(keywords)
        return {"status":"SEO_READY","engine":self.name,"version":self.version,"platform":platform,"title":title,"seo_title":seo_title,"meta_description":description,"slug":slug,"keywords":keywords,"tags":tags,"excerpt":excerpt or self.create_excerpt(content),"canonical_url":self._clean(article.get("canonical_url","")),"robots":"index,follow","schema_type":"NewsArticle"}
    def create_title(self,title:str,platform:str="website")->str:
        title=self._clean(title)
        if not title:return "Latest News and Updates"
        p=platform.lower().strip()
        if p in {"website","google","seo","search"}:
            return self._limit(title,65)
        if p in {"reddit","community"}:
            return self._limit(title,120)
        if p in {"facebook","x","twitter","social"}:
            return self._limit(title,100)
        return self._limit(title,80)
    def create_description(self,text:str,title:str="")->str:
        text=self._clean(text)
        if not text:text=title
        text=re.sub(r"\s+"," ",text)
        return self._limit(text,155)
    def create_excerpt(self,text:str,max_length:int=240)->str:
        text=self._clean(text)
        return self._limit(text,max_length)
    def extract_keywords(self,text:str,topic:str="")->List[str]:
        words=re.findall(r"\b[a-zA-Z][a-zA-Z0-9'-]{2,}\b",str(text).lower())
        counts={}
        for word in words:
            word=word.strip("'-")
            if word in self.stop_words:continue
            counts[word]=counts.get(word,0)+1
        result=[w for w,_ in sorted(counts.items(),key=lambda x:(-x[1],x[0]))]
        topic_words=re.findall(r"\b[a-zA-Z][a-zA-Z0-9'-]{2,}\b",str(topic).lower())
        for word in reversed(topic_words):
            if word not in self.stop_words and word not in result:result.insert(0,word)
        return result[:15]
    def create_tags(self,keywords:List[str])->List[str]:
        return list(dict.fromkeys(str(x).strip() for x in keywords if str(x).strip()))[:10]
    def create_slug(self,title:str)->str:
        value=html.unescape(str(title).lower())
        value=re.sub(r"[^a-z0-9\s-]","",value)
        value=re.sub(r"[\s-]+","-",value).strip("-")
        return value[:100].rstrip("-")
    def build_platform_package(self,article:Dict[str,Any],platforms:List[str]=None)->Dict[str,Any]:
        platforms=platforms if isinstance(platforms,list) and platforms else ["website","google","reddit","social"]
        packages={}
        for platform in platforms:
            packages[platform]=self.optimize(article,platform)
        return {"status":"PLATFORM_SEO_READY","article_id":article.get("id",""),"packages":packages}
    def _limit(self,text:str,length:int)->str:
        text=self._clean(text)
        if len(text)<=length:return text
        value=text[:length].rsplit(" ",1)[0].strip()
        return value or text[:length].strip()
    def _clean(self,value:Any)->str:
        if value is None:return ""
        return re.sub(r"\s+"," ",str(value)).strip()
    def status(self)->Dict[str,Any]:
        return {"engine":self.name,"version":self.version,"status":"READY"}

seo_engine=SEOEngine()

def optimize_article(article,platform="website"):
    return seo_engine.optimize(article,platform)

def build_platform_seo(article,platforms=None):
    return seo_engine.build_platform_package(article,platforms)

if __name__=="__main__":
    test={"title":"Government Announces New Economic Policy","content":"Government officials announced a new economic policy today.","topic":"economic policy"}
    print(optimize_article(test))
