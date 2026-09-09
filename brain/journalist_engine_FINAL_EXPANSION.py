from __future__ import annotations
import json,re,logging,os
from typing import Any,Dict,List
logger=logging.getLogger(__name__)

class JournalistEngine:
    def __init__(self,ai=None):
        self.ai=ai
        self.target_words=int(os.getenv("JOURNALIST_TARGET_WORDS","1400"))
        self.min_words=int(os.getenv("JOURNALIST_MIN_WORDS","650"))
        self.max_words=int(os.getenv("JOURNALIST_MAX_WORDS","2000"))
        self.temperature=float(os.getenv("JOURNALIST_TEMPERATURE","0.45"))
        self.max_tokens=int(os.getenv("JOURNALIST_MAX_TOKENS","5000"))

    def write(self,article_plan=None,story=None,sources=None,claims=None,evidence=None,verification=None,synthesis=None,story_model=None,narrative=None,angles=None,psychology=None,reader_psychology=None,engagement=None,significance=None,ai=None,**kwargs):
        client=ai or self.ai
        research=self._research(article_plan,story,sources,claims,evidence,verification,synthesis,story_model,narrative,angles,psychology,reader_psychology,engagement,significance)
        if not research["publishable"]:
            return self._failure("JOURNALISM_BLOCKED","Insufficient verified material for a publishable article.",research)
        if not client:
            return self._failure("JOURNALISM_FAILED","No AI client was supplied to JournalistEngine.",research)
        try:
            result=self._call_ai(client,research)
            article=self._clean_article(result,research)
            if self._word_count(article.get("content","")) < self.min_words:
                result=self._expand_if_needed(client,research,result)
                article=self._clean_article(result,research)
            if not self._quality_ok(article,research):
                words=self._word_count(article.get("content",""))
                logger.warning("Journalist quality gate rejected output | words=%s min=%s",words,self.min_words)
                return self._failure("JOURNALISM_QUALITY_FAILED","AI returned an article, but it did not meet the newsroom quality threshold. Reprocess this story.",research)
            article.update(status="JOURNALISM_COMPLETE",publication_safe=True,research_grounded=True,quality_score=self._quality_score(article,research))
            return article
        except Exception as exc:
            logger.exception("Journalist AI generation failed: %s",exc)
            return self._failure("JOURNALISM_FAILED",f"Journalist AI generation failed: {type(exc).__name__}: {exc}",research)

    create=write
    generate=write
    produce=write
    compose=write

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
        usable=[]
        for s in sources:
            if not isinstance(s,dict): continue
            url=self._text(s.get("url") or s.get("source_url") or s.get("link"))
            name=self._text(s.get("source") or s.get("source_name") or s.get("publisher") or s.get("name"))
            text=self._text(s.get("content") or s.get("description") or s.get("summary") or s.get("text"))
            if url or text: usable.append({"name":name,"url":url,"text":text[:14000]})
        facts=[]
        for item in verified:
            text=self._text(item.get("claim") or item.get("text") or item.get("statement") or item.get("fact")) if isinstance(item,dict) else self._text(item)
            if text: facts.append(text)
        for e in evidence:
            text=self._text(e.get("text") or e.get("evidence") or e.get("claim")) if isinstance(e,dict) else self._text(e)
            if text: facts.append(text)
        facts=self._unique(facts)
        context=[]
        for name,obj in (("story_model",story_model),("narrative",narrative),("angles",angles),("psychology",psychology),("reader_psychology",reader_psychology),("engagement",engagement),("significance",significance)):
            text=self._structured_text(obj)
            if text: context.append(f"{name}: {text[:8000]}")
        source_text=sum(len(x["text"]) for x in usable)
        publishable=bool(summary or facts or usable) and bool(verified or facts or summary or usable)
        return {"title":title,"summary":summary,"facts":facts[:60],"sources":usable[:20],"context":context[:20],"plan":plan,"story":story,"verification":verification,"source_text_size":source_text,"publishable":publishable}

    def _verified_claims(self,claims,verification):
        out=[]; bad=("unverified","disputed","false","contradict","rejected","unsupported","uncorroborated","fabricated")
        checked={}
        for key in ("claims","results","verified_claims","fact_check"):
            value=verification.get(key) if isinstance(verification,dict) else None
            if isinstance(value,list):
                for item in value:
                    if isinstance(item,dict):
                        ident=self._text(item.get("claim_id") or item.get("id") or item.get("claim") or item.get("text")).lower()
                        if ident: checked[ident]=item
        for c in claims:
            if isinstance(c,str):
                if c.strip() and not any(x in c.lower() for x in bad): out.append(c.strip())
                continue
            if not isinstance(c,dict): continue
            text=self._text(c.get("claim") or c.get("text") or c.get("statement") or c.get("fact"))
            ident=self._text(c.get("claim_id") or c.get("id") or text).lower()
            match=checked.get(ident,{})
            status=self._text(match.get("status") or match.get("verification") or match.get("verdict") or c.get("status") or c.get("verification") or c.get("verdict")).lower()
            if text and not any(x in status for x in bad) and (not status or any(x in status for x in ("verified","confirmed","supported","corroborated","true","high","strong"))): out.append(text)
        return self._unique(out)

    def _call_ai(self,client,research):
        system=f'''You are the lead writer of a serious digital newsroom. Write the ACTUAL finished news article, not an outline, template, plan, research note, list of questions, or instructions.
Use ONLY the supplied research. Never invent facts, names, quotes, statistics, dates, motives, locations, background details, or events. Never manufacture quotations. Do not turn analysis or speculation into fact.
Write specifically for THIS story. Use a strong factual lead, then develop the story naturally with verified chronology, context, reactions, consequences and other story-specific material when supported. Vary paragraph length and structure. Use subheads only when genuinely useful and never use generic/template headings or questions.
Never print headings such as "What actually happened?", "The bigger picture", "The takeaway", "What remains unclear?", "Why is this happening now?", "Who is affected?", "What happens next?", "What does this mean?", or similar template language. Those questions may guide your reasoning internally but must never appear as headings or filler in the article.
Do not repeat facts to inflate length. Do not pad with generic advice. Do not create fake suspense. End naturally on the latest confirmed position, meaningful unresolved issue, or verified next development.
Aim for about {self.target_words} words when the supplied evidence supports it. Publication range: {self.min_words}-{self.max_words}. Prefer 1,200-1,500 words when the evidence supports it, but shorter complete stories are acceptable down to the minimum; longer stories are acceptable up to the maximum when supported by evidence. Do not pad.
Return ONLY valid JSON with exactly these fields: title,headline,dek,lead,content,sections,key_facts,context,why_it_matters,what_happens_next,what_is_unknown,sources,seo_title,seo_description,slug.
content must be the complete article body. sections is metadata only and must not be used as a substitute for content. Include a lead section in sections when a lead exists. Do not include a title, byline, JSON fences, or meta commentary inside content.'''
        payload={"title":research["title"],"summary":research["summary"],"verified_facts":research["facts"],"sources":research["sources"],"editorial_context":research["context"]}
        response=client.chat(messages=[{"role":"system","content":system},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],temperature=self.temperature,max_tokens=self.max_tokens,enable_thinking=False,response_format={"type":"json_object"})
        raw=self._strip_fences(self._response_text(response))
        if not raw: raise ValueError("NVIDIA returned empty journalist content")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            repaired=self._repair_json(raw)
            return json.loads(repaired)

    def _repair_json(self,text):
        text=str(text or "").strip()
        text=re.sub(r"^```(?:json)?\\s*|\\s*```$","",text,flags=re.I).strip()
        return text

    def _response_text(self,response):
        if isinstance(response,str): return response
        if isinstance(response,dict):
            choices=response.get("choices")
            if isinstance(choices,list) and choices:
                m=choices[0].get("message") if isinstance(choices[0],dict) else None
                if isinstance(m,dict): return str(m.get("content") or "")
                return str(choices[0].get("text") or "") if isinstance(choices[0],dict) else ""
            return str(response.get("content") or response.get("text") or "")
        choices=getattr(response,"choices",None)
        if choices:
            m=getattr(choices[0],"message",None)
            return str(getattr(m,"content","") or "") if m else str(getattr(choices[0],"text","") or "")
        return str(getattr(response,"content","") or "")

    def _expand_if_needed(self,client,research,result):
        if not isinstance(result,dict): return result
        content=self._text(result.get("content")); words=self._word_count(content)
        if words>=self.min_words: return result
        system=f"""You are the senior editor completing a serious digital news article.
The supplied draft is below the minimum publication length. Rewrite and expand it into a complete article of at least {self.min_words} words and preferably around {self.target_words} words, but never beyond {self.max_words} words.
Use ONLY facts and information contained in the supplied research and draft. Do not invent names, quotes, statistics, dates, motives, locations, events, background details, or reactions.
Add useful verified context, chronology, consequences, significance, and story-specific detail where supported by the research. Do not pad, repeat facts, or create generic filler.
Do not use generic/template headings or questions. Return ONLY valid JSON with exactly these fields: title,headline,dek,lead,content,sections,key_facts,context,why_it_matters,what_happens_next,what_is_unknown,sources,seo_title,seo_description,slug.
content must be the complete rewritten article body."""
        payload={"research":research,"draft":result,"instruction":f"Current draft is {words} words. Expand it to at least {self.min_words} words using only supplied evidence."}
        response=client.chat(messages=[{"role":"system","content":system},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],temperature=self.temperature,max_tokens=self.max_tokens,enable_thinking=False,response_format={"type":"json_object"})
        raw=self._strip_fences(self._response_text(response))
        if not raw: raise ValueError("NVIDIA returned empty journalist expansion")
        try: return json.loads(raw)
        except json.JSONDecodeError: return json.loads(self._repair_json(raw))

    def _clean_article(self,result,research):
        if not isinstance(result,dict): raise ValueError("Journalist AI returned invalid JSON object")
        title=self._clean_text(result.get("title") or result.get("headline") or research["title"])
        headline=self._clean_text(result.get("headline") or title)
        lead=self._clean_text(result.get("lead"))
        content=self._clean_content(result.get("content") or "")
        if not content: content=lead
        sections=result.get("sections") if isinstance(result.get("sections"),list) else []
        if lead and not any(isinstance(s,dict) and self._clean_text(s.get("heading")).lower()=="lead" for s in sections):
            sections=[{"heading":"lead","content":lead}]+sections
        return {"title":title,"headline":headline,"dek":self._clean_text(result.get("dek")),"lead":lead,"content":content,"sections":sections[:20],"key_facts":self._clean_list(result.get("key_facts"),research["facts"]),"context":self._clean_list(result.get("context"),research["context"]),"why_it_matters":self._clean_text(result.get("why_it_matters")),"what_happens_next":self._clean_text(result.get("what_happens_next")),"what_is_unknown":self._clean_text(result.get("what_is_unknown")),"sources":result.get("sources") if isinstance(result.get("sources"),list) else research["sources"],"seo_title":self._clean_text(result.get("seo_title") or title),"seo_description":self._clean_text(result.get("seo_description") or result.get("dek") or lead)[:320],"slug":self._slug(result.get("slug") or title)}

    def _clean_content(self,text):
        text=str(text or "").strip()
        text=re.sub(r"^```(?:markdown|md|text)?\s*|\s*```$","",text,flags=re.I)
        generic=r"What actually happened\?|The bigger picture|The takeaway|What remains unclear\??|Why is this happening now\?|Who is affected\?|What does this mean\??|What does this mean for ordinary people\?|What happens next\?|What information is still unconfirmed\??|What information is still unclear\??"
        text=re.sub(rf"(?im)^\s*#{1,6}\s*(?:{generic})\s*$","",text)
        text=re.sub(rf"(?im)^\s*(?:{generic})\s*$","",text)
        text=re.sub(r"(?im)^\s*By\s+[A-Za-z][A-Za-z .,'’-]{1,80}\s*$","",text)
        text=re.sub(r"\n{3,}","\n\n",text)
        paragraphs=[]; seen=set()
        for p in re.split(r"\n\s*\n",text):
            p=re.sub(r"\s+"," ",p).strip()
            if not p: continue
            key=re.sub(r"[^a-z0-9]","",p.lower())
            if key in seen: continue
            seen.add(key); paragraphs.append(p)
        return "\n\n".join(paragraphs)

    def _quality_ok(self,article,research):
        content=article.get("content","")
        words=self._word_count(content)
        if words<self.min_words or words>self.max_words+300: return False
        paragraphs=self._paragraphs(content)
        if len(paragraphs)<8 or len(self._sentences(content))<14: return False
        low=content.lower()
        banned=("what actually happened?","what remains unclear?","why is this happening now?","who is affected?","what happens next?","the takeaway","the bigger picture","what information is still unconfirmed?")
        if any(x in low for x in banned): return False
        if len(paragraphs)!=len(set(p.lower() for p in paragraphs)): return False
        if research["facts"] and sum(self._fact_overlap(f,content) for f in research["facts"])<max(1,min(3,len(research["facts"]))): return False
        return True

    def _quality_score(self,article,research):
        words=self._word_count(article.get("content","")); score=50
        if words>=self.min_words: score+=15
        if words>=self.target_words: score+=10
        if len(self._paragraphs(article.get("content","")))>=12: score+=5
        if research["facts"]: score+=10
        if research["sources"]: score+=10
        return min(score,100)

    def _failure(self,status,message,research):
        return {"title":research.get("title",""),"headline":research.get("title",""),"dek":"","lead":"","content":"","key_facts":research.get("facts",[]),"context":research.get("context",[]),"why_it_matters":"","what_happens_next":"","what_is_unknown":message,"sources":research.get("sources",[]),"seo_title":research.get("title",""),"seo_description":"","slug":self._slug(research.get("title","news")),"status":status,"publication_safe":False,"research_grounded":False,"quality_score":0}

    def _structured_text(self,value):
        if value is None: return ""
        if isinstance(value,dict):
            parts=[]
            for k,v in value.items():
                t=self._clean_text(v)
                if t: parts.append(f"{k}: {t}")
            return "; ".join(parts)
        if isinstance(value,list): return "; ".join(self._clean_text(x) for x in value if self._clean_text(x))
        return self._clean_text(value)

    def _clean_list(self,value,fallback):
        if not isinstance(value,list): return fallback[:20]
        out=[]
        for item in value:
            t=self._clean_text(item)
            if t and t not in out: out.append(t)
        return out[:30] or fallback[:20]

    def _unique(self,values):
        out=[];seen=set()
        for v in values:
            t=self._clean_text(v); k=t.lower()
            if t and k not in seen: seen.add(k);out.append(t)
        return out

    def _paragraphs(self,text): return [p.strip() for p in re.split(r"\n\s*\n",text or "") if p.strip()]
    def _sentences(self,text): return [s.strip() for s in re.split(r"(?<=[.!?])\s+",text or "") if len(s.strip())>35]
    def _word_count(self,text): return len(re.findall(r"\b[\w’'-]+\b",text or ""))
    def _fact_overlap(self,fact,content):
        words=set(w.lower() for w in re.findall(r"\b[a-zA-Z]{5,}\b",self._clean_text(fact)))
        return not words or sum(w in content.lower() for w in words)>=max(1,min(3,len(words)))
    def _clean_text(self,value):
        if value is None:return ""
        if isinstance(value,(dict,list)):return json.dumps(value,ensure_ascii=False)
        return re.sub(r"\s+"," ",str(value)).strip()
    def _text(self,value): return self._clean_text(value)
    def _strip_fences(self,text):
        return re.sub(r"^```(?:json)?\s*|\s*```$","",str(text or "").strip(),flags=re.I).strip()
    def _slug(self,value):
        t=self._clean_text(value).lower();t=re.sub(r"[^a-z0-9\s-]","",t);t=re.sub(r"[\s_-]+","-",t).strip("-");return t[:140] or "news-story"

JournalistEngineV4=JournalistEngine
JournalistEngineV3=JournalistEngine
journalist_engine=JournalistEngine()
