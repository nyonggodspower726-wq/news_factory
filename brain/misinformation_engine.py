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
