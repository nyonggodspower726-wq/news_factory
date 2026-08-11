"""AI NEWS FACTORY - READER PSYCHOLOGY & ENGAGEMENT ENGINE"""
import re
from typing import Any,Dict,List
from typing import Any,Dict,List

class PsychologyEngine:
    def __init__(self):
        self.name="Reader Psychology & Engagement Engine"
        self.version="1.1.0"
        self.target_readability={"minimum":55,"ideal":75,"maximum":95}
        self.forbidden_engagement_patterns=[
            "you won't believe","shocking","this will blow your mind",
            "the internet is going crazy","what happened next",
            "doctors hate this","they don't want you to know"
        ]

    def analyze(self,article_plan:Dict[str,Any])->Dict[str,Any]:
        if not isinstance(article_plan,dict):
            article_plan={}
        article=article_plan.get("article",{}) or {}
        headline=article.get("headline",{}) or {}
        lead=article.get("lead",{}) or {}
        attention=self._attention_score(article_plan)
        curiosity=self._curiosity_score(article_plan)
        relevance=self._relevance_score(article_plan)
        emotional_salience=self._emotional_salience(article_plan)
        cognitive_load=self._cognitive_load(article_plan)
        retention=self._retention_score(attention,curiosity,relevance,cognitive_load)
        risks=self._detect_manipulation(headline,lead)
        recommendations=self._generate_recommendations(article_plan,attention,curiosity,relevance,cognitive_load,risks)
        return {
            "engine":self.name,
            "version":self.version,
            "status":"ANALYZED",
            "scores":{
                "attention":attention,
                "curiosity":curiosity,
                "relevance":relevance,
                "emotional_salience":emotional_salience,
                "cognitive_load":cognitive_load,
                "retention":retention
            },
            "reader_questions":self._reader_questions(article_plan),
            "manipulation_risks":risks,
            "recommendations":recommendations,
            "engagement_strategy":self._engagement_strategy(retention,risks)
        }

    def _attention_score(self,article_plan:Dict[str,Any])->int:
        significance=article_plan.get("significance",{}) or {}
        return self._clamp(significance.get("score",50),50)

    def _curiosity_score(self,article_plan:Dict[str,Any])->int:
        angles=article_plan.get("angles",{}) or {}
        primary=angles.get("primary_angle",{}) or {}
        score=self._number(primary.get("total_score",50),50)
        questions=self._reader_questions(article_plan)
        if len(questions)>=3: score+=10
        return self._clamp(score,50)

    def _relevance_score(self,article_plan:Dict[str,Any])->int:
        significance=article_plan.get("significance",{}) or {}
        breakdown=significance.get("breakdown",{}) or {}
        return self._clamp(breakdown.get("reader_interest",50),50)

    def _emotional_salience(self,article_plan:Dict[str,Any])->int:
        story=article_plan.get("story",{}) or {}
        story_data=story.get("story",{}) if isinstance(story,dict) else {}
        if not isinstance(story_data,dict): story_data={}
        impact=str(story_data.get("initial_impact","low")).lower()
        return {"high":90,"medium":65,"low":35}.get(impact,35)

    def _cognitive_load(self,article_plan:Dict[str,Any])->int:
        article=article_plan.get("article",{}) or {}
        facts=article.get("key_facts",{}) or {}
        if not isinstance(facts,dict): facts={}
        fact_list=facts.get("facts",[]) or []
        if not isinstance(fact_list,list): fact_list=[]
        context=article.get("context",{}) or {}
        score=30
        if len(fact_list)>8: score+=20
        if len(fact_list)>15: score+=20
        if context: score+=10
        return min(score,100)

    def _retention_score(self,attention:int,curiosity:int,relevance:int,cognitive_load:int)->int:
        score=attention*.30+curiosity*.25+relevance*.30+(100-cognitive_load)*.15
        return max(0,min(int(score),100))

    def _reader_questions(self,article_plan:Dict[str,Any])->List[str]:
        story=article_plan.get("story",{}) or {}
        story_data=story.get("story",{}) if isinstance(story,dict) else {}
        if not isinstance(story_data,dict): story_data={}
        supplied=story_data.get("reader_questions",[]) or []
        if not isinstance(supplied,list): supplied=[]
        questions=[str(q) for q in supplied if str(q).strip()]
        standard=[
            "What happened?","Why does it matter?","Who is affected?",
            "What changes now?","What happens next?","What is still unknown?"
        ]
        for q in standard:
            if q not in questions: questions.append(q)
        return questions[:10]

    def _detect_manipulation(self,headline:Any,lead:Any)->List[Dict[str,str]]:
        risks=[]
        combined=(self._text(headline)+" "+self._text(lead)).lower()
        for pattern in self.forbidden_engagement_patterns:
            if pattern in combined:
                risks.append({
                    "pattern":pattern,
                    "severity":"HIGH",
                    "action":"REMOVE_MANIPULATIVE_LANGUAGE"
                })
        if re.search(r"!{2,}",combined):
            risks.append({
                "pattern":"excessive_exclamation",
                "severity":"MEDIUM",
                "action":"REDUCE_EMOTIONAL_PUNCTUATION"
            })
        if re.search(r"\b(urgent|breaking|exclusive)\b",combined):
            risks.append({
                "pattern":"urgency_language",
                "severity":"MEDIUM",
                "action":"VERIFY_URGENCY_CLAIM"
            })
        return risks

    def _generate_recommendations(self,article_plan:Dict[str,Any],attention:int,curiosity:int,relevance:int,cognitive_load:int,risks:List[Dict[str,str]])->List[str]:
        recommendations=[]
        if attention<60:
            recommendations.append("Strengthen the lead using the most newsworthy verified fact.")
        if curiosity<60:
            recommendations.append("Clarify the unresolved question or consequence without withholding essential facts.")
        if relevance<60:
            recommendations.append("Explain why the verified development matters to affected readers.")
        if cognitive_load>70:
            recommendations.append("Reduce information density and divide complex material into clearer sections.")
        if not risks:
            recommendations.append("Maintain curiosity through clear unanswered questions rather than sensational language.")
        else:
            recommendations.append("Remove manipulative engagement patterns before publication.")
        recommendations.append("Preserve attribution and uncertainty throughout the article.")
        recommendations.append("Do not introduce facts that are absent from the verified reporting package.")
        return recommendations

    def _engagement_strategy(self,retention:int,risks:List[Dict[str,str]])->Dict[str,Any]:
        if any(r.get("severity")=="HIGH" for r in risks):
            level="REVISE"
        elif retention>=80:
            level="STRONG"
        elif retention>=65:
            level="MODERATE"
        else:
            level="NEEDS_IMPROVEMENT"
        return {
            "level":level,
            "retention_score":retention,
            "ethical":True,
            "clickbait_allowed":False,
            "manipulation_detected":bool(risks)
        }

    def _number(self,value:Any,default:int=50)->int:
        try:return int(float(value))
        except(TypeError,ValueError):return default

    def _clamp(self,value:Any,default:int=50)->int:
        return max(0,min(self._number(value,default),100))

    def _text(self,value:Any)->str:
        if isinstance(value,dict):
            return " ".join(str(v) for v in value.values())
        if isinstance(value,list):
            return " ".join(str(v) for v in value)
        return str(value or "")
