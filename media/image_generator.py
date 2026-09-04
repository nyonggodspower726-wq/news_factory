import os,re,base64,logging,requests
from pathlib import Path
from typing import Any,Dict,Optional
logger=logging.getLogger(__name__)

class ImageGenerator:
 def __init__(self,api_url=None,api_key=None,model=None,output_dir="media/generated"):
  self.name="AI News Image Generator";self.version="1.2.0"
  self.api_url=api_url or os.getenv("IMAGE_API_URL","").strip()
  self.api_key=api_key or os.getenv("CLOUDFLARE_API_TOKEN","").strip() or os.getenv("IMAGE_API_KEY","").strip()
  self.model=model or os.getenv("IMAGE_MODEL","").strip()
  self.output_dir=Path(output_dir);self.timeout=120
  self.styles={"breaking_news":"professional editorial news photography, realistic documentary scene, natural lighting","politics":"professional editorial political news photography, realistic formal environment","business":"professional editorial business photography, realistic corporate or economic environment","technology":"professional editorial technology photography, realistic modern environment","sports":"professional editorial sports photography, realistic action and stadium environment","crime":"professional editorial documentary scene, respectful, non-graphic, realistic environment","health":"professional editorial health photography, realistic clinical environment, non-graphic","general":"professional editorial news photography, realistic documentary style"}
  self.forbidden_terms={"fake evidence","fabricated evidence","fake photograph","altered evidence","misleading proof"}

 def generate(self,article:Dict[str,Any],platform="website",mode="auto",output_format="png",width=1280,height=720)->Dict[str,Any]:
  if not isinstance(article,dict): raise TypeError("Article must be a dictionary.")
  prompt=self.build_prompt(article);story_type=self.story_type(article)
  if mode=="licensed": return {"status":"LICENSE_REQUIRED","generated":False,"source_type":"LICENSED","prompt":prompt}
  if not self.api_url or not self.api_key:
   return {"status":"NOT_CONFIGURED","generated":False,"source_type":"AI_GENERATED","prompt":prompt,"message":"IMAGE_API_URL and API token are not configured."}
  try:
   response=requests.post(self.api_url,headers=self._headers(),json=self._payload(prompt,width,height),timeout=self.timeout)
   response.raise_for_status()
   image=self._extract_image_response(response)
   if not image:return {"status":"FAILED","generated":False,"source_type":"AI_GENERATED","prompt":prompt,"error":"Empty or unusable image response."}
   path=self._save(image,article,output_format);url=self._public_url(path)
   return {"status":"IMAGE_READY","generated":True,"source_type":"AI_GENERATED","image_url":url,"local_path":str(path),"prompt":prompt,"story_type":story_type,"platform":platform,"width":width,"height":height,"alt_text":self.create_alt_text(article),"caption":self.create_caption(article),"credit":"AI-generated editorial illustration"}
  except requests.HTTPError as e:
   logger.exception("Cloudflare image generation HTTP error")
   return {"status":"FAILED","generated":False,"source_type":"AI_GENERATED","prompt":prompt,"error":str(e),"http_status":e.response.status_code if e.response is not None else None}
  except requests.RequestException as e:
   logger.exception("Image generation request failed")
   return {"status":"FAILED","generated":False,"source_type":"AI_GENERATED","prompt":prompt,"error":str(e)}
  except Exception as e:
   logger.exception("Image generation failed")
   return {"status":"FAILED","generated":False,"source_type":"AI_GENERATED","prompt":prompt,"error":str(e)}

 def build_prompt(self,article):
  title=self._text(article.get("title",article.get("headline","")))
  summary=self._text(article.get("excerpt",article.get("summary",article.get("lead",""))))
  topic=self._text(article.get("topic",article.get("category","general")))
  location=self._text(article.get("location",""))
  event=self._text(article.get("event_type",article.get("story_type","general")))
  style=self.styles.get(self.story_type(article),self.styles["general"])
  return self._clean(f"{style}. Create an original editorial image illustrating the verified news topic. Topic: {topic}. Event: {event}. Headline: {title}. Context: {summary}. Location: {location}. Make it realistic, relevant, non-deceptive and non-graphic. Do not create fake evidence, fabricated documents, misleading proof or deceptive visual claims.")

 def story_type(self,article):
  text=self._text(" ".join(str(article.get(k,"")) for k in ("title","headline","topic","category","content","excerpt"))).lower()
  groups={"politics":["president","minister","government","election","parliament","senate","political","policy"],"business":["business","company","market","stock","economy","economic","investment","bank"],"technology":["technology","software","ai","artificial intelligence","cyber","robot","chip","app"],"sports":["football","soccer","basketball","tennis","sports","league","match","coach","player"],"crime":["police","arrest","murder","crime","court","suspect","investigation"],"health":["doctor","hospital","disease","health","medical","virus","medicine"],"breaking_news":["breaking","explosion","earthquake","flood","fire","crash","attack"]}
  scores={k:sum(1 for w in v if w in text) for k,v in groups.items()}
  best=max(scores,key=scores.get)
  return best if scores[best]>0 else "general"

 def create_alt_text(self,article):
  return self._text(article.get("title",article.get("headline","")))[:125] or "News image"

 def create_caption(self,article):
  title=self._text(article.get("title",article.get("headline","")))
  return f"Editorial image illustrating: {title}" if title else "Editorial news image."
