import os,re,base64,logging,requests
from pathlib import Path

logger=logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self,api_url=None,api_key=None,model=None,output_dir="media/generated"):
        self.name="AI News Image Generator"
        self.version="1.3.0"
        self.api_url=api_url or os.getenv("IMAGE_API_URL","").strip()
        self.api_key=api_key or os.getenv("CLOUDFLARE_API_TOKEN","").strip() or os.getenv("IMAGE_API_KEY","").strip()
        self.model=model or os.getenv("IMAGE_MODEL","").strip()
        self.output_dir=Path(output_dir)
        self.timeout=120

    def generate(self,article,platform="website",mode="auto",output_format="png",width=1280,height=720):
        if not isinstance(article,dict):
            raise TypeError("Article must be a dictionary.")
        prompt=self.build_prompt(article)
        story_type=self.story_type(article)
        if mode=="licensed":
            return {"status":"LICENSE_REQUIRED","generated":False,"prompt":prompt}
        if not self.api_url or not self.api_key:
            return {"status":"NOT_CONFIGURED","generated":False,"prompt":prompt}
        try:
            r=requests.post(
                self.api_url,
                headers=self._headers(),
                json={"prompt":prompt,"width":width,"height":height},
                timeout=self.timeout
            )
            r.raise_for_status()
            image=self._extract(r)
            if not image:
                return {
                    "status":"FAILED",
                    "generated":False,
                    "prompt":prompt,
                    "error":"Empty image response."
                }
            path=self._save(image,article,output_format)
            return {
                "status":"IMAGE_READY",
                "generated":True,
                "image_url":self._public_url(path),
                "local_path":str(path),
                "prompt":prompt,
                "story_type":story_type,
                "platform":platform,
                "width":width,
                "height":height,
                "alt_text":self.alt(article),
                "caption":self.caption(article),
                "credit":"AI-generated editorial illustration"
            }
        except requests.HTTPError as e:
            return {
                "status":"FAILED",
                "generated":False,
                "prompt":prompt,
                "error":str(e),
                "http_status":e.response.status_code if e.response is not None else None
            }
        except Exception as e:
            logger.exception("Image generation failed")
            return {
                "status":"FAILED",
                "generated":False,
                "prompt":prompt,
                "error":str(e)
            }

    def build_prompt(self,article):
        title=self._text(article.get("title",article.get("headline","")))
        summary=self._text(article.get("excerpt",article.get("summary",article.get("lead",""))))
        topic=self._text(article.get("topic",article.get("category","general")))
        location=self._text(article.get("location",""))
        style=self.story_type(article)

        return self._clean(
            f"Create a premium editorial news photograph for a professional international news website. "
            f"Use realistic documentary photography and sophisticated cinematic composition. "
            f"Create a visual scene that represents the subject of this verified news story. "
            f"Visual subject: {title}. "
            f"Topic: {topic}. "
            f"Story context for visual interpretation only: {summary}. "
            f"Location: {location}. "
            f"Story type: {style}. "
            f"Show the people, environment, objects, technology, architecture, or events that naturally represent the story. "
            f"Make the image visually powerful, realistic, credible, modern and suitable for a premium newsroom. "
            f"IMPORTANT: THE IMAGE MUST CONTAIN ZERO TEXT. "
            f"Do not generate any words, letters, numbers, headlines, captions, subtitles, typography, "
            f"newspaper pages, magazine pages, books, documents, articles, text messages, website pages, "
            f"computer screens with writing, phone screens with writing, signs, banners, posters, labels, "
            f"logos, trademarks, watermarks, charts with labels, interface text, handwriting or readable writing. "
            f"If a screen, sign, newspaper, document or display naturally appears in the scene, keep it blank, "
            f"abstract or out of focus with no readable characters. "
            f"Do not invent fake evidence or fake documents. "
            f"Do not depict misleading proof. "
            f"Do not include graphic or disturbing content. "
            f"Visual storytelling only. No typography anywhere in the image."
        )

    def story_type(self,article):
        text=self._text(
            " ".join(
                str(article.get(k,""))
                for k in ("title","headline","topic","category","content","excerpt")
            )
        ).lower()

        groups={
            "politics":[
                "president","minister","government","election",
                "parliament","senate","political","policy"
            ],
            "business":[
                "business","company","market","stock","economy",
                "economic","investment","bank"
            ],
            "technology":[
                "technology","software","ai","artificial intelligence",
                "cyber","robot","chip","app"
            ],
            "sports":[
                "football","soccer","basketball","tennis",
                "sports","league","match","coach","player"
            ],
            "crime":[
                "police","arrest","murder","crime","court",
                "suspect","investigation"
            ],
            "health":[
                "doctor","hospital","disease","health","medical",
                "virus","medicine"
            ],
            "breaking_news":[
                "breaking","explosion","earthquake","flood",
                "fire","crash","attack"
            ]
        }

        scores={k:sum(w in text for w in words) for k,words in groups.items()}
        best=max(scores,key=scores.get)
        return best if scores[best]>0 else "general"

    def alt(self,article):
        return self._text(
            article.get("title",article.get("headline","News image"))
        )[:125]

    def caption(self,article):
        t=self._text(article.get("title",article.get("headline","")))
        return f"Editorial image illustrating: {t}" if t else "Editorial news image."

    def generate_prompt_only(self,article):
        return {
            "status":"PROMPT_READY",
            "prompt":self.build_prompt(article),
            "story_type":self.story_type(article),
            "alt_text":self.alt(article),
            "caption":self.caption(article)
        }

    def _headers(self):
        return {
            "Authorization":f"Bearer {self.api_key}",
            "Content-Type":"application/json",
            "Accept":"image/png,image/jpeg,image/webp,application/octet-stream",
            "User-Agent":"AI-News-Factory/1.3"
        }

    def _extract(self,response):
        data=response.content
        if not data:
            return None

        ct=response.headers.get("Content-Type","").lower()

        if (
            ct.startswith("image/")
            or data.startswith(b"\x89PNG")
            or data.startswith(b"\xff\xd8\xff")
            or data.startswith(b"RIFF")
        ):
            return data

        try:
            obj=response.json()
        except ValueError:
            return data

        return self._json_image(obj)

    def _json_image(self,obj):
        if isinstance(obj,dict):
            for k in ("image","image_url","url","b64_json","data","result"):
                v=obj.get(k)

                if isinstance(v,(dict,list)):
                    x=self._json_image(v)
                    if x:
                        return x

                elif isinstance(v,str):
                    if v.startswith(("http://","https://")):
                        r=requests.get(v,timeout=self.timeout)
                        r.raise_for_status()
                        return r.content
                    return v

        if isinstance(obj,list):
            for v in obj:
                x=self._json_image(v)
                if x:
                    return x

        return None

    def _save(self,image,article,fmt):
        self.output_dir.mkdir(parents=True,exist_ok=True)

        title=self._text(
            article.get("title",article.get("headline","news"))
        ).lower()

        slug=re.sub(
            r"[^a-z0-9]+",
            "-",
            title
        ).strip("-")[:70] or "news"

        ext="jpg" if fmt.lower() in ("jpg","jpeg") else "png"

        path=self.output_dir/f"{slug}_{abs(hash(title))%100000}.{ext}"

        if isinstance(image,(bytes,bytearray)):
            path.write_bytes(bytes(image))

        elif isinstance(image,str):
            if image.startswith(("http://","https://")):
                r=requests.get(image,timeout=self.timeout)
                r.raise_for_status()
                path.write_bytes(r.content)
            else:
                if image.startswith("data:image"):
                    image=image.split(",",1)[1]
                path.write_bytes(base64.b64decode(image))

        else:
            raise ValueError("Unsupported image response.")

        return path

    def _public_url(self,path):
        base=os.getenv("MEDIA_PUBLIC_BASE_URL","").rstrip("/")
        return f"{base}/{path.name}" if base else str(path)

    def validate_result(self,result):
        return (
            isinstance(result,dict)
            and result.get("status")=="IMAGE_READY"
            and bool(result.get("image_url"))
        )

    def _text(self,value):
        if value is None:
            return ""

        if isinstance(value,dict):
            return " ".join(
                str(v)
                for v in value.values()
                if v
            )

        if isinstance(value,list):
            return " ".join(
                str(v)
                for v in value
                if v
            )

        return str(value).strip()

    def _clean(self,text):
        return re.sub(
            r"\s+",
            " ",
            str(text or "")
        ).strip()

    def status(self):
        token=os.getenv("CLOUDFLARE_API_TOKEN","").strip()
        key=os.getenv("IMAGE_API_KEY","").strip()

        source=(
            "CLOUDFLARE_API_TOKEN"
            if token
            else ("IMAGE_API_KEY" if key else "NONE")
        )

        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY" if self.api_url and self.api_key else "NOT_CONFIGURED",
            "configured":bool(self.api_url and self.api_key),
            "credential_source":source
        }

image_generator=ImageGenerator()

def generate_news_image(
    article,
    platform="website",
    mode="auto",
    width=1280,
    height=720
):
    return image_generator.generate(
        article,
        platform,
        mode,
        "png",
        width,
        height
    )

def build_image_prompt(article):
    return image_generator.generate_prompt_only(article)
