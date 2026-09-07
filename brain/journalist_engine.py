import json,re,logging,os
from typing import Any,Dict,List
logger=logging.getLogger("NewsFactory.JournalistEngine")

class JournalistEngine:
    def __init__(self,ai=None)->None:
        self.name="AI Journalist Engine"
        self.version="3.0.0"
        self.ai=ai
        self.target_words=int(os.getenv("NEWS_TARGET_WORDS","1600"))
        self.minimum_words=int(os.getenv("NEWS_MINIMUM_WORDS","900"))
        self.maximum_words=int(os.getenv("NEWS_MAXIMUM_WORDS","2400"))
        self.temperature=float(os.getenv("NEWS_WRITER_TEMPERATURE","0.35"))
        self.max_tokens=int(os.getenv("NEWS_WRITER_MAX_TOKENS","3200"))
        self.required_sections=["headline","dek","lead","key_facts","context","why_it_matters","what_happens_next","what_is_unknown","sources"]

    def status(self)->Dict[str,Any]:
        return {"status":"READY","engine":self.name,"version":self.version,"ai_connected":self.ai is not None,"target_words":self.target_words,"minimum_words":self.minimum_words,"maximum_words":self.maximum_words}

    def write(self,article_plan:Dict[str,Any]=None,story:Dict[str,Any]=None,sources:List[Dict[str,Any]]=None,claims:List[Dict[str,Any]]=None,evidence:Dict[str,Any]=None,verification:Dict[str,Any]=None,synthesis:Dict[str,Any]=None,story_model:Dict[str,Any]=None,narrative:Dict[str,Any]=None,angles:Dict[str,Any]=None,psychology:Dict[str,Any]=None,reader_psychology:Dict[str,Any]=None,engagement:Dict[str,Any]=None,significance:Dict[str,Any]=None,ai=None,**kwargs)->Dict[str,Any]:
        story=story if isinstance(story,dict) else {}
        sources=sources if isinstance(sources,list) else []
        claims=claims if isinstance(claims,list) else []
        evidence=evidence if isinstance(evidence,dict) else {}
        verification=verification if isinstance(verification,dict) else {}
        synthesis=synthesis if isinstance(synthesis,dict) else {}
        story_model=story_model if isinstance(story_model,dict) else synthesis
        narrative=narrative if isinstance(narrative,dict) else {}
        angles=angles if isinstance(angles,dict) else {}
        psychology=psychology if isinstance(psychology,dict) else {}
        reader_psychology=reader_psychology if isinstance(reader_psychology,dict) else {}
        engagement=engagement if isinstance(engagement,dict) else {}
        significance=significance if isinstance(significance,dict) else {}
        article_plan=article_plan if isinstance(article_plan,dict) else {}
        client=ai or self.ai
        research=self._research(story,sources,claims,evidence,verification,synthesis,story_model,narrative,angles,psychology,reader_psychology,engagement,significance,article_plan)
        if not client:
            return self._fallback(research)
        try:
            raw=self._call_ai(client,research)
            article=self._parse(raw)
            article=self._clean_article(article,research)
            if not article.get("content"):
                raise ValueError("Writer returned empty article.")
            article["status"]="ARTICLE_WRITTEN"
            article["engine"]=self.name
            article["version"]=self.version
            article["word_count"]=self._word_count(article.get("content",""))
            article["long_form"]=article["word_count"]>=self.minimum_words
            article["publication_safe"]=True
            article["research_grounded"]=True
            article["source_count"]=len(sources)
            article["source_url"]=self._text(story.get("source_url"))
            article["image_url"]=self._text(story.get("image_url"))
            return {"status":"JOURNALISM_COMPLETE","engine":self.name,"version":self.version,"article":article,"content":article["content"],"body":article["content"],"title":article.get("title",""),"headline":article.get("headline",article.get("title","")),"word_count":article["word_count"],"research_grounded":True,"publication_safe":True}
        except Exception as exc:
            logger.exception("Journalist AI writing failed.")
            fallback=self._fallback(research)
            fallback["writer_error"]=str(exc)
            return fallback

    def create(self,**kwargs)->Dict[str,Any]:
        return self.write(**kwargs)

    def generate(self,**kwargs)->Dict[str,Any]:
        return self.write(**kwargs)

    def produce(self,**kwargs)->Dict[str,Any]:
        return self.write(**kwargs)

    def compose(self,**kwargs)->Dict[str,Any]:
        return self.write(**kwargs)

    def build_article(self,newsroom_package:Dict[str,Any])->Dict[str,Any]:
        return self.write(**self._package_args(newsroom_package))

    def create_article_plan(self,newsroom_package:Dict[str,Any])->Dict[str,Any]:
        return self.write(**self._package_args(newsroom_package))

    def _package_args(self,p:Dict[str,Any])->Dict[str,Any]:
        p=p if isinstance(p,dict) else {}
        return {"article_plan":p.get("article_plan",p),"story":p.get("story",{}),"sources":p.get("sources",[]),"claims":p.get("claims",[]),"evidence":p.get("evidence",{}),"verification":p.get("verification",{}),"synthesis":p.get("synthesis",p.get("story_model",{})),"story_model":p.get("story_model",{}),"narrative":p.get("narrative",{}),"angles":p.get("angles",{}),"psychology":p.get("psychology",{}),"reader_psychology":p.get("reader_psychology",{}),"engagement":p.get("engagement",{}),"significance":p.get("significance",{}),"ai":p.get("ai")}

    def _research(self,story,sources,claims,evidence,verification,synthesis,story_model,narrative,angles,psychology,reader_psychology,engagement,significance,article_plan)->Dict[str,Any]:
        safe=[]
        for item in claims:
            if isinstance(item,str):
                safe.append({"claim":item,"status":"CONFIRMED"})
                continue
            if not isinstance(item,dict):continue
            status=self._text(item.get("status",item.get("verification_status",item.get("publication_status","")))).upper()
            if status in {"CONTRADICTED","DISPUTED","UNVERIFIED","HOLD_FOR_REVIEW","REJECTED"}:continue
            text=self._text(item.get("claim",item.get("text",item.get("content",""))))
            if text:safe.append({"claim":text,"status":status or "SUPPORTED","source":item.get("source","")})
        verified=self._verified_claims(verification)
        for item in verified:
            if not any(self._text(x.get("claim")).lower()==self._text(item).lower() for x in safe):
                safe.append({"claim":self._text(item),"status":"VERIFIED"})
        return {"story":self._trim(story),"sources":self._trim_list(sources,30),"verified_claims":safe[:40],"evidence":self._trim(evidence),"verification":self._trim(verification),"synthesis":self._trim(synthesis),"story_model":self._trim(story_model),"narrative":self._trim(narrative),"angles":self._trim(angles),"psychology":self._trim(psychology),"reader_psychology":self._trim(reader_psychology),"engagement":self._trim(engagement),"significance":self._trim(significance),"article_plan":self._trim(article_plan)}

    def _call_ai(self,client,research):
        system="""You are the senior newsroom journalist inside an automated digital news organization. Write the actual publishable news article, not an outline, plan, prompt, notes, bullet list, or summary. Your job is to transform the supplied verified newsroom intelligence into a substantial, natural, human-sounding news report.
STRICT FACTUAL RULES:
1. Use only information supported by the supplied newsroom research.
2. Never invent quotes, people, dates, numbers, events, motives, locations, reactions, statistics or background facts.
3. Attribute claims clearly when they belong to a person, organization or source.
4. Never turn an unverified or disputed claim into established fact.
5. If important information is unknown, say so naturally rather than filling the gap.
6. Do not manufacture balance by inventing an opposing view.
7. Do not copy source wording unnecessarily. Synthesize and rewrite naturally.
WRITING STANDARD:
Write like a strong human reporter for a respected modern news website. The article must have a compelling but accurate headline, a useful dek, a strong opening paragraph, natural paragraph-to-paragraph transitions, clear chronology or logical progression, relevant context, important details, why the development matters, what may happen next based only on supported information, and a natural ending.
Do not make every paragraph the same length. Avoid robotic patterns. Avoid repetitive sentences. Avoid generic filler such as 'What actually happened?', 'The bigger picture', 'The takeaway', or questions that contain no answer. Do not repeat the lead later. Do not use fake quotations.
SEO:
Make the article genuinely useful to a Google searcher. Naturally identify the people, organizations, places, event and subject readers are likely to search for. Use descriptive subheadings where helpful. Do not keyword-stuff. Do not write for search engines at the expense of readers.
ENGAGEMENT:
Create curiosity through the facts themselves. Explain why the development matters to ordinary readers when the evidence supports that connection. Keep the reader moving through the story without sensationalism or clickbait.
LENGTH:
Aim for approximately 1600 words when the research supports that depth. Never pad an article merely to hit a word count. Prefer a shorter accurate article over invented material.
OUTPUT:
Return ONLY valid JSON with these keys:
title,headline,dek,lead,content,key_facts,context,why_it_matters,what_happens_next,what_is_unknown,sources,seo_title,seo_description,slug
The content field must contain the complete article in Markdown. Do not put the headline or dek inside content because they are separate fields."""
        user="NEWSROOM RESEARCH:\n"+json.dumps(research,ensure_ascii=False,default=str,separators=(",",":"))
        messages=[{"role":"system","content":system},{"role":"user","content":user}]
        return client.chat(messages,temperature=self.temperature,max_tokens=self.max_tokens)

    def _parse(self,raw)->Dict[str,Any]:
        text=str(raw or "").strip()
        if text.startswith("```"):
            text=re.sub(r"^```(?:json)?\s*","",text,flags=re.I)
            text=re.sub(r"\s*```$","",text)
        try:return json.loads(text)
        except Exception:
            match=re.search(r"\{.*\}",text,re.S)
            if match:return json.loads(match.group(0))
            raise ValueError("NVIDIA journalist response was not valid JSON.")

    def _clean_article(self,a,research)->Dict[str,Any]:
        if not isinstance(a,dict):return {}
        title=self._clean_title(a.get("title") or a.get("headline") or research["story"].get("title") or research["story"].get("headline") or "Latest News Development")
        content=self._clean_content(a.get("content") or a.get("body") or "")
        lead=self._text(a.get("lead"))
        if not lead:
            lead=self._first_paragraph(content)
        if not content and lead:content=lead
        a["title"]=title
        a["headline"]=self._clean_title(a.get("headline") or title)
        a["dek"]=self._text(a.get("dek"))
        a["lead"]=lead
        a["content"]=content
        a["body"]=content
        a["slug"]=self._slug(a.get("slug") or title)
        a["seo_title"]=self._text(a.get("seo_title") or title)[:70]
        a["seo_description"]=self._text(a.get("seo_description") or lead)[:160]
        for key in ("key_facts","context","why_it_matters","what_happens_next","what_is_unknown","sources"):
            if not isinstance(a.get(key),list):a[key]=self._listify(a.get(key))
        return a

    def _clean_content(self,text):
        text=str(text or "").strip()
        text=re.sub(r"\n{3,}","\n\n",text)
        text=re.sub(r"(?im)^\s*(What actually happened\?|The bigger picture|The takeaway)\s*\n?","",text)
        lines=text.splitlines()
        out=[]
        for line in lines:
            if out and line.strip() and line.strip()==out[-1].strip():continue
            out.append(line.rstrip())
        return "\n".join(out).strip()

    def _fallback(self,research):
        story=research["story"]
        title=self._clean_title(story.get("title") or story.get("headline") or "Latest News Development")
        summary=self._text(story.get("summary") or story.get("description") or research["synthesis"].get("central_event"))
        facts=[self._text(x.get("claim")) for x in research["verified_claims"] if self._text(x.get("claim"))]
        paragraphs=[]
        if summary:paragraphs.append(summary)
        for fact in facts:
            if fact and fact not in paragraphs:paragraphs.append(fact)
        content="\n\n".join(paragraphs)
        return {"status":"JOURNALISM_FALLBACK","engine":self.name,"version":self.version,"article":{"title":title,"headline":title,"dek":summary[:180],"lead":summary or (facts[0] if facts else title),"content":content,"body":content,"slug":self._slug(title),"key_facts":facts,"context":[],"why_it_matters":[],"what_happens_next":[],"what_is_unknown":[],"sources":research["sources"],"seo_title":title[:70],"seo_description":(summary or title)[:160],"word_count":self._word_count(content),"long_form":False,"publication_safe":bool(content)},"content":content,"body":content,"title":title,"headline":title,"word_count":self._word_count(content),"research_grounded":True,"publication_safe":bool(content)}
