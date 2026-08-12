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
        self.version="1.0.0"

        self.website_publisher=website_publisher
        self.wordpress_publisher=wordpress_publisher
        self.social_publisher=social_publisher
        self.github_publisher=github_publisher

        self.platforms={
            "website",
            "wordpress",
            "social",
            "github"
        }


    def prepare(
        self,
        article:Dict[str,Any],
        platform:str="website"
    )->Dict[str,Any]:

        if not isinstance(article,dict):

            return {
                "status":"FAILED",
                "platform":platform,
                "error":"Article must be a dictionary."
            }

        platform=self._normalize_platform(
            platform
        )

        if platform not in self.platforms:

            return {
                "status":"UNSUPPORTED_PLATFORM",
                "platform":platform,
                "supported_platforms":sorted(
                    self.platforms
                )
            }

        prepared=dict(article)

        prepared["platform"]=platform

        prepared["platform_style"]=self._platform_style(
            platform
        )

        prepared["platform_title"]=self._platform_title(
            article,
            platform
        )

        prepared["platform_excerpt"]=self._platform_excerpt(
            article,
            platform
        )

        prepared["platform_tags"]=self._platform_tags(
            article,
            platform
        )

        prepared["platform_payload"]=self._build_payload(
            prepared,
            platform
        )

        return {
            "status":"READY",
            "platform":platform,
            "article":prepared,
            "payload":prepared["platform_payload"]
        }


    def publish(
        self,
        article:Dict[str,Any],
        platform:str="website"
    )->Dict[str,Any]:

        prepared=self.prepare(
            article,
            platform
        )

        if prepared.get(
            "status"
        )!="READY":

            return {
                **prepared,
                "published":False
            }

        platform=prepared["platform"]
        payload=prepared["payload"]

        publisher=self._publisher(
            platform
        )

        if publisher is None:

            return {
                **prepared,
                "status":"PLATFORM_NOT_CONNECTED",
                "published":False,
                "message":(
                    f"No publisher connected for {platform}."
                )
            }

        try:

            if hasattr(
                publisher,
                "publish"
            ):

                result=publisher.publish(
                    payload
                )

            else:

                return {
                    **prepared,
                    "status":"INVALID_PUBLISHER",
                    "published":False,
                    "message":(
                        f"Publisher for {platform} "
                        "does not expose publish()."
                    )
                }

            if not isinstance(
                result,
                dict
            ):

                result={
                    "status":"UNKNOWN",
                    "published":False,
                    "response":result
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
                    else "PUBLISH_FAILED"
                ),
                "published":published,
                "publisher_result":result
            }

        except Exception as exc:

            logger.exception(
                "Platform publishing failed."
            )

            return {
                **prepared,
                "status":"PUBLISH_FAILED",
                "published":False,
                "error":str(exc)
            }


    def _publisher(
        self,
        platform:str
    ):

        if platform=="website":
            return self.website_publisher

        if platform=="wordpress":
            return self.wordpress_publisher

        if platform=="social":
            return self.social_publisher

        if platform=="github":
            return self.github_publisher

        return None


    def _normalize_platform(
        self,
        platform:Any
    )->str:

        value=str(
            platform or "website"
        ).strip().lower()

        aliases={
            "site":"website",
            "web":"website",
            "blog":"website",
            "wp":"wordpress",
            "word_press":"wordpress",
            "facebook":"social",
            "reddit":"social",
            "x":"social",
            "twitter":"social"
        }

        return aliases.get(
            value,
            value
        )


    def _platform_style(
        self,
        platform:str
    )->str:

        styles={

            "website":
                "SEO_NEWS_ARTICLE",

            "wordpress":
                "LONG_FORM_NEWS_BLOG",

            "social":
                "SOCIAL_NEWS_POST",

            "github":
                "TECHNICAL_NEWS_DOCUMENT"
        }

        return styles.get(
            platform,
            "GENERAL_NEWS"
        )


    def _platform_title(
        self,
        article:Dict[str,Any],
        platform:str
    )->str:

        seo=article.get(
            "seo",
            {}
        )

        if not isinstance(
            seo,
            dict
        ):

            seo={}

        platform_titles=seo.get(
            "platform_titles",
            {}
        )

        if isinstance(
            platform_titles,
            dict
        ):

            title=platform_titles.get(
                platform,
                ""
            )

            if title:
                return str(
                    title
                ).strip()

        existing=article.get(
            "platform_title",
            ""
        )

        if existing:
            return str(
                existing
            ).strip()

        seo_title=article.get(
            "seo_title",
            ""
        )

        if seo_title:
            return str(
                seo_title
            ).strip()

        return str(
            article.get(
                "title",
                article.get(
                    "headline",
                    ""
                )
            )
        ).strip()


    def _platform_excerpt(
        self,
        article:Dict[str,Any],
        platform:str
    )->str:

        excerpt=article.get(
            "excerpt",
            ""
        )

        if platform=="social":

            return self._shorten(
                excerpt,
                280
            )

        if platform=="wordpress":

            return self._shorten(
                excerpt,
                320
            )

        return self._shorten(
            excerpt,
            300
        )


    def _platform_tags(
        self,
        article:Dict[str,Any],
        platform:str
    )->list:

        tags=article.get(
            "tags",
            []
        )

        if not isinstance(
            tags,
            list
        ):

            tags=[]

        cleaned=[]

        for tag in tags:

            value=str(
                tag
            ).strip()

            if value and value not in cleaned:

                cleaned.append(
                    value
                )

        if platform=="social":

            return cleaned[:10]

        return cleaned[:30]


    def _build_payload(
        self,
        article:Dict[str,Any],
        platform:str
    )->Dict[str,Any]:

        seo=article.get(
            "seo",
            {}
        )

        if not isinstance(
            seo,
            dict
        ):

            seo={}

        return {

            "title":
                self._platform_title(
                    article,
                    platform
                ),

            "content":
                article.get(
                    "content",
                    ""
                ),

            "excerpt":
                self._platform_excerpt(
                    article,
                    platform
                ),

            "slug":
                article.get(
                    "slug",
                    ""
                ),

            "category":
                article.get(
                    "category",
                    "news"
                ),

            "tags":
                self._platform_tags(
                    article,
                    platform
                ),

            "keywords":
                article.get(
                    "keywords",
                    seo.get(
                        "keywords",
                        []
                    )
                ),

            "meta_description":
                article.get(
                    "meta_description",
                    seo.get(
                        "meta_description",
                        ""
                    )
                ),

            "image_url":
                article.get(
                    "image_url",
                    ""
                ),

            "image_alt":
                article.get(
                    "image_alt",
                    ""
                ),

            "image_caption":
                article.get(
                    "image_caption",
                    ""
                ),

            "image_credit":
                article.get(
                    "image_credit",
                    ""
                ),

            "source_url":
                article.get(
                    "source_url",
                    ""
                ),

            "platform":
                platform,

            "platform_style":
                self._platform_style(
                    platform
                ),

            "seo":
                seo
        }


    def _shorten(
        self,
        text:Any,
        limit:int
    )->str:

        value=str(
            text or ""
        ).strip()

        if len(value)<=limit:

            return value

        return value[:limit-3].rstrip()+ "..."


    def status(
        self
    )->Dict[str,Any]:

        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "platforms":sorted(
                self.platforms
            ),
            "connected":{
                "website":self.website_publisher is not None,
                "wordpress":self.wordpress_publisher is not None,
                "social":self.social_publisher is not None,
                "github":self.github_publisher is not None
            }
        }


platform_router=PlatformRouter()


def prepare_platform(
    article,
    platform="website"
):

    return platform_router.prepare(
        article,
        platform
    )


def publish_platform(
    article,
    platform="website"
):

    return platform_router.publish(
        article,
        platform
    )


if __name__=="__main__":

    print(
        platform_router.status()
    )
