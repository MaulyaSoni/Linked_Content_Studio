"""
Safety & Reliability Chains - Production-Level Hallucination Guard
Controls LLM-generated claims against verified sources.
"""

from typing import List, Dict, Tuple
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import re
import json
from datetime import datetime


class HallucinationGuard:
    """
    Prevents hallucinated claims by validating against source context.
    
    Flow:
    1. Extract factual claims from generated post
    2. Check each claim against source documents
    3. Rewrite unverified claims as qualitative statements
    4. Return cleaned post with validation log
    """
    
    def __init__(self, llm: ChatGroq = None):
        """Initialize hallucination guard."""
        if llm is None:
            self.llm = ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=0.3,
                timeout=30
            )
        else:
            self.llm = llm
    
    def extract_claims(self, post: str, context: str) -> Dict[str, List[str]]:
        """
        Extract factual claims from post.
        
        Returns:
            {
                "quantitative": ["Increased by 300%", "5 million users"],
                "qualitative": ["significant improvement", "better experience"],
                "source_attributed": ["According to...", "Based on..."]
            }
        """
        extraction_prompt = PromptTemplate.from_template("""
        Extract ALL factual claims (specific numbers, percentages, dates, metrics) from this LinkedIn post.
        
        POST:
        {post}
        
        Return ONLY a JSON object with:
        - "quantitative": list of any specific numbers/percentages/metrics
        - "qualitative": list of general claims without numbers
        - "source_attributed": list of claims that cite sources
        
        RESPOND ONLY WITH VALID JSON, NO OTHER TEXT:
        """)
        
        try:
            response = self.llm.invoke(extraction_prompt.format(post=post))
            content = response.content.strip()
            
            # Clean markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content)
        except Exception as e:
            return {
                "quantitative": [],
                "qualitative": [],
                "source_attributed": []
            }
    
    def validate_claims(self, claims: List[str], context: str) -> Dict[str, bool]:
        """
        Validate each claim against context documents.
        
        Returns: {"claim": verified_or_not}
        """
        validation_prompt = PromptTemplate.from_template("""
        Given this context, verify if each claim is mentioned or directly supported:
        
        CONTEXT:
        {context}
        
        CLAIMS TO VERIFY:
        {claims}
        
        For each claim, respond with ONLY "VERIFIED" or "UNVERIFIED".
        Format as JSON: {{"claim_1": "VERIFIED", "claim_2": "UNVERIFIED"}}
        """)
        
        claims_text = "\n".join(f"- {claim}" for claim in claims)
        
        try:
            response = self.llm.invoke(
                validation_prompt.format(context=context, claims=claims_text)
            )
            content = response.content.strip()
            
            if "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                if content.startswith("json"):
                    content = content[4:].strip()
            
            return json.loads(content)
        except Exception:
            return {claim: False for claim in claims}
    
    def rewrite_unverified(self, post: str, verified_map: Dict[str, bool]) -> Tuple[str, Dict]:
        """
        Rewrite unverified claims as qualitative statements.
        
        Example:
        "Increased by 300%" → "Achieved significant improvements"
        """
        corrections = []
        cleaned_post = post
        
        rewrite_prompt = PromptTemplate.from_template("""
        Rewrite these unverified claims to be qualitative and honest:
        
        {unverified_claims}
        
        Return ONLY the rewritten versions as a JSON object:
        {{"original": "rewritten"}}
        
        Keep them professional and LinkedIn-appropriate.
        """)
        
        unverified = [claim for claim, verified in verified_map.items() if not verified]
        
        if not unverified:
            return cleaned_post, {"verified": len(verified_map), "corrected": 0, "details": []}
        
        try:
            claims_text = "\n".join(f"- {claim}" for claim in unverified)
            response = self.llm.invoke(
                rewrite_prompt.format(unverified_claims=claims_text)
            )
            content = response.content.strip()
            
            if "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                if content.startswith("json"):
                    content = content[4:].strip()
            
            rewrites = json.loads(content)
            
            for original, rewritten in rewrites.items():
                if original in cleaned_post:
                    cleaned_post = cleaned_post.replace(original, rewritten)
                    corrections.append({
                        "original": original,
                        "rewritten": rewritten,
                        "reason": "unverified_claim"
                    })
        except Exception as e:
            pass
        
        return cleaned_post, {
            "verified": sum(1 for v in verified_map.values() if v),
            "corrections": len(corrections),
            "details": corrections
        }
    
    def guard_post(self, post: str, context: str) -> Dict:
        """
        Main safety guard function.
        
        Returns:
            {
                "original_post": str,
                "cleaned_post": str,
                "validation_log": {
                    "claims_extracted": int,
                    "claims_verified": int,
                    "corrections_made": int,
                    "details": list
                },
                "is_safe": bool,
                "confidence": float,
                "timestamp": str
            }
        """
        # Extract claims
        claim_data = self.extract_claims(post, context)
        all_claims = (
            claim_data.get("quantitative", []) + 
            claim_data.get("qualitative", [])
        )
        
        # Validate claims
        verified_map = self.validate_claims(all_claims, context)
        
        # Rewrite unverified
        cleaned_post, correction_log = self.rewrite_unverified(post, verified_map)
        
        # Calculate confidence
        if len(verified_map) > 0:
            confidence = sum(1 for v in verified_map.values() if v) / len(verified_map)
        else:
            confidence = 1.0
        
        return {
            "original_post": post,
            "cleaned_post": cleaned_post,
            "validation_log": {
                "claims_extracted": len(all_claims),
                "claims_verified": correction_log["verified"],
                "corrections_made": correction_log["corrections"],
                "correction_details": correction_log["details"]
            },
            "is_safe": confidence >= 0.7,
            "safety_confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }


class PolicyGuardrail:
    """
    Prevents misleading claims based on LinkedIn Professional Policy.
    """
    
    FORBIDDEN_PATTERNS = {
        "misleading_growth": [
            r"(?:guaranteed|100%|absolutely certain).*(?:growth|success|increase)",
            r"(?:only|just).*(?:days?|weeks?|months?).*(?:make|earn).*(?:\$|dollars|revenue)"
        ],
        "exaggerated_metrics": [
            r"(?:became|was).*(?:world|best|top|only)",
            r"(?:\d+).*(?:%|x).*(?:overnight|immediately|instant)"
        ],
        "unverified_endorsements": [
            r"(?:everyone|all|companies|experts).*(?:agree|confirm|validate)"
        ]
    }
    
    @staticmethod
    def check_policy(post: str) -> Tuple[bool, List[str]]:
        """
        Check if post violates LinkedIn Professional Policy.
        
        Returns: (is_compliant, violations_list)
        """
        violations = []
        
        for violation_type, patterns in PolicyGuardrail.FORBIDDEN_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, post, re.IGNORECASE):
                    violations.append(f"{violation_type}: {pattern[:50]}...")
        
        return len(violations) == 0, violations


