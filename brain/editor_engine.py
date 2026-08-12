"""
AI NEWS FACTORY
EDITOR ENGINE
Final editorial quality-control gate.
"""

import re
from typing import Any,Dict,List

class EditorEngine:
    def __init__(self):
        self.name="AI Senior Editor"
        self.version="2.0.0"
        self.minimum_approval_score=80
        self.maximum_blocking_errors=0

    def review(self,article_plan:Dict[str,Any]=None,psychology:Dict[str,Any]=None,verification:Dict[str,Any]=None,cluster:Dict[str,Any]=None,article:Dict[str,Any]=None,story:Dict[str,Any]=None,claims:List[Dict[str,Any]]=None,evidence:Dict[str,Any]=None,headline:Dict[str,Any]=None,misinformation:Dict[str,Any]=None,investigation:Dict[str,Any]=None,narrative:Dict[str,Any]=None,**kwargs)->Dict[str,Any]:
        article_plan=self._dict(article_plan)
        psychology=self._dict(psychology)
        verification=self._dict(verification)
        cluster=self._dict(cluster)
        article=self._dict(article) or self._extract_article(article_plan)
        story=self._dict(story)
        claims=claims if isinstance(claims,list) else []
        evidence=self._dict(evidence)
        headline=self._dict(headline)
        misinformation=self._dict(misinformation)
        investigation=self._dict(investigation)
        narrative=self._dict(narrative)

        if not verification:
            verification=self._dict(article_plan.get("verification"))
        if not psychology:
            psychology=self._dict(article_plan.get("psychology"))

        checks=[
            self._check_verification(verification),
            self._check_headline(article_plan,article,headline),
            self._check_lead(article_plan,article),
            self._check_claims(article_plan,verification,claims),
            self._check_structure(article_plan,article),
            self._check_reader_value(article_plan,article),
            self._check_psychology(psychology),
            self._check_source_diversity(cluster),
            self._check_repetition(article_plan,article,claims),
            self._check_misinformation(misinformation),
            self._check_investigation(investigation)
        ]

        errors=self._collect_errors(checks)
        warnings=self._collect_warnings(checks)
        score=self._calculate_score(checks,errors)
        decision=self._decision(score,errors,warnings)

        return {
            "engine":self.name,
            "version":self.version,
            "editorial_score":score,
            "decision":decision,
            "checks":checks,
            "errors":errors,
            "warnings":warnings,
            "publication_gate":decision in {"APPROVED","APPROVED_WITH_WARNINGS"},
            "publication_safe":not bool(errors),
            "editor_note":self._editor_note(decision,errors,warnings)
        }

    def edit(self,*args,**kwargs):
        return self.review(*args,**kwargs)

    def evaluate(self,*args,**kwargs):
        return self.review(*args,**kwargs)

    def analyze(self,*args,**kwargs):
        return self.review(*args,**kwargs)

    def approve(self,*args,**kwargs):
        return self.review(*args,**kwargs)

    def _check_verification(self,verification):
        verification=self._dict(verification)
        status=str(verification.get("publication_status",verification.get("status","UNKNOWN")) or "UNKNOWN").upper()
        if status in {"VERIFICATION_PASSED","VERIFIED","PASSED","COMPLETE","APPROVED"}:
            return self._pass("verification","Verification passed.")
        if status in {"REQUIRES_EDITORIAL_REVIEW","HUMAN_REVIEW_REQUIRED","WARNING","PENDING"}:
            return self._warning("verification","Some claims require additional review.")
        if status=="UNKNOWN" and not verification:
            return self._warning("verification","Verification result is unavailable.")
        return self._error("verification","Verification failed or is incomplete.")

    def _check_headline(self,article_plan,article,headline):
        headline=self._dict(headline)
        article=self._dict(article)
        plan=self._dict(article_plan)
        value=article.get("headline") or headline.get("headline") or plan.get("headline")
        if isinstance(value,dict):
            value=value.get("text") or value.get("title") or value.get("headline")
        if value:
            return self._pass("headline","Headline is available.")
        return self._warning("headline","Headline is missing or incomplete.")

    def _check_lead(self,article_plan,article):
        article=self._dict(article) or self._extract_article(article_plan)
        lead=article.get("lead")
        if isinstance(lead,dict):
            if lead.get("text") or lead.get("content") or lead.get("required_information"):
                return self._pass("lead","Lead structure exists.")
        elif lead:
            return self._pass("lead","Lead exists.")
        return self._warning("lead","Lead section is missing or incomplete.")

    def _check_claims(self,article_plan,verification,claims):
        plan=self._dict(article_plan)
        verification=self._dict(verification)
        safe_claims=plan.get("safe_claims",[])
        if not isinstance(safe_claims,list):
            safe_claims=[]
        verification_claims=verification.get("claims",[])
        if not isinstance(verification_claims,list):
            verification_claims=[]
        contradicted=[x for x in verification_claims if isinstance(x,dict) and str(x.get("status","")).upper()=="CONTRADICTED"]
        if contradicted:
            return self._error("claims","Contradicted claims are present.")
        if plan.get("excluded_claims"):
            return self._warning("claims","Some claims require exclusion or attribution.")
        if safe_claims or claims or verification_claims:
            count=len(safe_claims) or len(claims) or len(verification_claims)
            return self._pass("claims",f"{count} claim records available.")
        return self._warning("claims","No explicit verified claim list is available.")

    def _check_structure(self,article_plan,article):
        article=self._dict(article) or self._extract_article(article_plan)
        if not article:
            return self._warning("structure","Article structure is not yet populated.")
        required=["headline","lead"]
        missing=[x for x in required if not article.get(x)]
        if missing:
            return self._warning("structure","Missing sections: "+", ".join(missing))
        return self._pass("structure","Core article structure is present.")

    def _check_reader_value(self,article_plan,article):
        article=self._dict(article) or self._extract_article(article_plan)
        present=0
        for key in ("why_it_matters","what_happens_next","what_is_unknown"):
            if article.get(key):
                present+=1
        if present>=2:
            return self._pass("reader_value","Reader-value sections are present.")
        return self._warning("reader_value","Reader-value sections need strengthening.")

    def _check_psychology(self,psychology):
        psychology=self._dict(psychology)
        risks=psychology.get("manipulation_risks",[])
        if not isinstance(risks,list):
            risks=[]
        if risks:
            return self._error("psychology","Manipulative engagement patterns detected.")
        scores=self._dict(psychology.get("scores"))
        retention=scores.get("retention")
        if retention is not None:
            try:
                if float(retention)<50:
                    return self._warning("psychology","Reader-retention structure is weak.")
            except (TypeError,ValueError):
                pass
        return self._pass("psychology","Psychology review passes.")

    def _check_source_diversity(self,cluster):
        cluster=self._dict(cluster)
        domains=cluster.get("independent_domain_count")
        if domains is None:
            metrics=self._dict(cluster.get("metrics"))
            domains=metrics.get("independent_domain_count")
        if domains is None:
            source_domains=cluster.get("domains",[])
            if isinstance(source_domains,list):
                domains=len(set(str(x).lower() for x in source_domains if x))
            else:
                domains=0
        try:
            domains=int(domains)
        except (TypeError,ValueError):
            domains=0
        if domains>=3:
            return self._pass("source_diversity","Multiple independent domains are available.")
        if domains==2:
            return self._warning("source_diversity","Two independent domains are available.")
        return self._warning("source_diversity","Independent source diversity is limited.")

    def _check_repetition(self,article_plan,article,claims):
        plan=self._dict(article_plan)
        article=self._dict(article)
        safe_claims=plan.get("safe_claims",[])
        if not isinstance(safe_claims,list):
            safe_claims=[]
        if not safe_claims and isinstance(claims,list):
            safe_claims=claims
        texts=[]
        for claim in safe_claims:
            if isinstance(claim,dict):
                text=claim.get("claim",claim.get("text",""))
            else:
                text=str(claim)
            text=re.sub(r"\s+"," ",str(text).lower().strip())
            if text:
                texts.append(text)
        if texts and len(texts)!=len(set(texts)):
            return self._warning("repetition","Repeated factual statements detected.")
        return self._pass("repetition","No obvious duplicate claims detected.")

    def _check_misinformation(self,misinformation):
        misinformation=self._dict(misinformation)
        status=str(misinformation.get("status","") or "").upper()
        risk=str(misinformation.get("risk_level","") or "").upper()
        if status in {"BLOCKED","FAILED","HIGH_RISK"} or risk in {"HIGH","CRITICAL"}:
            return self._error("misinformation","Misinformation risk requires review.")
        if status in {"WARNING","REVIEW_REQUIRED"} or risk=="MEDIUM":
            return self._warning("misinformation","Misinformation review contains warnings.")
        return self._pass("misinformation","No blocking misinformation result detected.")

    def _check_investigation(self,investigation):
        investigation=self._dict(investigation)
        status=str(investigation.get("status","") or "").upper()
        if status in {"BLOCKED","FAILED","CRITICAL"}:
            return self._error("investigation","Investigation stage reports a blocking condition.")
        if status in {"HUMAN_REVIEW_REQUIRED","REVIEW_REQUIRED","PENDING"}:
            return self._warning("investigation","Investigation requires additional review.")
        return self._pass("investigation","Investigation stage is acceptable.")

    def _calculate_score(self,checks,errors):
        score=100
        for check in checks:
            status=check.get("status")
            if status=="WARNING":
                score-=5
            elif status=="ERROR":
                score-=25
        score-=len(errors)*10
        return max(0,min(score,100))

    def _decision(self,score,errors,warnings):
        if errors:
            return "BLOCKED"
        if score<self.minimum_approval_score:
            return "NEEDS_REVISION"
        if warnings:
            return "APPROVED_WITH_WARNINGS"
        return "APPROVED"

    def _collect_errors(self,checks):
        return [x for x in checks if x.get("status")=="ERROR"]

    def _collect_warnings(self,checks):
        return [x for x in checks if x.get("status")=="WARNING"]

    def _editor_note(self,decision,errors,warnings):
        if decision=="BLOCKED":
            return "Publication blocked. Critical editorial failures must be resolved."
        if decision=="NEEDS_REVISION":
            return "The article requires another editorial pass."
        if decision=="APPROVED_WITH_WARNINGS":
            return "Article passes the main editorial gate with non-critical warnings."
        return "Article passed the editorial gate."

    def _extract_article(self,article_plan):
        if not isinstance(article_plan,dict):
            return {}
        article=article_plan.get("article",{})
        if isinstance(article,dict):
            return article
        return {}

    def _dict(self,value):
        return value if isinstance(value,dict) else {}

    def status(self):
        return {"engine":self.name,"version":self.version,"status":"READY","minimum_approval_score":self.minimum_approval_score}

def edit_article(article_plan=None,psychology=None,verification=None,cluster=None,**kwargs):
    return EditorEngine().review(article_plan,psychology,verification,cluster,**kwargs)

if __name__=="__main__":
    import json
    print(json.dumps(EditorEngine().status(),indent=2))
