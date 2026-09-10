import logging,re
from typing import Any,Dict,List
logger=logging.getLogger("NewsFactory.ArticleEngine")

class ArticleEngine:
    def __init__(self)->None:
        self.name="News Article Production Engine"
        self.version="3.0.0"
        self.max_facts=30
        self.max_context=15
        self.max_consequences=15
        self.max_next_steps=10
        self.max_questions=10
        self.max_sections=20
        self.target_words=1400
        self.minimum_words=650
        self.maximum_words=2000

    def create(self,package:Dict[str,Any])->Dict[str,Any]:
        package=package if isinstance(package,dict) else {}
        existing=self._finished_article(package)
        if existing:
            article=self._normalize_finished(existing,package)
            article["publication_safe"]=self._publication_safe(package)
            return article

        story=package.get("story",{}) or {}
        synthesis=package.get("synthesis",package.get("story_model",{})) or {}
        verification=package.get("verification",{}) or {}
        significance=package.get("significance",{}) or {}
        angles=package.get("angles",{}) or {}
        source_intelligence=package.get("source_intelligence",package.get("source_intel",{})) or {}
        reader_intelligence=package.get("reader_intelligence",{}) or {}
        topic=self._text(package.get("topic",story.get("topic","")))
        title=self._title(story,package.get("headline",{}),synthesis)
        facts=self._facts(package,synthesis,verification)
        context=self._context(package,synthesis)
        consequences=self._consequences(synthesis,significance)
        next_steps=self._next_steps(synthesis,story)
        lead=self._lead(title,facts,story,synthesis)
        body=self._fallback_body(lead,facts,context,consequences,next_steps)
        word_count=self._word_count(body)
        return {
            "status":"ARTICLE_READY",
            "engine":self.name,
            "version":self.version,
            "title":title,
            "headline":title,
            "slug":self._slug(title),
            "topic":topic,
            "category":self._category(story,synthesis,topic),
            "tags":self._tags(package,topic),
            "lead":lead,
            "excerpt":self._excerpt(lead),
            "content":body,
            "body":body,
            "sections":[],
            "key_facts":{"facts":facts},
            "context":context,
            "consequences":consequences,
            "next_steps":next_steps,
            "reader_questions":[],
            "reactions":[],
            "details":[],
            "sources":self._source_links(package),
            "source_count":len(self._source_links(package)),
            "word_count":word_count,
            "long_form":word_count>=self.minimum_words,
            "target_word_count":self.target_words,
            "significance":significance,
            "angle":angles.get("primary_angle",angles.get("recommended_angle",{})),
            "verification":verification,
            "source_intelligence":source_intelligence,
            "reader_intelligence":reader_intelligence,
            "publication_safe":self._publication_safe(package),
            "image_url":self._text(story.get("image_url","")),
            "source_url":self._text(story.get("source_url",package.get("source_url","")))
        }

    def create_article_plan(self,package:Dict[str,Any])->Dict[str,Any]:
        article=self.create(package)
        return {"status":"ARTICLE_PLAN_READY","engine":self.name,"version":self.version,"article":article,"publication_safe":article.get("publication_safe",False)}

    def _finished_article(self,package:Dict[str,Any])->Dict[str,Any]:
        candidates=[
            package.get("article"),
            package.get("journalism"),
        ]
        for candidate in candidates:
            if not isinstance(candidate,dict):
                continue
            nested=candidate.get("article")
            if isinstance(nested,dict):
                candidate=nested
            content=self._text(candidate.get("content",candidate.get("body",candidate.get("text",""))))
            title=self._text(candidate.get("title",candidate.get("headline","")))
            status=self._text(candidate.get("status","")).upper()
            if content and len(content)>=300 and status not in {"FAILED","ERROR","JOURNALISM_FAILED"}:
                return dict(candidate)
            if title and content and len(content)>=300:
                return dict(candidate)
        return {}

    def _normalize_finished(self,article:Dict[str,Any],package:Dict[str,Any])->Dict[str,Any]:
        story=package.get("story",{}) if isinstance(package.get("story",{}),dict) else {}
        title=self._text(article.get("title",article.get("headline",""))) or self._text(story.get("title",story.get("headline",""))) or "Latest News Development"
        content=self._clean_article_content(article.get("content",article.get("body",article.get("text",""))))
        lead=self._text(article.get("lead",article.get("dek","")))
        if not lead:
            lead=self._first_paragraph(content) or title
        sources=article.get("sources",[])
        if not isinstance(sources,list):
            sources=self._source_links(package)
        tags=article.get("tags",[])
        if not isinstance(tags,list):
            tags=self._tags(package,self._text(package.get("topic",story.get("topic",""))))
        word_count=self._word_count(content)
        result=dict(article)
        result.update({
            "status":"ARTICLE_READY",
            "engine":self.name,
            "version":self.version,
            "title":title,
            "headline":self._text(article.get("headline","")) or title,
            "slug":self._text(article.get("slug","")) or self._slug(title),
            "topic":self._text(article.get("topic",package.get("topic",story.get("topic","")))),
            "category":self._text(article.get("category",story.get("category","general"))) or "general",
            "tags":tags,
            "lead":lead,
            "excerpt":self._text(article.get("excerpt",article.get("summary",""))) or self._excerpt(lead),
            "content":content,
            "body":content,
            "sources":sources,
            "source_count":len(sources),
            "word_count":word_count,
            "long_form":word_count>=self.minimum_words,
            "target_word_count":self.target_words,
            "publication_safe":self._publication_safe(package),
            "source_url":self._text(article.get("source_url",story.get("source_url",package.get("source_url",""))))
        })
        return result

    def _clean_article_content(self,text:Any)->str:
        text=self._text(text)
        banned=[
            "What actually happened?",
            "What exactly happened?",
            "Why is this happening now?",
            "Who is affected?",
            "What does this mean for ordinary people?",
            "What happens next?",
            "What information is still unconfirmed?",
            "What remains unclear",
            "The bigger picture",
            "The takeaway",
            "The central development is that"
        ]
        lines=[]
        for line in text.splitlines():
            clean=self._clean_text(line)
            if not clean:
                continue
            if any(clean.lower()==item.lower() for item in banned):
                continue
            lines.append(clean)
        cleaned="\n\n".join(lines)
        cleaned=re.sub(r"\n{3,}","\n\n",cleaned)
        return cleaned.strip()

    def _fallback_body(self,lead,facts,context,consequences,next_steps)->str:
        values=[]
        for group in (lead,facts,context,consequences,next_steps):
            if isinstance(group,list):
                values.extend(group)
            elif group:
                values.append(group)
        return "\n\n".join(self._unique_text(values))

    def _title(self,story,headline,synthesis)->str:
        for value in (
            headline.get("recommended_headline") if isinstance(headline,dict) else "",
            headline.get("headline") if isinstance(headline,dict) else "",
            story.get("headline"),
            story.get("title"),
            synthesis.get("headline") if isinstance(synthesis,dict) else ""
        ):
            value=self._text(value)
            if value:return self._clean_title(value)
        return "Latest News Development"

    def _facts(self,package,synthesis,verification)->List[str]:
        raw=[]
        if isinstance(synthesis,dict):
            for key in ("confirmed_facts","key_facts","important_facts"):
                value=synthesis.get(key,[])
                if isinstance(value,list):raw.extend(value)
        if isinstance(package,dict):
            value=package.get("fact_candidates",[])
            if isinstance(value,list):raw.extend(value)
        if isinstance(verification,dict):
            for key in ("claims","verified_claims"):
                value=verification.get(key,[])
                if isinstance(value,list):raw.extend(value)
        output=[];seen=set()
        for item in raw:
            if isinstance(item,dict):
                text=self._text(item.get("text",item.get("claim",item.get("content",""))))
                status=self._text(item.get("status",item.get("publication_status",""))).upper()
            else:
                text=self._text(item);status=""
            if not text or status in {"CONTRADICTED","DISPUTED","UNVERIFIED","HOLD_FOR_REVIEW"}:
                continue
            key=text.lower()
            if key in seen:continue
            seen.add(key);output.append(text)
            if len(output)>=self.max_facts:break
        return output

    def _lead(self,title,facts,story,synthesis)->str:
        summary=self._text(story.get("summary",story.get("description",""))) if isinstance(story,dict) else ""
        if summary:return summary
        if facts:return facts[0]
        central=self._text(synthesis.get("central_event","")) if isinstance(synthesis,dict) else ""
        return central or title

    def _context(self,package,synthesis)->List[str]:
        values=[]
        for source in (synthesis,package):
            if not isinstance(source,dict):continue
            for key in ("context","background","background_context","historical_context","previous_developments"):
                value=source.get(key)
                if isinstance(value,list):values.extend(value)
                elif value:values.append(value)
        return self._unique_text(values)[:self.max_context]

    def _consequences(self,synthesis,significance)->List[str]:
        values=[]
        for source in (synthesis,significance):
            if not isinstance(source,dict):continue
            for key in ("consequences","implications","impact","potential_impact","why_it_matters","reasons"):
                value=source.get(key)
                if isinstance(value,list):values.extend(value)
                elif value:values.append(value)
        return self._unique_text(values)[:self.max_consequences]

    def _next_steps(self,synthesis,story)->List[str]:
        values=[]
        for source in (synthesis,story):
            if not isinstance(source,dict):continue
            for key in ("next_steps","what_happens_next","future","upcoming","expected_developments"):
                value=source.get(key)
                if isinstance(value,list):values.extend(value)
                elif value:values.append(value)
        return self._unique_text(values)[:self.max_next_steps]

    def _source_links(self,package)->List[Dict[str,str]]:
        sources=package.get("sources",[]) if isinstance(package,dict) else []
        if not isinstance(sources,list):return []
        output=[];seen=set()
        for source in sources:
            if not isinstance(source,dict):continue
            url=self._text(source.get("url",source.get("source_url","")))
            if not re.match(r"^https?://",url) or url in seen:continue
            seen.add(url)
            output.append({"name":self._text(source.get("name",source.get("publisher",""))),"url":url})
        return output

    def _publication_safe(self,package)->bool:
        verification=package.get("verification",{}) if isinstance(package,dict) else {}
        editorial=package.get("editorial",{}) if isinstance(package,dict) else {}
        if not isinstance(verification,dict):verification={}
        if not isinstance(editorial,dict):editorial={}
        status=self._text(verification.get("publication_status",verification.get("status",""))).upper()
        decision=self._text(editorial.get("decision","")).upper()
        errors=editorial.get("errors",[])
        publication_ready=package.get("publication_ready")
        approved={"APPROVED","APPROVED_WITH_WARNINGS"}
        hard_blocks={"BLOCK_PUBLICATION","BLOCKED","FAILED","CONTRADICTED","HIGH_RISK","CRITICAL"}
        if status in hard_blocks:return False
        if publication_ready is False:return False
        if status=="HUMAN_REVIEW_REQUIRED" and decision not in approved:return False
        if isinstance(errors,list) and errors:return False
        if decision and decision not in approved:return False
        if editorial.get("publication_gate") is False and decision not in approved:return False
        return True

    def _category(self,story,synthesis,topic)->str:
        value=self._text(story.get("category",story.get("story_type",synthesis.get("story_type","general"))))
        return value.lower().replace(" ","-") if value else "general"

    def _tags(self,package,topic)->List[str]:
        values=[]
        if topic:
            values+=re.findall(r"\b[a-zA-Z][a-zA-Z0-9'-]{2,}\b",topic.lower())
        story=package.get("story",{}) if isinstance(package,dict) else {}
        entities=story.get("entities",{}) if isinstance(story,dict) else {}
        if isinstance(entities,dict):
            for key in ("people","organizations","locations","topics"):
                value=entities.get(key,[])
                if isinstance(value,list):values+=value
        return self._unique_text(values)[:15]

    def _slug(self,title)->str:
        slug=self._text(title).lower()
        slug=re.sub(r"[^a-z0-9\s-]","",slug)
        return re.sub(r"[\s-]+","-",slug).strip("-")[:100]

    def _excerpt(self,text)->str:
        text=self._clean_text(text)
        if len(text)<=260:return text
        return text[:260].rsplit(" ",1)[0]+"..."

    def _clean_title(self,text)->str:
        return self._clean_text(text)[:140]

    def _clean_text(self,text:Any)->str:
        return re.sub(r"\s+"," ",self._text(text)).strip()

    def _text(self,value:Any)->str:
        if value is None:return ""
        if isinstance(value,dict):
            return self._clean_text(value.get("text",value.get("content",value.get("title",""))))
        if isinstance(value,list):
            return self._clean_text(" ".join(str(item) for item in value))
        return str(value).strip()

    def _first_paragraph(self,text)->str:
        parts=[self._clean_text(x) for x in text.split("\n\n") if self._clean_text(x)]
        return parts[0] if parts else ""

    def _word_count(self,text)->int:
        return len(re.findall(r"\b[\w'-]+\b",re.sub(r"#{1,6}\s*","",text or "")))

    def _unique_text(self,values)->List[str]:
        output=[];seen=set()
        for value in values:
            text=self._clean_text(value)
            if not text:continue
            key=text.lower()
            if key in seen:continue
            seen.add(key);output.append(text)
        return output

    def status(self)->Dict[str,str]:
        return {"engine":self.name,"version":self.version,"status":"READY"}

article_engine=ArticleEngine()

def create_article(package:Dict[str,Any])->Dict[str,Any]:
    return article_engine.create(package)

def create_article_plan(package:Dict[str,Any])->Dict[str,Any]:
    return article_engine.create_article_plan(package)

if __name__=="__main__":
    test={
        "story":{"title":"Officials announce a new development","summary":"Officials announced a new development that could have wider consequences for the public.","category":"general"},
        "journalism":{
            "status":"JOURNALISM_COMPLETE",
            "title":"Officials announce a new development",
            "content":"Officials announced a new development that could have wider consequences for the public. The development follows earlier discussions and is now being closely watched."
        },
        "verification":{"publication_status":"VERIFIED"},
        "publication_ready":True
    }
    print(create_article(test))
