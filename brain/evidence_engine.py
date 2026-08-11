from typing import Any,Dict,List
import re

class EvidenceEngine:
    def __init__(self):
        self.name="Evidence Intelligence Engine";self.version="1.0.0"
        self.claim_types={"FACT","ALLEGATION","OPINION","ANALYSIS","PREDICTION","UNCONFIRMED"}
        self.strong_source_types={"PRIMARY","OFFICIAL","GOVERNMENT","COURT","REGULATORY","ACADEMIC","WIRE"}
        self.weak_source_types={"SOCIAL","USER_GENERATED","UNKNOWN"}
        self.uncertainty_words={"may","might","could","possibly","reportedly","allegedly","apparently","unconfirmed","rumored","rumour","rumor","expected","likely"}
        self.attribution_words={"according","said","says","reported","confirmed","stated","announced","claimed","told"}

    def analyze(self,claims:List[Dict[str,Any]],sources:List[Dict[str,Any]])->Dict[str,Any]:
        claims=self._normalize_claims(claims);sources=self._normalize_sources(sources)
        assessments=[self._assess_claim(c,sources) for c in claims]
        return {"engine":self.name,"version":self.version,"status":"ANALYZED","claim_count":len(assessments),"claims":assessments,"summary":self._summary(assessments),"publication_readiness":self._publication_readiness(assessments)}

    def _normalize_claims(self,claims):
        if isinstance(claims,str):claims=[{"text":claims}]
        elif isinstance(claims,dict):claims=[claims]
        if not isinstance(claims,list):return []
        out=[]
        for i,c in enumerate(claims):
            if isinstance(c,str):c={"text":c}
            if not isinstance(c,dict):continue
            text=str(c.get("text",c.get("claim",""))).strip()
            if not text:continue
            ids=c.get("source_ids",[])
            if isinstance(ids,str):ids=[ids]
            out.append({"id":c.get("id",f"claim_{i+1}"),"text":text,"type":str(c.get("type","")).upper(),"importance":str(c.get("importance","MEDIUM")).upper(),"source_ids":ids if isinstance(ids,list) else [],"entities":c.get("entities",[])})
        return out

    def _normalize_sources(self,sources):
        if isinstance(sources,dict):sources=list(sources.values())
        if not isinstance(sources,list):return []
        out=[]
        for i,s in enumerate(sources):
            if isinstance(s,str):s={"url":s}
            if not isinstance(s,dict):continue
            out.append({"id":s.get("id",f"source_{i+1}"),"name":s.get("name",s.get("publisher","Unknown")),"url":s.get("url",""),"title":s.get("title",""),"text":s.get("text",s.get("excerpt",s.get("description",s.get("content","")))),"type":str(s.get("type",s.get("source_type","UNKNOWN"))).upper(),"domain":s.get("domain",""),"primary":bool(s.get("primary",False)),"official":bool(s.get("official",False)),"independent":bool(s.get("independent",False)),"quality_score":self._number(s.get("quality_score",s.get("reliability",50)),50),"published_at":s.get("published_at")})
        return out

    def _assess_claim(self,claim,sources):
        ctype=self._classify_claim(claim);support=[];oppose=[]
        for s in sources:
            rel=self._source_relationship(claim,s)
            if rel=="SUPPORTS":support.append(s)
            elif rel=="OPPOSES":oppose.append(s)
        direct=self._directness_score(claim,support);strength=self._source_strength(support);ind=self._independence_score(support);primary=self._primary_score(support);fresh=self._freshness_score(support);contr=self._contradiction_score(support,oppose);attr=self._attribution_score(claim);unc=self._uncertainty_score(claim)
        score=int(max(0,min(direct*.25+strength*.20+ind*.15+primary*.15+fresh*.10+attr*.05+(100-contr)*.10,100)))
        if ctype in {"ALLEGATION","PREDICTION","OPINION","ANALYSIS"}:status="ATTRIBUTE_OR_LABEL"
        elif contr>=60:status="HOLD_FOR_REVIEW"
        elif score>=80:status="STRONG_SUPPORT"
        elif score>=60:status="MODERATE_SUPPORT"
        elif score>=40:status="WEAK_SUPPORT"
        else:status="INSUFFICIENT_SUPPORT"
        return {"claim_id":claim["id"],"claim":claim["text"],"claim_type":ctype,"importance":claim["importance"],"supporting_sources":self._source_names(support), "opposing_sources":self._source_names(oppose),"supporting_source_count":len(support),"opposing_source_count":len(oppose),"evidence_score":score,"evidence_dimensions":{"directness":direct,"source_strength":strength,"independence":ind,"primary_source":primary,"freshness":fresh,"attribution":attr,"contradiction":contr,"uncertainty":unc},"publication_status":status,"recommended_treatment":self._recommended_treatment(ctype,score,contr)}

    def _source_relationship(self,claim,source):
        claim_text=claim["text"].lower();source_text=(str(source.get("title",""))+" "+str(source.get("text",""))).lower()
        if not source_text:return "NEUTRAL"
