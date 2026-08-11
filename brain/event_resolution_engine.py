from typing import Any,Dict,List,Set
from datetime import datetime
import re

class EventResolutionEngine:
    def __init__(self):
        self.name="Event Resolution Intelligence Engine"
        self.version="1.0.0"
        self.event_words={"attack","arrest","election","protest","explosion","fire","flood","earthquake","crash","accident","court","ruling","verdict","resignation","appointment","launch","meeting","summit","agreement","deal","strike","war","conflict","death","killing","injury","announcement","ban","sanction","outage","recall","investigation"}
        self.stop_words={"this","that","with","from","have","were","been","will","they","their","about","after","before","said","says","into","what","when","where","which","there","while","would","could","should"}

    def resolve(self,events:List[Dict[str,Any]])->Dict[str,Any]:
        events=self._normalize_events(events);relationships=[]
        for i,first in enumerate(events):
            for second in events[i+1:]:
                comparison=self._compare_events(first,second)
                if comparison["relationship"]!="DIFFERENT":
                    relationships.append({"event_a":first.get("event_id"),"event_b":second.get("event_id"),**comparison})
        clusters=self._build_clusters(events,relationships)
        timeline=self._build_timeline(events,clusters)
        duplicates=self._find_duplicate_groups(clusters)
        evolving=self._find_evolving_events(clusters,relationships)
        return {"engine":self.name,"version":self.version,"status":"EVENT_RESOLUTION_COMPLETE","event_count":len(events),"relationships":relationships,"clusters":clusters,"duplicate_event_groups":duplicates,"evolving_events":evolving,"timeline":timeline}

    def _normalize_events(self,events):
        if not isinstance(events,list):return []
        out=[]
        for i,event in enumerate(events):
            if isinstance(event,str):event={"title":event}
            if not isinstance(event,dict):continue
            event_id=str(event.get("event_id",event.get("id",f"event:{i+1}")))
            title=str(event.get("title",event.get("headline",""))).strip()
            description=str(event.get("description",event.get("summary",event.get("content","")))).strip()
            entities=event.get("entities",{})
            if not isinstance(entities,dict):entities={}
            out.append({"event_id":event_id,"title":title,"description":description,"text":f"{title} {description}".strip(),"people":self._entity_values(entities,"people"),"organizations":self._entity_values(entities,"organizations"),"locations":self._entity_values(entities,"locations"),"date":self._extract_date(event),"time":self._extract_time(event),"source_id":event.get("source_id"),"published_at":event.get("published_at"),"event_type":event.get("event_type","")})
        return out

    def _entity_values(self,entities,key):
        values=entities.get(key,[])
        if isinstance(values,str):values=[values]
        if not isinstance(values,list):return set()
        return {self._normalize_text(v) for v in values if str(v).strip()}

    def _compare_events(self,first,second):
        title_score=self._similarity(first.get("title",""),second.get("title",""))
        content_score=self._similarity(first.get("text",""),second.get("text",""))
        people_score=self._set_similarity(first.get("people",set()),second.get("people",set()))
        organization_score=self._set_similarity(first.get("organizations",set()),second.get("organizations",set()))
        location_score=self._set_similarity(first.get("locations",set()),second.get("locations",set()))
        date_score=self._date_similarity(first.get("date"),second.get("date"))
        event_type_score=self._text_exact_score(first.get("event_type",""),second.get("event_type",""))
        total=min(1.0,title_score*.20+content_score*.25+people_score*.15+organization_score*.10+location_score*.15+date_score*.10+event_type_score*.05)
        same_location=location_score>=.80 and bool(first.get("locations"))
        same_people=people_score>=.80 and bool(first.get("people"))
        same_date=date_score>=.90
        strong_text=title_score>=.65 or content_score>=.60

        if total>=.78 and (same_location or same_people or same_date) and strong_text:
            relationship="SAME_EVENT"
        elif total>=.55:
            relationship="RELATED"
        elif self._developing_relationship(first,second):
            relationship="EVOLVING_EVENT"
        else:
            relationship="DIFFERENT"

        return {"relationship":relationship,"confidence":round(total,3),"signals":{"title_similarity":round(title_score,3),"content_similarity":round(content_score,3),"people_similarity":round(people_score,3),"organization_similarity":round(organization_score,3),"location_similarity":round(location_score,3),"date_similarity":round(date_score,3),"event_type_similarity":round(event_type_score,3)}}

    def _developing_relationship(self,first,second):
        shared_people=first.get("people",set())&second.get("people",set())
        shared_orgs=first.get("organizations",set())&second.get("organizations",set())
        shared_locations=first.get("locations",set())&second.get("locations",set())
        return bool((shared_people and shared_locations) or (shared_orgs and shared_locations))

    def _build_clusters(self,events,relationships):
        adjacency={e.get("event_id"):set() for e in events}
        for r in relationships:
            if r.get("relationship") not in {"SAME_EVENT","EVOLVING_EVENT"}:continue
            a,b=r.get("event_a"),r.get("event_b")
            if a in adjacency:adjacency[a].add(b)
            if b in adjacency:adjacency[b].add(a)

        clusters=[];visited=set()
        for event_id in adjacency:
            if event_id in visited:continue
            stack=[event_id];ids=[]
            while stack:
                current=stack.pop()
                if current in visited:continue
                visited.add(current);ids.append(current);stack.extend(adjacency.get(current,set())-visited)
            clusters.append({"cluster_id":f"event_cluster_{len(clusters)+1}","event_ids":ids,"size":len(ids),"cluster_type":"DUPLICATE_OR_DEVELOPING" if len(ids)>1 else "SINGLE_EVENT"})
        return clusters
    def _find_duplicate_groups(self,clusters):
        duplicates=[]
        for cluster in clusters:
            if cluster.get("size",0)<=1:continue
            duplicates.append({"cluster_id":cluster.get("cluster_id"),"event_ids":cluster.get("event_ids",[]),"recommendation":"Merge reports into one event record and preserve source-specific updates."})
        return duplicates

    def _find_evolving_events(self,clusters,relationships):
        return [{"event_a":r.get("event_a"),"event_b":r.get("event_b"),"confidence":r.get("confidence"),"recommendation":"Treat as potentially related developments and verify chronology before merging."} for r in relationships if r.get("relationship")=="EVOLVING_EVENT"]

    def _build_timeline(self,events,clusters):
        event_map={e.get("event_id"):e for e in events}
        timeline=[]
        for cluster in clusters:
            items=[event_map[eid] for eid in cluster.get("event_ids",[]) if eid in event_map]
            items.sort(key=lambda e:str(e.get("published_at","")))
            for index,event in enumerate(items,1):
                timeline.append({"cluster_id":cluster.get("cluster_id"),"sequence":index,"event_id":event.get("event_id"),"title":event.get("title",""),"date":event.get("date"),"time":event.get("time"),"published_at":event.get("published_at"),"source_id":event.get("source_id")})
        return timeline

    def _extract_date(self,event):
        for key in ("date","event_date","published_at","published","datetime"):
            value=event.get(key)
            if value:
                text=str(value)
                match=re.search(r"\b\d{4}-\d{2}-\d{2}\b",text)
                if match:return match.group(0)
                match=re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",text)
                if match:return match.group(0)
        return None

    def _extract_time(self,event):
        for key in ("time","event_time","datetime","published_at"):
            value=event.get(key)
            if value:
                match=re.search(r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s?[APap][Mm])?\b",str(value))
                if match:return match.group(0)
        return None

    def _normalize_text(self,text):
        text=str(text or "").lower()
        text=re.sub(r"https?://\S+"," ",text)
        text=re.sub(r"[^a-z0-9\s]"," ",text)
        text=re.sub(r"\s+"," ",text).strip()
        return " ".join(w for w in text.split() if w not in self.stop_words)

    def _tokens(self,text):
        return set(self._normalize_text(text).split())

    def _similarity(self,a,b):
        a=self._normalize_text(a);b=self._normalize_text(b)
        if not a or not b:return 0.0
        if a==b:return 1.0
        return len(self._tokens(a)&self._tokens(b))/max(len(self._tokens(a)|self._tokens(b)),1)

    def _set_similarity(self,a,b):
        a=set(a or set());b=set(b or set())
        if not a and not b:return 1.0
        if not a or not b:return 0.0
        return len(a&b)/max(len(a|b),1)

    def _text_exact_score(self,a,b):
        a=self._normalize_text(a);b=self._normalize_text(b)
        if not a or not b:return 0.0
        return 1.0 if a==b else self._similarity(a,b)

    def _date_similarity(self,a,b):
        if not a or not b:return 0.0
        return 1.0 if str(a)==str(b) else 0.0
