import inspect,logging,os,requests
from typing import Any,Dict,List
from brain.claim_engine import ClaimEngine
from brain.corroboration_engine import CorroborationEngine
from brain.fact_checker import FactChecker
from brain.story_synthesis_engine import StorySynthesisEngine
from brain.journalist_engine import JournalistEngine
from brain.headline_engine import HeadlineEngine
from brain.editor_engine import EditorEngine
from brain.story_analyzer import StoryAnalyzer
from brain.source_intelligence_engine import SourceIntelligenceEngine
from brain.source_graph_engine import SourceGraphEngine
from brain.significance_engine import SignificanceEngine
from brain.angle_finder import AngleFinder
from brain.reader_psychology_engine import ReaderPsychologyEngine
from brain.engagement_engine import EngagementEngine
from brain.narrative_engine import NarrativeEngine
from brain.event_resolution_engine import EventResolutionEngine
from brain.evidence_engine import EvidenceEngine
from brain.investigation_engine import InvestigationEngine
from brain.misinformation_engine import MisinformationEngine
from brain.source_verification import SourceVerificationEngine
from brain.story_cluster import StoryCluster
from brain.psychology_engine import PsychologyEngine
from factory_pipeline import FactoryPipeline
logger=logging.getLogger("NewsFactory.BrainPipeline")
class NvidiaBrainClient:
    def __init__(self,model:str="meta/llama-3.3-70b-instruct",base_url:str="https://integrate.api.nvidia.com/v1"):
        self.name="NVIDIA Brain Client";self.version="2.2.0";self.model=model;self.base_url=base_url.rstrip("/")
        self.api_keys=[os.getenv("NVIDIA_API_KEY_1","").strip(),os.getenv("NVIDIA_API_KEY_2","").strip(),os.getenv("NVIDIA_API_KEY_3","").strip(),os.getenv("NVIDIA_API_KEY_4","").strip()]
        self.api_keys=[x for x in self.api_keys if x];self.current_key_index=0;self.timeout=int(os.getenv("NVIDIA_TIMEOUT","60"))
    def status(self)->Dict[str,Any]:
        return {"provider":"NVIDIA","client":self.name,"version":self.version,"model":self.model,"configured_keys":len(self.api_keys),"failover_enabled":True,"current_key_slot":self.current_key_index+1 if self.api_keys else None}
    def chat(self,messages:List[Dict[str,str]],temperature:float=0.2,max_tokens:int=1500)->str:
        if not self.api_keys:raise RuntimeError("No NVIDIA API keys configured.")
        last_error=None
        total=len(self.api_keys)
        for attempt in range(total):
            index=(self.current_key_index+attempt)%total
            key=self.api_keys[index]
            try:
                result=self._request(key,messages,temperature,max_tokens);self.current_key_index=index;return result
            except Exception as exc:
                last_error=exc;logger.warning("NVIDIA key slot %s/%s failed: %s",index+1,total,exc)
        raise RuntimeError(f"All NVIDIA API keys failed. Last error: {last_error}")
    def _request(self,api_key:str,messages:List[Dict[str,str]],temperature:float,max_tokens:int)->str:
        response=requests.post(self.base_url+"/chat/completions",headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json","Accept":"application/json"},json={"model":self.model,"messages":messages,"temperature":temperature,"max_tokens":max_tokens},timeout=self.timeout)
        response.raise_for_status()
        data=response.json()
        choices=data.get("choices",[])
        if not choices:raise RuntimeError("NVIDIA API returned no choices.")
        content=choices[0].get("message",{}).get("content")
        if not content:raise RuntimeError("NVIDIA API returned empty content.")
        return str(content).strip()
class BrainPipeline:
    def __init__(self):
        logger.info("Initializing central brain...")
        self.ai=NvidiaBrainClient()
        self.story_analyzer=StoryAnalyzer();self.source_intelligence=SourceIntelligenceEngine();self.source_verification=SourceVerificationEngine();self.story_cluster=StoryCluster();self.event_resolution=EventResolutionEngine()
        self.claim_engine=ClaimEngine();self.evidence=EvidenceEngine();self.source_graph=SourceGraphEngine();self.corroboration=CorroborationEngine();self.fact_checker=FactChecker();self.investigation=InvestigationEngine();self.misinformation=MisinformationEngine()
        self.story_synthesis=StorySynthesisEngine();self.significance=SignificanceEngine();self.angle_finder=AngleFinder();self.reader_psychology=ReaderPsychologyEngine();self.psychology=PsychologyEngine();self.engagement=EngagementEngine();self.narrative=NarrativeEngine()
        self.journalist=JournalistEngine();self.headline=HeadlineEngine();self.editor=EditorEngine();self.factory_pipeline=FactoryPipeline()
        logger.info("Central brain initialized with full intelligence stack.")
    def status(self)->Dict[str,Any]:
        names=["story_analyzer","source_intelligence","source_verification","story_cluster","event_resolution","claim_engine","evidence","source_graph","corroboration","fact_checker","investigation","misinformation","story_synthesis","significance","angle_finder","reader_psychology","psychology","engagement","narrative","journalist","headline","editor"]
        components={name:self._component_ready(getattr(self,name,None)) for name in names}
        return {"status":"READY","engine":"BrainPipeline","version":"2.2.0","initialized":True,"total_brains":len(names),"loaded_brains":[name for name,value in components.items() if value],"brains":components,"ai_provider":self.ai.status(),"factory_pipeline":self._component_status(self.factory_pipeline)}
    def run(self,sources:List[Dict[str,Any]],story:Dict[str,Any]=None,topic:str="",platform:str="website",prepare_publication:bool=True)->Dict[str,Any]:
        sources=sources if isinstance(sources,list) else []
        story=self._safe_dict(story)
        package={"story":story,"sources":sources,"topic":topic or "","claims":[],"claim_analysis":{},"evidence":{},"verification":{},"source_verification":{},"corroboration":{},"source_graph":{},"source_intelligence":{},"cluster":{},"event_resolution":{},"investigation":{},"misinformation":{},"significance":{},"angles":{},"psychology":{},"reader_psychology":{},"engagement":{},"narrative":{},"synthesis":{},"story_model":{},"article_plan":{},"article":{},"headline":{},"editorial":{},"publication":{},"ai":self.ai}
        logger.info("="*70);logger.info("CENTRAL BRAIN PIPELINE STARTED");logger.info("="*70)
        package["story_analysis"]=self._safe("story_analysis",self.story_analyzer,["analyze"],{"story":package["story"]})
        if isinstance(package["story_analysis"],dict):
            analyzed_story=package["story_analysis"].get("story")
            if isinstance(analyzed_story,dict):package["story"].update(analyzed_story)
        package["source_intelligence"]=self._safe("source_intelligence",self.source_intelligence,["analyze"],{"sources":sources})
        package["source_verification"]=self._safe("source_verification",self.source_verification,["analyze","verify"],{"sources":sources})
        package["cluster"]=self._safe("story_cluster",self.story_cluster,["cluster_stories","cluster","analyze"],{"stories":sources,"sources":sources,"story":package["story"]})
        events=self._build_events(sources,package["story"])
        package["event_resolution"]=self._safe("event_resolution",self.event_resolution,["resolve","analyze"],{"events":events,"sources":sources,"story":package["story"]})
        package["claim_analysis"]=self._safe("claim_engine",self.claim_engine,["analyze","extract"],{"story":package["story"],"sources":sources,"topic":topic,"research":package["source_intelligence"]})
        package["claims"]=self._extract_claims(package["claim_analysis"])
        package["evidence"]=self._safe("evidence_engine",self.evidence,["analyze","evaluate"],{"claims":package["claims"],"sources":sources})
        package["source_graph"]=self._safe("source_graph",self.source_graph,["build_graph","analyze"],{"sources":sources,"claims":package["claims"],"entities":self._extract_entities(package["story"])})
        package["corroboration"]=self._safe("corroboration",self.corroboration,["analyze","corroborate"],{"sources":sources,"claims":package["claims"],"evidence":package["evidence"]})
        package["verification"]=self._safe("fact_checker",self.fact_checker,["verify_story","verify","analyze"],{"story":package["story"],"sources":sources,"claims":package["claims"],"evidence":package["evidence"]})
        package["investigation"]=self._safe("investigation",self.investigation,["investigate","analyze"],{"story":package["story"],"research":package["source_intelligence"],"claims":package["claims"],"sources":sources})
        package["misinformation"]=self._safe("misinformation",self.misinformation,["analyze","assess"],{"claims":package["claims"],"sources":sources,"story":package["story"]})
        package["significance"]=self._safe("significance",self.significance,["evaluate","analyze","assess"],{"story":package["story"],"sources":sources,"claims":package["claims"],"evidence":package["evidence"]})
        package["angles"]=self._safe("angle_finder",self.angle_finder,["analyze","find","find_angles","evaluate"],{"story":package["story"],"related_stories":self._related_stories(package["cluster"]),"evidence":package["evidence"],"trend_data":package["significance"],"article_plan":package["article_plan"],"cluster":package["cluster"]})
        package["synthesis"]=self._safe("story_synthesis",self.story_synthesis,["synthesize","analyze"],{"sources":sources,"evidence":package["evidence"],"metadata":{"topic":topic,"story":package["story"],"claims":package["claims"],"verification":package["verification"],"corroboration":package["corroboration"],"source_graph":package["source_graph"],"source_intelligence":package["source_intelligence"],"investigation":package["investigation"],"misinformation":package["misinformation"],"significance":package["significance"],"angles":package["angles"]}})
        package["story_model"]=self._safe_dict(package["synthesis"])
        package["article_plan"]=self._build_provisional_article_plan(package)
        package["reader_psychology"]=self._safe("reader_psychology",self.reader_psychology,["analyze","evaluate","assess"],{"article_plan":package["article_plan"],"story":package["story"],"significance":package["significance"],"angles":package["angles"],"claims":package["claims"],"evidence":package["evidence"]})
        package["psychology"]=self._safe("psychology",self.psychology,["analyze","evaluate","assess"],{"article_plan":package["article_plan"],"story":package["story"],"significance":package["significance"],"angles":package["angles"],"reader_psychology":package["reader_psychology"],"claims":package["claims"],"evidence":package["evidence"]})
        package["engagement"]=self._safe("engagement",self.engagement,["analyze","evaluate","optimize"],{"article_plan":package["article_plan"],"story":package["story"],"significance":package["significance"],"angles":package["angles"],"psychology":package["psychology"],"reader_psychology":package["reader_psychology"],"claims":package["claims"]})
        package["narrative"]=self._safe("narrative",self.narrative,["analyze","build","construct","create"],{"article_plan":package["article_plan"],"story":package["story"],"synthesis":package["synthesis"],"story_model":package["story_model"],"claims":package["claims"],"evidence":package["evidence"],"angles":package["angles"],"psychology":package["psychology"],"reader_psychology":package["reader_psychology"],"engagement":package["engagement"]})
        final_plan=self._safe("journalist",self.journalist,["write","create","generate","produce","compose","analyze"],{"article_plan":package["article_plan"],"story":package["story"],"sources":sources,"claims":package["claims"],"evidence":package["evidence"],"verification":package["verification"],"synthesis":package["synthesis"],"story_model":package["story_model"],"narrative":package["narrative"],"angles":package["angles"],"psychology":package["psychology"],"reader_psychology":package["reader_psychology"],"engagement":package["engagement"],"significance":package["significance"],"ai":self.ai})
        package["article_plan"]=self._merge_article_plan(package["article_plan"],final_plan)
        package["article"]=self._extract_article(package["article_plan"])
        package["headline"]=self._safe("headline",self.headline,["generate","create","analyze","optimize"],{"article_plan":package["article_plan"],"article":package["article"],"story":package["story"],"significance":package["significance"],"angles":package["angles"],"psychology":package["psychology"],"platform":platform})
        package["editorial"]=self._safe("editor",self.editor,["review","edit","evaluate","analyze","approve"],{"article_plan":package["article_plan"],"article":package["article"],"story":package["story"],"claims":package["claims"],"evidence":package["evidence"],"verification":package["verification"],"misinformation":package["misinformation"],"investigation":package["investigation"],"headline":package["headline"],"narrative":package["narrative"],"cluster":package["cluster"],"psychology":package["psychology"]})
        package["publication_ready"]=self._editor_allows_publication(package["editorial"])
        package["brain_summary"]={"status":"BRAIN_COMPLETE","topic":topic,"source_count":len(sources),"claim_count":len(package["claims"]),"publication_ready":package["publication_ready"],"verification":self._status_value(package["verification"]),"misinformation":self._status_value(package["misinformation"]),"investigation":self._status_value(package["investigation"]),"editorial":self._status_value(package["editorial"])}
        if prepare_publication:
            try:
                publication=self.factory_pipeline.prepare(package,platform);package["publication"]=self._safe_dict(publication);package["publication_ready"]=package["publication"].get("status")=="READY"
            except Exception as exc:
                logger.exception("Brain-to-factory handoff failed.");package["publication"]={"status":"FAILED","stage":"FACTORY_HANDOFF","error":str(exc)};package["publication_ready"]=False
        package["pipeline_status"]="BRAIN_COMPLETE"
        package["status"]="BRAIN_COMPLETE"
        logger.info("BRAIN PIPELINE STATUS: BRAIN_COMPLETE")
        logger.info("="*70);logger.info("CENTRAL BRAIN PIPELINE COMPLETE");logger.info("="*70)
        return package
    def _safe(self,name,engine,methods,context):
        context=self._normalize_context(context)
        if engine is None:return {"status":"MISSING","engine":name}
        method=None;method_name=""
        for candidate in methods:
            fn=getattr(engine,candidate,None)
            if callable(fn):method=fn;method_name=candidate;break
        if method is None:return {"status":"UNSUPPORTED","engine":name,"error":"No compatible method found.","methods":methods}
        try:
            arguments=self._adapt_arguments(method,context);result=method(**arguments)
            if result is None:return {"status":"COMPLETE","engine":name,"method":method_name,"result":{}}
            if isinstance(result,dict):return result
            return {"status":"COMPLETE","engine":name,"method":method_name,"result":result}
        except TypeError as first_error:
            logger.warning("%s.%s keyword call failed: %s",name,method_name,first_error)
            try:
                result=self._positional_fallback(method,context)
                if result is None:return {"status":"COMPLETE","engine":name,"method":method_name,"result":{}}
                if isinstance(result,dict):return result
                return {"status":"COMPLETE","engine":name,"method":method_name,"result":result}
            except Exception as fallback_error:
                logger.exception("%s fallback failed.",name);return {"status":"ERROR","engine":name,"method":method_name,"error":str(fallback_error)}
        except Exception as exc:
            logger.exception("%s.%s failed.",name,method_name);return {"status":"ERROR","engine":name,"method":method_name,"error":str(exc)}
    def _adapt_arguments(self,method,context):
        try:signature=inspect.signature(method)
        except (TypeError,ValueError):return context
        aliases={"source":"sources","source_list":"sources","source_data":"sources","claim":"claims","claim_list":"claims","claim_data":"claims","research_data":"research","article_data":"article","story_data":"story","trend":"trend_data","event_list":"events","items":"stories","plan":"article_plan","cluster_data":"cluster"}
        fallback_defaults={"article_plan":{},"story":{},"sources":[],"claims":[],"evidence":{},"research":{},"metadata":{},"article":{},"events":[],"stories":[],"trend_data":{},"cluster":{},"psychology":{},"verification":{},"misinformation":{},"investigation":{},"headline":{},"narrative":{}}
        arguments={}
        for name,parameter in signature.parameters.items():
            if name=="self" or parameter.kind in {inspect.Parameter.VAR_KEYWORD,inspect.Parameter.VAR_POSITIONAL}:continue
            if name in context:value=context[name]
            elif aliases.get(name) in context:value=context[aliases[name]]
            elif name in fallback_defaults:value=fallback_defaults[name]
            elif parameter.default is not inspect.Parameter.empty:continue
            else:raise TypeError(f"Required parameter '{name}' cannot be mapped.")
            arguments[name]=value
        return arguments
