import logging
from typing import Any,Dict,List,Optional

from article_engine import ArticleEngine
from seo_engine import SEOEngine
from media.media_manager import MediaManager
from publishing.content_formatter import ContentFormatter
from publishing.platform_router import PlatformRouter
from publishing.publication_guard import PublicationGuard
from publishing.publication_queue import PublicationQueue
from publishing.publication_tracker import PublicationTracker
from publishing.publication_history import PublicationHistory
from publishing.distribution_manager import DistributionManager
from publication_orchestrator import PublicationOrchestrator

logger=logging.getLogger("NewsFactory.FactoryPipeline")


class FactoryPipeline:
    def __init__(
        self,
        article_engine:Optional[ArticleEngine]=None,
        seo_engine:Optional[SEOEngine]=None,
        media_manager:Optional[MediaManager]=None,
        formatter:Optional[ContentFormatter]=None,
        router:Optional[PlatformRouter]=None,
        guard:Optional[PublicationGuard]=None,
        queue:Optional[PublicationQueue]=None,
        tracker:Optional[PublicationTracker]=None,
        history:Optional[PublicationHistory]=None,
        distribution:Optional[DistributionManager]=None,
        orchestrator:Optional[PublicationOrchestrator]=None
    ):
        self.name="AI News Factory Pipeline"
        self.version="1.0.0"
        self.article_engine=article_engine or ArticleEngine()
        self.seo_engine=seo_engine or SEOEngine()
        self.media_manager=media_manager or MediaManager()
        self.formatter=formatter or ContentFormatter()
        self.router=router or PlatformRouter()
        self.guard=guard or PublicationGuard()
        self.queue=queue or PublicationQueue()
        self.tracker=tracker or PublicationTracker()
        self.history=history or PublicationHistory()
        self.distribution=distribution or DistributionManager(
            router=self.router,
            queue=self.queue,
            tracker=self.tracker,
            history=self.history,
            guard=self.guard
        )
        self.orchestrator=orchestrator or PublicationOrchestrator(
            article_engine=self.article_engine,
            seo_engine=self.seo_engine,
            media_manager=self.media_manager,
            platform_router=self.router
        )

    def prepare(
        self,
        package:Dict[str,Any],
        platform:str="website"
    )->Dict[str,Any]:
        if not isinstance(package,dict):
            return self._fail("INPUT","Pipeline package must be a dictionary.")

        try:
            article=self.article_engine.create(package)
            if not isinstance(article,dict):
                return self._fail("ARTICLE","Article engine returned invalid data.")

            seo=self.seo_engine.optimize(article,platform)
            if not isinstance(seo,dict):
                return self._fail("SEO","SEO engine returned invalid data.")

            article=dict(article)
            article["seo"]=seo
            article["seo_title"]=seo.get("seo_title",article.get("title",""))
            article["meta_description"]=seo.get("meta_description","")
            article["slug"]=seo.get("slug",article.get("slug",""))
            article["keywords"]=seo.get("keywords",[])
            article["tags"]=seo.get("tags",article.get("tags",[]))

            story=package.get("story",{})
            story=dict(story) if isinstance(story,dict) else {}
            story.update({
                "title":article.get("title",""),
                "headline":article.get("headline",""),
                "topic":article.get("topic",""),
                "excerpt":article.get("excerpt",""),
                "source_url":article.get("source_url",""),
                "image_url":article.get("image_url","")
            })

            try:
                article=self.media_manager.attach(
                    article,
                    story,
                    generate_image=True,
                    platform=platform
                )
            except TypeError:
                article=self.media_manager.attach(
                    article,
                    story
                )

            gate_package=dict(package)
            gate_package["article"]=article
            gate_package["verification"]=package.get("verification",{})
            gate_package["misinformation"]=package.get("misinformation",{})
            gate_package["investigation"]=package.get("investigation",{})
            gate_package["sources"]=package.get("sources",article.get("sources",[]))
            gate_package["publication_ready"]=package.get("publication_ready",True)

            guard_result=self.guard.check(
                gate_package,
                platform
            )

            formatted=self.formatter.format(
                article,
                platform
            )

            router_result=self.router.prepare(
                formatted,
                platform
            )

            return {
                "status":"READY" if guard_result.get("publication_allowed") and router_result.get("status")=="READY" else "BLOCKED",
                "platform":platform,
                "article":article,
                "seo":seo,
                "media":self.media_manager.prepare_social(article),
                "guard":guard_result,
                "formatted":formatted,
                "router":router_result
            }

        except Exception as exc:
            logger.exception("Factory preparation failed.")
            return self._fail("PIPELINE",str(exc))

    def publish(
        self,
        package:Dict[str,Any],
        platform:str="website",
        queue_first:bool=False
    )->Dict[str,Any]:
        prepared=self.prepare(package,platform)

        if prepared.get("status")!="READY":
            return {
                **prepared,
                "published":False
            }

        article=prepared["article"]

        if queue_first:
            queued=self.queue.enqueue(
                article,
                platform
            )
            return {
                **prepared,
                "status":"QUEUED",
                "published":False,
                "queue":queued
            }

        result=self.router.publish(
            article,
            platform
        )

        published=bool(
            result.get("published",False)
        )

        try:
            self.tracker.record(
                article,
                platform,
                result
            )
        except Exception:
            logger.exception("Tracker recording failed.")

        try:
            self.history.record(
                article,
                platform,
                result
            )
        except Exception:
            logger.exception("History recording failed.")

        return {
            **prepared,
            "status":"PUBLISHED" if published else result.get("status","PUBLISH_FAILED"),
            "published":published,
            "publisher_result":result
        }

    def queue(
        self,
        package:Dict[str,Any],
        platforms:Optional[List[str]]=None,
        priority:str="NORMAL"
    )->Dict[str,Any]:
        prepared=self.prepare(
            package,
            "website"
        )

        if prepared.get("status")!="READY":
            return {
                **prepared,
                "queued":False
            }

        article=prepared["article"]
        result=self.distribution.queue(
            article,
            platforms,
            priority
        )

        return {
            **prepared,
            "status":result.get("status","QUEUED"),
            "queued":result.get("queued_count",0)>0,
            "queue_result":result
        }

    def publish_many(
        self,
        package:Dict[str,Any],
        platforms:Optional[List[str]]=None
    )->Dict[str,Any]:
        prepared=self.prepare(
            package,
            "website"
        )

        if prepared.get("status")!="READY":
            return {
                **prepared,
                "published_count":0
            }

        result=self.distribution.distribute(
            prepared["article"],
            platforms
        )

        return {
            **prepared,
            "status":"COMPLETE",
            "published_count":result.get("published_count",0),
            "distribution":result
        }

    def process_queue(
        self,
        platform:Optional[str]=None,
        limit:int=10
    )->Dict[str,Any]:
        return self.distribution.process_queue(
            platform,
            limit
        )

    def status(self)->Dict[str,Any]:
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "components":{
                "article_engine":self.article_engine.status(),
                "seo_engine":self.seo_engine.status(),
                "media_manager":self.media_manager.status(),
                "formatter":self.formatter.status(),
                "router":self.router.status(),
                "guard":self.guard.status(),
                "queue":self.queue.status(),
                "tracker":self.tracker.status(),
                "history":self.history.status(),
                "distribution":self.distribution.status(),
                "orchestrator":self.orchestrator.status()
            }
        }

    def _fail(self,stage,error):
        return {
            "status":"FAILED",
            "stage":stage,
            "published":False,
            "error":str(error)
        }


factory_pipeline=FactoryPipeline()


def prepare_news(package,platform="website"):
    return factory_pipeline.prepare(
        package,
        platform
    )


def publish_news(package,platform="website",queue_first=False):
    return factory_pipeline.publish(
        package,
        platform,
        queue_first
    )


def publish_many(package,platforms=None):
    return factory_pipeline.publish_many(
        package,
        platforms
    )


def queue_news(package,platforms=None,priority="NORMAL"):
    return factory_pipeline.queue(
        package,
        platforms,
        priority
    )


def process_publication_queue(platform=None,limit=10):
    return factory_pipeline.process_queue(
        platform,
        limit
    )


if __name__=="__main__":
    print(factory_pipeline.status())
