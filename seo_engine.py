import re,html
from typing import Any,Dict,List

class SEOEngine:
    def __init__(self):
        self.name="News SEO Intelligence Engine"
        self.version="2.0.0"
        self.stop_words={"a","an","and","are","as","at","be","by","for","from","in","into","is","it","of","on","or","that","the","this","to","was","were","with"}
        self.platform_limits={"website":65,"google":65,"search":65,"wordpress":70,"reddit":120,"social":100,"facebook":100,"x":100,"twitter":100}
        self.platform_styles={
            "website":"clear factual news headline with strong search relevance",
            "google":"search-friendly news headline with the main event and entity first",
            "wordpress":"human-readable news/blog headline with useful context",
            "reddit":"direct community-oriented headline without clickbait",
            "social":"short compelling social headline without misleading claims",
            "facebook":"clear conversational headline suitable for social sharing",
            "x":"concise headline preserving the main verified development",
            "twitter":"concise headline preserving the main verified development"
        }

    def optimize(self,article:Dict[str,Any],platform:str="website")->Dict[str,Any]:
        if not isinstance(article,dict):
            raise TypeError("Article must be a dictionary.")
        platform=self._normalize_platform(platform)
        title=self._clean(article.get("title",article.get("headline","")))
        content=self._clean(article.get("content",article.get("body","")))
        excerpt=self._clean(article.get("excerpt",article.get("summary",article.get("lead",""))))
        topic=self._clean(article.get("topic",article.get("category","")))
        location=self._clean(article.get("location",""))
        entities=self._entities(article)
        keywords=self.extract_keywords(" ".join([title,content,topic,location,entities]),topic)
        seo_title=self.create_title(title,platform,keywords,topic)
        description=self.create_description(excerpt or content,title,topic)
        slug=self.create_slug(seo_title)
        tags=self.create_tags(keywords)
        headline_variants=self._platform_titles(article,keywords,topic)
        primary_keyword=self._primary_keyword(keywords,topic)
        h1=self._limit(title or seo_title,90)
        canonical=self._clean(article.get("canonical_url",""))
        return {
            "status":"SEO_READY",
            "engine":self.name,
            "version":self.version,
            "platform":platform,
            "title":title or seo_title,
            "seo_title":seo_title,
            "h1":h1,
            "meta_title":seo_title,
            "meta_description":description,
            "description":description,
            "slug":slug,
            "primary_keyword":primary_keyword,
            "keywords":keywords,
            "tags":tags,
            "excerpt":excerpt or self.create_excerpt(content),
            "canonical_url":canonical,
            "robots":"index,follow",
            "schema_type":"NewsArticle",
            "image_alt":self._image_alt(article,title,primary_keyword),
            "headline":headline_variants.get(platform,seo_title),
            "platform_titles":headline_variants,
            "search_intent":self._search_intent(title,content,topic),
            "seo_score":self._seo_score(title,content,keywords,description,slug)
        }

    def build_platform_package(self,article:Dict[str,Any],platforms:List[str]=None)->Dict[str,Any]:
        if not isinstance(article,dict):
            raise TypeError("Article must be a dictionary.")
        platforms=platforms if isinstance(platforms,list) and platforms else ["website","google","wordpress","reddit","social"]
        common_keywords=self.extract_keywords(
            " ".join(str(article.get(k,"")) for k in ("title","headline","content","body","topic","excerpt","summary")),
            self._clean(article.get("topic",""))
        )
        packages={}
        for platform in platforms:
            packages[platform]=self.optimize(article,platform)
            if common_keywords:
                packages[platform]["keywords"]=common_keywords
                packages[platform]["tags"]=self.create_tags(common_keywords)
        return {
            "status":"PLATFORM_SEO_READY",
            "article_id":article.get("id",article.get("article_id","")),
            "packages":packages,
            "platforms":list(packages.keys())
        }

    def create_title(self,title:str,platform:str="website",keywords:List[str]=None,topic:str="")->str:
        title=self._clean(title)
        keywords=keywords or []
        if not title:
            title=topic or (keywords[0] if keywords else "Latest News")
        limit=self.platform_limits.get(platform,65)
        style=self.platform_styles.get(platform,self.platform_styles["website"])
        if platform in {"google","search"}:
            title=self._search_title(title,keywords,topic)
        elif platform=="wordpress":
            title=self._wordpress_title(title,topic)
        elif platform=="reddit":
            title=self._reddit_title(title)
        elif platform in {"social","facebook","x","twitter"}:
            title=self._social_title(title)
        return self._limit(title,limit)

    def _platform_titles(self,article,keywords,topic):
        title=self._clean(article.get("title",article.get("headline","")))
        return {
            "website":self.create_title(title,"website",keywords,topic),
            "google":self.create_title(title,"google",keywords,topic),
            "wordpress":self.create_title(title,"wordpress",keywords,topic),
            "reddit":self.create_title(title,"reddit",keywords,topic),
            "social":self.create_title(title,"social",keywords,topic),
            "facebook":self.create_title(title,"facebook",keywords,topic),
            "x":self.create_title(title,"x",keywords,topic),
            "twitter":self.create_title(title,"twitter",keywords,topic)
        }

    def _search_title(self,title,keywords,topic):
        first=keywords[0] if keywords else ""
        if first and first.lower() not in title.lower() and len(title)<50:
            return f"{first.title()}: {title}"
        return title

    def _wordpress_title(self,title,topic):
        if topic and topic.lower() not in title.lower() and len(title)<60:
            return f"{title}: What to Know"
        return title

    def _reddit_title(self,title):
        title=re.sub(r"^(breaking|urgent|exclusive)\s*[:!-]?\s*","",title,flags=re.I)
        return title.strip()

    def _social_title(self,title):
        title=re.sub(r"\s+"," ",title).strip()
        return title

    def create_description(self,text:str,title:str="",topic:str="")->str:
        text=self._clean(text)
        if not text:
            text=title
        if topic and topic.lower() not in text.lower() and len(text)<115:
            text=f"{text} Follow the latest verified developments on {topic}."
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
            if word not in self.stop_words and word not in result:
                result.insert(0,word)
        return result[:20]

    def create_tags(self,keywords:List[str])->List[str]:
        tags=[]
        for item in keywords:
            value=self._clean(item)
            if value and value.lower() not in {x.lower() for x in tags}:
                tags.append(value)
        return tags[:12]

    def create_slug(self,title:str)->str:
        value=html.unescape(str(title).lower())
        value=re.sub(r"[^a-z0-9\s-]","",value)
        value=re.sub(r"[\s-]+","-",value).strip("-")
        return value[:100].rstrip("-")

    def _primary_keyword(self,keywords,topic):
        if topic:
            topic_words=re.findall(r"\b[a-zA-Z][a-zA-Z0-9'-]{2,}\b",topic.lower())
            if topic_words:
                return " ".join(topic_words[:4])
        return keywords[0] if keywords else ""

    def _image_alt(self,article,title,keyword):
        alt=self._clean(article.get("image_alt",""))
        if alt:return alt[:125]
        return self._limit(f"{title} news image" if title else f"{keyword} news image",125)

    def _search_intent(self,title,content,topic):
        text=" ".join([title,content,topic]).lower()
        if any(x in text for x in ("how to","guide","steps","tutorial")):return "informational"
        if any(x in text for x in ("price","buy","best","compare","cost")):return "commercial"
        if any(x in text for x in ("official","announces","arrested","election","breaking","latest","today")):return "news"
        return "informational"

    def _entities(self,article):
        value=article.get("entities",{})
        if isinstance(value,dict):
            items=[]
            for key in ("people","organizations","locations"):
                x=value.get(key,[])
                if isinstance(x,list):items.extend(str(v) for v in x)
            return " ".join(items)
        if isinstance(value,list):return " ".join(str(x) for x in value)
        return ""

    def _seo_score(self,title,content,keywords,description,slug):
        score=0
        if title:score+=15
        if 35<=len(title)<=65:score+=15
        if content:score+=15
        if keywords:score+=15
        if description:score+=15
        if 100<=len(description)<=155:score+=10
        if slug:score+=10
        if keywords and keywords[0].lower() in title.lower():score+=5
        return min(score,100)

    def _limit(self,text,length):
        text=self._clean(text)
        if len(text)<=length:return text
        value=text[:length].rsplit(" ",1)[0].strip()
        return value or text[:length].strip()

    def _clean(self,value):
        if value is None:return ""
        return re.sub(r"\s+"," ",str(value)).strip()

    def _normalize_platform(self,platform):
        value=self._clean(platform).lower()
        aliases={"site":"website","web":"website","blog":"wordpress","wp":"wordpress","community":"reddit","twitter":"x"}
        return aliases.get(value,value)

    def status(self):
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "platforms":sorted(self.platform_limits.keys())
        }

seo_engine=SEOEngine()

def optimize_article(article,platform="website"):
    return seo_engine.optimize(article,platform)

def build_platform_seo(article,platforms=None):
    return seo_engine.build_platform_package(article,platforms)

if __name__=="__main__":
    test={
        "title":"Government Announces New Economic Policy",
        "content":"Government officials announced a new economic policy today.",
        "topic":"economic policy",
        "excerpt":"Officials announced a new economic policy today."
    }
    print(optimize_article(test,"website"))
    print(build_platform_seo(test))
