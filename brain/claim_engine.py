from typing import Any,Dict,List
from collections import defaultdict
import re
class ClaimEngine:
    def __init__(self):
        self.name="Claim & Evidence Engine"
        self.version="1.2.0"
        self.status_weights={"VERIFIED":100,"WELL_SUPPORTED":85,"PARTIALLY_SUPPORTED":60,"UNVERIFIED":25,"CONTRADICTED":0,"OPINION":50,"PREDICTION":40,"ATTRIBUTED_CLAIM":65}
    def analyze(self,story:Dict[str,Any])->Dict[str,Any]:
        story=story if isinstance(story,dict) else {}
        claims=self._extract_claims(story)
        evidence=self._extract_evidence(story)
        analyzed_claims=[]
        for claim in claims:
            matched=self._match_evidence(claim,evidence)
            analyzed_claims.append(self._assess_claim(claim,matched))
        summary=self._build_summary(analyzed_claims)
        publication_status=self._publication_status(analyzed_claims)
        return {"engine":self.name,"version":self.version,"status":"ANALYZED","claim_count":len(analyzed_claims),"claims":analyzed_claims,"summary":summary,"publication_status":publication_status}
    def _extract_claims(self,story:Dict[str,Any])->List[Dict[str,Any]]:
        raw=story.get("claims")
        claims=[]
        if isinstance(raw,list):
            for item in raw:
                if isinstance(item,str):
                    text=item.strip()
                    if text:
                        claims.append({"id":None,"text":text,"type":self._infer_claim_type(text),"importance":"NORMAL","attribution":None})
                elif isinstance(item,dict):
                    text=str(item.get("text",item.get("claim",item.get("statement",""))) or "").strip()
                    if text:
                        claims.append({"id":item.get("id") or item.get("claim_id"),"text":text,"type":str(item.get("type","FACT") or "FACT").upper(),"importance":str(item.get("importance","NORMAL") or "NORMAL").upper(),"attribution":item.get("attribution")})
        if claims:
            return self._deduplicate_claims(claims)
        bodies=[]
        body=str(story.get("body",story.get("content",story.get("summary",story.get("description","")))) or "").strip()
        if body:
            bodies.append((body,None))
        sources=story.get("sources",[])
        if isinstance(sources,dict):
            sources=list(sources.values())
        if isinstance(sources,list):
            for source in sources:
                if not isinstance(source,dict):
                    continue
                content=str(source.get("content",source.get("text",source.get("description",source.get("excerpt",source.get("summary",""))))) or "").strip()
                if content:
                    source_name=source.get("name") or source.get("publisher") or source.get("source_id") or source.get("source")
                    bodies.append((content,source_name))
        for text,attribution in bodies:
            for sentence in self._sentences(text):
                if len(sentence)<15:
                    continue
                claims.append({"id":None,"text":sentence,"type":self._infer_claim_type(sentence),"importance":"NORMAL","attribution":attribution})
        return self._deduplicate_claims(claims)
    def _sentences(self,text:str)->List[str]:
        text=re.sub(r"\s+"," ",text).strip()
        if not text:
            return []
        return [x.strip() for x in re.split(r"(?<=[.!?])\s+",text) if x.strip()]
    def _extract_evidence(self,story:Dict[str,Any])->List[Dict[str,Any]]:
        raw=story.get("evidence")
        if raw is None:
            raw=story.get("sources",[])
        if isinstance(raw,dict):
            raw=list(raw.values())
        if not isinstance(raw,list):
            return []
        evidence=[]
        for index,item in enumerate(raw):
            if isinstance(item,str):
                text=item.strip()
                if text:
                    evidence.append({"id":f"evidence_{index+1}","text":text,"source":None,"type":"UNKNOWN","authority":30,"independent":False,"primary":False,"supports":[],"contradicts":[]})
                continue
            if not isinstance(item,dict):
                continue
            text=str(item.get("text",item.get("content",item.get("excerpt",item.get("description",item.get("summary",""))))) or "").strip()
            if not text:
                continue
            source=item.get("source") or item.get("publisher") or item.get("source_url") or item.get("url") or item.get("source_id")
            domain=self._domain(source)
            try:
                authority=float(item.get("authority",0) or 0)
            except (TypeError,ValueError):
                authority=0
            primary=bool(item.get("primary",False))
            independent=bool(item.get("independent",False))
            if authority<=0:
                authority=self._source_authority(source,domain)
            supports=item.get("supports",[])
            contradicts=item.get("contradicts",[])
            if isinstance(supports,str):
                supports=[supports]
            if not isinstance(supports,list):
                supports=[]
            if isinstance(contradicts,str):
                contradicts=[contradicts]
            if not isinstance(contradicts,list):
                contradicts=[]
            evidence.append({"id":item.get("id") or item.get("source_id") or f"evidence_{index+1}","text":text,"source":source,"type":str(item.get("type","SOURCE") or "SOURCE").upper(),"authority":authority,"independent":independent,"primary":primary,"supports":supports,"contradicts":contradicts,"contradiction":bool(item.get("contradiction",False))})
        return evidence
    def _match_evidence(self,claim:Dict[str,Any],evidence:List[Dict[str,Any]])->List[Dict[str,Any]]:
        claim_id=claim.get("id")
        claim_text=str(claim.get("text","")).lower()
        matched=[]
        for item in evidence:
            supports=item.get("supports",[])
            contradicts=item.get("contradicts",[])
            if claim_id and claim_id in supports:
                matched.append(item)
                continue
            if claim_id and claim_id in contradicts:
                matched.append(item)
                continue
            evidence_text=str(item.get("text","")).lower()
            similarity=self._text_similarity(claim_text,evidence_text)
            if similarity>=0.12 or self._key_phrase_match(claim_text,evidence_text):
                matched.append(item)
        return matched
    def _assess_claim(self,claim:Dict[str,Any],evidence:List[Dict[str,Any]])->Dict[str,Any]:
        claim_type=str(claim.get("type","FACT") or "FACT").upper()
        if claim_type in {"OPINION","COMMENTARY"}:
            status="OPINION"
        elif claim_type in {"PREDICTION","FORECAST"}:
            status="PREDICTION"
        elif claim_type in {"ATTRIBUTED","ATTRIBUTED_CLAIM"}:
            status="ATTRIBUTED_CLAIM"
        else:
            status=self._evidence_status(evidence,claim)
        contradictions=[x for x in evidence if self._evidence_contradicts(x,claim)]
        if contradictions:
            status="CONTRADICTED"
        return {"claim_id":claim.get("id"),"claim":claim.get("text",""),"type":claim_type,"importance":claim.get("importance","NORMAL"),"attribution":claim.get("attribution"),"status":status,"support_score":self._support_score(evidence),"evidence_count":len(evidence),"independent_evidence_count":self._independent_count(evidence),"primary_evidence_count":sum(1 for x in evidence if x.get("primary",False)),"contradiction_count":len(contradictions),"evidence":[{"id":x.get("id"),"source":x.get("source"),"domain":self._domain(x.get("source")),"type":x.get("type"),"authority":x.get("authority",0),"primary":x.get("primary",False),"independent":x.get("independent",False)} for x in evidence]}
    def _evidence_status(self,evidence:List[Dict[str,Any]],claim:Dict[str,Any])->str:
        if not evidence:
            return "UNVERIFIED"
        if any(self._evidence_contradicts(x,claim) for x in evidence):
            return "CONTRADICTED"
        independent=self._independent_count(evidence)
        primary=sum(1 for x in evidence if x.get("primary",False))
        score=self._support_score(evidence)
        if primary>=1 and score>=75:
            return "VERIFIED"
        if independent>=2 and score>=70:
            return "WELL_SUPPORTED"
        if score>=45:
            return "PARTIALLY_SUPPORTED"
        return "UNVERIFIED"
    def _support_score(self,evidence:List[Dict[str,Any]])->int:
        if not evidence:
            return 0
        scores=[]
        for item in evidence:
            try:
                authority=float(item.get("authority",0) or 0)
            except (TypeError,ValueError):
                authority=0
            if authority<=0:
                if item.get("primary",False):
                    authority=100
                elif item.get("independent",False):
                    authority=70
                else:
                    authority=30
            scores.append(authority)
        strongest=max(scores)
        bonus=min(self._independent_count(evidence)*10,30)
        return int(min(strongest+bonus,100))
    def _evidence_contradicts(self,evidence:Dict[str,Any],claim:Dict[str,Any])->bool:
        contradictions=evidence.get("contradicts",[])
        claim_id=claim.get("id")
        if claim_id and claim_id in contradictions:
            return True
        return bool(evidence.get("contradiction",False))
    def _independent_count(self,evidence:List[Dict[str,Any]])->int:
        domains=set()
        for item in evidence:
            if not item.get("independent",False):
                continue
            source=item.get("source") or item.get("id")
            domain=self._domain(source)
            if domain:
                domains.add(domain)
        return len(domains)
