"""
AI NEWS FACTORY
SOURCE GRAPH ENGINE
Builds relationships between sources, publishers, claims and entities.
"""

from typing import Any,Dict,List
from urllib.parse import urlparse
import re

class SourceGraphEngine:
    def __init__(self):
        self.name="Source Relationship Graph Engine"
        self.version="2.0.0"
        self.entity_types={"source","publisher","person","organization","claim","event","location"}
        self.relationship_types={"PUBLISHED_BY","QUOTES","CITES","REPOSTS","REFERENCES","SUPPORTS","CONTRADICTS","MENTIONS","ABOUT","LOCATED_IN","INVOLVES"}

    def build_graph(self,sources:List[Dict[str,Any]],claims:List[Dict[str,Any]]=None,entities:Dict[str,List[str]]=None)->Dict[str,Any]:
        sources=self._normalize_sources(sources)
        claims=claims if isinstance(claims,list) else []
        entities=entities if isinstance(entities,dict) else {}
        nodes=[];edges=[];publishers={}

        for source in sources:
            nodes.append(self._source_node(source))

        for source in sources:
            publisher=str(source.get("publisher",source.get("name","")) or "").strip()
            if not publisher: continue
            publisher_id="publisher:"+self._slug(publisher)
            if publisher_id not in publishers:
                publishers[publisher_id]={"id":publisher_id,"type":"publisher","name":publisher}
                nodes.append(publishers[publisher_id])
            edges.append({"from":self._source_id(source.get("source_id")),"to":publisher_id,"relationship":"PUBLISHED_BY"})

        edges.extend(self._source_relationships(sources))

        for index,claim in enumerate(claims):
            if not isinstance(claim,dict): continue
            raw_id=str(claim.get("claim_id",claim.get("id",f"{index+1}")))
            claim_id=raw_id if raw_id.startswith("claim:") else "claim:"+raw_id
            claim_node={"id":claim_id,"type":"claim","text":str(claim.get("text",claim.get("claim","")))}
            nodes.append(claim_node)
            source_id=claim.get("source_id")
            if source_id:
                edges.append({"from":self._source_id(source_id),"to":claim_id,"relationship":"REFERENCES"})

        entity_nodes,entity_edges=self._build_entity_nodes(entities,sources)
        nodes.extend(entity_nodes)
        edges.extend(entity_edges)

        return {
            "engine":self.name,
            "version":self.version,
            "status":"SOURCE_GRAPH_COMPLETE",
            "nodes":nodes,
            "edges":edges,
            "metrics":self._metrics(nodes,edges),
            "hubs":self._find_hubs(nodes,edges),
            "isolated_nodes":self._isolated_nodes(nodes,edges),
            "source_lineage":self._source_lineage(sources,edges)
        }

    def _normalize_sources(self,sources):
        if isinstance(sources,dict): sources=list(sources.values())
        if not isinstance(sources,list): return []
        normalized=[]
        for index,source in enumerate(sources):
            if isinstance(source,str): source={"content":source}
            if not isinstance(source,dict): continue
            normalized.append({
                "source_id":str(source.get("source_id",source.get("id",f"source:{index+1}"))),
                "name":source.get("name",source.get("publisher","")),
                "publisher":source.get("publisher",source.get("name","")),
                "url":source.get("url",source.get("source_url","")),
                "title":source.get("title",source.get("headline","")),
                "content":source.get("content",source.get("text",source.get("body",""))),
                "type":source.get("type",source.get("source_type","unknown")),
                "original_source":source.get("original_source",""),
                "quoted_source":source.get("quoted_source",""),
                "author":source.get("author",""),
                "primary":bool(source.get("primary",False))
            })
        return normalized

    def _source_node(self,source):
        source_id=self._source_id(source.get("source_id"))
        return {
            "id":source_id,
            "type":"source",
            "name":source.get("name",""),
            "publisher":source.get("publisher",""),
            "domain":self._domain(source.get("url","")),
            "title":source.get("title",""),
            "source_type":source.get("type","unknown"),
            "primary":bool(source.get("primary",False))
        }

    def _source_relationships(self,sources):
        edges=[]
        for source in sources:
            source_id=self._source_id(source.get("source_id"))
            for field,relationship in [("original_source","REPOSTS"),("quoted_source","QUOTES")]:
                reference=str(source.get(field,"") or "").strip()
                if reference:
                    target=self._resolve_source(reference,sources)
                    if target and target!=source_id:
                        edges.append({"from":source_id,"to":target,"relationship":relationship})

        for index,first in enumerate(sources):
            for second in sources[index+1:]:
                first_text=f"{first.get('title','')} {first.get('content','')}"
                second_text=f"{second.get('title','')} {second.get('content','')}"
                similarity=self._similarity(first_text,second_text)
                if similarity>=0.70:
                    edges.append({
                        "from":self._source_id(first.get("source_id")),
                        "to":self._source_id(second.get("source_id")),
                        "relationship":"REPOSTS",
                        "confidence":round(similarity,3)
                    })
        return edges

    def _build_entity_nodes(self,entities,sources):
        nodes=[];edges=[]
        entity_map={"people":"person","organizations":"organization","locations":"location"}
        for category,entity_type in entity_map.items():
            values=entities.get(category,[])
            if isinstance(values,str): values=[values]
            if not isinstance(values,list): continue
            for value in values:
                value=str(value).strip()
                if not value: continue
                entity_id=entity_type+":"+self._slug(value)
                nodes.append({"id":entity_id,"type":entity_type,"name":value})
                for source in sources:
                    text=f"{source.get('title','')} {source.get('content','')}".lower()
                    if value.lower() in text:
                        edges.append({
                            "from":self._source_id(source.get("source_id")),
                            "to":entity_id,
                            "relationship":"MENTIONS"
                        })
        return nodes,edges

    def _resolve_source(self,reference,sources):
        reference=str(reference or "").lower().strip()
        for source in sources:
            source_id=str(source.get("source_id","")).lower()
            publisher=str(source.get("publisher","")).lower()
            name=str(source.get("name","")).lower()
            domain=self._domain(source.get("url","")).lower()
            if reference in {source_id,publisher,name,domain}:
                return self._source_id(source.get("source_id"))
        return ""

    def _source_id(self,value):
        value=str(value or "").strip()
        if not value: return "source:unknown"
        return value if value.startswith("source:") else "source:"+value

    def _domain(self,url):
        value=str(url or "").strip()
        if not value: return ""
        try:
            parsed=urlparse(value if "://" in value else "https://"+value)
            domain=(parsed.netloc or parsed.path.split("/")[0]).lower()
            if domain.startswith("www."): domain=domain[4:]
            return domain
        except Exception:
            return ""

    def _slug(self,text):
        value=str(text or "").lower().strip()
        value=re.sub(r"[^a-z0-9]+","-",value)
        return value.strip("-") or "unknown"

    def _similarity(self,a,b):
        a=self._tokens(a);b=self._tokens(b)
        if not a or not b: return 0.0
        intersection=len(a&b)
        union=len(a|b)
        return intersection/union if union else 0.0

    def _tokens(self,text):
        words=re.findall(r"[a-z0-9]{4,}",str(text or "").lower())
        stop={"this","that","with","from","have","were","been","will","they","their","about","after","before","said","says","into","what","when","where","which","there","while","would","could","should","news"}
        return {x for x in words if x not in stop}

    def _metrics(self,nodes,edges):
        degrees={}
        for node in nodes: degrees[node.get("id")]=0
        for edge in edges:
            source=edge.get("from")
            target=edge.get("to")
            if source in degrees: degrees[source]+=1
            if target in degrees: degrees[target]+=1
        return {
            "node_count":len(nodes),
            "edge_count":len(edges),
            "connected_nodes":sum(1 for x in degrees.values() if x>0),
            "isolated_count":sum(1 for x in degrees.values() if x==0)
        }

    def _find_hubs(self,nodes,edges):
        degree={}
        for edge in edges:
            for key in ("from","to"):
                value=edge.get(key)
                if value: degree[value]=degree.get(value,0)+1
        ranked=sorted(degree.items(),key=lambda x:x[1],reverse=True)[:10]
        lookup={x.get("id"):x for x in nodes}
        return [
            {
                "id":node_id,
                "name":lookup.get(node_id,{}).get("name",node_id),
                "degree":count
            }
            for node_id,count in ranked
        ]

    def _isolated_nodes(self,nodes,edges):
        connected=set()
        for edge in edges:
            if edge.get("from"): connected.add(edge["from"])
            if edge.get("to"): connected.add(edge["to"])
        return [
            node.get("id")
            for node in nodes
            if node.get("id") not in connected
        ]

    def _source_lineage(self,sources,edges):
        lineage={}
        for source in sources:
            source_id=self._source_id(source.get("source_id"))
            lineage[source_id]={
                "source_id":source_id,
                "name":source.get("name",""),
                "publisher":source.get("publisher",""),
                "domain":self._domain(source.get("url","")),
                "relationships":[]
            }
        for edge in edges:
            source=edge.get("from")
            if source in lineage:
                lineage[source]["relationships"].append({
                    "to":edge.get("to"),
                    "relationship":edge.get("relationship"),
                    "confidence":edge.get("confidence")
                })
        return lineage

    def status(self):
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "entity_types":sorted(self.entity_types),
            "relationship_types":sorted(self.relationship_types)
        }

source_graph_engine=SourceGraphEngine()

def build_source_graph(sources,claims=None,entities=None):
    return source_graph_engine.build_graph(sources,claims,entities)

def source_graph_status():
    return source_graph_engine.status()

if __name__=="__main__":
    import json
    print(json.dumps(source_graph_engine.status(),indent=2,default=str))
