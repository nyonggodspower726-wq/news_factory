import logging
from typing import Any,Dict,Optional

from article_engine import ArticleEngine
from seo_engine import SEOEngine
from media.media_manager import MediaManager
from Publishing.website_publisher import WebsitePublisher

logger=logging.getLogger("NewsFactory.PublicationOrchestrator")


class PublicationOrchestrator:

    def __init__(
        self,
        article_engine:Optional[ArticleEngine]=None,
        seo_engine:Optional[SEOEngine]=None,
        media_manager:Optional[MediaManager]=None,
        website_publisher:Optional[WebsitePublisher]=None
    ):

        self.name="Publication Orchestrator"
        self.version="1.0.0"

        self.article_engine=(
            article_engine
            or ArticleEngine()
        )

        self.seo_engine=(
            seo_engine
            or SEOEngine()
        )

        self.media_manager=(
            media_manager
            or MediaManager()
        )

        self.website_publisher=(
            website_publisher
            or WebsitePublisher()
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

            article_result=self.article_engine.create(
                package
            )

        except Exception as exc:

            logger.exception(
                "Article engine failed."
            )

            return {
                "status":"FAILED",
                "stage":"ARTICLE",
                "publication_safe":False,
                "error":str(exc)
            }


        if not isinstance(
            article_result,
            dict
        ):

            return {
                "status":"FAILED",
                "stage":"ARTICLE",
                "publication_safe":False,
                "error":"Article engine returned invalid data."
            }


        if article_result.get(
            "publication_safe"
        ) is False:

            return {
                "status":"BLOCKED",
                "stage":"EDITORIAL_GATE",
                "publication_safe":False,
                "reason":"Article failed the publication safety gate.",
                "article":article_result
            }


        try:

            seo_result=self.seo_engine.optimize(
                article_result,
                platform=platform
            )

        except Exception as exc:

            logger.exception(
                "SEO engine failed."
            )

            return {
                "status":"FAILED",
                "stage":"SEO",
                "publication_safe":False,
                "error":str(exc),
                "article":article_result
            }


        if not isinstance(
            seo_result,
            dict
        ):

            seo_result={}


        article=dict(
            article_result
        )


        article["seo"]=seo_result

        article["seo_title"]=seo_result.get(
            "seo_title",
            ""
        )

        article["meta_description"]=seo_result.get(
            "meta_description",
            ""
        )

        article["slug"]=seo_result.get(
            "slug",
            ""
        )

        article["keywords"]=seo_result.get(
            "keywords",
            []
        )

        article["tags"]=seo_result.get(
            "tags",
            []
        )

        article["title"]=(
            article.get("title")
            or seo_result.get("title","")
        )

        article["excerpt"]=(
            article.get("excerpt")
            or seo_result.get("excerpt","")
        )


        story=package.get(
            "story",
            {}
        )

        if not isinstance(
            story,
            dict
        ):

            story={}


        media_story=dict(
            story
        )

        media_story["title"]=article.get(
            "title",
            ""
        )

        media_story["topic"]=article.get(
            "topic",
            ""
        )

        media_story["source_url"]=article.get(
            "source_url",
            ""
        )

        media_story["excerpt"]=article.get(
            "excerpt",
            ""
        )


        try:

            article=self.media_manager.attach(
                article,
                media_story
            )

        except Exception as exc:

            logger.exception(
                "Media manager failed."
            )

            return {
                "status":"FAILED",
                "stage":"MEDIA",
                "publication_safe":False,
                "error":str(exc),
                "article":article,
                "seo":seo_result
            }


        try:

            validation=self.media_manager.validate_article_media(
                article
            )

        except Exception as exc:

            logger.exception(
                "Media validation failed."
            )

            validation={
                "valid":False,
                "has_image":False,
                "error":str(exc)
            }


        social_media=self.media_manager.prepare_social(
            article
        )


        publication_safe=bool(
            article.get(
                "publication_safe",
                True
            )
        )


        if not validation.get(
            "valid",
            False
        ) and validation.get(
            "has_image",
            False
        ):

            publication_safe=False


        return {

            "status":(
                "READY_FOR_PUBLICATION"
                if publication_safe
                else "REVIEW_REQUIRED"
            ),

            "publication_safe":
                publication_safe,

            "platform":
                platform,

            "article":
                article,

            "seo":
                seo_result,

            "media":
                social_media,

            "media_validation":
                validation
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


        if platform.lower()=="website":

            try:

                result=self.website_publisher.publish(
                    article
                )

            except Exception as exc:

                logger.exception(
                    "Website publisher failed."
                )

                return {
                    **prepared,
                    "published":False,
                    "status":"PUBLISH_FAILED",
                    "publisher_result":{
                        "status":"FAILED",
                        "published":False,
                        "error":str(exc)
                    }
                }


        else:

            return {
                **prepared,
                "published":False,
                "status":"PLATFORM_NOT_CONNECTED",
                "platform":platform,
                "message":(
                    f"No publisher adapter is connected for {platform}."
                )
            }


        published=bool(
            result.get(
                "published",
                False
            )
        )


        return {

            **prepared,

            "published":
                published,

            "publisher_result":
                result,

            "status":
                "PUBLISHED"
                if published
                else "PUBLISH_FAILED"
        }


    def publish_approved(
        self,
        package:Dict[str,Any],
        platform:str="website"
    )->Dict[str,Any]:

        if not isinstance(
            package,
            dict
        ):

            return {
                "status":"BLOCKED",
                "published":False,
                "reason":"Invalid pipeline package."
            }


        editorial=package.get(
            "editorial",
            {}
        )


        if isinstance(
            editorial,
            dict
        ):

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


    def status(
        self
    )->Dict[str,Any]:

        return {

            "engine":
                self.name,

            "version":
                self.version,

            "status":
                "READY",

            "article_engine":
                getattr(
                    self.article_engine,
                    "name",
                    "ArticleEngine"
                ),

            "seo_engine":
                getattr(
                    self.seo_engine,
                    "name",
                    "SEOEngine"
                ),

            "media_manager":
                getattr(
                    self.media_manager,
                    "name",
                    "MediaManager"
                ),

            "website_publisher":
                getattr(
                    self.website_publisher,
                    "name",
                    "WebsitePublisher"
                )
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
