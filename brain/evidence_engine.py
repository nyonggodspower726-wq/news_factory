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
        ct=set(self._tokens(claim_text));st=set(self._tokens(source_text))
        if not ct:return "NEUTRAL"
        ratio=len(ct&st)/len(ct)
        if ratio<.20:return "NEUTRAL"
        for negative,positive in [("denied","confirmed"),("false","true"),("rejected","approved"),("disputed","confirmed")]:
            if negative in source_text and positive in claim_text:return "OPPOSES"
        return "SUPPORTS"

    def _directness_score(self,claim,supporting):
        if not supporting:return 0
        ct=set(self._tokens(claim["text"]));best=0
        for s in supporting:
            st=set(self._tokens(str(s.get("title",""))+" "+str(s.get("text",""))))
            if not st:continue
            score=int(len(ct&st)/max(len(ct),1)*100)
            if s.get("primary"):score+=15
            best=max(best,min(score,100))
        return best

    def _source_strength(self,sources):
        if not sources:return 0
        scores=[]
        for s in sources:
            value=self._number(s.get("quality_score",50),50);typ=s.get("type","UNKNOWN")
            if typ in self.strong_source_types:value+=10
            if typ in self.weak_source_types:value-=20
            if s.get("primary"):value+=20
            scores.append(max(0,min(value,100)))
        return int(sum(scores)/len(scores))

    def _independence_score(self,sources):
        if not sources:return 0
        domains={str(s.get("domain","")).lower().strip() for s in sources if s.get("domain")}
        explicit=sum(1 for s in sources if s.get("independent"))
        return min(100,min(len(domains)*20,60)+min(explicit*15,40))

    def _primary_score(self,sources):
        if not sources:return 0
        primary=sum(1 for s in sources if s.get("primary"))
        official=sum(1 for s in sources if s.get("official"))
        return min(100,primary*60+official*40)

    def _freshness_score(self,sources):
        if not sources:return 0
        return 80 if any(s.get("published_at") for s in sources) else 50

    def _contradiction_score(self,supporting,opposing):
        if not opposing:return 0
        return min(100,len(opposing)*40)

    def _attribution_score(self,claim):
        text=claim.get("text","").lower()
        return 80 if any(w in text for w in self.attribution_words) else 40

    def _uncertainty_score(self,claim):
        text=claim.get("text","").lower()
        return min(100,sum(15 for w in self.uncertainty_words if w in text))

    def _classify_claim(self,claim):
        supplied=str(claim.get("type","")).upper()
        if supplied in self.claim_types:return supplied
        text=claim.get("text","").lower()
        if any(w in text for w in ("allegedly","alleged","claims","accused")):return "ALLEGATION"
        if any(w in text for w in ("may","might","could","expected","likely")):return "PREDICTION"
        if any(w in text for w in ("i think","in my view","should","best")):return "OPINION"
        return "FACT"

    def _source_names(self,sources):
        return [{"id":s.get("id"),"name":s.get("name"),"domain":s.get("domain"),"url":s.get("url")} for s in sources]

    def _recommended_treatment(self,ctype,score,contradiction):
        if ctype=="ALLEGATION":return "ATTRIBUTED_ALLEGATION"
        if ctype=="PREDICTION":return "LABEL_AS_PREDICTION"
        if ctype in {"OPINION","ANALYSIS"}:return "LABEL_OR_ATTRIBUTE"
        if contradiction>=60:return "HOLD_AND_VERIFY"
        if score>=80:return "PUBLISH_IF_EDITOR_APPROVES"
        if score>=60:return "USE_WITH_CONTEXT"
        return "VERIFY_BEFORE_PUBLICATION"
    def _summary(self,claims):
        counts={}
        for c in claims:
            status=c.get("publication_status","INSUFFICIENT_SUPPORT");counts[status]=counts.get(status,0)+1
        total=len(claims);avg=round(sum(c.get("evidence_score",0) for c in claims)/total,2) if total else 0
        return {"total_claims":total,"strong_support":counts.get("STRONG_SUPPORT",0),"moderate_support":counts.get("MODERATE_SUPPORT",0),"weak_support":counts.get("WEAK_SUPPORT",0),"insufficient_support":counts.get("INSUFFICIENT_SUPPORT",0),"hold_for_review":counts.get("HOLD_FOR_REVIEW",0),"attribute_or_label":counts.get("ATTRIBUTE_OR_LABEL",0),"average_evidence_score":avg}

    def _publication_readiness(self,claims):
        if not claims:return {"status":"NO_CLAIMS","score":0,"ready":False}
        blockers=sum(1 for c in claims if c.get("publication_status") in {"HOLD_FOR_REVIEW","INSUFFICIENT_SUPPORT"})
        scores=[c.get("evidence_score",0) for c in claims if c.get("claim_type")=="FACT"]
        avg=sum(scores)/len(scores) if scores else 0
        ready=blockers==0 and avg>=70
        return {"status":"READY" if ready else "REVIEW_REQUIRED","score":round(avg,2),"blocking_claims":blockers,"ready":ready}

    def _number(self,value,default=0):
        try:return float(value)
        except (TypeError,ValueError):return default

    def _tokens(self,text):
        return re.findall(r"\b[a-z0-9]{3,}\b",str(text or "").lower())


evidence_engine=EvidenceEngine()

def analyze_evidence(claims,sources):
    return evidence_engine.analyze(claims,sources)

def analyze(claims,sources):
    return evidence_engine.analyze(claims,sources)
if __name__=="__main__":
    test_claims=[{
        "id":"claim_1",
        "text":"Officials announced a new development.",
        "type":"FACT"
    }]
    test_sources=[{
        "id":"source_1",
        "name":"Example News",
        "domain":"example.com",
        "title":"Officials announced a new development",
        "text":"Officials announced a new development.",
        "type":"ESTABLISHED_NEWS",
        "quality_score":80,
        "published_at":"2026-08-11"
    }]
    print(
        analyze_evidence(
            test_claims,
            test_sources
        )
    )
