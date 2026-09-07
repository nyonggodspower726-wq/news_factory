from __future__ import annotations
import json,re,logging,os
from typing import Any,Dict,List,Optional

logger=logging.getLogger(__name__)

class JournalistEngine:
    def __init__(self,ai=None):
        self.ai=ai
        self.target_words=int(os.getenv("JOURNALIST_TARGET_WORDS","1600"))
        self.min_words=int(os.getenv("JOURNALIST_MIN_WORDS","1000"))
        self.max_words=int(os.getenv("JOURNALIST_MAX_WORDS","2400"))
        self.temperature=float(os.getenv("JOURNALIST_TEMPERATURE","0.55"))
        self.max_tokens=int(os.getenv("JOURNALIST_MAX_TOKENS","5000"))

    def write(self,article_plan=None,story=None,sources=None,claims=None,evidence=None,verification=None,synthesis=None,story_model=None,narrative=None,angles=None,psychology=None,reader_psychology=None,engagement=None,significance=None,ai=None,**kwargs):
        client=ai or self.ai
        research=self._research(article_plan,story,sources,claims,evidence,verification,synthesis,story_model,narrative,angles,psychology,reader_psychology,engagement,significance)
        if not research.get("publishable"):
            return self._failure("JOURNALISM_BLOCKED","Insufficient verified material for a publishable article.",research)
        if client:
            try:
                result=self._call_ai(client,research)
                article=self._clean_article(result,research)
                if self._quality_ok(article,research):
                    article["status"]="JOURNALISM_COMPLETE"
                    article["publication_safe"]=True
                    article["research_grounded"]=True
                    article["quality_score"]=self._quality_score(article,research)
                    return article
            except Exception as exc:
                logger.exception("Journalist AI generation failed: %s",exc)
        return self._failure("JOURNALISM_FAILED","The article did not meet the newsroom quality threshold and should be reprocessed.",research)

    def create(self,*args,**kwargs):
        return self.write(*args,**kwargs)
    def generate(self,*args,**kwargs):
        return self.write(*args,**kwargs)
    def produce(self,*args,**kwargs):
        return self.write(*args,**kwargs)
    def compose(self,*args,**kwargs):
        return self.write(*args,**kwargs)

    def _research(self,article_plan,story,sources,claims,evidence,verification,synthesis,story_model,narrative,angles,psychology,reader_psychology,engagement,significance):
        plan=article_plan if isinstance(article_plan,dict) else {}
        story=story if isinstance(story,dict) else {}
        sources=sources if isinstance(sources,list) else []
        claims=claims if isinstance(claims,list) else []
        evidence=evidence if isinstance(evidence,list) else []
        verification=verification if isinstance(verification,dict) else {}
        verified=self._verified_claims(claims,verification)
        summary=self._text(synthesis) or self._text(plan.get("summary")) or self._text(story.get("summary")) or self._text(story.get("description"))
        title=self._text(plan.get("title")) or self._text(story.get("title")) or self._text(story.get("headline")) or "News report"
        usable_sources=[]
        for s in sources:
            if not isinstance(s,dict): continue
            url=self._text(s.get("url") or s.get("source_url") or s.get("link"))
            name=self._text(s.get("source") or s.get("source_name") or s.get("publisher") or s.get("name"))
            text=self._text(s.get("content") or s.get("description") or s.get("summary") or s.get("text"))
            if url or text:
                usable_sources.append({"name":name,"url":url,"text":text[:12000]})
        facts=[]
        for c in verified:
            if isinstance(c,dict):
                text=self._text(c.get("claim") or c.get("text") or c.get("statement") or c.get("fact"))
                if text: facts.append(text)
            elif isinstance(c,str) and c.strip(): facts.append(c.strip())
        if not facts:
            for e in evidence:
                if isinstance(e,dict):
                    text=self._text(e.get("text") or e.get("evidence") or e.get("claim"))
                    if text: facts.append(text)
        context=[]
        for key,obj in (("story_model",story_model),("narrative",narrative),("angles",angles),("psychology",psychology),("reader_psychology",reader_psychology),("engagement",engagement),("significance",significance)):
            if isinstance(obj,dict):
                for k,v in obj.items():
                    t=self._text(v)
                    if t and len(t)>20: context.append(f"{key}.{k}: {t}")
            elif isinstance(obj,list):
                for v in obj:
                    t=self._text(v)
                    if t and len(t)>20: context.append(f"{key}: {t}")
            else:
                t=self._text(obj)
                if t and len(t)>20: context.append(f"{key}: {t}")
        source_text=sum(len(x.get("text","")) for x in usable_sources)
        publishable=bool(summary or facts or usable_sources) and bool(verified or facts or evidence or summary)
        return {"title":title,"summary":summary,"facts":facts[:50],"sources":usable_sources[:20],"context":context[:50],"plan":plan,"story":story,"verification":verification,"source_text_size":source_text,"publishable":publishable}

    def _verified_claims(self,claims,verification):
        out=[]
        bad=("unverified","disputed","false","contradict","rejected","unsupported","uncorroborated")
        statuses={}
        if isinstance(verification,dict):
            for key in ("claims","results","verified_claims","fact_check"):
                value=verification.get(key)
                if isinstance(value,list):
                    for item in value:
                        if isinstance(item,dict):
                            ident=str(item.get("claim_id") or item.get("id") or item.get("claim") or "").strip()
                            if ident: statuses[ident.lower()]=item
        for c in claims:
            if isinstance(c,str):
                if c.strip() and not any(x in c.lower() for x in bad): out.append(c.strip())
                continue
            if not isinstance(c,dict): continue
            text=self._text(c.get("claim") or c.get("text") or c.get("statement") or c.get("fact"))
            status=self._text(c.get("status") or c.get("verification") or c.get("verdict")).lower()
            ident=self._text(c.get("claim_id") or c.get("id") or text).lower()
            matched=statuses.get(ident,{})
            matched_status=self._text(matched.get("status") or matched.get("verification") or matched.get("verdict")).lower() if isinstance(matched,dict) else ""
            final_status=matched_status or status
            if text and not any(x in final_status for x in bad):
                if not final_status or any(x in final_status for x in ("verified","confirmed","supported","corroborated","high","strong","true")):
                    out.append(text)
        return out

    def _call_ai(self,client,research):
        system=f"""You are the lead writer of a serious digital newsroom.
Write the ACTUAL finished news article, not an outline, template, research note, plan, summary, list of questions, or writing instructions.
Use ONLY the supplied research. Never invent facts, names, quotes, statistics, dates, motives, locations, background details, or events.
Never manufacture a quotation. Use quotation marks only for wording explicitly supplied in the research.
Do not turn analysis or speculation into fact. Clearly distinguish confirmed information from uncertainty.
Write with the natural rhythm of an experienced human reporter. Vary sentence length, paragraph length, pacing and section structure.
The article must feel written specifically for THIS story. Do not reuse a fixed sequence of headings across stories.
Do not use generic/template headings or questions such as "What actually happened?", "The bigger picture", "The takeaway", "What remains unclear?", "Why is this happening now?", "Who is affected?", "What happens next?", "What does this mean?", "What information is still unconfirmed?", or similar repeated newsroom-template language.
Do not repeat the same fact merely to increase word count.
Do not pad the story with generic advice or unrelated background.
Start with a strong, specific lead that immediately tells the reader why the development matters.
Build the story organically. Depending on the evidence, you may use a mix of narrative paragraphs, useful subheads, chronology, verified context, reactions, numbers, consequences, competing explanations, practical details, or other story-specific elements.
Use subheads only when they genuinely improve navigation. A story may have several subheads, a few subheads, or none.
Keep the article engaging enough for a news-feed reader to continue scrolling, but accuracy always outranks drama.
Include the most important verified details early, then deepen the story with verified context and implications.
Do not create fake suspense. Do not ask the reader questions as filler.
End naturally with the latest confirmed position, a meaningful unresolved issue, or the next verified development rather than a generic "takeaway".
Aim for about {self.target_words} words when the evidence supports it. The acceptable publication range is approximately {self.min_words}-{self.max_words} words. If the evidence genuinely cannot support that length, write only what can be supported and do NOT invent material; the newsroom quality gate will reject insufficient work.
Return ONLY valid JSON with exactly these fields:
title,headline,dek,lead,content,key_facts,context,why_it_matters,what_happens_next,what_is_unknown,sources,seo_title,seo_description,slug
content must be the complete article body and must not contain an author byline or duplicate title."""
        payload={"title":research["title"],"summary":research["summary"],"verified_facts":research["facts"],"sources":research["sources"],"editorial_context":research["context"]}
        response=client.chat(messages=[{"role":"system","content":system},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],temperature=self.temperature,max_tokens=self.max_tokens)
        raw=self._strip_fences(self._response_text(response))
        return json.loads(raw)

    def _response_text(self,response):
        if isinstance(response,str): return response
        if isinstance(response,dict):
            choices=response.get("choices")
            if isinstance(choices,list) and choices:
                choice=choices[0]
                if isinstance(choice,dict):
                    message=choice.get("message")
                    if isinstance(message,dict): return str(message.get("content") or "")
                    return str(choice.get("text") or "")
            return str(response.get("content") or response.get("text") or "")
        choices=getattr(response,"choices",None)
        if choices:
            choice=choices[0]
            message=getattr(choice,"message",None)
            if message: return str(getattr(message,"content","") or "")
            return str(getattr(choice,"text","") or "")
        return str(getattr(response,"content","") or "")

    def _strip_fences(self,text):
        text=text.strip()
        text=re.sub(r"^```(?:json)?\s*","",text,flags=re.I)
        text=re.sub(r"\s*```$","",text)
        return text.strip()

    def _clean_article(self,result,research):
        if not isinstance(result,dict): raise ValueError("Journalist AI returned invalid article object")
        title=self._clean_text(result.get("title") or result.get("headline") or research["title"])
        headline=self._clean_text(result.get("headline") or title)
        dek=self._clean_text(result.get("dek"))
        lead=self._clean_text(result.get("lead"))
        content=self._clean_content(result.get("content") or "")
        if not content: content=lead
        slug=self._slug(result.get("slug") or title)
        sources=result.get("sources")
        if not isinstance(sources,list) or not sources: sources=research["sources"]
        return {"title":title,"headline":headline,"dek":dek,"lead":lead,"content":content.strip(),"key_facts":self._clean_list(result.get("key_facts"),research["facts"]),"context":self._clean_list(result.get("context"),research["context"]),"why_it_matters":self._clean_text(result.get("why_it_matters")),"what_happens_next":self._clean_text(result.get("what_happens_next")),"what_is_unknown":self._clean_text(result.get("what_is_unknown")),"sources":sources,"seo_title":self._clean_text(result.get("seo_title") or title),"seo_description":self._clean_text(result.get("seo_description") or dek or lead)[:320],"slug":slug,"status":"JOURNALISM_COMPLETE","publication_safe":False,"research_grounded":True}

    def _clean_content(self,text):
        text=self._clean_text(text)
        generic=r"What actually happened\?|The bigger picture|The takeaway|What remains unclear|Why is this happening now\?|Who is affected\?|What does this mean\??|What does this mean for ordinary people\?|What happens next\?|What information is still unconfirmed\?|What information is still unclear\?"
        text=re.sub(rf"(?im)^\s*#{1,6}\s*(?:{generic})\s*$","",text)
        text=re.sub(rf"(?im)^\s*(?:{generic})\s*$","",text)
        text=re.sub(r"(?im)^\s*By\s+[A-Za-z][A-Za-z .,'’-]{1,80}\s*$","",text)
        text=re.sub(r"(?im)^\s*By\s+[A-Za-z][A-Za-z .,'’-]{1,80}\s+","",text)
        text=re.sub(r"\.{3,}","",text)
        text=re.sub(r"\n{3,}","\n\n",text)
        lines=[]; previous=""
        for line in text.splitlines():
            clean=line.strip()
            if not clean:
                if lines and lines[-1]!="": lines.append("")
                continue
            if clean.lower()==previous.lower(): continue
            lines.append(line.rstrip()); previous=clean
        return "\n".join(lines).strip()

    def _paragraphs(self,content):
        return [p.strip() for p in re.split(r"\n\s*\n",content) if p.strip()]

    def _sentences(self,content):
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+",content) if len(s.strip())>35]

    def _quality_ok(self,article,research):
        content=article.get("content","").strip()
        words=len(re.findall(r"\b[\w’'-]+\b",content))
        if words<self.min_words: return False
        if words>self.max_words+300: return False
        if len(self._paragraphs(content))<8: return False
        if len(self._sentences(content))<14: return False
        if "..." in content: return False
        low=content.lower()
        bad=("what actually happened?","what remains unclear?","why is this happening now?","who is affected?","what happens next?","the takeaway","the bigger picture","what information is still unconfirmed?")
        if any(x in low for x in bad): return False
        paragraphs=self._paragraphs(content)
        normalized=[re.sub(r"[^a-z0-9 ]","",p.lower()) for p in paragraphs]
        if len(normalized)!=len(set(normalized)): return False
        if research["facts"] and sum(1 for f in research["facts"] if self._fact_overlap(f,content))<max(1,min(3,len(research["facts"]))): return False
        if article.get("lead") and self._similarity(article["lead"],content[:1200])>0.85: return False
        if self._template_score(content)>0.25: return False
        return True

    def _template_score(self,content):
        patterns=("what happened","what happens next","why it matters","the bigger picture","the takeaway","who is affected","what remains unclear","what this means")
        low=content.lower()
        return sum(low.count(x) for x in patterns)/max(1,len(self._paragraphs(content)))

    def _similarity(self,a,b):
        wa=set(re.findall(r"\b[a-zA-Z]{5,}\b",self._clean_text(a).lower()))
        wb=set(re.findall(r"\b[a-zA-Z]{5,}\b",self._clean_text(b).lower()))
        return len(wa&wb)/max(1,len(wa|wb))

    def _fact_overlap(self,fact,content):
        words=[w.lower() for w in re.findall(r"\b[a-zA-Z]{5,}\b",fact)]
        if not words: return True
        hits=sum(1 for w in set(words) if w in content.lower())
        return hits>=max(1,min(3,len(set(words))))

    def _quality_score(self,article,research):
        content=article.get("content","")
        words=len(re.findall(r"\b[\w’'-]+\b",content))
        score=50
        if words>=self.min_words: score+=15
        if words>=self.target_words: score+=10
        if len(self._paragraphs(content))>=12: score+=5
        if research["facts"]: score+=10
        if research["sources"]: score+=10
        return min(score,100)

    def _fallback(self,research):
        return self._failure("JOURNALISM_FAILED","No publication-quality article was produced. Reprocess this story or use another verified candidate.",research)

    def _failure(self,status,message,research):
        return {"title":research.get("title",""),"headline":research.get("title",""),"dek":"","lead":"","content":"","key_facts":research.get("facts",[]),"context":research.get("context",[]),"why_it_matters":"","what_happens_next":"","what_is_unknown":message,"sources":research.get("sources",[]),"seo_title":research.get("title",""),"seo_description":"","slug":self._slug(research.get("title","news")),"status":status,"publication_safe":False,"research_grounded":False,"quality_score":0}

    def _clean_list(self,value,fallback):
        if not isinstance(value,list): return fallback[:20]
        out=[]
        for item in value:
            text=self._clean_text(item)
            if text and text not in out: out.append(text)
        return out[:30] or fallback[:20]

    def _clean_text(self,value):
        if value is None: return ""
        if isinstance(value,(dict,list)): return json.dumps(value,ensure_ascii=False)
        text=str(value).strip()
        text=re.sub(r"\s+"," ",text)
        return text

    def _text(self,value):
        return self._clean_text(value)

    def _slug(self,value):
        text=self._clean_text(value).lower()
        text=re.sub(r"[^a-z0-9\s-]","",text)
        text=re.sub(r"[\s_-]+","-",text).strip("-")
        return text[:140] or "news-story"

JournalistEngineV4=JournalistEngine
JournalistEngineV3=JournalistEngine
journalist_engine=JournalistEngine()