class SafetyChain:
    """
    Full safety pipeline combining hallucination guard and policy checks.
    """
    
    def __init__(self, llm: ChatGroq = None):
        self.hallucination_guard = HallucinationGuard(llm)
        self.policy_guardrail = PolicyGuardrail()
    
    def run_safety_check(self, post: str, context: str) -> Dict:
        """
        Run complete safety check on generated post.
        
        Returns comprehensive safety report.
        """
        # 1. Hallucination guard
        hallucination_report = self.hallucination_guard.guard_post(post, context)
        cleaned_post = hallucination_report["cleaned_post"]
        
        # 2. Policy check
        is_compliant, policy_violations = self.policy_guardrail.check_policy(cleaned_post)
        
        # 3. Final decision
        is_safe = (
            hallucination_report["is_safe"] and 
            is_compliant and
            hallucination_report["safety_confidence"] >= 0.6
        )
        
        return {
            "is_safe": is_safe,
            "final_post": cleaned_post,
            "hallucination_check": {
                "confidence": hallucination_report["safety_confidence"],
                "corrections": hallucination_report["validation_log"]["corrections_made"],
                "details": hallucination_report["validation_log"]["correction_details"]
            },
            "policy_check": {
                "compliant": is_compliant,
                "violations": policy_violations
            },
            "recommendation": (
                "✅ Ready to post" if is_safe 
                else "⚠️ Review before posting" if hallucination_report["safety_confidence"] >= 0.5
                else "❌ Needs revision"
            ),
            "timestamp": datetime.now().isoformat()
        }
