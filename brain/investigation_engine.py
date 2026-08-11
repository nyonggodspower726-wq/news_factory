from typing import Any,Dict,List
import re

class InvestigationEngine:
    def __init__(self):
        self.name="Investigation Intelligence Engine"
        self.version="1.0.0"
        self.high_risk_terms={"alleged","allegedly","accused","accusation","corruption","fraud","scam","murder","killed","abuse","assault","terrorist","terrorism","criminal","stolen","bribery","sexual","exploit","illegal","ban","banned","arrested","resigned","impeached"}
        self.high_impact_terms={"president","government","election","minister","court","police","military","bank","economy","market","currency","crisis","war","attack","earthquake","flood","explosion","pandemic"}
        self.question_patterns=["why","how","what happened","who","when","where","whether","is it true","did","will"]

    def investigate(self,story:Dict[str,Any]=None,research:Dict[str,Any]=None,claims:List[Dict[str,Any]]=None,sources:List[Dict[str,Any]]=None)->Dict[str,Any]:
        story=story if isinstance(story,dict) else {}
        research=research if isinstance(research,dict) else {}
        claims=claims if isinstance(claims,list) else research.get("claim_candidates",[])
        sources=sources if isinstance(sources,list) else research.get("sources",[])
        signals=self._collect_signals(story,research,claims,sources)
        score=self._investigation_score(signals)
        level=self._level(score)
        questions=self._questions(story,research,claims,signals)
        actions=self._actions(level,signals,questions)
        priorities=self._priorities(claims,signals)
        return {
            "engine":self.name,
            "version":self.version,
            "status":"INVESTIGATION_ASSESSMENT_COMPLETE",
            "investigation_score":score,
            "investigation_level":level,
            "signals":signals,
            "critical_questions":questions,
            "recommended_actions":actions,
            "claim_priorities":priorities,
            "publication_recommendation":self._publication_recommendation(level)
        }

    def _collect_signals(self,story,research,claims,sources):
        contradictions=research.get("contradictions",[])
        gaps=research.get("research_gaps",[])
        duplicates=research.get("duplicates",[])
        primary=sum(1 for s in sources if isinstance(s,dict) and s.get("primary"))
        allegations=0;unsupported=0
        for claim in claims:
            if not isinstance(claim,dict):continue
            text=str(claim.get("text","")).lower()
            if any(x in text for x in {"alleged","allegedly","accused","accusation"}):allegations+=1
            if claim.get("requires_verification",False):unsupported+=1
        story_text=" ".join(str(story.get(k,"")) for k in ("title","topic","description","content","summary")).lower()
        return {
            "source_count":len(sources),
            "primary_source_count":primary,
            "contradiction_count":len(contradictions),
            "research_gap_count":len(gaps),
            "duplicate_group_count":len(duplicates),
            "allegation_count":allegations,
            "verification_required_count":unsupported,
            "high_risk_topic":self._contains_terms(story_text,self.high_risk_terms),
            "high_impact_topic":self._contains_terms(story_text,self.high_impact_terms),
            "breaking_story":bool(story.get("breaking") or story.get("is_breaking")),
            "rapidly_changing":bool(story.get("developing") or story.get("rapidly_changing"))
        }

    def _investigation_score(self,signals):
        score=0
        score+=min(signals.get("contradiction_count",0)*15,35)
        score+=min(signals.get("research_gap_count",0)*5,20)
        score+=min(signals.get("allegation_count",0)*10,25)
        verification=signals.get("verification_required_count",0)
        score+=15 if verification>=5 else 8 if verification>=2 else 0
        score+=min(signals.get("duplicate_group_count",0)*5,15)
        if signals.get("primary_source_count",0)==0:score+=15
        if signals.get("high_risk_topic"):score+=20
        if signals.get("high_impact_topic"):score+=15
        if signals.get("breaking_story"):score+=10
        if signals.get("rapidly_changing"):score+=15
        return min(100,score)

    def _level(self,score):
        if score>=80:return "URGENT"
        if score>=60:return "DEEP"
        if score>=35:return "STANDARD"
        if score>=15:return "LIGHT"
        return "NONE"

    def _questions(self,story,research,claims,signals):
        questions=[str(x) for x in research.get("research_gaps",[]) if x]
        if signals.get("primary_source_count",0)==0:
            questions.append("Can the original or primary source of the information be located?")
        if signals.get("contradiction_count",0)>0:
            questions.extend(["Which conflicting account is supported by stronger evidence?","Are the conflicting reports actually independent?"])
        if signals.get("duplicate_group_count",0)>0:
            questions.append("Are multiple reports independently confirmed or merely repeating the same original report?")
        if signals.get("allegation_count",0)>0:
            questions.extend(["What evidence exists for each allegation?","Has the person or organization named in the allegation responded?"])
        if signals.get("rapidly_changing",False):
            questions.append("What is confirmed now, and what remains developing?")
        if not questions:
            questions.append("No major unanswered research question was automatically detected.")
        return self._unique(questions)
    def _actions(self,level,signals,questions):
        actions=[]
        if level in {"DEEP","URGENT"}:
            actions.extend([
                {"action":"locate_primary_evidence","priority":"CRITICAL","reason":"High investigation score requires stronger evidence."},
                {"action":"cross_check_independent_sources","priority":"CRITICAL","reason":"Do not treat repeated reporting as independent confirmation."}
            ])
        if signals.get("contradiction_count",0):
            actions.append({"action":"resolve_conflicting_claims","priority":"HIGH","reason":"Conflicting claims were detected."})
        if signals.get("allegation_count",0):
            actions.append({"action":"seek_response_from_subject","priority":"HIGH","reason":"The story contains allegations or accusations."})
        if signals.get("rapidly_changing",False):
            actions.append({"action":"monitor_story_for_updates","priority":"HIGH","reason":"The story appears to be developing."})
        actions.extend([
            {"action":"run_claim_verification","priority":"REQUIRED","reason":"All material factual claims should pass verification."},
            {"action":"run_editorial_review","priority":"REQUIRED","reason":"Research findings must be evaluated before publication."}
        ])
        return actions

    def _priorities(self,claims,signals):
        priorities=[]
        for i,claim in enumerate(claims):
            if not isinstance(claim,dict):continue
            text=str(claim.get("text",claim.get("claim",""))).strip()
            if not text:continue
            risk=0
            low=text.lower()
            if any(x in low for x in self.high_risk_terms):risk+=40
            if claim.get("requires_verification"):risk+=30
            if str(claim.get("importance","")).upper() in {"HIGH","CRITICAL"}:risk+=30
            if signals.get("contradiction_count",0):risk+=10
            risk=min(risk,100)
            priorities.append({
                "claim_id":claim.get("id",claim.get("claim_id",f"claim_{i+1}")),
                "claim":text,
                "priority_score":risk,
                "priority":"CRITICAL" if risk>=80 else "HIGH" if risk>=50 else "MEDIUM" if risk>=25 else "LOW",
                "requires_deep_investigation":risk>=50
            })
        priorities.sort(key=lambda x:x.get("priority_score",0),reverse=True)
        return priorities

    def _publication_recommendation(self,level):
        mapping={
            "URGENT":{"decision":"HOLD_PUBLICATION","reason":"Urgent investigation is required before publication."},
            "DEEP":{"decision":"HOLD_FOR_INVESTIGATION","reason":"Deep investigation is required before publication."},
            "STANDARD":{"decision":"EDITORIAL_REVIEW","reason":"Standard investigation should be completed before publication."},
            "LIGHT":{"decision":"LIGHT_REVIEW","reason":"A light verification pass is recommended."},
            "NONE":{"decision":"NORMAL_EDITORIAL_FLOW","reason":"No major investigation requirement was detected."}
        }
        return mapping.get(level,mapping["STANDARD"])

    def _contains_terms(self,text,terms):
        text=str(text or "").lower()
        return any(term.lower() in text for term in terms)

    def _unique(self,values):
        result=[];seen=set()
        for value in values:
            value=str(value or "").strip()
            if not value:continue
            key=value.lower()
            if key in seen:continue
            seen.add(key);result.append(value)
        return result
