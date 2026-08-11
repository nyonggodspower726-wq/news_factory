from typing import Any,Dict,Optional
from media.image_engine import ImageEngine
from media.image_generator import ImageGenerator

class MediaManager:
    def __init__(self,image_engine:Optional[ImageEngine]=None,image_generator:Optional[ImageGenerator]=None):
        self.image_engine=image_engine or ImageEngine()
        self.image_generator=image_generator or ImageGenerator()
        self.name="Media Manager"
        self.version="2.0.0"

    def prepare(self,story:Dict[str,Any],generate_image:bool=True,platform:str="website")->Dict[str,Any]:
        if not isinstance(story,dict):
            raise TypeError("Story must be a dictionary.")
        existing=self.image_engine.build_article_media(story)
        if existing.get("has_image"):
            return {
                "status":"MEDIA_READY",
                "article_media":existing,
                "has_image":True,
                "source_type":"EXISTING"
            }
        if generate_image:
            generated=self.image_generator.generate(
                story,
                platform=platform,
                mode="auto"
            )
            if generated.get("generated") and generated.get("image_url"):
                media={
                    "image_url":generated.get("image_url",""),
                    "has_image":True,
                    "alt":generated.get("alt_text",self.image_generator.create_alt_text(story)),
                    "credit":generated.get("credit","AI-generated editorial illustration"),
                    "source_url":generated.get("source_url",story.get("source_url","")),
                    "caption":generated.get("caption",""),
                    "source_type":"AI_GENERATED",
                    "local_path":generated.get("local_path","")
                }
                return {
                    "status":"MEDIA_READY",
                    "article_media":media,
                    "has_image":True,
                    "source_type":"AI_GENERATED"
                }
            return {
                "status":"NO_IMAGE",
                "article_media":{
                    "image_url":"",
                    "has_image":False,
                    "alt":self.image_generator.create_alt_text(story),
                    "credit":"",
                    "source_url":story.get("source_url",""),
                    "caption":""
                },
                "has_image":False,
                "source_type":"NONE",
                "generation":generated
            }
        return {
            "status":"NO_IMAGE",
            "article_media":existing,
            "has_image":False,
            "source_type":"NONE"
        }

    def attach(self,article:Dict[str,Any],story:Dict[str,Any],generate_image:bool=True,platform:str="website")->Dict[str,Any]:
        if not isinstance(article,dict):
            raise TypeError("Article must be a dictionary.")
        prepared=self.prepare(story,generate_image,platform)
        media=prepared.get("article_media",{})
        updated=dict(article)
        updated["image_url"]=media.get("image_url","")
        updated["image_alt"]=media.get("alt","")
        updated["image_credit"]=media.get("credit","")
        updated["image_source_url"]=media.get("source_url","")
        updated["image_caption"]=media.get("caption","")
        updated["image_source_type"]=media.get("source_type","")
        updated["image_local_path"]=media.get("local_path","")
        updated["has_image"]=media.get("has_image",False)
        return updated

    def prepare_social(self,article:Dict[str,Any])->Dict[str,Any]:
        image_url=self._clean(article.get("image_url",""))
        title=self._clean(article.get("title",article.get("headline","")))
        source=self._clean(article.get("image_credit",""))
        return self.image_engine.build_social_media(
            image_url=image_url,
            title=title,
            source=source
        )

    def validate_article_media(self,article:Dict[str,Any])->Dict[str,Any]:
        image_url=self._clean(article.get("image_url",""))
        if not image_url:
            return {
                "valid":True,
                "has_image":False,
                "message":"Article has no image."
            }
        validation=self.image_engine.validate(image_url)
        return {
            "valid":validation.get("valid",False),
            "has_image":validation.get("valid",False),
            "image_url":image_url,
            "content_type":validation.get("content_type",""),
            "error":validation.get("error","")
        }

    def generate_missing_image(self,story:Dict[str,Any],platform:str="website")->Dict[str,Any]:
        return self.prepare(
            story,
            generate_image=True,
            platform=platform
        )

    def status(self)->Dict[str,Any]:
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "image_engine":self.image_engine.status(),
            "image_generator":self.image_generator.status()
        }

    def _clean(self,value:Any)->str:
        return "" if value is None else str(value).strip()

def create_media_manager(
    image_engine:Optional[ImageEngine]=None,
    image_generator:Optional[ImageGenerator]=None
)->MediaManager:
    return MediaManager(
        image_engine=image_engine,
        image_generator=image_generator
            )
