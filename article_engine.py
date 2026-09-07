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
