from typing import Any,Dict,List
from collections import defaultdict
from urllib.parse import urlparse
import re

class SourceVerificationEngine:
    def __init__(self):
        self.name="Source Verification & Provenance Engine"
        self.version="1.1.0"
        self.source_levels={"PRIMARY":100,"DIRECT_REPORTING":85,"INDEPENDENT_SECONDARY":70,"SPECIALIST":65,"AGGREGATOR":35,"SOCIAL_REPOST":20,"UNKNOWN":10}
        self.minimum_independent_sources=2
        self.social_domains={"twitter.com","x.com","facebook.com","instagram.com","tiktok.com","youtube.com","reddit.com","threads.net"}
        self.aggregator_domains={"news.google.com","news.yahoo.com","flipboard.com","feedly.com"}
        self.primary_keywords={"official","government","gov","ministry","police","court","agency","regulator","university","company"}
    
    def analyze(self,sources:List[Dict[str,Any]])->Dict[str,Any]:
        if isinstance(sources,dict): sources=list(sources.values())
        if not isinstance(sources,list) or not sources:
            return {"engine":self.name,"version":self.version,"status":"NO_SOURCES","confidence":0,"sources":[],"independence":{"independent_count":0}}
        normalized=[self._normalize_source(s) for s in sources if isinstance(s,(dict,str))]
        clusters=self._build_provenance_clusters(normalized)
        independent=self._find_independent_sources(normalized)
        primary=[s for s in normalized if s.get("classification")=="PRIMARY"]
        source_score=self._calculate_source_score(normalized)
        independence_score=self._calculate_independence_score(independent)
        provenance_score=self._calculate_provenance_score(normalized,clusters)
        confidence=self._overall_confidence(source_score,independence_score,provenance_score)
        warnings=self._generate_warnings(normalized,independent,clusters)
        return {
            "engine":self.name,
            "version":self.version,
            "status":"ANALYZED",
            "source_count":len(normalized),
            "primary_source_count":len(primary),
            "independent_source_count":len(independent),
            "source_score":source_score,
            "independence_score":independence_score,
            "provenance_score":provenance_score,
            "confidence":confidence,
            "sources":normalized,
            "provenance_clusters":clusters,
            "warnings":warnings,
            "independence":{"independent_count":len(independent),"domains":self._unique_domains(independent)},
            "recommendation":self._recommendation(confidence,warnings)
        }

    def _normalize_source(self,source):
        if isinstance(source,str): source={"url":source,"title":"","content":""}
        if not isinstance(source,dict): return {}
        url=str(source.get("url","")).strip()
        title=str(source.get("title",source.get("headline","")) or "").strip()
        name=str(source.get("name",source.get("publisher","")) or "").strip()
        content=str(source.get("content",source.get("text",source.get("body",""))) or "").strip()
        domain=self._domain(url)
        source_type=str(source.get("source_type",source.get("type","UNKNOWN")) or "UNKNOWN").upper()
        original=str(source.get("original_source","") or "").strip()
        classification=self._classify_source(source_type,domain,source,original)
        return {
            "source_id":source.get("source_id",source.get("id",f"source_{abs(hash((url,title,content)))%100000000}")),
            "name":name or domain or "Unknown Source",
            "url":url,
            "domain":domain,
            "title":title,
            "content":content,
            "text":content,
            "author":source.get("author",""),
            "published_at":source.get("published_at"),
            "updated_at":source.get("updated_at"),
            "source_type":source_type,
            "classification":classification,
            "original_source":original,
            "verified":bool(source.get("verified",False)),
            "primary":bool(source.get("primary",False)) or classification=="PRIMARY",
            "independent":bool(source.get("independent",False)),
            "quality_score":self._source_quality(source,classification,domain),
            "content_fingerprint":self._fingerprint(title+" "+content)
        }

    def _classify_source(self,source_type,domain,source,original):
        if source.get("primary") or source.get("official"): return "PRIMARY"
        if original and self._domain(original) and self._domain(original)!=domain:
            return "AGGREGATOR" if domain in self.aggregator_domains else "DIRECT_REPORTING"
        if domain in self.social_domains: return "SOCIAL_REPOST"
        if domain in self.aggregator_domains: return "AGGREGATOR"
        mapping={"PRIMARY":"PRIMARY","OFFICIAL":"PRIMARY","GOVERNMENT":"PRIMARY","COURT":"PRIMARY","REGULATORY":"PRIMARY","DIRECT_REPORTING":"DIRECT_REPORTING","WIRE":"DIRECT_REPORTING","ESTABLISHED_NEWS":"DIRECT_REPORTING","SPECIALIST":"SPECIALIST","SPECIALIST_MEDIA":"SPECIALIST","INDEPENDENT_SECONDARY":"INDEPENDENT_SECONDARY","SECONDARY":"INDEPENDENT_SECONDARY","AGGREGATOR":"AGGREGATOR","SOCIAL":"SOCIAL_REPOST","SOCIAL_REPOST":"SOCIAL_REPOST","USER_GENERATED":"UNKNOWN","UNKNOWN":"UNKNOWN"}
        return mapping.get(source_type,"UNKNOWN")

    def _source_quality(self,source,classification,domain):
        score=self.source_levels.get(classification,10)
        if source.get("verified"): score+=5
        if source.get("author"): score+=3
        if source.get("published_at"): score+=3
        if source.get("url"): score+=3
        if source.get("content") or source.get("text") or source.get("body"): score+=3
        return min(100,score)

    def _build_provenance_clusters(self,sources):
        clusters=[]
        for source in sources:
            placed=False
            for cluster in clusters:
                rep=cluster["sources"][0]
                same_original=bool(source.get("original_source") and source.get("original_source")==rep.get("original_source"))
                same_fingerprint=source.get("content_fingerprint")==rep.get("content_fingerprint")
                similar=self._similarity(source.get("title",""),rep.get("title",""))
                if same_original or same_fingerprint or similar>=0.55:
                    cluster["sources"].append(source)
                    placed=True
                    break
            if not placed:
                clusters.append({"cluster_id":f"provenance_{len(clusters)+1}","sources":[source]})
        result=[]
        for cluster in clusters:
            ss=cluster["sources"]
            domains=self._unique_domains(ss)
            result.append({
                "cluster_id":cluster["cluster_id"],
                "source_count":len(ss),
                "domains":domains,
                "independent_domains":len(domains),
                "sources":[s.get("source_id") for s in ss],
                "names":[s.get("name") for s in ss],
                "primary_sources":[s.get("name") for s in ss if s.get("classification")=="PRIMARY"],
                "likely_repetition":len(ss)>1 and len(domains)<=1
            })
        return result

    def _find_independent_sources(self,sources):
        seen=set()
        result=[]
        for source in sorted(sources,key=lambda x:x.get("quality_score",0),reverse=True):
            domain=source.get("domain") or source.get("source_id")
            if domain in seen: continue
            if source.get("classification") in {"SOCIAL_REPOST","AGGREGATOR"}: continue
            seen.add(domain)
            result.append(source)
        return result

    def _calculate_source_score(self,sources):
        if not sources:return 0
        return round(sum(s.get("quality_score",0) for s in sources)/len(sources),2)

    def _calculate_independence_score(self,sources):
        count=len(sources)
        if count==0:return 0
        return min(100,count*35)

    def _calculate_provenance_score(self,sources,clusters):
        if not sources:return 0
        score=sum(s.get("quality_score",0) for s in sources)/len(sources)
        repetition=sum(1 for c in clusters if c.get("likely_repetition"))
        score-=min(30,repetition*15)
        if any(s.get("classification")=="PRIMARY" for s in sources): score+=10
        return round(max(0,min(100,score)),2)

    def _overall_confidence(self,source_score,independence_score,provenance_score):
        score=source_score*.35+independence_score*.30+provenance_score*.35
        return round(max(0,min(100,score)),2)

    def _generate_warnings(self,sources,independent,clusters):
        warnings=[]
        if len(sources)==1:
            warnings.append("Only one source is available; independent confirmation is missing.")
        if len(independent)<self.minimum_independent_sources:
            warnings.append("Fewer than two independent sources are available.")
        if not any(s.get("classification")=="PRIMARY" for s in sources):
            warnings.append("No clear primary source was identified.")
        if any(c.get("likely_repetition") for c in clusters):
            warnings.append("Multiple reports may originate from the same underlying source.")
        if any(s.get("classification")=="SOCIAL_REPOST" for s in sources):
            warnings.append("Social reposts should not be counted as independent confirmation.")
        if any(s.get("classification")=="UNKNOWN" for s in sources):
            warnings.append("One or more sources have unknown provenance.")
        return warnings

    def _recommendation(self,confidence,warnings):
        if confidence>=80 and not warnings:
            return "STRONG_PROVENANCE"
        if confidence>=65:
            return "PROVISIONALLY_SUPPORTED"
        if confidence>=45:
            return "NEEDS_ADDITIONAL_VERIFICATION"
        return "WEAK_PROVENANCE"

    def _unique_domains(self,sources):
        return sorted({s.get("domain") for s in sources if s.get("domain")})

    def _domain(self,url):
        try:
            host=urlparse(str(url)).netloc.lower()
            return host[4:] if host.startswith("www.") else host
        except Exception:
            return ""

    def _fingerprint(self,text):
        text=re.sub(r"[^a-z0-9\s]"," ",str(text).lower())
        return " ".join(text.split())[:500]

    def _similarity(self,a,b):
        a=set(re.findall(r"\b[a-z]{4,}\b",str(a).lower()))
        b=set(re.findall(r"\b[a-z]{4,}\b",str(b).lower()))
        if not a or not b:return 0
        return len(a&b)/max(1,len(a|b))

    def __repr__(self):
        return f"<{self.name} v{self.version}>"

def verify_sources(sources):
    return SourceVerificationEngine().analyze(sources)
