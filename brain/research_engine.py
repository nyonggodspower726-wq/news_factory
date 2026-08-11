from typing import Any,Dict,List
from collections import Counter
from urllib.parse import urlparse
import re

class ResearchEngine:
    def __init__(self):
        self.name="Research Intelligence Engine"
        self.version="1.1.0"
        self.stop_words={"about","after","again","against","being","between","could","first","from","have","into","more","other","said","says","some","than","that","their","there","these","they","this","those","through","under","were","which","while","with","would","where","when","what","will","your"}
        self.important_terms={"killed","dead","injured","arrested","missing","election","government","president","minister","court","police","company","attack","crash","fire","explosion","flood","earthquake","storm","warning","decision","announced","approved","banned","released","resigned","elected"}

    def research(self,sources:List[Dict[str,Any]],topic:str="",event:Dict[str,Any]=None)->Dict[str,Any]:
        sources=self._normalize_sources(sources)
        event=event if isinstance(event,dict) else {}
        records=[self._process_source(s) for s in sources]
        corpus=self._build_corpus(records)
        entities=self._extract_entities(corpus)
        facts=self._extract_fact_candidates(records)
        claims=self._extract_claim_candidates(records)
        gaps=self._identify_research_gaps(records,claims,facts)
        contradictions=self._detect_internal_conflicts(records,claims)
        duplicates=self._detect_duplicates(records)
        timeline=self._build_timeline(records)
        source_map=self._build_source_map(records)
        priority=self._calculate_research_priority(topic,records,claims,contradictions)
        return {
            "engine":self.name,
            "version":self.version,
            "status":"RESEARCH_COMPLETE",
            "topic":topic,
            "event":event,
            "source_count":len(records),
            "sources":records,
            "corpus":corpus,
            "entities":entities,
            "fact_candidates":facts,
            "claim_candidates":claims,
            "research_gaps":gaps,
            "contradictions":contradictions,
            "duplicates":duplicates,
            "timeline":timeline,
            "source_map":source_map,
            "research_priority":priority
        }

    def _normalize_sources(self,sources)->List[Dict[str,Any]]:
        if isinstance(sources,dict):
            sources=list(sources.values())
        if not isinstance(sources,list):
            return []
        out=[]
        for i,source in enumerate(sources):
            if isinstance(source,str):
                source={"content":source}
            if not isinstance(source,dict):
                continue
            out.append({
                "source_id":source.get("source_id",source.get("id",f"research_source_{i+1}")),
                "name":source.get("name",source.get("publisher","")),
                "url":source.get("url",""),
                "type":source.get("type",source.get("source_type","unknown")),
                "title":source.get("title",source.get("headline","")),
                "content":source.get("content",source.get("text",source.get("body",""))),
                "author":source.get("author",""),
                "published_at":source.get("published_at"),
                "updated_at":source.get("updated_at"),
                "verified":source.get("verified",False),
                "primary":source.get("primary",False),
                "original_source":source.get("original_source","")
            })
        return out

    def _process_source(self,source):
        title=str(source.get("title","")).strip()
        content=str(source.get("content","")).strip()
        combined=(title+" "+content).strip()
        sentences=self._split_sentences(content)
        keywords=self._extract_keywords(combined)
        return {
            "source_id":source.get("source_id"),
            "name":source.get("name"),
            "domain":self._domain(source.get("url","")),
            "type":source.get("type"),
            "title":title,
            "content":content,
            "author":source.get("author"),
            "published_at":source.get("published_at"),
            "updated_at":source.get("updated_at"),
            "verified":source.get("verified",False),
            "primary":source.get("primary",False),
            "original_source":source.get("original_source",""),
            "word_count":len(content.split()),
            "sentence_count":len(sentences),
            "keywords":keywords,
            "importance_terms":[w for w in keywords if w in self.important_terms]
        }

    def _build_corpus(self,sources):
        titles=[s["title"] for s in sources if s.get("title")]
        texts=[s["content"] for s in sources if s.get("content")]
        words=[]
        for s in sources:
            words.extend(s.get("keywords",[]))
        freq=Counter(words)
        return {
            "titles":titles,
            "combined_text":"\n\n".join(texts),
            "top_keywords":[{"keyword":w,"frequency":n} for w,n in freq.most_common(30)],
            "total_words":sum(len(x.split()) for x in texts)
        }

    def _extract_keywords(self,text):
        words=re.findall(r"\b[a-zA-Z][a-zA-Z0-9'-]{3,}\b",text.lower())
        cleaned=[]
        for word in words:
            word=word.strip("'-")
            if word in self.stop_words or word.isdigit():
                continue
            cleaned.append(word)
        return [w for w,_ in Counter(cleaned).most_common(50)]

    def _extract_entities(self,corpus):
        text=str(corpus.get("combined_text",""))
        people=set()
        organizations=set()
        locations=set()
        names=re.findall(r"\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){1,2}\b",text)
        for item in names:
            if len(item.split())>=2:
                people.add(item.strip())
        markers=["Inc","Ltd","Corporation","Company","Government","Ministry","Agency","University","Bank","Court","Police"]
        for marker in markers:
            pattern=rf"\b[A-Z][A-Za-z0-9&'-]*(?:\s+[A-Z][A-Za-z0-9&'-]*){{0,4}}\s+{marker}\b"
            for match in re.findall(pattern,text):
                organizations.add(match.strip())
        known=["Nigeria","United States","United Kingdom","Ghana","Kenya","South Africa","Lagos","Abuja","London","New York","Washington","Accra"]
        low=text.lower()
        for location in known:
            if location.lower() in low:
                locations.add(location)
        return {"people":sorted(people),"organizations":sorted(organizations),"locations":sorted(locations)}

    def _extract_fact_candidates(self,sources):
        facts=[]
        patterns=[
            r"\b\d+(?:\.\d+)?%\b",
            r"\b\d{1,3}(?:,\d{3})+\b",
            r"\b\d+\s+(?:people|persons|students|workers|victims|days|years)\b",
            r"\b(?:on|in|at)\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b"
        ]
        for source in sources:
            for sentence in self._split_sentences(source.get("content","")):
                if any(re.search(p,sentence,re.I) for p in patterns):
                    facts.append({
                        "source_id":source.get("source_id"),
                        "text":sentence.strip(),
                        "type":"specific_fact_candidate"
                    })
        return facts[:100]

    def _extract_claim_candidates(self,sources):
        claims=[]
        markers=["said","announced","reported","confirmed","claimed","alleged","according to","stated","warned","revealed","denied","disputed"]
        for source in sources:
            for sentence in self._split_sentences(source.get("content","")):
                low=sentence.lower()
                if any(m in low for m in markers):
                    claims.append({
                        "claim_id":f"claim_{len(claims)+1}",
                        "text":sentence.strip(),
                        "source_id":source.get("source_id"),
                        "source_name":source.get("name"),
                        "claim_type":self._claim_type(low),
                        "requires_verification":True
                    })
        return claims[:150]

    def _claim_type(self,text):
        if any(w in text for w in {"denied","disputed","false","incorrect"}):
            return "disputed_claim"
        if any(w in text for w in {"alleged","allegedly"}):
            return "allegation"
        if any(w in text for w in {"confirmed","officially"}):
            return "confirmed_claim"
        if any(w in text for w in {"reported","according to","said","stated"}):
            return "reported_claim"
        if any(w in text for w in {"warned","warning"}):
            return "warning"
        if any(w in text for w in {"announced","revealed"}):
            return "announcement"
        if any(w in text for w in {"claimed"}):
            return "claim"
        return "general_claim"

    def _identify_research_gaps(self,sources,claims,facts):
        gaps=[]
        if not sources:
            gaps.append({"type":"missing_sources","question":"No sources were provided."})
            return gaps
        if len(sources)==1:
            gaps.append({"type":"independent_confirmation","question":"Can this information be confirmed by an independent source?"})
        if not any(s.get("verified") for s in sources):
            gaps.append({"type":"verification","question":"Which important claims have independent verification?"})
        if not facts:
            gaps.append({"type":"specific_facts","question":"What concrete numbers, dates, locations or measurable facts are available?"})
        if claims:
            gaps.append({"type":"claim_verification","question":"Which reported claims require confirmation?"})
        return gaps

    def _detect_internal_conflicts(self,sources,claims):
        conflicts=[]
        by_key={}
        for claim in claims:
            text=claim.get("text","")
            key=self._claim_key(text)
            by_key.setdefault(key,[]).append(claim)
        for key,items in by_key.items():
            types={x.get("claim_type") for x in items}
            if len(items)>1 and "disputed_claim" in types:
                conflicts.append({
                    "topic":key,
                    "claims":items,
                    "reason":"Related claims include disputed information."
                })
        return conflicts[:50]

    def _detect_duplicates(self,sources):
        duplicates=[]
        seen={}
        for source in sources:
            text=self._normalize_text(source.get("content",""))
            if not text:
                continue
            key=text[:300]
            if key in seen:
                duplicates.append({
                    "source_ids":[seen[key],source.get("source_id")],
                    "reason":"Sources contain highly similar opening content."
                })
            else:
                seen[key]=source.get("source_id")
        return duplicates

    def _build_timeline(self,sources):
        timeline=[]
        for source in sources:
            date=source.get("published_at") or source.get("updated_at")
            if date:
                timeline.append({
                    "date":date,
                    "source_id":source.get("source_id"),
                    "title":source.get("title","")
                })
        return sorted(timeline,key=lambda x:str(x.get("date","")))

    def _build_source_map(self,sources):
        result={}
        for source in sources:
            sid=source.get("source_id")
            result[sid]={
                "name":source.get("name"),
                "domain":source.get("domain"),
                "type":source.get("type"),
                "verified":source.get("verified",False),
                "primary":source.get("primary",False),
                "url":source.get("url","")
            }
        return result

    def _calculate_research_priority(self,topic,sources,claims,contradictions):
        score=0
        if topic:
            score+=10
        score+=min(len(sources)*5,30)
        score+=min(len(claims)*2,20)
        score+=min(len(contradictions)*10,30)
        if any(s.get("primary") for s in sources):
            score+=10
        score=min(score,100)
        if score>=70:
            level="HIGH"
        elif score>=40:
            level="MEDIUM"
        else:
            level="LOW"
        return {
            "score":score,
            "level":level,
            "reason":"Priority based on source volume, claims, contradictions, primary-source availability and topic context."
        }

    def _split_sentences(self,text):
        if not text:
            return []
        text=re.sub(r"\s+"," ",str(text)).strip()
        return [x.strip() for x in re.split(r"(?<=[.!?])\s+",text) if x.strip()]

    def _domain(self,url):
        try:
            parsed=urlparse(str(url))
            host=parsed.netloc.lower()
            return host[4:] if host.startswith("www.") else host
        except Exception:
            return ""

    def _normalize_text(self,text):
        return re.sub(r"\s+"," ",str(text).lower()).strip()

    def _claim_key(self,text):
        words=re.findall(r"\b[a-z]{4,}\b",str(text).lower())
        words=[w for w in words if w not in self.stop_words]
        return " ".join(words[:12])

    def __repr__(self):
        return f"<{self.name} v{self.version}>"
