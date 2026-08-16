from typing import Any,Dict,List
from collections import defaultdict
import re
class ClaimEngine:
    def __init__(self):
        self.name="Claim & Evidence Engine"
        self.version="1.1.0"
        self.status_weights={"VERIFIED":100,"WELL_SUPPORTED":85,"PARTIALLY_SUPPORTED":60,"UNVERIFIED":25,"CONTRADICTED":0,"OPINION":50,"PREDICTION":40,"ATTRIBUTED_CLAIM":65}
    def analyze(self,story:Dict[str,Any])->Dict[str,Any]:
        claims=self._extract_claims(story)
        evidence=self._extract_evidence(story)
        analyzed_claims=[]
        for claim in claims:
            matched_evidence=self._match_evidence(claim,evidence)
            analyzed_claims.append(self._assess_claim(claim,matched_evidence))
        summary=self._build_summary(analyzed_claims)
        publication_status=self._publication_status(analyzed_claims)
        return {"engine":self.name,"version":self.version,"status":"ANALYZED","claim_count":len(analyzed_claims),"claims":analyzed_claims,"summary":summary,"publication_status":publication_status}
    def _extract_claims(self,story:Dict[str,Any])->List[Dict[str,Any]]:
        raw_claims=story.get("claims")
        claims=[]
        if isinstance(raw_claims,list):
            for item in raw_claims:
                if isinstance(item,str):
                    text=item.strip()
                    if text:
                        claims.append({"text":text,"type":self._infer_claim_type(text),"importance":"NORMAL","attribution":None})
                elif isinstance(item,dict):
                    text=str(item.get("text",item.get("claim",""))).strip()
                    if text:
                        claims.append({"id":item.get("id"),"text":text,"type":item.get("type","FACT"),"importance":item.get("importance","NORMAL"),"attribution":item.get("attribution")})
        if claims:
            return claims
        body=str(story.get("body",story.get("summary","")) or "").strip()
        if not body:
            sources=story.get("sources",[])
            if isinstance(sources,dict):
                sources=list(sources.values())
            if isinstance(sources,list):
                for source in sources:
                    if isinstance(source,dict):
                        content=str(source.get("content",source.get("text",source.get("description",source.get("excerpt","")))) or "").strip()
                        if content:
                            source_name=source.get("name") or source.get("source_id") or source.get("source")
                            sentences=re.split(r"(?<=[.!?])\s+",content)
                            for sentence in sentences:
                                sentence=sentence.strip()
                                if len(sentence)>=15:
                                    claims.append({"id":None,"text":sentence,"type":self._infer_claim_type(sentence),"importance":"NORMAL","attribution":source_name})
                if claims:
                    return self._deduplicate_claims(claims)
        sentences=re.split(r"(?<=[.!?])\s+",body)
        for sentence in sentences:
            sentence=sentence.strip()
            if len(sentence)<15:
                continue
            claims.append({"text":sentence,"type":self._infer_claim_type(sentence),"importance":"NORMAL","attribution":None})
        return self._deduplicate_claims(claims)
    def _extract_evidence(self,story:Dict[str,Any])->List[Dict[str,Any]]:
        raw=story.get("evidence",story.get("sources",[]))
        evidence=[]
        if isinstance(raw,dict):
            raw=list(raw.values())
        if not isinstance(raw,list):
            return []
        for item in raw:
            if isinstance(item,str):
                text=item.strip()
                if text:
                    evidence.append({"text":text,"source":None,"type":"UNKNOWN","authority":0,"independent":False,"primary":False,"supports":[],"contradicts":[]})
            elif isinstance(item,dict):
                text=str(item.get("text",item.get("content",item.get("excerpt",item.get("description","")))) or "").strip()
                if not text:
                    continue
                source=item.get("source") or item.get("url") or item.get("source_id")
                domain=self._domain(source)
                authority=float(item.get("authority",0) or 0)
                primary=bool(item.get("primary",False))
                independent=bool(item.get("independent",False))
                if authority<=0:
                    authority=self._source_authority(source,domain)
                if not independent:
                    independent=True
                evidence.append({"id":item.get("id") or item.get("source_id"),"text":text,"source":source,"type":item.get("type","SOURCE"),"authority":authority,"independent":independent,"primary":primary,"supports":item.get("supports",[]),"contradicts":item.get("contradicts",[])})
        return evidence
    def _match_evidence(self,claim:Dict[str,Any],evidence:List[Dict[str,Any]])->List[Dict[str,Any]]:
        claim_id=claim.get("id")
        claim_text=claim["text"].lower()
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
        claim_type=str(claim.get("type","FACT")).upper()
        if claim_type in {"OPINION","COMMENTARY"}:
            status="OPINION"
        elif claim_type in {"PREDICTION","FORECAST"}:
            status="PREDICTION"
        else:
            status=self._evidence_status(evidence)
        support_score=self._support_score(evidence)
        contradictions=[item for item in evidence if self._evidence_contradicts(item,claim)]
        if contradictions:
            status="CONTRADICTED"
        return {"claim":claim["text"],"type":claim_type,"importance":claim.get("importance","NORMAL"),"attribution":claim.get("attribution"),"status":status,"support_score":support_score,"evidence_count":len(evidence),"independent_evidence_count":self._independent_count(evidence),"primary_evidence_count":sum(1 for item in evidence if item.get("primary",False)),"contradiction_count":len(contradictions),"evidence":[{"source":item.get("source"),"type":item.get("type"),"primary":item.get("primary",False),"independent":item.get("independent",False)} for item in evidence]}
    def _evidence_status(self,evidence:List[Dict[str,Any]])->str:
        if not evidence:
            return "UNVERIFIED"
        contradictions=[item for item in evidence if item.get("contradicts")]
        if contradictions:
            return "CONTRADICTED"
        independent=self._independent_count(evidence)
        primary=sum(1 for item in evidence if item.get("primary",False))
        support_score=self._support_score(evidence)
        if primary>=1 and support_score>=75:
            return "VERIFIED"
        if independent>=2 and support_score>=70:
            return "WELL_SUPPORTED"
        if support_score>=45:
            return "PARTIALLY_SUPPORTED"
        return "UNVERIFIED"
    def _support_score(self,evidence:List[Dict[str,Any]])->int:
        if not evidence:
            return 0
        scores=[]
        for item in evidence:
            authority=float(item.get("authority",0) or 0)
            if authority<=0:
                authority=100 if item.get("primary",False) else 70 if item.get("independent",False) else 30
            scores.append(authority)
        strongest=max(scores)
        independent_bonus=min(self._independent_count(evidence)*10,30)
        return int(min(strongest+independent_bonus,100))
    def _evidence_contradicts(self,evidence:Dict[str,Any],claim:Dict[str,Any])->bool:
        contradictions=evidence.get("contradicts",[])
        claim_id=claim.get("id")
        if claim_id and claim_id in contradictions:
            return True
        return bool(evidence.get("contradiction",False))
    def _independent_count(self,evidence:List[Dict[str,Any]])->int:
        sources=set()
        for item in evidence:
            if not item.get("independent",False):
                continue
            source=item.get("source") or item.get("id")
            if source:
                domain=self._domain(str(source))
                sources.add(domain or str(source))
        return len(sources)
    def _build_summary(self,claims:List[Dict[str,Any]])->Dict[str,Any]:
        counts=defaultdict(int)
        for claim in claims:
            counts[claim["status"]]+=1
        total=len(claims)
        supported=counts["VERIFIED"]+counts["WELL_SUPPORTED"]
        return {"total_claims":total,"verified":counts["VERIFIED"],"well_supported":counts["WELL_SUPPORTED"],"partially_supported":counts["PARTIALLY_SUPPORTED"],"unverified":counts["UNVERIFIED"],"contradicted":counts["CONTRADICTED"],"opinions":counts["OPINION"],"predictions":counts["PREDICTION"],"support_rate":round(supported/max(total,1)*100,2)}
    def _publication_status(self,claims:List[Dict[str,Any]])->str:
        if not claims:
            return "NO_CLAIMS"
        critical_unverified=0
        contradicted=0
        for claim in claims:
            if claim["status"]=="CONTRADICTED":
                contradicted+=1
            if claim["status"]=="UNVERIFIED" and str(claim.get("importance","")).upper() in {"HIGH","CRITICAL"}:
                critical_unverified+=1
        if contradicted>0:
            return "HOLD_FOR_REVIEW"
        if critical_unverified>0:
            return "HOLD_FOR_VERIFICATION"
        return "READY_FOR_EDITOR_REVIEW"
    def _infer_claim_type(self,sentence:str)->str:
        lowered=sentence.lower()
        opinion_markers=["i think","in my view","arguably","should","must","best"]
        prediction_markers=["could","may","might","expected to","likely","forecast"]
        if any(marker in lowered for marker in opinion_markers):
            return "OPINION"
        if any(marker in lowered for marker in prediction_markers):
            return "PREDICTION"
        return "FACT"
    def _text_similarity(self,text_a:str,text_b:str)->float:
        words_a=set(self._tokens(text_a))
        words_b=set(self._tokens(text_b))
        if not words_a or not words_b:
            return 0.0
        intersection=words_a&words_b
        union=words_a|words_b
        return len(intersection)/max(len(union),1)
    def _key_phrase_match(self,text_a:str,text_b:str)->bool:
        a=set(self._tokens(text_a))
        b=set(self._tokens(text_b))
        if len(a)<3 or len(b)<3:
            return False
        common=a&b
        return len(common)>=3 and len(common)/max(min(len(a),len(b)),1)>=0.25
    def _tokens(self,text:str)->List[str]:
        return re.findall(r"\b[a-z0-9]{3,}\b",text.lower())
    def _domain(self,url:Any)->str:
        if not url:
            return ""
        match=re.search(r"https?://(?:www\.)?([^/]+)",str(url).lower())
        return match.group(1) if match else str(url).lower()
    def _source_authority(self,source:Any,domain:str)->float:
        d=(domain or "").lower()
        if "nasa.gov" in d:
            return 100
        if "esa.int" in d:
            return 95
        if "reuters.com" in d:
            return 90
        return 60
    def _deduplicate_claims(self,claims:List[Dict[str,Any]])->List[Dict[str,Any]]:
        result=[]
        seen=set()
        for claim in claims:
            key=re.sub(r"\s+"," ",claim["text"].strip().lower())
            if key and key not in seen:
                seen.add(key)
                result.append(claim)
        return result
def analyze_claims(story:Dict[str,Any])->Dict[str,Any]:
    return ClaimEngine().analyze(story)
