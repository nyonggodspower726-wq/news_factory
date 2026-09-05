import os
import re
import base64
import logging
import requests
from typing import Any, Dict, Optional
from pathlib import Path

logger=logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self,api_url: Optional[str]=None,api_key: Optional[str]=None,model: Optional[str]=None,output_dir: str="media/generated"):
        self.name="AI News Image Generator"
        self.version="1.3.0"
        self.api_url=api_url or os.getenv("IMAGE_API_URL","").strip()
        self.api_key=api_key or os.getenv("CLOUDFLARE_API_TOKEN","").strip() or os.getenv("IMAGE_API_KEY","").strip()
        self.model=model or os.getenv("IMAGE_MODEL","").strip()
        self.output_dir=Path(output_dir)
        self.timeout=120
        self.styles={
            "breaking_news":"professional editorial news photography, realistic documentary scene, natural lighting, cinematic composition",
            "politics":"professional editorial news photography, realistic political environment, authentic people and setting, documentary composition",
            "business":"professional editorial business photography, realistic corporate or economic environment, sophisticated composition",
            "technology":"professional editorial technology photography, realistic modern environment, cinematic lighting, sophisticated composition",
            "sports":"professional editorial sports photography, realistic action, authentic stadium or sporting environment",
            "crime":"professional editorial documentary photography, respectful non-graphic scene, realistic environment",
            "health":"professional editorial health photography, realistic clinical or medical environment, respectful non-graphic scene",
            "general":"professional editorial news photography, realistic documentary style, natural lighting, cinematic composition"
        }

    def generate(self,article: Dict[str,Any],platform: str="website",mode: str="auto",output_format: str="png",width: int=1280,height: int=720)->Dict[str,Any]:
        if not isinstance(article,dict):
            raise TypeError("Article must be a dictionary.")
        prompt=self.build_prompt(article)
        story_type=self.story_type(article)
        if mode=="licensed":
            return {"status":"LICENSE_REQUIRED","generated":False,"source_type":"LICENSED","prompt":prompt}
        if not self.api_url or not self.api_key:
            return {"status":"NOT_CONFIGURED","generated":False,"source_type":"AI_GENERATED","prompt":prompt,"message":"IMAGE_API_URL and a valid API token are not configured."}
        try:
            payload=self._payload(prompt,width,height,output_format)
            response=requests.post(self.api_url,headers=self._headers(),json=payload,timeout=self.timeout)
            response.raise_for_status()
            content_type=response.headers.get("Content-Type","").lower()
            if content_type.startswith("image/") or self._looks_like_image(response.content):
                image=response.content
            else:
                try:
                    data=response.json()
                except ValueError:
                    return {"status":"FAILED","generated":False,"source_type":"AI_GENERATED","prompt":prompt,"error":"Image API returned neither a usable image nor valid JSON."}
                image=self._extract_image(data)
            if not image:
                return {"status":"FAILED","generated":False,"source_type":"AI_GENERATED","prompt":prompt,"error":"Image API returned no usable image."}
            path=self._save(image,article,output_format)
            return {
                "status":"IMAGE_READY","generated":True,"source_type":"AI_GENERATED",
                "image_url":self._public_url(path),"local_path":str(path),"prompt":prompt,
                "story_type":story_type,"platform":platform,"width":width,"height":height,
                "alt_text":self.create_alt_text(article),"caption":self.create_caption(article),
                "credit":"AI-generated editorial illustration"
            }
        except requests.RequestException as exc:
            logger.exception("Image generation request failed.")
            return {"status":"FAILED","generated":False,"source_type":"AI_GENERATED","prompt":prompt,"error":str(exc)}
        except Exception as exc:
            logger.exception("Image generation failed.")
            return {"status":"FAILED","generated":False,"source_type":"AI_GENERATED","prompt":prompt,"error":str(exc)}

    def build_prompt(self,article: Dict[str,Any])->str:
        title=self._text(article.get("title",article.get("headline","")))
        summary=self._text(article.get("excerpt",article.get("summary",article.get("lead",""))))
        topic=self._text(article.get("topic",article.get("category","general")))
        location=self._text(article.get("location",""))
        event=self._text(article.get("event_type",article.get("story_type","general")))
        style=self.styles.get(self.story_type(article),self.styles["general"])
        context_part=f"Story context for visual interpretation only: {summary}. " if summary else ""
        location_part=f"Location: {location}. " if location else ""
        prompt=(
            f"{style}. "
            "Create an original, realistic editorial image that visually represents the verified news story. "
            f"Visual subject: {title}. "
            f"Topic: {topic}. "
            f"Event type: {event}. "
            f"{context_part}{location_part}"
            "Use visual storytelling only. The headline and story details are provided only to understand the subject; "
            "they must NOT appear as text in the image. "
            "IMPORTANT: absolutely no readable text anywhere in the image. "
            "Do not generate words, letters, numbers, headlines, captions, subtitles, newspaper pages, magazine pages, "
            "documents, articles, website interfaces, computer screens containing text, signs, posters, labels, logos, "
            "watermarks, typography, charts with labels, or fake written material. "
            "If a screen, sign, paper, book, newspaper, document, or display appears naturally in the scene, keep it blank, "
            "abstract, blurred, or unreadable. "
            "Do not fabricate evidence, documents, logos, or visual proof. "
            "The final image must look like a clean premium newsroom photograph or editorial illustration with no typography."
        )
        return self._clean(prompt)

    def story_type(self,article: Dict[str,Any])->str:
        text=self._text(" ".join(str(article.get(k,"")) for k in ("title","headline","topic","category","content","excerpt"))).lower()
        mapping={
            "politics":["president","minister","government","election","parliament","senate","political","policy"],
            "business":["business","company","market","stock","economy","economic","investment","bank"],
            "technology":["technology","software","ai","artificial intelligence","cyber","robot","chip","app"],
            "sports":["football","soccer","basketball","tennis","sports","league","match","coach","player"],
            "crime":["police","arrest","murder","crime","court","suspect","investigation"],
            "health":["doctor","hospital","disease","health","medical","virus","medicine"],
            "breaking_news":["breaking","explosion","earthquake","flood","fire","crash","attack"]
        }
        scores={category:sum(1 for word in words if word in text) for category,words in mapping.items()}
        if not scores:return "general"
        best_score=max(scores.values())
        if best_score==0:return "general"
        return max(scores,key=scores.get)

    def create_alt_text(self,article: Dict[str,Any])->str:
        title=self._text(article.get("title",article.get("headline","")))
        return (title or "News image")[:125]

    def create_caption(self,article: Dict[str,Any])->str:
        title=self._text(article.get("title",article.get("headline","")))
        return f"Editorial image illustrating: {title}" if title else "Editorial news image."

    def generate_prompt_only(self,article: Dict[str,Any])->Dict[str,Any]:
        return {"status":"PROMPT_READY","prompt":self.build_prompt(article),"story_type":self.story_type(article),"alt_text":self.create_alt_text(article),"caption":self.create_caption(article)}

    def _payload(self,prompt: str,width: int,height: int,output_format: str)->Dict[str,Any]:
        payload={"prompt":prompt,"width":width,"height":height,"format":output_format}
        if self.model:payload["model"]=self.model
        return payload

    def _headers(self)->Dict[str,str]:
        return {"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json","Accept":"image/*, application/json","User-Agent":"AI-News-Factory/1.3"}

    def _looks_like_image(self,content: bytes)->bool:
        if not content:return False
        if content[:3]==b"\xff\xd8\xff":return True
        if content[:8]==b"\x89PNG\r\n\x1a\n":return True
        if content[:6] in (b"GIF87a",b"GIF89a"):return True
        return len(content)>=12 and content[:4]==b"RIFF" and content[8:12]==b"WEBP"

    def _extract_image(self,data: Any)->Optional[str]:
        if not isinstance(data,dict):return None
        for key in ("image_url","url","image","b64_json","data"):
            value=data.get(key)
            if key=="data" and isinstance(value,list) and value:
                item=value[0]
                if isinstance(item,dict):value=item.get("url",item.get("b64_json"))
            if value and isinstance(value,str):return value
        return None

    def _save(self,image: Any,article: Dict[str,Any],output_format: str)->Path:
        self.output_dir.mkdir(parents=True,exist_ok=True)
        title=self._text(article.get("title",article.get("headline","news"))).lower()
        slug=re.sub(r"[^a-z0-9]+","-",title).strip("-")[:70] or "news"
        ext=self._detect_extension(image,output_format)
        path=self.output_dir/f"{slug}_{abs(hash(title))%100000}.{ext}"
        if isinstance(image,(bytes,bytearray)):
            path.write_bytes(bytes(image))
        elif isinstance(image,str) and image.startswith(("http://","https://")):
            response=requests.get(image,timeout=self.timeout,headers={"User-Agent":"AI-News-Factory/1.3"})
            response.raise_for_status()
            path.write_bytes(response.content)
        elif isinstance(image,str):
            if image.startswith("data:image"):image=image.split(",",1)[1]
            path.write_bytes(base64.b64decode(image))
        else:
            raise ValueError("Unsupported image response.")
        return path

    def _detect_extension(self,image: Any,requested_format: str)->str:
        if isinstance(image,(bytes,bytearray)):
            data=bytes(image)
            if data[:3]==b"\xff\xd8\xff":return "jpg"
            if data[:8]==b"\x89PNG\r\n\x1a\n":return "png"
            if data[:6] in (b"GIF87a",b"GIF89a"):return "gif"
            if len(data)>=12 and data[:4]==b"RIFF" and data[8:12]==b"WEBP":return "webp"
        return "jpg" if (requested_format or "png").lower() in {"jpg","jpeg"} else "png"

    def _public_url(self,path: Path)->str:
        base=os.getenv("MEDIA_PUBLIC_BASE_URL","").rstrip("/")
        return f"{base}/{path.name}" if base else str(path)

    def validate_result(self,result: Dict[str,Any])->bool:
        return isinstance(result,dict) and result.get("status")=="IMAGE_READY" and bool(result.get("image_url"))

    def _text(self,value: Any)->str:
        if value is None:return ""
        if isinstance(value,dict):return " ".join(str(v) for v in value.values() if v)
        if isinstance(value,list):return " ".join(str(v) for v in value if v)
        return str(value).strip()

    def _clean(self,text: str)->str:
        return re.sub(r"\s+"," ",str(text or "")).strip()

    def status(self)->Dict[str,Any]:
        token=os.getenv("CLOUDFLARE_API_TOKEN","").strip()
        key=os.getenv("IMAGE_API_KEY","").strip()
        source="CLOUDFLARE_API_TOKEN" if token else ("IMAGE_API_KEY" if key else "NONE")
        return {"engine":self.name,"version":self.version,"status":"READY" if self.api_url and self.api_key else "NOT_CONFIGURED","configured":bool(self.api_url and self.api_key),"credential_source":source}

image_generator=ImageGenerator()

def generate_news_image(article,platform="website",mode="auto",width=1280,height=720):
    return image_generator.generate(article,platform,mode,"png",width,height)

def build_image_prompt(article):
    return image_generator.generate_prompt_only(article)

if __name__=="__main__":
    test={"title":"Officials announce a new development","topic":"breaking news","excerpt":"Officials announced a new development today.","location":"Lagos"}
    print(build_image_prompt(test))
        
