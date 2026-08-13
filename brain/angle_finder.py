"""
AI NEWS FACTORY
EDITORIAL ANGLE INTELLIGENCE ENGINE
"""
from typing import Any,Dict,List,Optional

class AngleFinder:
    def __init__(self):
        self.name="Editorial Angle Intelligence Engine"
        self.version="2.1.0"
        self.minimum_score=50
        self.angle_types=["WHAT_HAPPENED","WHY_IT_MATTERS","WHAT_IT_MEANS_FOR_PEOPLE","WHAT_CHANGES_NOW","WHAT_HAPPENS_NEXT","EXPLAINER","TIMELINE","IMPACT","CONTEXT","KEY_QUESTIONS","WHAT_IS_UNKNOWN","LOCAL_ANGLE","CONSEQUENCES","DEVELOPING_STORY"]

    def find_angles(self,story:Dict[str,Any],related_stories:List[Dict[str,Any]]=None,evidence:Dict[str,Any]=None,trend_data:Dict[str,Any]=None,article_plan:Dict[str,Any]=None,cluster:Dict[str,Any]=None)->Dict[str,Any]:
        story=self._normalize_story(story)
        related_stories=related_stories if isinstance(related_stories,list) else []
        evidence=evidence if isinstance(evidence,dict) else {}
        trend_data=trend_data if isinstance(trend_data,dict) else {}
        article_plan=article_plan if isinstance(article_plan,dict) else {}
        if cluster and not related_stories:
            related_stories=self._related_from_cluster(cluster)
        story_data=self._story_data(story)
        original=self._safe_dict(story.get("original"))
        title=str(original.get("title") or story_data.get("title") or story.get("title") or story.get("headline") or "").strip()
        summary=str(story_data.get("summary") or story_data.get("description") or story.get("summary") or story.get("description") or "").strip()
        story_type=str(story_data.get("story_type") or story.get("story_type") or "general").strip()
        urgency=str(story_data.get("urgency") or story.get("urgency") or "normal").strip()
        impact=str(story_data.get("initial_impact") or story_data.get("impact") or story.get("impact") or "low").strip()
        locations=story_data.get("locations") or story.get("locations") or []
        if isinstance(locations,str):locations=[locations]
        reader_questions=story_data.get("reader_questions") or story.get("reader_questions") or []
        if isinstance(reader_questions,str):reader_questions=[reader_questions]
        keywords=story_data.get("keywords") or story.get("keywords") or []
        if isinstance(keywords,str):keywords=[keywords]
        context={"story":story,"story_data":story_data,"title":title,"summary":summary,"story_type":story_type,"urgency":urgency,"impact":impact,"locations":locations,"reader_questions":reader_questions,"keywords":keywords,"related_stories":related_stories,"evidence":evidence,"trend_data":trend_data,"article_plan":article_plan,"cluster":cluster or {}}
        candidates=self._generate_candidates(**context)
        if not isinstance(candidates,list):candidates=[]
        scored=[]
        for candidate in candidates:
            if isinstance(candidate,dict):
                scored.append(self._score_angle(candidate,context))
        scored.sort(key=lambda x:x.get("total_score",0),reverse=True)
        selected=scored[0] if scored else None
        backups=scored[1:4] if len(scored)>1 else []
        return {"engine":self.name,"version":self.version,"status":"ANGLE_ANALYSIS_COMPLETE","primary_angle":selected,"backup_angles":backups,"all_angles":scored,"editorial_instruction":self._build_editorial_instruction(selected),"summary":self._summary(selected)}

    def _generate_candidates(self,title="",summary="",story_type="general",urgency="normal",impact="low",locations=None,reader_questions=None,keywords=None,**kwargs):
        locations=locations if isinstance(locations,list) else []
        reader_questions=reader_questions if isinstance(reader_questions,list) else []
        candidates=[
            {"type":"WHAT_HAPPENED","title":"What actually happened?","purpose":"Establish the confirmed event clearly."},
            {"type":"WHY_IT_MATTERS","title":"Why this story matters","purpose":"Explain the significance beyond the announcement."},
            {"type":"WHAT_IT_MEANS_FOR_PEOPLE","title":"What this means for ordinary people","purpose":"Translate the development into practical reader impact."},
            {"type":"WHAT_CHANGES_NOW","title":"What changes now?","purpose":"Identify confirmed immediate changes."},
            {"type":"WHAT_HAPPENS_NEXT","title":"What happens next?","purpose":"Explain supported next steps and remaining uncertainty."},
            {"type":"EXPLAINER","title":"The story explained","purpose":"Make a complicated development understandable."},
            {"type":"CONTEXT","title":"The context behind the story","purpose":"Provide essential background."},
            {"type":"TIMELINE","title":"How we got here","purpose":"Show the important sequence of events."},
            {"type":"WHAT_IS_UNKNOWN","title":"What we still don't know","purpose":"Separate confirmed information from unresolved questions."},
            {"type":"CONSEQUENCES","title":"What could happen as a result","purpose":"Identify evidence-supported consequences without presenting speculation as fact."},
            {"type":"IMPACT","title":"Who is affected and how","purpose":"Focus on measurable effects and affected groups."},
            {"type":"DEVELOPING_STORY","title":"The latest confirmed development","purpose":"Prioritize the newest verified information."}
        ]
        if locations:candidates.append({"type":"LOCAL_ANGLE","title":"What this means locally","purpose":"Connect the development to the affected location or audience."})
        if reader_questions:candidates.append({"type":"KEY_QUESTIONS","title":"The key questions readers have","purpose":"Answer the most important unanswered reader questions."})
        return candidates

    def _score_angle(self,candidate,context):
        angle_type=str(candidate.get("type","WHAT_HAPPENED"))
        story=context.get("story",{})
        story_data=context.get("story_data",{})
        evidence=context.get("evidence",{})
        locations=context.get("locations",[])
        related=context.get("related_stories",[])
        evidence_score=self._evidence_score(angle_type,story,evidence)
        local_score=self._local_relevance(angle_type,story_data,locations)
        risk=self._risk_score(angle_type,story)
        reader_score=self._reader_value(angle_type,context)
        novelty=self._novelty_score(angle_type,related)
        urgency_bonus=self._urgency_bonus(angle_type,context.get("urgency","normal"))
        total=max(0,min(100,round(evidence_score*0.40+local_score*0.10+reader_score*0.20+novelty*0.10+urgency_bonus*0.10+(100-risk)*0.10)))
        decision=self._angle_decision(total,evidence_score,risk)
        return {"type":angle_type,"title":candidate.get("title",""),"purpose":candidate.get("purpose",""),"total_score":total,"decision":decision,"factors":{"evidence_support":round(evidence_score,2),"local_relevance":round(local_score,2),"reader_value":round(reader_score,2),"novelty":round(novelty,2),"urgency_bonus":round(urgency_bonus,2),"misinformation_risk":round(risk,2)}}

    def _evidence_score(self,angle_type,story,evidence=None):
        story=self._normalize_story(story)
        data=self._story_data(story)
        items=data.get("evidence",[]) or story.get("evidence",[]) or []
        claims=data.get("claims",[]) or story.get("claims",[]) or []
        baseline={"WHAT_HAPPENED":92,"TIMELINE":88,"WHAT_IS_UNKNOWN":90,"EXPLAINER":84,"CONTEXT":82,"WHY_IT_MATTERS":78,"WHAT_IT_MEANS_FOR_PEOPLE":76,"WHAT_CHANGES_NOW":80,"WHAT_HAPPENS_NEXT":68,"CONSEQUENCES":65,"LOCAL_ANGLE":72,"IMPACT":80,"DEVELOPING_STORY":88,"KEY_QUESTIONS":78}
        score=baseline.get(angle_type,70)
        if isinstance(items,list):score+=min(len(items)*2,10)
        if isinstance(claims,list):score+=min(len(claims),5)
        if isinstance(evidence,dict):
            if evidence.get("verified") is True:score+=5
            if evidence.get("status") in {"VERIFIED","PASSED","COMPLETE"}:score+=3
        return min(score,100)

    def _local_relevance(self,angle_type,story_data,locations=None):
        locations=locations if isinstance(locations,list) else []
        if angle_type=="LOCAL_ANGLE":return 100 if locations else 20
        return 75 if locations else 50

    def _risk_score(self,angle_type,story):
        story=self._normalize_story(story)
        data=self._story_data(story)
        uncertainty=str(data.get("uncertainty") or story.get("uncertainty") or "normal").lower()
        risk={"WHAT_HAPPENED":15,"WHY_IT_MATTERS":25,"WHAT_IT_MEANS_FOR_PEOPLE":30,"WHAT_CHANGES_NOW":25,"WHAT_HAPPENS_NEXT":40,"EXPLAINER":20,"TIMELINE":15,"CONTEXT":20,"WHAT_IS_UNKNOWN":10,"KEY_QUESTIONS":15,"CONSEQUENCES":45,"LOCAL_ANGLE":25,"IMPACT":30,"DEVELOPING_STORY":20}.get(angle_type,30)
        if uncertainty in {"high","very_high","extreme"}:risk+=15
        return min(risk,100)

    def _reader_value(self,angle_type,context):
        if angle_type in {"WHAT_IT_MEANS_FOR_PEOPLE","WHY_IT_MATTERS","WHAT_CHANGES_NOW","WHAT_HAPPENS_NEXT","KEY_QUESTIONS","IMPACT"}:return 90
        if angle_type in {"WHAT_HAPPENED","EXPLAINER","WHAT_IS_UNKNOWN","CONTEXT"}:return 82
        if angle_type=="LOCAL_ANGLE":return 95 if context.get("locations") else 40
        return 75

    def _novelty_score(self,angle_type,related):
        if not related:return 60
        if angle_type in {"WHAT_HAPPENS_NEXT","DEVELOPING_STORY","WHY_IT_MATTERS","WHAT_CHANGES_NOW"}:return 85
        return 65

    def _urgency_bonus(self,angle_type,urgency):
        urgency=str(urgency or "normal").lower()
        if urgency in {"breaking","urgent","high"} and angle_type in {"DEVELOPING_STORY","WHAT_HAPPENS_NEXT","WHAT_CHANGES_NOW"}:return 100
        if urgency in {"breaking","urgent","high"}:return 80
        return 55

    def _angle_decision(self,score,evidence,risk):
        if evidence<50 or risk>=80:return "REJECT"
        if score>=85:return "STRONG_PRIMARY"
        if score>=75:return "STRONG_BACKUP"
        if score>=65:return "USABLE"
        if score>=50:return "WEAK"
        return "REJECT"

    def _build_editorial_instruction(self,selected):
        if not isinstance(selected,dict):return "No sufficiently supported editorial angle was identified. Return to evidence gathering."
        instructions={"WHAT_HAPPENED":"Lead with confirmed facts and avoid unsupported interpretation.","WHY_IT_MATTERS":"Explain the significance and why readers should care.","WHAT_IT_MEANS_FOR_PEOPLE":"Translate the confirmed development into practical reader consequences.","WHAT_CHANGES_NOW":"Focus on confirmed immediate changes.","WHAT_HAPPENS_NEXT":"Explain supported next steps and clearly label uncertainty.","EXPLAINER":"Explain the issue simply with necessary context.","TIMELINE":"Organize the story chronologically and distinguish confirmed events from disputed claims.","IMPACT":"Identify affected groups and evidence-supported effects.","CONTEXT":"Provide only background necessary to understand the development.","WHAT_IS_UNKNOWN":"Clearly identify unresolved questions.","KEY_QUESTIONS":"Answer the most important reader questions using evidence.","LOCAL_ANGLE":"Connect the confirmed development to the affected location.","CONSEQUENCES":"Discuss supported consequences while separating possibilities from facts.","DEVELOPING_STORY":"Prioritize the newest confirmed development and unresolved issues."}
        return instructions.get(selected.get("type"),instructions["WHAT_HAPPENED"])

    def _summary(self,selected):
        if not isinstance(selected,dict):
            return {"primary_type":None,"primary_title":None,"score":0,"decision":"NONE"}
        return {"primary_type":selected.get("type"),"primary_title":selected.get("title"),"score":selected.get("total_score",0),"decision":selected.get("decision","UNKNOWN")}

    def get_primary_angle(self,story):return self.analyze(story).get("primary_angle")
    def get_backup_angles(self,story):return self.analyze(story).get("backup_angles",[])
    d get_angle_types(self):return list(self.angle_types)
    def validate_angle(self,angle):
        if not isinstance(angle,dict):return {"valid":False,"reason":"Angle must be a dictionary."}
        required=["type","title","purpose","total_score"]
        missing=[x for x in required if x not in angle]
        if missing:return {"valid":False,"reason":"Missing required fields: "+", ".join(missing)}
        if angle["type"] not in self.angle_types:return {"valid":False,"reason":"Unknown angle type: "+str(angle["type"])}
        return {"valid":True,"reason":"Angle is valid."}

    def filter_acceptable_angles(self,angles):
        if not isinstance(angles,list):return []
        acceptable=[]
        for angle in angles:
            if not isinstance(angle,dict):continue
            if self.validate_angle(angle)["valid"] and angle.get("decision")!="REJECT":acceptable.append(angle)
        acceptable.sort(key=lambda x:x.get("total_score",0),reverse=True)
        return acceptable

    def select_safest_angle(self,angles):
        acceptable=self.filter_acceptable_angles(angles)
        if not acceptable:return {"type":"WHAT_HAPPENED","title":"What actually happened?","purpose":"Focus only on confirmed information.","total_score":0,"decision":"FALLBACK"}
        acceptable.sort(key=lambda x:(x.get("factors",{}).get("evidence_support",0),x.get("total_score",0)),reverse=True)
        return acceptable[0]

    def create_summary(self,result):
        if not isinstance(result,dict):return {"primary_type":None,"primary_title":None,"score":0,"editorial_instruction":""}
        primary=result.get("primary_angle")
        if not isinstance(primary,dict):return {"primary_type":None,"primary_title":None,"score":0,"editorial_instruction":result.get("editorial_instruction","")}
        return {"primary_type":primary.get("type"),"primary_title":primary.get("title"),"score":primary.get("total_score",0),"decision":primary.get("decision"),"editorial_instruction":result.get("editorial_instruction","")}

    def analyze(self,story:Dict[str,Any]=None,related_stories=None,evidence=None,trend_data=None,article_plan=None,cluster=None,**kwargs):
        if story is None or not isinstance(story,dict):story={}
        if cluster is not None and not related_stories:related_stories=self._related_from_cluster(cluster)
        result=self.find_angles(story=story,related_stories=related_stories,evidence=evidence,trend_data=trend_data,article_plan=article_plan,cluster=cluster)
        result["summary"]=self.create_summary(result)
        return result

    def run(self,story=None,**kwargs):return self.analyze(story=story,**kwargs)

    def analyze_many(self,stories):
        if not isinstance(stories,list):return []
        results=[]
        for story in stories:
            try:results.append(self.analyze(story))
            except Exception as exc:results.append({"success":False,"error":str(exc),"story":story})
        return results

    def best_angle_from_stories(self,stories):
        candidates=[]
        for result in self.analyze_many(stories):
            primary=result.get("primary_angle") if isinstance(result,dict) else None
            if isinstance(primary,dict):candidates.append(primary)
        if not candidates:return None
        return max(candidates,key=lambda x:x.get("total_score",0))

    def health_check(self):
        return {"engine":self.name,"version":self.version,"status":"READY","angle_types":len(self.angle_types),"minimum_score":self.minimum_score}

    def status(self):return self.health_check()

    def _normalize_story(self,story):
        if not isinstance(story,dict):return {}
        if isinstance(story.get("story"),dict):return story
        return {"story":story,"original":story}

    def _story_data(self,story):
        if not isinstance(story,dict):return {}
        data=story.get("story",{})
        return data if isinstance(data,dict) else story

    def _safe_dict(self,value):return value if isinstance(value,dict) else {}

    def _related_from_cluster(self,cluster):
        if not isinstance(cluster,dict):return []
        for key in ("stories","related_stories","items","clusters"):
            value=cluster.get(key)
            if isinstance(value,list):return value
        return []

angle_finder=AngleFinder()

def find_angles(story):return angle_finder.find_angles(story)
def analyze(story,**kwargs):return angle_finder.analyze(story,**kwargs)
def run(story,**kwargs):return angle_finder.run(story,**kwargs)
def get_primary_angle(story):return angle_finder.get_primary_angle(story)
def get_backup_angles(story):return angle_finder.get_backup_angles(story)

__all__=["AngleFinder","angle_finder","find_angles","analyze","run","get_primary_angle","get_backup_angles"]

if __name__=="__main__":
    test={"story":{"title":"Example News Story","summary":"A confirmed development occurred.","evidence":["Source A","Source B"],"claims":["Confirmed claim"],"locations":[],"uncertainty":"normal"}}
    result=angle_finder.analyze(test)
    print("ANGLE FINDER TEST")
    print("Status:",result.get("status"))
    print("Primary:",result.get("summary",{}))
    print("Health:",angle_finder.health_check())
