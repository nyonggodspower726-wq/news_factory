import logging
from typing import Any,Dict,Optional
from article_engine import ArticleEngine
from seo_engine import SEOEngine
from media.media_manager import MediaManager
from publishing.platform_router import PlatformRouter
from publishing.website_publisher import WebsitePublisher
from publishing.wordpress_publisher import WordPressPublisher
from publishing.reddit_publisher import RedditPublisher
from publishing.social_publisher import SocialPublisher
from publishing.github_publisher import GitHubPublisher
logger=logging.getLogger("NewsFactory.PublicationOrchestrator")

class PublicationOrchestrator:
    def __init__(self,article_engine:Optional[ArticleEngine]=None,seo_engine:Optional[SEOEngine]=None,media_manager:Optional[MediaManager]=None,platform_router:Optional[PlatformRouter]=None):
        self.name="Publication Orchestrator"
        self.version="2.0.0"
        self.article_engine=article_engine or ArticleEngine()
        self.seo_engine=seo_engine or SEOEngine()
        self.media_manager=media_manager or MediaManager()
        self.github_publisher=GitHubPublisher()
        self.website_publisher=self.github_publisher
        self.wordpress_publisher=WordPressPublisher()
        self.reddit_publisher=RedditPublisher()
        self.social_publisher=SocialPublisher()
        self.platform_router=(
            platform_router or
            PlatformRouter(
                website_publisher=self.github_publisher,
                wordpress_publisher=self.wordpress_publisher,
                social_publisher=self.social_publisher,
                github_publisher=self.github_publisher
            )
        )

    def prepare(self,package:Dict[str,Any],platform:str="website")->Dict[str,Any]:
        if not isinstance(package,dict):
            return {"status":"FAILED","stage":"INPUT","publication_safe":False,"error":"Pipeline package must be a dictionary."}
        try:
            article_result=self.article_engine.create(package)
            if not isinstance(article_result,dict):
                return {"status":"FAILED","stage":"ARTICLE","publication_safe":False,"error":"Article engine returned invalid data."}
            if article_result.get("publication_safe") is False:
                return {"status":"BLOCKED","stage":"ARTICLE_SAFETY","publication_safe":False,"reason":"Article failed publication safety.","article":article_result}
            article=dict(article_result)
            seo_result=self.seo_engine.optimize(article,platform=platform)
            if not isinstance(seo_result,dict):seo_result={}
            article["seo"]=seo_result
            article["seo_title"]=seo_result.get("seo_title",article.get("title",""))
            article["meta_description"]=seo_result.get("meta_description","")
            article["slug"]=seo_result.get("slug",article.get("slug",""))
            article["keywords"]=seo_result.get("keywords",article.get("keywords",[]))
            article["tags"]=seo_result.get("tags",article.get("tags",[]))
            article["title"]=article.get("title") or seo_result.get("title","")
            article["excerpt"]=article.get("excerpt") or seo_result.get("excerpt","")
            story=package.get("story",{})
            if not isinstance(story,dict):story={}
            media_story=dict(story)
            media_story.update({"title":article.get("title",""),"topic":article.get("topic",""),"source_url":article.get("source_url",""),"excerpt":article.get("excerpt","")})
            article=self.media_manager.attach(article,media_story)
            media_validation=self.media_manager.validate_article_media(article)
            if not isinstance(media_validation,dict):media_validation={"valid":True}
            router_result=self.platform_router.prepare(article,platform)
            if not isinstance(router_result,dict):
                return {"status":"FAILED","stage":"PLATFORM_ROUTER","publication_safe":False,"error":"Platform router returned invalid data."}
            if router_result.get("status")!="READY":
                return {"status":"FAILED","stage":"PLATFORM_ROUTER","publication_safe":False,"router":router_result,"article":article}
            prepared_article=router_result.get("article",article)
            return {"status":"READY_FOR_PUBLICATION","publication_safe":True,"platform":platform,"article":prepared_article,"seo":seo_result,"media":self.media_manager.prepare_social(prepared_article),"media_validation":media_validation,"router":router_result}
        except Exception as exc:
            logger.exception("Publication preparation failed.")
            return {"status":"FAILED","stage":"ORCHESTRATOR","publication_safe":False,"error":str(exc)}

    def publish(self,package:Dict[str,Any],platform:str="website")->Dict[str,Any]:
        prepared=self.prepare(package,platform)
        if prepared.get("status")!="READY_FOR_PUBLICATION":
            return {**prepared,"published":False}
        article=prepared.get("article",{})
        try:
            result=self.platform_router.publish(article,platform)
        except Exception as exc:
            logger.exception("Publication failed.")
            result={"status":"PUBLISH_FAILED","published":False,"error":str(exc)}
        if not isinstance(result,dict):
            result={"status":"PUBLISH_FAILED","published":False,"response":result}
        published=bool(result.get("published",False))
        return {**prepared,"status":"PUBLISHED" if published else "PUBLISH_FAILED","published":published,"publisher_result":result}

    def publish_approved(self,package:Dict[str,Any],platform:str="website")->Dict[str,Any]:
        if not isinstance(package,dict):
            return {"status":"BLOCKED","published":False,"reason":"Invalid pipeline package."}
        editorial=package.get("editorial",{})
        if isinstance(editorial,dict):
            decision=str(editorial.get("decision","")).strip().upper()
            if decision and decision!="APPROVED":
                return {"status":"BLOCKED","published":False,"reason":f"Editorial decision is {decision}."}
        if package.get("publication_ready") is False:
            return {"status":"BLOCKED","published":False,"reason":"Pipeline marked package as not publication-ready."}
        return self.publish(package,platform)

    def status(self)->Dict[str,Any]:
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "components":{
                "article_engine":self._component_status(self.article_engine),
                "seo_engine":self._component_status(self.seo_engine),
                "media_manager":self._component_status(self.media_manager),
                "platform_router":self._component_status(self.platform_router),
                "publishers":{
                    "website":self._component_status(self.website_publisher),
                    "wordpress":self._component_status(self.wordpress_publisher),
                    "reddit":self._component_status(self.reddit_publisher),
                    "social":self._component_status(self.social_publisher),
                    "github":self._component_status(self.github_publisher)
                }
            }
        }

    def _component_status(self,component:Any)->Dict[str,Any]:
        if component is None:return {"status":"MISSING"}
        try:
            if hasattr(component,"status"):
                result=component.status()
                if isinstance(result,dict):return result
            return {"status":"READY","component":component.__class__.__name__}
        except Exception as exc:
            return {"status":"ERROR","error":str(exc)}

publication_orchestrator=PublicationOrchestrator()

def prepare_publication(package,platform="website"):
    return publication_orchestrator.prepare(package,platform)

def publish_publication(package,platform="website"):
    return publication_orchestrator.publish(package,platform)

def publish_approved(package,platform="website"):
    return publication_orchestrator.publish_approved(package,platform)

def publication_status():
    return publication_orchestrator.status()

if __name__=="__main__":
    import json
    print(json.dumps(publication_orchestrator.status(),indent=2,default=str))
