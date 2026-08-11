import hashlib,re
from collections import Counter
from datetime import datetime
from typing import Any,Dict,List
from urllib.parse import urlparse

class StoryCluster:
    def __init__(self):
        self.name="Story Clustering Engine"
        self.version="1.1.0"
        self.STRONG_MATCH=0.80
        self.POSSIBLE_MATCH=0.60
        self.stop_words={"about","after","again","against","being","before","between","could","from","have","having","into","more","other","over","said","same","some","than","that","their","there","these","they","this","those","through","under","were","which","while","with","would","according"}

    def cluster_stories(self,stories:List[Dict[str,Any]])->List[Dict[str,Any]]:
        if isinstance(stories,dict): stories=list(stories.values())
        if not isinstance(stories,list): return []
        clusters=[]
        for story in stories:
            if not isinstance(story,dict): continue
            placed=False
            for cluster in clusters:
                similarity=self._story_similarity(story,cluster["representative"])
                if similarity>=self.STRONG_MATCH:
                    self._add_to_cluster(cluster,story,similarity)
                    placed=True
                    break
            if not placed: clusters.append(self._create_cluster(story))
        return [self._finalize_cluster(c) for c in clusters]

    def cluster(self,stories):
        return self.cluster_stories(stories)

    def _create_cluster(self,story):
        domain=self._domain(story.get("url",""))
        return {
            "cluster_id":self._generate_cluster_id(story),
            "representative":story,
            "stories":[story],
            "similarity_scores":[],
            "sources":[self._source_name(story)],
            "domains":[domain] if domain else [],
            "created_at":datetime.utcnow().isoformat()
        }

    def _add_to_cluster(self,cluster,story,similarity):
        cluster["stories"].append(story)
        cluster["similarity_scores"].append(round(similarity,4))
        source=self._source_name(story)
        if source and source not in cluster["sources"]: cluster["sources"].append(source)
        domain=self._domain(story.get("url",""))
        if domain and domain not in cluster["domains"]: cluster["domains"].append(domain)

    def _finalize_cluster(self,cluster):
        stories=cluster["stories"]
        source_count=len([s for s in cluster["sources"] if s])
        domain_count=len([d for d in cluster["domains"] if d])
        representative=max(stories,key=self._content_richness)
        return {
            "cluster_id":cluster["cluster_id"],
            "story_count":len(stories),
            "source_count":source_count,
            "independent_domain_count":domain_count,
            "representative":representative,
            "stories":stories,
            "sources":cluster["sources"],
            "domains":cluster["domains"],
            "verification_level":self._verification_level(source_count,domain_count),
            "information_map":self._extract_information_map(stories),
            "coverage_strength":self._coverage_strength(source_count,domain_count),
            "duplicate_risk":self._duplicate_risk(len(stories))
        }

    def _story_similarity(self,first,second):
        title_a=self._normalize(first.get("title",""))
        title_b=self._normalize(second.get("title",""))
        content_a=self._normalize(str(first.get("description",""))+" "+str(first.get("content","")))
        content_b=self._normalize(str(second.get("description",""))+" "+str(second.get("content","")))
        title_similarity=self._token_similarity(title_a,title_b)
        content_similarity=self._token_similarity(content_a,content_b)
        entity_similarity=self._entity_similarity(first,second)
        return round(min(title_similarity*.45+content_similarity*.35+entity_similarity*.20,1.0),4)

    def _token_similarity(self,first,second):
        a=self._tokens(first)
        b=self._tokens(second)
        if not a or not b:return 0.0
        return len(a&b)/len(a|b)

    def _entity_similarity(self,first,second):
        groups=[]
        for key in ("people","locations","organizations","entities"):
            a={str(x).lower() for x in first.get(key,[]) if x}
            b={str(x).lower() for x in second.get(key,[]) if x}
            if a or b:
                groups.append(len(a&b)/len(a|b) if a|b else 0)
        if not groups:return 0.0
        return sum(groups)/len(groups)

    def _extract_entities_from_text(self,text):
        words=re.findall(r"\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*\b",str(text))
        return set(words)

    def _tokens(self,text):
        return {w for w in re.findall(r"\b[a-z0-9]{3,}\b",str(text).lower()) if w not in self.stop_words}

    def _normalize(self,text):
        text=str(text or "").lower()
        text=re.sub(r"https?://\S+"," ",text)
        text=re.sub(r"[^a-z0-9\s]"," ",text)
        return re.sub(r"\s+"," ",text).strip()

    def _content_richness(self,story):
        title=str(story.get("title","") or "")
        content=str(story.get("content",story.get("description","")) or "")
        entities=sum(len(story.get(k,[]) or []) for k in ("people","locations","organizations","entities"))
        return len(content.split())+len(title.split())*2+entities*5

    def _source_name(self,story):
        return str(story.get("source_name",story.get("publisher",story.get("source",""))) or "").strip()

    def _domain(self,url):
        try:
            host=urlparse(str(url)).netloc.lower()
            return host[4:] if host.startswith("www.") else host
        except Exception:
            return ""

    def _generate_cluster_id(self,story):
        raw="|".join([
            str(story.get("title","")),
            str(story.get("url","")),
            str(story.get("published_at",story.get("date","")))
        ])
        return "cluster_"+hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def _verification_level(self,source_count,domain_count):
        if domain_count>=3 and source_count>=3:return "STRONG"
        if domain_count>=2 and source_count>=2:return "MODERATE"
        if source_count>=2:return "LIMITED"
        return "SINGLE_SOURCE"

    def _coverage_strength(self,source_count,domain_count):
        score=min(100,source_count*15+domain_count*20)
        if score>=80:return {"score":score,"classification":"STRONG"}
        if score>=50:return {"score":score,"classification":"MODERATE"}
        if score>=25:return {"score":score,"classification":"LIMITED"}
        return {"score":score,"classification":"WEAK"}

    def _duplicate_risk(self,story_count):
        if story_count>=5:return {"score":95,"classification":"VERY_HIGH"}
        if story_count>=3:return {"score":80,"classification":"HIGH"}
        if story_count>=2:return {"score":60,"classification":"MODERATE"}
        return {"score":10,"classification":"LOW"}

    def _extract_information_map(self,stories):
        info=[]
        seen=set()
        for story in stories:
            source=self._source_name(story)
            content=str(story.get("content",story.get("description","")) or "")
            sentences=re.split(r"(?<=[.!?])\s+",content)
            for sentence in sentences:
                sentence=sentence.strip()
                key=self._normalize(sentence)
                if len(key)>=25 and key not in seen:
                    seen.add(key)
                    info.append({"source":source,"text":sentence})
        return info[:100]

    def compare(self,first,second):
        if not isinstance(first,dict) or not isinstance(second,dict):return 0.0
        return self._story_similarity(first,second)

    def is_duplicate(self,first,second):
        return self._story_similarity(first,second)>=self.STRONG_MATCH

    def __repr__(self):
        return f"<{self.name} v{self.version}>"

def cluster_stories(stories):
    return StoryCluster().cluster_stories(stories)

def run_story_clustering(stories):
    return StoryCluster().cluster_stories(stories)
