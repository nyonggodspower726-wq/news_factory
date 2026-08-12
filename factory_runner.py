import os,logging
from typing import Any,Dict,Optional,List
from factory_pipeline import FactoryPipeline

logger=logging.getLogger("NewsFactory.Runner")

class FactoryRunner:
    def __init__(self,pipeline:Optional[FactoryPipeline]=None):
        self.name="AI News Factory Runner"
        self.version="1.0.0"
        self.pipeline=pipeline or FactoryPipeline()

    def run(self,package:Dict[str,Any],platform:str="website",publish:bool=False,queue_first:bool=False)->Dict[str,Any]:
        if not isinstance(package,dict):
            return {"status":"FAILED","stage":"INPUT","error":"Package must be a dictionary."}
        config=self.config_status()
        if publish and not config.get("configured"):
            return {"status":"BLOCKED","stage":"CONFIGURATION","error":"Required API configuration is incomplete.","configuration":config}
        try:
            if publish:
                result=self.pipeline.publish(package,platform,queue_first)
            else:
                result=self.pipeline.prepare(package,platform)
            return {"status":result.get("status","UNKNOWN"),"publish_mode":publish,"platform":platform,"configuration":config,"result":result}
        except Exception as exc:
            logger.exception("Factory execution failed.")
            return {"status":"FAILED","stage":"RUNNER","error":str(exc),"configuration":config}

    def run_many(self,package:Dict[str,Any],platforms:Optional[List[str]]=None,publish:bool=False)->Dict[str,Any]:
        if not isinstance(package,dict):
            return {"status":"FAILED","error":"Package must be a dictionary."}
        platforms=platforms or ["website"]
        try:
            if publish:
                result=self.pipeline.publish_many(package,platforms)
            else:
                result={p:self.pipeline.prepare(package,p) for p in platforms}
            return {"status":"COMPLETE","publish_mode":publish,"platforms":platforms,"configuration":self.config_status(),"result":result}
        except Exception as exc:
            logger.exception("Multi-platform execution failed.")
            return {"status":"FAILED","error":str(exc)}

    def config_status(self)->Dict[str,Any]:
        checks={
            "news_site_api":bool(os.getenv("NEWS_SITE_API_URL") and os.getenv("NEWS_SITE_API_KEY")),
            "wordpress_api":bool(os.getenv("WORDPRESS_API_URL") and ((os.getenv("WORDPRESS_API_KEY")) or (os.getenv("WORDPRESS_USERNAME") and os.getenv("WORDPRESS_PASSWORD")))),
            "image_api":bool(os.getenv("IMAGE_API_URL") and os.getenv("IMAGE_API_KEY")),
            "media_public_url":bool(os.getenv("MEDIA_PUBLIC_BASE_URL")),
            "reddit_api":bool(os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET")),
            "social_api":bool(os.getenv("SOCIAL_API_URL") or os.getenv("SOCIAL_API_KEY")),
            "github_api":bool(os.getenv("GITHUB_TOKEN"))
        }
        required=["news_site_api","image_api"]
        configured=all(checks.get(x,False) for x in required)
        return {"configured":configured,"checks":checks,"required":required}

    def status(self)->Dict[str,Any]:
        try:pipeline_status=self.pipeline.status()
        except Exception as exc:pipeline_status={"status":"ERROR","error":str(exc)}
        return {"engine":self.name,"version":self.version,"status":"READY","configuration":self.config_status(),"pipeline":pipeline_status}

factory_runner=FactoryRunner()

def run_factory(package,platform="website",publish=False,queue_first=False):
    return factory_runner.run(package,platform,publish,queue_first)

def run_factory_many(package,platforms=None,publish=False):
    return factory_runner.run_many(package,platforms,publish)

def factory_config():
    return factory_runner.config_status()

def factory_status():
    return factory_runner.status()

if __name__=="__main__":
    import json
    print(json.dumps(factory_status(),indent=2,default=str))
