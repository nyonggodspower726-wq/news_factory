import logging
from typing import Any,Dict,List,Optional

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
        orchestrator:Optional[PublicationOrchestrator]=None,
        formatter:Optional[ContentFormatter]=None,
        router:Optional[PlatformRouter]=None,
        guard:Optional[PublicationGuard]=None,
        queue:Optional[PublicationQueue]=None,
        tracker:Optional[PublicationTracker]=None,
        history:Optional[PublicationHistory]=None,
        distribution:Optional[DistributionManager]=None
    ):
        self.name="AI News Factory Pipeline"
        self.version="2.0.0"

        self.orchestrator=(
            orchestrator
            or PublicationOrchestrator()
        )

        self.formatter=(
            formatter
            or ContentFormatter()
        )

        self.router=(
            router
            or self.orchestrator.platform_router
        )

        self.guard=(
            guard
            or PublicationGuard()
        )

        self.queue=(
            queue
            or PublicationQueue()
        )

        self.tracker=(
            tracker
            or PublicationTracker()
        )

        self.history=(
            history
            or PublicationHistory()
        )

        self.distribution=(
            distribution
            or DistributionManager(
                router=self.router,
                queue=self.queue,
                tracker=self.tracker,
                history=self.history,
                guard=self.guard
            )
        )

    # =====================================================
    # PREPARE
    # =====================================================

    def prepare(
        self,
        package:Dict[str,Any],
        platform:str="website"
    )->Dict[str,Any]:

        if not isinstance(package,dict):
            return self._fail(
                "INPUT",
                "Pipeline package must be a dictionary."
            )

        try:
            prepared=self.orchestrator.prepare(
                package,
                platform
            )
        except Exception as exc:
            logger.exception(
                "Orchestrator preparation failed."
            )
            return self._fail(
                "ORCHESTRATOR",
                str(exc)
            )

        if not isinstance(prepared,dict):
            return self._fail(
                "ORCHESTRATOR",
                "Orchestrator returned invalid data."
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
            guard_result=self.guard.check(
                {
                    **package,
                    "article":article,
                    "publication_ready":True
                },
                platform
            )
        except Exception as exc:
            logger.exception(
                "Publication guard failed."
            )
            return self._fail(
                "GUARD",
                str(exc)
            )

        if not guard_result.get(
            "publication_allowed",
            False
        ):
            return {
                **prepared,
                "status":"BLOCKED",
                "publication_safe":False,
                "guard":guard_result,
                "published":False
            }

        try:
            formatted=self.formatter.format(
                article,
                platform
            )
        except Exception as exc:
            logger.exception(
                "Content formatting failed."
            )
            return self._fail(
                "FORMATTER",
                str(exc)
            )

        return {
            **prepared,
            "status":"READY",
            "publication_safe":True,
            "article":article,
            "formatted":formatted,
            "guard":guard_result
        }

    # =====================================================
    # PUBLISH ONE
    # =====================================================

    def publish(
        self,
        package:Dict[str,Any],
        platform:str="website",
        queue_first:bool=False
    )->Dict[str,Any]:

        prepared=self.prepare(
            package,
            platform
        )

        if prepared.get(
            "status"
        )!="READY":

            return {
                **prepared,
                "published":False
            }

        article=prepared.get(
            "article",
            {}
        )

        if queue_first:

            try:
                queued=self.queue.enqueue(
                    article,
                    platform
                )
            except Exception as exc:
                logger.exception(
                    "Publication queue failed."
                )
                return {
                    **prepared,
                    "status":"QUEUE_FAILED",
                    "published":False,
                    "error":str(exc)
                }

            return {
                **prepared,
                "status":"QUEUED",
                "published":False,
                "queue":queued
            }

        try:
            result=self.router.publish(
                article,
                platform
            )
        except Exception as exc:
            logger.exception(
                "Publication failed."
            )
            result={
                "status":"PUBLISH_FAILED",
                "published":False,
                "error":str(exc)
            }

        if not isinstance(
            result,
            dict
        ):
            result={
                "status":"PUBLISH_FAILED",
                "published":False,
                "response":result
            }

        published=bool(
            result.get(
                "published",
                False
            )
        )

        self._record(
            article,
            platform,
            result
        )

        return {
            **prepared,
            "status":
                "PUBLISHED"
                if published
                else result.get(
                    "status",
                    "PUBLISH_FAILED"
                ),
            "published":
                published,
            "publisher_result":
                result
        }

    # =====================================================
    # PUBLISH MANY
    # =====================================================

    def publish_many(
        self,
        package:Dict[str,Any],
        platforms:Optional[List[str]]=None,
        queue_first:bool=False
    )->Dict[str,Any]:

        if not isinstance(
            platforms,
            list
        ) or not platforms:

            platforms=[
                "website"
            ]

        if queue_first:

            prepared=self.prepare(
                package,
                platforms[0]
            )

            if prepared.get(
                "status"
            )!="READY":

                return {
                    **prepared,
                    "published_count":0
                }

            article=prepared.get(
                "article",
                {}
            )

            try:
                queue_result=self.distribution.queue(
                    article,
                    platforms
                )
            except Exception as exc:
                return {
                    **prepared,
                    "status":"QUEUE_FAILED",
                    "published_count":0,
                    "error":str(exc)
                }

            return {
                **prepared,
                "status":"QUEUED",
                "published_count":0,
                "queue_result":queue_result
            }

        prepared=self.prepare(
            package,
            platforms[0]
        )

        if prepared.get(
            "status"
        )!="READY":

            return {
                **prepared,
                "published_count":0
            }

        article=prepared.get(
            "article",
            {}
        )

        try:
            result=self.distribution.distribute(
                article,
                platforms,
                queue_first=False
            )
        except Exception as exc:
            logger.exception(
                "Multi-platform distribution failed."
            )
            return {
                **prepared,
                "status":"DISTRIBUTION_FAILED",
                "published_count":0,
                "error":str(exc)
            }

        return {
            **prepared,
            "status":"COMPLETE",
            "published_count":result.get(
                "published_count",
                0
            ),
            "distribution":result
        }

    # =====================================================
    # QUEUE
    # =====================================================

    def queue(
        self,
        package:Dict[str,Any],
        platforms:Optional[List[str]]=None,
        priority:str="NORMAL"
    )->Dict[str,Any]:

        if not isinstance(
            platforms,
            list
        ) or not platforms:

            platforms=[
                "website"
            ]

        prepared=self.prepare(
            package,
            platforms[0]
        )

        if prepared.get(
            "status"
        )!="READY":

            return {
                **prepared,
                "queued":False
            }

        article=prepared.get(
            "article",
            {}
        )

        try:
            result=self.distribution.queue(
                article,
                platforms,
                priority
            )
        except Exception as exc:
            logger.exception(
                "Queue operation failed."
            )
            return {
                **prepared,
                "status":"QUEUE_FAILED",
                "queued":False,
                "error":str(exc)
            }

        return {
            **prepared,
            "status":result.get(
                "status",
                "QUEUED"
            ),
            "queued":result.get(
                "queued_count",
                0
            )>0,
            "queue_result":result
        }

    # =====================================================
    # PROCESS QUEUE
    # =====================================================

    def process_queue(
        self,
        platform:Optional[str]=None,
        limit:int=10
    )->Dict[str,Any]:

        try:
            return self.distribution.process_queue(
                platform,
                limit
            )
        except Exception as exc:
            logger.exception(
                "Queue processing failed."
            )
            return {
                "status":"FAILED",
                "processed":0,
                "error":str(exc)
            }

    # =====================================================
    # RECORD
    # =====================================================

    def _record(
        self,
        article:Dict[str,Any],
        platform:str,
        result:Dict[str,Any]
    ):

        try:
            self.tracker.record(
                article,
                platform,
                result
            )
        except Exception:
            logger.exception(
                "Publication tracker failed."
            )

        try:
            self.history.record(
                article,
                platform,
                result
            )
        except Exception:
            logger.exception(
                "Publication history failed."
            )

    # =====================================================
    # STATUS
    # =====================================================

    def status(self)->Dict[str,Any]:

        components={}

        for name,component in {
            "orchestrator":self.orchestrator,
            "formatter":self.formatter,
            "router":self.router,
            "guard":self.guard,
            "queue":self.queue,
            "tracker":self.tracker,
            "history":self.history,
            "distribution":self.distribution
        }.items():

            try:
                if hasattr(
                    component,
                    "status"
                ):
                    components[name]=component.status()
                else:
                    components[name]={
                        "status":"READY"
                    }
            except Exception as exc:
                components[name]={
                    "status":"ERROR",
                    "error":str(exc)
                }

        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "components":components
        }

    def _fail(
        self,
        stage:str,
        error:str
    )->Dict[str,Any]:

        return {
            "status":"FAILED",
            "stage":stage,
            "publication_safe":False,
            "published":False,
            "error":str(error)
        }


factory_pipeline=FactoryPipeline()


def prepare_news(
    package,
    platform="website"
):
    return factory_pipeline.prepare(
        package,
        platform
    )


def publish_news(
    package,
    platform="website",
    queue_first=False
):
    return factory_pipeline.publish(
        package,
        platform,
        queue_first
    )


def publish_many(
    package,
    platforms=None,
    queue_first=False
):
    return factory_pipeline.publish_many(
        package,
        platforms,
        queue_first
    )


def queue_news(
    package,
    platforms=None,
    priority="NORMAL"
):
    return factory_pipeline.queue(
        package,
        platforms,
        priority
    )


def process_publication_queue(
    platform=None,
    limit=10
):
    return factory_pipeline.process_queue(
        platform,
        limit
    )


def factory_status():
    return factory_pipeline.status()


if __name__=="__main__":
    print(
        factory_pipeline.status()
    )
