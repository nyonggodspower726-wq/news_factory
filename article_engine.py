import logging,re
from typing import Any,Dict,List
logger=logging.getLogger("NewsFactory.ArticleEngine")

class ArticleEngine:
    def __init__(self)->None:
        self.name="News Article Production Engine"
        self.version="2.0.0"
        self.max_facts=30
        self.max_context=15
        self.max_consequences=15
        self.max_next_steps=10
        self.max_questions=10
        self.max_sections=12
        self.target_words=1600
        self.minimum_words=900

    def create(self,package:Dict[str,Any])->Dict[str,Any]:
        package=package if isinstance(package,dict) else {}
        story=package.get("story",{}) or {}
        synthesis=package.get("synthesis",package.get("story_model",{})) or {}
        verification=package.get("verification",{}) or {}
        significance=package.get("significance",{}) or {}
        angles=package.get("angles",{}) or {}
        headline=package.get("headline",{}) or {}
        source_intelligence=package.get("source_intelligence",package.get("source_intel",{})) or {}
        reader_intelligence=package.get("reader_intelligence",{}) or {}
        topic=self._text(package.get("topic",story.get("topic","")))
        title=self._title(story,headline,synthesis)
        facts=self._facts(package,synthesis,verification)
        context=self._context(package,synthesis)
        consequences=self._consequences(synthesis,significance)
        next_steps=self._next_steps(synthesis,story)
        questions=self._questions(synthesis,story)
        reactions=self._reactions(package,story,synthesis)
        details=self._details(package,story,synthesis)
        sources=self._source_links(package)
        lead=self._lead(title,facts,story,synthesis)
        sections=self._sections(title,lead,facts,context,consequences,next_steps,questions,reactions,details,significance,angles,source_intelligence,reader_intelligence)
        body=self._body(sections)
        body=self._ensure_depth(body,facts,context,consequences,next_steps,reactions,details,significance)
        excerpt=self._excerpt(lead)
        category=self._category(story,synthesis,topic)
        tags=self._tags(package,topic)
        publication_safe=self._publication_safe(package)
        word_count=len(re.findall(r"\b[\w'-]+\b",re.sub(r"#{1,6}\s*","",body)))
        return {
            "status":"ARTICLE_READY",
            "engine":self.name,
            "version":self.version,
            "title":title,
            "headline":title,
            "slug":self._slug(title),
            "topic":topic,
            "category":category,
            "tags":tags,
            "lead":lead,
            "excerpt":excerpt,
            "content":body,
            "body":body,
            "sections":sections,
            "key_facts":{"facts":facts},
            "context":context,
            "consequences":consequences,
            "next_steps":next_steps,
            "reader_questions":questions,
            "reactions":reactions,
            "details":details,
            "sources":sources,
            "source_count":len(sources),
            "word_count":word_count,
            "long_form":word_count>=self.minimum_words,
            "target_word_count":self.target_words,
            "significance":significance,
            "angle":angles.get("primary_angle",angles.get("recommended_angle",{})),
            "verification":verification,
            "source_intelligence":source_intelligence,
            "reader_intelligence":reader_intelligence,
            "publication_safe":publication_safe,
            "image_url":self._text(story.get("image_url","")),
            "source_url":self._text(story.get("source_url",""))
        }

    def create_article_plan(self,package:Dict[str,Any])->Dict[str,Any]:
        article=self.create(package)
        return {"status":"ARTICLE_PLAN_READY","engine":self.name,"version":self.version,"article":article,"publication_safe":article.get("publication_safe",False)}

    def _title(self,story:Dict[str,Any],headline:Dict[str,Any],synthesis:Dict[str,Any])->str:
        for value in (headline.get("recommended_headline"),headline.get("headline"),story.get("headline"),story.get("title"),synthesis.get("headline")):
            value=self._text(value)
            if value:return self._clean_title(value)
        return "Latest News Development"

    def _facts(self,package:Dict[str,Any],synthesis:Dict[str,Any],verification:Dict[str,Any])->List[str]:
        raw=[]
        if isinstance(synthesis,dict):
            raw.extend(synthesis.get("confirmed_facts",[]))
            raw.extend(synthesis.get("key_facts",[]))
            raw.extend(synthesis.get("important_facts",[]))
        if isinstance(package,dict):raw.extend(package.get("fact_candidates",[]))
        if isinstance(verification,dict):
            raw.extend(verification.get("claims",[]))
            raw.extend(verification.get("verified_claims",[]))
        facts=[];seen=set()
        for item in raw:
            text="";status=""
            if isinstance(item,dict):
                text=self._text(item.get("text",item.get("claim",item.get("content",""))))
                status=self._text(item.get("status",item.get("publication_status",""))).upper()
            else:text=self._text(item)
            if not text:continue
            key=text.lower()
            if key in seen or status in {"CONTRADICTED","DISPUTED","UNVERIFIED","HOLD_FOR_REVIEW"}:continue
            seen.add(key);facts.append(text)
            if len(facts)>=self.max_facts:break
        return facts

    def _lead(self,title:str,facts:List[str],story:Dict[str,Any],synthesis:Dict[str,Any])->str:
        summary=self._text(story.get("summary",story.get("description",synthesis.get("central_event",""))))
        if summary and len(summary)>=80:return summary
        if facts:return facts[0]
        central=self._text(synthesis.get("central_event",""))
        return central or title

    def _context(self,package:Dict[str,Any],synthesis:Dict[str,Any])->List[str]:
        values=[]
        for source in (synthesis,package):
            if not isinstance(source,dict):continue
            for key in ("context","background","background_context","historical_context","previous_developments"):
                value=source.get(key)
                if isinstance(value,list):values.extend(value)
                elif value:values.append(value)
        return self._unique_text(values)[:self.max_context]

    def _consequences(self,synthesis:Dict[str,Any],significance:Dict[str,Any])->List[str]:
        values=[]
        if isinstance(synthesis,dict):
            for key in ("consequences","implications","impact","potential_impact","why_it_matters"):
                value=synthesis.get(key)
                if isinstance(value,list):values.extend(value)
                elif value:values.append(value)
        if isinstance(significance,dict):
            for key in ("reasons","implications","impact","why_it_matters"):
                value=significance.get(key)
                if isinstance(value,list):values.extend(value)
                elif value:values.append(value)
        return self._unique_text(values)[:self.max_consequences]

    def _next_steps(self,synthesis:Dict[str,Any],story:Dict[str,Any])->List[str]:
        values=[]
        for source in (synthesis,story):
            if not isinstance(source,dict):continue
            for key in ("next_steps","what_happens_next","future","upcoming","expected_developments"):
                value=source.get(key)
                if isinstance(value,list):values.extend(value)
                elif value:values.append(value)
        return self._unique_text(values)[:self.max_next_steps]

    def _questions(self,synthesis:Dict[str,Any],story:Dict[str,Any])->List[str]:
        values=[]
        for source in (synthesis,story):
            if not isinstance(source,dict):continue
            for key in ("unknowns","questions","open_questions","reader_questions","information_gaps"):
                value=source.get(key)
                if isinstance(value,list):values.extend(value)
                elif value:values.append(value)
        return self._unique_text(values)[:self.max_questions]

    def _reactions(self,package:Dict[str,Any],story:Dict[str,Any],synthesis:Dict[str,Any])->List[str]:
        values=[]
        for source in (package,story,synthesis):
            if not isinstance(source,dict):continue
            for key in ("reactions","quotes","statements","official_reactions","responses","comments"):
                value=source.get(key)
                if isinstance(value,list):values.extend(value)
                elif value:values.append(value)
        return self._unique_text(values)[:10]

    def _details(self,package:Dict[str,Any],story:Dict[str,Any],synthesis:Dict[str,Any])->List[str]:
        values=[]
        for source in (package,story,synthesis):
            if not isinstance(source,dict):continue
            for key in ("details","key_details","additional_details","evidence","reported_details","supporting_information"):
                value=source.get(key)
                if isinstance(value,list):values.extend(value)
                elif value:values.append(value)
        return self._unique_text(values)[:15]

    def _sections(self,title:str,lead:str,facts:List[str],context:List[str],consequences:List[str],next_steps:List[str],questions:List[str],reactions:List[str],details:List[str],significance:Dict[str,Any],angles:Dict[str,Any],source_intelligence:Dict[str,Any],reader_intelligence:Dict[str,Any])->List[Dict[str,Any]]:
        sections=[{"heading":"What happened","content":self._paragraphize([lead]+facts[:8])}]
        if details:sections.append({"heading":"The details behind the story","content":self._paragraphize(details)})
        if context:sections.append({"heading":"The background","content":self._paragraphize(context)})
        if reactions:sections.append({"heading":"What people involved are saying","content":self._paragraphize(reactions)})
        if consequences:sections.append({"heading":"Why this matters","content":self._paragraphize(consequences)})
        angle_text=self._extract_angle(angles)
        if angle_text:sections.append({"heading":"The bigger picture","content":self._paragraphize([angle_text])})
        significance_text=self._extract_significance(significance)
        if significance_text:sections.append({"heading":"What this could mean","content":self._paragraphize([significance_text])})
        if next_steps:sections.append({"heading":"What happens next","content":self._paragraphize(next_steps)})
        if questions:sections.append({"heading":"What remains unclear","content":self._paragraphize(questions)})
        source_text=self._extract_source_intelligence(source_intelligence)
        if source_text:sections.append({"heading":"What the available reporting shows","content":self._paragraphize([source_text])})
        reader_text=self._extract_reader_value(reader_intelligence)
        if reader_text:sections.append({"heading":"Why readers should keep watching","content":self._paragraphize([reader_text])})
        sections.append({"heading":"The takeaway","content":self._paragraphize([self._takeaway(title,facts,consequences,next_steps)])})
        return sections[:self.max_sections]

    def _paragraphize(self,values:List[Any])->List[str]:
        output=[]
        for value in values:
            text=self._clean_text(value)
            if not text:continue
            sentences=re.split(r"(?<=[.!?])\s+",text)
            if len(sentences)<=3:
                output.append(text);continue
            chunks=[];current=[]
            for sentence in sentences:
                current.append(sentence)
                if len(" ".join(current))>=260:
                    chunks.append(" ".join(current));current=[]
            if current:chunks.append(" ".join(current))
            output.extend(chunks)
        return self._unique_text(output)

    def _body(self,sections:List[Dict[str,Any]])->str:
        paragraphs=[]
        for section in sections:
            heading=self._text(section.get("heading"))
            content=section.get("content",[])
            if not heading or not content:continue
            paragraphs.append(f"## {heading}")
            if not isinstance(content,list):content=[content]
            for item in content:
                text=self._clean_text(item)
                if text:paragraphs.append(text)
        return "\n\n".join(paragraphs)

