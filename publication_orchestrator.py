import logging
from typing import Any,Dict,Optional

from article_engine import ArticleEngine
from seo_engine import SEOEngine
from media.media_manager import MediaManager
from Publishing.website_publisher import WebsitePublisher
from Publishing.platform_router import PlatformRouter

logger=logging.getLogger("NewsFactory.PublicationOrchestrator")


class PublicationOrchestrator:
    def __init__(
        self,
        article_engine:Optional[ArticleEngine]=None,
        seo_engine:Optional[SEOEngine]=None,
        media_manager:Optional[MediaManager]=None,
        website_publisher:Optional[WebsitePublisher]=None,
        platform_router:Optional[PlatformRouter]=None
    ):
        self.name="Publication Orchestrator"
        self.version="2.0.0"

        self.article_engine=(
            article_engine or ArticleEngine()
        )

        self.seo_engine=(
            seo_engine or SEOEngine()
        )

        self.media_manager=(
            media_manager or MediaManager()
        )

        self.website_publisher=(
            website_publisher or WebsitePublisher()
        )

        self.platform_router=(
            platform_router
            or PlatformRouter(
                website_publisher=self.website_publisher
            )
        )

    def prepare(
        self,
        package:Dict[str,Any],
        platform:str="website"
    )->Dict[str,Any]:

        if not isinstance(package,dict):
            return {
                "status":"FAILED",
                "stage":"INPUT",
                "publication_safe":False,
                "error":"Pipeline package must be a dictionary."
            }

        try:
            article=self.article_engine.create(package)
        except Exception as exc:
            logger.exception("Article generation failed.")
            return {
                "status":"FAILED",
                "stage":"ARTICLE",
                "publication_safe":False,
                "error":str(exc)
            }

        if not isinstance(article,dict):
            return {
                "status":"FAILED",
                "stage":"ARTICLE",
                "publication_safe":False,
                "error":"Article engine returned invalid data."
            }

        if article.get("publication_safe") is False:
            return {
                "status":"BLOCKED",
                "stage":"EDITORIAL_GATE",
                "publication_safe":False,
                "reason":"Article failed the publication safety gate.",
                "article":article
            }

        try:
            seo=self.seo_engine.optimize(
                article,
                platform=platform
            )
        except Exception as exc:
            logger.exception("SEO generation failed.")
            return {
                "status":"FAILED",
                "stage":"SEO",
                "publication_safe":False,
                "error":str(exc),
                "article":article
            }

        if not isinstance(seo,dict):
            seo={}

        article=dict(article)
        article["seo"]=seo
        article["seo_title"]=seo.get(
            "seo_title",
            article.get("title","")
        )
        article["meta_description"]=seo.get(
            "meta_description",
            ""
        )
        article["slug"]=seo.get(
            "slug",
            article.get("slug","")
        )
        article["keywords"]=seo.get(
            "keywords",
            []
        )
        article["tags"]=seo.get(
            "tags",
            article.get("tags",[])
        )

        story=package.get("story",{})
        if not isinstance(story,dict):
            story={}

        media_story=dict(story)
        media_story.update({
            "title":article.get("title",""),
            "headline":article.get("headline",""),
            "topic":article.get("topic",""),
            "excerpt":article.get("excerpt",""),
            "summary":article.get("excerpt",""),
            "source_url":article.get("source_url",""),
            "image_url":article.get("image_url","")
        })

        try:
            article=self.media_manager.attach(
                article,
                media_story,
                generate_image=True,
                platform=platform
            )
        except TypeError:
            article=self.media_manager.attach(
                article,
                media_story
            )
        except Exception as exc:
            logger.exception("Media preparation failed.")
            return {
                "status":"FAILED",
                "stage":"MEDIA",
                "publication_safe":False,
                "error":str(exc),
                "article":article,
                "seo":seo
            }

        try:
            media_validation=(
                self.media_manager.validate_article_media(
                    article
                )
            )
        except Exception as exc:
            media_validation={
                "valid":False,
                "has_image":False,
                "error":str(exc)
            }

        router_package=self.platform_router.prepare(
            article,
            platform
        )

        if router_package.get("status")!="READY":
            return {
                "status":"FAILED",
                "stage":"PLATFORM",
                "publication_safe":False,
                "article":article,
                "seo":seo,
                "media_validation":media_validation,
                "platform_result":router_package
            }

        final_article=router_package.get(
            "article",
            article
        )

        final_payload=router_package.get(
            "payload",
            {}
        )

        return {
            "status":"READY_FOR_PUBLICATION",
            "publication_safe":True,
            "platform":platform,
            "article":final_article,
            "seo":seo,
            "media":self.media_manager.prepare_social(
                final_article
            ),
            "media_validation":media_validation,
            "platform_result":router_package,
            "publisher_payload":final_payload
        }

    def publish(
        self,
        package:Dict[str,Any],
        platform:str="website"
    )->Dict[str,Any]:

        prepared=self.prepare(
            package,
            platform
        )

        if prepared.get(
            "status"
        )!="READY_FOR_PUBLICATION":
            return {
                **prepared,
                "published":False
            }

        article=prepared.get(
            "article",
            {}
        )

        try:
            result=self.platform_router.publish(
                article,
                platform
            )
        except Exception as exc:
            logger.exception(
                "Platform router publishing failed."
            )
            return {
                **prepared,
                "status":"PUBLISH_FAILED",
                "published":False,
                "publisher_result":{
                    "status":"FAILED",
                    "published":False,
                    "error":str(exc)
                }
            }

        published=bool(
            result.get(
                "published",
                False
            )
        )

        return {
            **prepared,
            "status":(
                "PUBLISHED"
                if published
                else result.get(
                    "status",
                    "PUBLISH_FAILED"
                )
            ),
            "published":published,
            "publisher_result":result
        }

    def publish_approved(
        self,
        package:Dict[str,Any],
        platform:str="website"
    )->Dict[str,Any]:

        if not isinstance(package,dict):
            return {
                "status":"BLOCKED",
                "published":False,
                "reason":"Invalid pipeline package."
            }

        editorial=package.get(
            "editorial",
            {}
        )

        if isinstance(editorial,dict):
            decision=str(
                editorial.get(
                    "decision",
                    ""
                )
            ).strip().upper()

            if decision and decision!="APPROVED":
                return {
                    "status":"BLOCKED",
                    "published":False,
                    "reason":(
                        f"Editorial decision is {decision}."
                    )
                }

        if package.get(
            "publication_ready"
        ) is False:
            return {
                "status":"BLOCKED",
                "published":False,
                "reason":(
                    "Pipeline marked this package "
                    "as not publication-ready."
                )
            }

        return self.publish(
            package,
            platform
        )

    def status(self)->Dict[str,Any]:
        try:
            media_status=self.media_manager.status()
        except Exception:
            media_status={"status":"UNKNOWN"}

        try:
            router_status=self.platform_router.status()
        except Exception:
            router_status={"status":"UNKNOWN"}

        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "article_engine":getattr(
                self.article_engine,
                "name",
                "Article Engine"
            ),
            "seo_engine":getattr(
                self.seo_engine,
                "name",
                "SEO Engine"
            ),
            "media_manager":getattr(
                self.media_manager,
                "name",
                "Media Manager"
            ),
            "website_publisher":getattr(
                self.website_publisher,
                "name",
                "Website Publisher"
            ),
            "media":media_status,
            "platform_router":router_status
        }


publication_orchestrator=PublicationOrchestrator()


def prepare_publication(
    package,
    platform="website"
):
    return publication_orchestrator.prepare(
        package,
        platform
    )


def publish_publication(
    package,
    platform="website"
):
    return publication_orchestrator.publish(
        package,
        platform
    )


def publish_approved(
    package,
    platform="website"
):
    return publication_orchestrator.publish_approved(
        package,
        platform
    )


if __name__=="__main__":
    print(
        publication_orchestrator.status()
        )
