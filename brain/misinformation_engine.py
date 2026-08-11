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
    def _analyze_duplication(self,sources):
        fingerprints={};groups=[]
        for s in sources:
            if not isinstance(s,dict):continue
            content=self._normalize_text(str(s.get("content",s.get("text",s.get("description","")))))
            if not content:continue
            fp=hashlib.sha256(content.encode()).hexdigest()[:16];fingerprints.setdefault(fp,[]).append(s.get("id",s.get("source_id")))
        for fp,ids in fingerprints.items():
            if len(ids)>1:groups.append({"fingerprint":fp,"source_ids":ids,"count":len(ids),"likely_recycled":True})
        return {"unique_fingerprints":len(fingerprints),"duplicate_groups":groups,"duplicate_group_count":len(groups),"risk":"HIGH" if groups else "LOW"}

    def _overall_assessment(self,claims,sources,temporal,dup):
        claim_risk=sum(c.get("risk_score",0) for c in claims)/len(claims) if claims else 0;source_score=sources.get("score",0);temporal_penalty=min(len(temporal.get("warnings",[]))*8,20);dup_penalty=min(dup.get("duplicate_group_count",0)*10,30);risk=min(100,int(claim_risk*.60+(100-source_score)*.40+temporal_penalty+dup_penalty));level=self._risk_level(risk)
        return {"risk_score":risk,"risk_level":level,"claim_risk_average":round(claim_risk,2),"source_quality_score":source_score,"temporal_penalty":temporal_penalty,"duplication_penalty":dup_penalty,"high_risk":level in {"HIGH","CRITICAL"}}

    def _editorial_action(self,overall):
        level=overall.get("risk_level","LOW")
        if level=="CRITICAL":return {"decision":"BLOCK_PUBLICATION","reason":"Critical misinformation risk detected."}
        if level=="HIGH":return {"decision":"HOLD_FOR_REVIEW","reason":"High misinformation risk requires verification."}
        if level=="MEDIUM":return {"decision":"VERIFY_BEFORE_PUBLICATION","reason":"Additional verification is recommended."}
        return {"decision":"NORMAL_REVIEW","reason":"No major misinformation risk signal detected."}

    def _risk_level(self,score):
        if score>=80:return "CRITICAL"
        if score>=60:return "HIGH"
        if score>=35:return "MEDIUM"
        if score>=15:return "LOW"
        return "MINIMAL"

    def _risk_inverse_level(self,score):
        if score>=80:return "STRONG"
        if score>=60:return "GOOD"
        if score>=40:return "MODERATE"
        return "WEAK"

    def _claim_recommendation(self,risk):
        if risk>=80:return "BLOCK_UNTIL_VERIFIED"
        if risk>=60:return "HUMAN_REVIEW"
        if risk>=35:return "VERIFY_AND_ATTRIBUTE"
        return "NORMAL_REVIEW"

    def _is_social_source(self,source):
        typ=str(source.get("type",source.get("source_type",""))).lower();domain=str(source.get("domain","")).lower().strip()
        if domain.startswith("www."):domain=domain[4:]
        if typ=="social":return True
        if not domain and source.get("url"):
            try:domain=urlparse(str(source["url"])).netloc.lower().removeprefix("www.")
            except Exception:domain=""
        return domain in self.social_domains or any(domain.endswith("."+d) for d in self.social_domains)

    def _normalize_text(self,text):
        text=str(text or "").lower();text=re.sub(r"https?://\S+"," ",text);text=re.sub(r"[^a-z0-9\s]"," ",text);return re.sub(r"\s+"," ",text).strip()

    def _unique(self,values):
        result=[];seen=set()
        for v in values:
            v=str(v or "").strip();k=v.lower()
            if v and k not in seen:seen.add(k);result.append(v)
        return result

    def _number(self,value,default=0):
        try:return float(value)
        except (TypeError,ValueError):return default

    def status(self):
        return {"engine":self.name,"version":self.version,"status":"READY"}

misinformation_engine=MisinformationEngine()

def analyze_misinformation(claims,sources=None,story=None):
    return misinformation_engine.analyze(claims,sources,story)

def analyze(claims,sources=None,story=None):
    return misinformation_engine.analyze(claims,sources,story)
