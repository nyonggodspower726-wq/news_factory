import logging
from typing import Any,Dict,Optional

logger=logging.getLogger("NewsFactory.PlatformRouter")


class PlatformRouter:
    def __init__(
        self,
        website_publisher=None,
        wordpress_publisher=None,
        social_publisher=None,
        github_publisher=None
    ):
        self.name="Platform Distribution Router"
        self.version="2.0.0"
        self.website_publisher=self._load(website_publisher,"publishing.website_publisher","WebsitePublisher")
        self.wordpress_publisher=self._load(wordpress_publisher,"publishing.wordpress_publisher","WordPressPublisher")
        self.social_publisher=self._load(social_publisher,"publishing.social_publisher","SocialPublisher")
        self.github_publisher=self._load(github_publisher,"publishing.github_publisher","GitHubPublisher")
        self.platforms={"website","wordpress","social","github"}

    def _load(self,instance,module_name,class_name):
        if instance is not None:return instance
        try:
            module=__import__(module_name,fromlist=[class_name])
            cls=getattr(module,class_name,None)
            return cls() if cls else None
        except Exception as exc:
            logger.warning("Could not load %s: %s",class_name,exc)
            return None

    def prepare(self,article:Dict[str,Any],platform:str="website")->Dict[str,Any]:
        if not isinstance(article,dict):
            return {"status":"FAILED","platform":platform,"error":"Article must be a dictionary."}
        platform=self._normalize_platform(platform)
        if platform not in self.platforms:
            return {"status":"UNSUPPORTED_PLATFORM","platform":platform,"supported_platforms":sorted(self.platforms)}
        prepared=dict(article)
        prepared["platform"]=platform
        prepared["platform_style"]=self._platform_style(platform)
        prepared["platform_title"]=self._platform_title(article,platform)
        prepared["platform_excerpt"]=self._platform_excerpt(article,platform)
        prepared["platform_tags"]=self._platform_tags(article,platform)
        prepared["platform_payload"]=self._build_payload(prepared,platform)
        return {"status":"READY","platform":platform,"article":prepared,"payload":prepared["platform_payload"]}

    def publish(self,article:Dict[str,Any],platform:str="website")->Dict[str,Any]:
        prepared=self.prepare(article,platform)
        if prepared.get("status")!="READY":
            return {**prepared,"published":False}
        publisher=self._publisher(prepared["platform"])
        if publisher is None:
            return {**prepared,"status":"PLATFORM_NOT_CONNECTED","published":False,"message":f"No publisher connected for {prepared['platform']}."}
        try:
            if not hasattr(publisher,"publish"):
                return {**prepared,"status":"INVALID_PUBLISHER","published":False,"message":"Publisher does not expose publish()."}
            result=publisher.publish(prepared["payload"])
            if not isinstance(result,dict):
                result={"status":"UNKNOWN","published":False,"response":result}
            published=bool(result.get("published",False))
            return {**prepared,"status":"PUBLISHED" if published else "PUBLISH_FAILED","published":published,"publisher_result":result}
        except Exception as exc:
            logger.exception("Platform publishing failed.")
            return {**prepared,"status":"PUBLISH_FAILED","published":False,"error":str(exc)}

    def publish_many(self,article:Dict[str,Any],platforms=None)->Dict[str,Any]:
        platforms=platforms if isinstance(platforms,list) and platforms else ["website"]
        results={}
        for platform in platforms:
            results[self._normalize_platform(platform)]=self.publish(article,platform)
        return {"status":"COMPLETE","results":results,"published_count":sum(1 for x in results.values() if x.get("published"))}

    def _publisher(self,platform):
        return {
            "website":self.website_publisher,
            "wordpress":self.wordpress_publisher,
            "social":self.social_publisher,
            "github":self.github_publisher
        }.get(platform)

    def _normalize_platform(self,platform:Any)->str:
        value=str(platform or "website").strip().lower()
        aliases={
            "site":"website","web":"website","blog":"wordpress",
            "wp":"wordpress","word_press":"wordpress",
            "facebook":"social","reddit":"social",
            "x":"social","twitter":"social"
        }
        return aliases.get(value,value)

    def _platform_style(self,platform):
        return {
            "website":"SEO_NEWS_ARTICLE",
            "wordpress":"LONG_FORM_NEWS_BLOG",
            "social":"SOCIAL_NEWS_POST",
            "github":"TECHNICAL_NEWS_DOCUMENT"
        }.get(platform,"GENERAL_NEWS")

    def _platform_title(self,article,platform):
        seo=article.get("seo",{}) if isinstance(article.get("seo",{}),dict) else {}
        titles=seo.get("platform_titles",{}) if isinstance(seo.get("platform_titles",{}),dict) else {}
        return str(titles.get(platform) or article.get("platform_title") or article.get("seo_title") or article.get("title") or article.get("headline") or "").strip()

    def _platform_excerpt(self,article,platform):
        text=str(article.get("excerpt",article.get("summary","")) or "").strip()
        return self._shorten(text,280 if platform=="social" else 320 if platform=="wordpress" else 300)

    def _platform_tags(self,article,platform):
        tags=article.get("tags",[])
        if not isinstance(tags,list):tags=[]
        result=[]
        for tag in tags:
            tag=str(tag).strip()
            if tag and tag.lower() not in {x.lower() for x in result}:result.append(tag)
        return result[:10] if platform=="social" else result[:30]

    def _build_payload(self,article,platform):
        seo=article.get("seo",{}) if isinstance(article.get("seo",{}),dict) else {}
        return {
            "title":self._platform_title(article,platform),
            "content":article.get("content",article.get("body","")),
            "excerpt":self._platform_excerpt(article,platform),
            "slug":article.get("slug",""),
            "category":article.get("category","news"),
            "tags":self._platform_tags(article,platform),
            "keywords":article.get("keywords",seo.get("keywords",[])),
            "meta_description":article.get("meta_description",seo.get("meta_description","")),
            "image_url":article.get("image_url",""),
            "image_alt":article.get("image_alt",""),
            "image_caption":article.get("image_caption",""),
            "image_credit":article.get("image_credit",""),
            "source_url":article.get("source_url",""),
            "platform":platform,
            "platform_style":self._platform_style(platform),
            "seo":seo
        }

    def _shorten(self,text,limit):
        text=str(text or "").strip()
        return text if len(text)<=limit else text[:limit-3].rstrip()+"..."

    def status(self):
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "platforms":sorted(self.platforms),
            "connected":{
                "website":self.website_publisher is not None,
                "wordpress":self.wordpress_publisher is not None,
                "social":self.social_publisher is not None,
                "github":self.github_publisher is not None
            }
        }


platform_router=PlatformRouter()


def prepare_platform(article,platform="website"):
    return platform_router.prepare(article,platform)


def publish_platform(article,platform="website"):
    return platform_router.publish(article,platform)


def publish_many(article,platforms=None):
    return platform_router.publish_many(article,platforms)
