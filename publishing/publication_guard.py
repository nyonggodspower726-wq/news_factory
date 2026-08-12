from typing import Any,Dict,List

class PublicationGuard:
    def __init__(self):
        self.name="Publication Safety Guard"
        self.version="1.0.0"
        self.minimum_source_count=1
        self.minimum_evidence_score=60
        self.blocked_statuses={
            "BLOCK_PUBLICATION",
            "HOLD_FOR_REVIEW",
            "INSUFFICIENT_SUPPORT",
            "REVIEW_REQUIRED"
        }

    def check(self,package:Dict[str,Any],platform:str="website")->Dict[str,Any]:
        if not isinstance(package,dict):
            return self._blocked("Invalid publication package.")

        reasons=[]
        warnings=[]
        article=package.get("article",{}) or {}
        verification=package.get("verification",{}) or {}
        misinformation=package.get("misinformation",package.get("misinformation_analysis",{})) or {}
        investigation=package.get("investigation",{}) or {}
        sources=package.get("sources",[]) or article.get("sources",[])
        evidence=package.get("evidence",{}) or {}

        if not isinstance(article,dict):
            return self._blocked("Article data is invalid.")

        if article.get("publication_safe") is False:
            reasons.append("Article failed its publication safety flag.")

        if package.get("publication_ready") is False:
            reasons.append("Pipeline marked the package as not publication-ready.")

        if isinstance(verification,dict):
            status=str(verification.get("publication_status",verification.get("status",""))).upper()
            if status in self.blocked_statuses:
                reasons.append(f"Verification status is {status}.")
            score=self._number(verification.get("verification_score",verification.get("score",100)),100)
            if score<self.minimum_evidence_score:
                reasons.append(f"Verification score is below {self.minimum_evidence_score}.")

        if isinstance(misinformation,dict):
            overall=misinformation.get("overall",misinformation)
            risk=self._number(overall.get("risk_score",0),0) if isinstance(overall,dict) else 0
            level=str(overall.get("risk_level","")).upper() if isinstance(overall,dict) else ""
            if level in {"HIGH","CRITICAL"} or risk>=60:
                reasons.append("Misinformation risk is too high for automatic publication.")

        if isinstance(investigation,dict):
            level=str(investigation.get("investigation_level","")).upper()
            if level=="URGENT":
                reasons.append("Investigation level is URGENT.")
            elif level=="DEEP":
                warnings.append("Deep investigation is recommended before publication.")

        if not isinstance(sources,list):
            sources=[]
        if len(sources)<self.minimum_source_count:
            warnings.append("Very few sources are attached to the publication package.")

        title=str(article.get("title",article.get("headline","")) or "").strip()
        content=str(article.get("content",article.get("body","")) or "").strip()

        if not title:
            reasons.append("Article has no title.")
        if len(title)<10:
            warnings.append("Headline is unusually short.")
        if not content:
            reasons.append("Article has no content.")
        if len(content.split())<80:
            warnings.append("Article is unusually short for a full news publication.")

        media_url=str(article.get("image_url","") or "").strip()
        if not media_url:
            warnings.append("No featured image is attached.")

        seo=article.get("seo",{}) or {}
        if isinstance(seo,dict):
            if not seo.get("seo_title",article.get("seo_title","")):
                warnings.append("SEO title is missing.")
            if not seo.get("meta_description",article.get("meta_description","")):
                warnings.append("Meta description is missing.")

        duplicate=self._duplicate_signal(package,article)
        if duplicate:
            reasons.append(duplicate)

        allowed=not reasons

        return {
            "status":"APPROVED" if allowed else "BLOCKED",
            "publication_allowed":allowed,
            "platform":str(platform or "website"),
            "reasons":reasons,
            "warnings":warnings,
            "source_count":len(sources),
            "article_title":title,
            "has_content":bool(content),
            "has_image":bool(media_url),
            "checks":{
                "article":bool(title and content),
                "verification":not any("Verification status" in x or "Verification score" in x for x in reasons),
                "misinformation":not any("Misinformation risk" in x for x in reasons),
                "investigation":not any("Investigation level" in x for x in reasons),
                "seo":bool(seo) if isinstance(seo,dict) else False
            }
        }

    def approve(self,package:Dict[str,Any],platform:str="website")->bool:
        return bool(self.check(package,platform).get("publication_allowed",False))

    def require_approval(self,package:Dict[str,Any],platform:str="website")->Dict[str,Any]:
        result=self.check(package,platform)
        if result.get("publication_allowed"):
            return result
        return result

    def _duplicate_signal(self,package,article):
        duplicates=package.get("duplicates",[])
        if isinstance(duplicates,list) and duplicates:
            return "Duplicate or repeated coverage signals were detected."
        history=package.get("publication_history",[])
        article_id=str(article.get("id",article.get("article_id","")) or "")
        if article_id and isinstance(history,list):
            for item in history:
                if isinstance(item,dict) and str(item.get("article_id",""))==article_id and item.get("published"):
                    return "This article appears to have already been published."
        return ""

    def _blocked(self,reason):
        return {
            "status":"BLOCKED",
            "publication_allowed":False,
            "platform":"unknown",
            "reasons":[reason],
            "warnings":[],
            "source_count":0
        }

    def _number(self,value,default=0):
        try:
            return float(value)
        except (TypeError,ValueError):
            return default

    def status(self):
        return {
            "engine":self.name,
            "version":self.version,
            "status":"READY",
            "minimum_source_count":self.minimum_source_count,
            "minimum_evidence_score":self.minimum_evidence_score
        }

publication_guard=PublicationGuard()

def check_publication(package,platform="website"):
    return publication_guard.check(package,platform)

def approve_publication(package,platform="website"):
    return publication_guard.approve(package,platform)
