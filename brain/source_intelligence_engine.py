from typing import Any,Dict,List
from urllib.parse import urlparse
from difflib import SequenceMatcher
import re

class SourceIntelligenceEngine:
    def __init__(self):
        self.name="Source Intelligence Engine";self.version="1.0.0"
        self.source_type_weights={"PRIMARY":100,"OFFICIAL":100,"GOVERNMENT":95,"COURT":95,"REGULATORY":95,"ACADEMIC":90,"ESTABLISHED_NEWS":85,"WIRE":85,"SPECIALIST_MEDIA":80,"LOCAL_NEWS":75,"EXPERT":75,"BLOG":50,"SOCIAL":30,"USER_GENERATED":20,"UNKNOWN":25}
        self.high_risk_source_types={"UNKNOWN","USER_GENERATED"}
        self.social_domains={"twitter.com","x.com","facebook.com","instagram.com","tiktok.com","youtube.com","reddit.com","threads.net"}
        self.official_keywords={"gov","government","official","ministry","court","police","agency","regulator","university"}

    def analyze(self,sources:List[Dict[str,Any]])->Dict[str,Any]:
        normalized=self._normalize_sources(sources);scored=[self._score_source(s) for s in normalized];clusters=self._cluster_sources(scored);independence=self._independence_analysis(scored,clusters);source_chain=self._build_source_chain(scored);conflicts=self._detect_conflicts(scored);overall=self._overall_source_quality(scored,independence,conflicts)
        return {"engine":self.name,"version":self.version,"status":"ANALYZED","source_count":len(scored),"sources":scored,"source_clusters":clusters,"independence":independence,"source_chain":source_chain,"conflicts":conflicts,"overall_quality":overall,"recommendation":self._recommendation(overall,conflicts,independence)}

    def _normalize_sources(self,sources):
        if isinstance(sources,dict):sources=list(sources.values())
        if not isinstance(sources,list):return []
        out=[]
        for i,s in enumerate(sources):
            if isinstance(s,str):s={"url":s}
            if not isinstance(s,dict):continue
            url=str(s.get("url","")).strip();title=str(s.get("title",s.get("headline",""))).strip();name=str(s.get("name",s.get("publisher",""))).strip();typ=str(s.get("type",s.get("source_type","UNKNOWN"))).upper();domain=self._domain(url);name=name or domain or "Unknown Source"
            out.append({"id":s.get("id",f"source_{i+1}"),"url":url,"title":title,"name":name,"domain":domain,"type":typ,"published_at":s.get("published_at"),"retrieved_at":s.get("retrieved_at"),"author":s.get("author"),"text":s.get("text",s.get("excerpt",s.get("description",s.get("content","")))),"primary":bool(s.get("primary",False)),"official":bool(s.get("official",False)),"independent":bool(s.get("independent",False)),"authority":s.get("authority",0),"original_source":s.get("original_source"),"reliability":s.get("reliability"),"freshness_score":s.get("freshness_score")})
        return out

    def _score_source(self,source):
        authority=self._authority_score(source);transparency=self._transparency_score(source);primary=100 if source.get("primary") else 0;freshness=self._freshness_score(source);independence=100 if source.get("independent") else 50;dup=20 if self._is_social_source(source) else 0
        if not source.get("author"):dup+=5
        total=int(max(0,min(authority*.30+transparency*.15+primary*.20+freshness*.10+independence*.10+(100-dup)*.15,100)))
        return {**source,"authority_score":authority,"transparency_score":transparency,"primary_source_score":primary,"freshness_score":freshness,"independence_score":independence,"duplication_risk":dup,"quality_score":total,"classification":self._classification(total)}

    def _authority_score(self,source):
        explicit=source.get("authority")
        if explicit is not None:
            try:
                value=float(explicit)
                if value>0:return int(max(0,min(value,100)))
            except (TypeError,ValueError):pass
        typ=str(source.get("type","UNKNOWN")).upper();score=self.source_type_weights.get(typ,25)
        if source.get("official"):score=max(score,90)
        domain=str(source.get("domain","")).lower()
        if any(k in domain for k in self.official_keywords):score+=5
        return min(score,100)

    def _transparency_score(self,source):
        score=35+15*bool(source.get("name"))+15*bool(source.get("author"))+15*bool(source.get("published_at"))+10*bool(source.get("url"))+10*bool(source.get("text"));return min(score,100)

    def _freshness_score(self,source):
        value=source.get("freshness_score")
        if value is not None:
            try:return int(max(0,min(int(value),100)))
            except (TypeError,ValueError):pass
        return 80 if source.get("published_at") else 50

    def _cluster_sources(self,sources):
        clusters=[]
        for source in sources:
            placed=False
            for cluster in clusters:
                rep=cluster["sources"][0];similarity=self._text_similarity(source.get("title",""),rep.get("title",""));same_original=bool(source.get("original_source")) and source.get("original_source")==rep.get("original_source");same_domain=bool(source.get("domain")) and source.get("domain")==rep.get("domain")
                if similarity>=.45 or same_original or (same_domain and similarity>=.30):cluster["sources"].append(source);placed=True;break
            if not placed:clusters.append({"cluster_id":f"cluster_{len(clusters)+1}","sources":[source]})
        result=[]
        for cluster in clusters:
            cs=cluster["sources"];domains=self._unique([s.get("domain") for s in cs if s.get("domain")]);result.append({"cluster_id":cluster["cluster_id"],"source_count":len(cs),"independent_domains":len(domains),"domains":domains,"primary_sources":[s.get("name") for s in cs if s.get("primary")],"likely_repetition":len(domains)<=1 and len(cs)>1})
        return result