# === PART 1 ENDS HERE ===
    def _ensure_depth(self,body:str,facts:List[str],context:List[str],consequences:List[str],next_steps:List[str],reactions:List[str],details:List[str],significance:Dict[str,Any])->str:
        words=len(re.findall(r"\b[\w'-]+\b",body))
        if words>=self.minimum_words:return body
        values=details+context+consequences+reactions+next_steps
        text=self._extract_significance(significance)
        if text:values.append(text)
        additions=self._paragraphize(values)
        extra=[];existing=body.lower()
        for item in additions:
            if item.lower() in existing:continue
            extra.append(item)
            if len(re.findall(r"\b[\w'-]+\b"," ".join(extra)))>=600:break
        if not extra:return body
        return body+"\n\n## More context\n\n"+"\n\n".join(extra)

    def _extract_angle(self,angles:Dict[str,Any])->str:
        if not isinstance(angles,dict):return ""
        for key in ("primary_angle","recommended_angle","main_angle","angle","description"):
            text=self._text(angles.get(key))
            if text:return text
        return ""

    def _extract_significance(self,significance:Dict[str,Any])->str:
        if not isinstance(significance,dict):return ""
        values=[]
        for key in ("summary","assessment","analysis","importance","why_it_matters","impact"):
            value=significance.get(key)
            if isinstance(value,list):values.extend(value)
            elif value:values.append(value)
        return " ".join(self._unique_text(values)[:5])

    def _extract_source_intelligence(self,data:Dict[str,Any])->str:
        if not isinstance(data,dict):return ""
        values=[]
        for key in ("overall_quality","recommendation","source_quality","corroboration","independence"):
            value=data.get(key)
            if isinstance(value,list):values.extend(value)
            elif value:values.append(value)
        return " ".join(self._unique_text(values)[:4])

    def _extract_reader_value(self,data:Dict[str,Any])->str:
        if not isinstance(data,dict):return ""
        values=[]
        for key in ("reader_value","engagement_reason","audience_interest","reader_relevance"):
            value=data.get(key)
            if isinstance(value,list):values.extend(value)
            elif value:values.append(value)
        return " ".join(self._unique_text(values)[:3])

    def _takeaway(self,title:str,facts:List[str],consequences:List[str],next_steps:List[str])->str:
        parts=[]
        if facts:parts.append(f"The central development is that {self._lower_first(facts[0])}")
        if consequences:parts.append(f"The wider significance will depend on how the situation develops, particularly around {self._lower_first(consequences[0])}")
        if next_steps:parts.append(f"The next development to watch is {self._lower_first(next_steps[0])}")
        return " ".join(parts) if parts else title

    def _source_links(self,package:Dict[str,Any])->List[Dict[str,str]]:
        sources=package.get("sources",[]) if isinstance(package,dict) else []
        if not isinstance(sources,list):return []
        output=[];seen=set()
        for source in sources:
            if not isinstance(source,dict):continue
            url=self._text(source.get("url",source.get("source_url","")))
            if not url or not re.match(r"^https?://",url) or url in seen:continue
            seen.add(url)
            output.append({"name":self._text(source.get("name",source.get("publisher",""))),"url":url})
        return output

    def _publication_safe(self,package:Dict[str,Any])->bool:
        verification=package.get("verification",{}) if isinstance(package,dict) else {}
        editorial=package.get("editorial",{}) if isinstance(package,dict) else {}
        if not isinstance(verification,dict):verification={}
        if not isinstance(editorial,dict):editorial={}
        editorial_gate=editorial.get("publication_gate")
        decision=self._text(editorial.get("decision","")).upper()
        errors=editorial.get("errors",[])
        publication_ready=package.get("publication_ready")
        status=self._text(verification.get("publication_status",verification.get("status",""))).upper()
        approved={"APPROVED","APPROVED_WITH_WARNINGS"}
        hard_blocks={"BLOCK_PUBLICATION","BLOCKED","FAILED","CONTRADICTED","HIGH_RISK","CRITICAL"}
        has_errors=bool(errors)
        editorial_approved=decision in approved and not has_errors
        logger.info("PUBLICATION GATE CHECK | verification=%s | editorial_gate=%s | decision=%s | errors=%s | publication_ready=%s",status,editorial_gate,decision,len(errors) if isinstance(errors,list) else bool(errors),publication_ready)
        if status in hard_blocks:
            logger.warning("PUBLICATION BLOCKED | reason=VERIFICATION_%s",status)
            return False
        if publication_ready is False:
            logger.warning("PUBLICATION BLOCKED | reason=PUBLICATION_READY_FALSE")
            return False
        if status=="HUMAN_REVIEW_REQUIRED":
            if not editorial_approved:
                logger.warning("PUBLICATION BLOCKED | reason=HUMAN_REVIEW_REQUIRED_WITHOUT_EDITOR_APPROVAL")
                return False
            logger.info("PUBLICATION REVIEW ACCEPTED | editor_decision=%s",decision)
        if editorial_gate is False and not editorial_approved:
            logger.warning("PUBLICATION BLOCKED | reason=EDITORIAL_GATE_FALSE")
            return False
        if has_errors:
            logger.warning("PUBLICATION BLOCKED | reason=EDITORIAL_ERRORS")
            return False
        if decision and decision not in approved:
            logger.warning("PUBLICATION BLOCKED | reason=EDITORIAL_DECISION_%s",decision)
            return False
        logger.info("PUBLICATION GATE PASSED | verification=%s | decision=%s",status,decision)
        return True

    def _category(self,story:Dict[str,Any],synthesis:Dict[str,Any],topic:str)->str:
        value=self._text(story.get("category",story.get("story_type",synthesis.get("story_type","general"))))
        return value.lower().replace(" ","-") if value else "general"

    def _tags(self,package:Dict[str,Any],topic:str)->List[str]:
        values=[]
        if topic:values+=re.findall(r"\b[a-zA-Z][a-zA-Z0-9'-]{2,}\b",topic.lower())
        story=package.get("story",{}) if isinstance(package,dict) else {}
        entities=story.get("entities",{}) if isinstance(story,dict) else {}
        if isinstance(entities,dict):
            for key in ("people","organizations","locations","topics"):
                value=entities.get(key,[])
                if isinstance(value,list):values+=value
        return self._unique_text(values)[:15]

    def _slug(self,title:str)->str:
        slug=self._text(title).lower()
        slug=re.sub(r"[^a-z0-9\s-]","",slug)
        slug=re.sub(r"[\s-]+","-",slug).strip("-")
        return slug[:100]

    def _excerpt(self,text:str)->str:
        text=self._clean_text(text)
        if len(text)<=260:return text
        return text[:260].rsplit(" ",1)[0]+"..."

    def _clean_title(self,text:str)->str:
        return self._clean_text(text)[:140]

    def _clean_text(self,text:Any)->str:
        return re.sub(r"\s+"," ",self._text(text)).strip()

    def _text(self,value:Any)->str:
        if value is None:return ""
        if isinstance(value,dict):
            return self._clean_text(value.get("text",value.get("content",value.get("title",""))))
        if isinstance(value,list):return self._clean_text(" ".join(str(item) for item in value))
        return str(value).strip()

    def _lower_first(self,text:str)->str:
        text=self._clean_text(text)
        return text[0].lower()+text[1:] if text else text

    def _unique_text(self,values:List[Any])->List[str]:
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
        "synthesis":{
            "confirmed_facts":["Officials announced a new development.","The announcement follows earlier discussions."],
            "context":["The issue has attracted attention because of its potential impact."],
            "consequences":["The development could affect people directly involved in the situation."],
            "next_steps":["Officials are expected to provide additional information."]
        },
        "verification":{},
        "significance":{"reasons":["The development may affect the public."]},
        "publication_ready":True
    }
    result=create_article(test)
    print(result)
