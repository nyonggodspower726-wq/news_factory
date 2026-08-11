from typing import Any,Dict,List
from datetime import datetime
from urllib.parse import urlparse
import hashlib,re

class MisinformationEngine:
    def __init__(self):
        self.name="Misinformation Intelligence Engine";self.version="1.0.0"
        self.high_risk_words={"shocking","secret","exposed","confirmed","guaranteed","everyone","nobody","destroyed","definitely","undeniable","miracle","scam","hoax","breaking"}
        self.uncertainty_words={"allegedly","reportedly","possibly","apparently","may","might","could","unconfirmed","rumor","rumour"}
        self.attribution_patterns=["according to","officials said","police said","the company said","the government said","a spokesperson said","court documents","court filing","statement","document","report"]
        self.denial_patterns=["denied","disputed","rejected","called the claim false","said the claim was false","not true","no evidence","misleading","incorrect"]
        self.social_domains={"x.com","twitter.com","facebook.com","instagram.com","tiktok.com","reddit.com","youtube.com"}

    def analyze(self,claims:List[Any],sources:List[Dict[str,Any]]=None,story:Dict[str,Any]=None)->Dict[str,Any]:
        claims=self._normalize_claims(claims);sources=sources if isinstance(sources,list) else [];story=story if isinstance(story,dict) else {}
        results=[self._analyze_claim(c,sources,story) for c in claims]
        source_analysis=self._analyze_sources(sources);temporal=self._analyze_temporal_consistency(sources,story);dup=self._analyze_duplication(sources);overall=self._overall_assessment(results,source_analysis,temporal,dup)
        return {"engine":self.name,"version":self.version,"status":"ANALYZED","overall":overall,"claims":results,"source_analysis":source_analysis,"temporal_analysis":temporal,"duplication_analysis":dup,"editorial_action":self._editorial_action(overall)}

    def _normalize_claims(self,claims):
        if isinstance(claims,(str,dict)):claims=[claims]
        if not isinstance(claims,list):return []
        out=[]
        for i,c in enumerate(claims):
            if isinstance(c,str):out.append({"id":f"claim_{i+1}","text":c,"continue":0,"sources":[]});continue
            if not isinstance(c,dict):continue
            text=str(c.get("text",c.get("claim",""))).strip()
            if text:out.append({"id":c.get("id",f"claim_{i+1}"),"text":text,"confidence":c.get("confidence",0),"sources":c.get("sources",[])})
        return out

    def _analyze_claim(self,claim,sources,story):
        text=str(claim.get("text","")).strip();lower=text.lower();risk=0;signals=[];positives=[]
        attributed=any(x in lower for x in self.attribution_patterns)
        if attributed:positives.append("Claim contains attribution language.")
        else:risk+=10;signals.append("Claim has no obvious attribution.")
        if any(x in lower for x in self.uncertainty_words):positives.append("Claim contains uncertainty language.")
        if any(x in lower for x in self.denial_patterns):risk+=20;signals.append("Claim appears to involve a denial or dispute.")
        sensational=[w for w in self.high_risk_words if re.search(rf"\b{re.escape(w)}\b",lower)]
        if sensational:risk+=min(len(sensational)*5,20);signals.append("Sensational wording detected: "+", ".join(sensational[:5]))
        absolute=sum(1 for p in [r"\balways\b",r"\bnever\b",r"\beveryone\b",r"\bnobody\b",r"\b100%\b",r"\bcompletely\b",r"\bdefinitely\b"] if re.search(p,lower))
        if absolute:risk+=min(absolute*6,18);signals.append("Absolute language may indicate excessive certainty.")
        numbers=re.findall(r"\b\d+(?:\.\d+)?%?\b",text)
        if numbers:
            if not attributed:risk+=8;signals.append("Numerical claim requires identifiable evidence.")
            else:positives.append("Claim contains specific numerical information.")
        exceptional=[x for x in ("cure","miracle","secret technology","government cover-up","world-changing","never before","first ever","impossible","proof that") if x in lower]
        if exceptional:risk+=min(len(exceptional)*8,25);signals.append("Exceptional claim requires strong supporting evidence.")
        matches=self._find_claim_sources(claim,sources)
        if not matches:risk+=15;signals.append("No supplied source clearly supports the claim.")
        else:positives.append("At least one supplied source appears relevant to the claim.")
        if len(text.split())<5:risk+=5;signals.append("Claim is too short to evaluate reliably.")
        risk=min(risk,100)
        return {"claim_id":claim.get("id"),"claim":text,"risk_score":risk,"risk_level":self._risk_level(risk),"signals":signals,"positive_signals":positives,"source_matches":matches,"recommendation":self._claim_recommendation(risk)}

    def _find_claim_sources(self,claim,sources):
        words={w for w in re.findall(r"\b[a-zA-Z]{5,}\b",str(claim.get("text","")).lower())}
        if not words:return []
        matches=[]
        for s in sources:
            if not isinstance(s,dict):continue
            st=" ".join([str(s.get("title","")),str(s.get("content",s.get("text","")))]).lower();sw=set(re.findall(r"\b[a-zA-Z]{5,}\b",st));overlap=len(words&sw)/max(len(words),1)
            if overlap>=.20:matches.append(str(s.get("source_id",s.get("id",""))))
        return matches

    def _analyze_sources(self,sources):
        if not sources:return {"score":0,"level":"NO_DATA","warnings":["No source material supplied."],"primary_sources":0,"named_sources":0,"anonymous_sources":0,"social_sources":0}
        primary=anonymous=social=named=0
        for s in sources:
            if not isinstance(s,dict):continue
            typ=str(s.get("type",s.get("source_type",""))).lower();name=str(s.get("name",s.get("publisher",""))).strip()
            primary+=bool(s.get("primary"));anonymous+=typ in {"anonymous","unknown"};social+=self._is_social_source(s);named+=bool(name)
        score=max(0,min(40+min(primary*15,30)+min(named*5,20)-min(anonymous*10,25)-min(social*3,15),100));warnings=[]
        if primary==0:warnings.append("No clear primary source was identified.")
        if anonymous:warnings.append("Anonymous or unidentified sources are present.")
        if social:warnings.append("Social sources should be treated as leads unless independently verified.")
        return {"score":score,"level":self._risk_inverse_level(score),"primary_sources":primary,"named_sources":named,"anonymous_sources":anonymous,"social_sources":social,"warnings":warnings}

    def _analyze_temporal_consistency(self,sources,story):
        dates=[str(s.get("published_at")) for s in sources if isinstance(s,dict) and s.get("published_at")];warnings=[]
        if len(dates)>=2 and len(set(dates))==1:warnings.append("All supplied sources share the same publication timestamp; this may indicate syndicated material.")
        event_date=story.get("event_date")
        if event_date and dates:warnings.append("Event date should be compared with publication dates before publication.")
        return {"source_dates":dates,"event_date":event_date,"warnings":warnings,"status":"REVIEW_REQUIRED" if warnings else "NO_MAJOR_SIGNAL"}
