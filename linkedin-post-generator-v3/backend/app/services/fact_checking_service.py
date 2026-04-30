from typing import List, Dict, Optional
from pydantic import BaseModel
from app.services.llm_service import LLMService


class ClaimVerification(BaseModel):
    """Result of verifying a single claim."""
    claim: str
    is_verified: bool
    confidence: float
    sources: List[Dict] = []


class FactCheckResult(BaseModel):
    """Result of fact-checking a post."""
    post: str
    claims: List[str]
    verification_results: List[ClaimVerification]
    flagged_claims: List[ClaimVerification]
    confidence_score: float
    recommendations: List[str]
    is_safe: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "confidence_score": self.confidence_score,
            "is_safe": self.is_safe,
            "total_claims": len(self.claims),
            "verified_claims": sum(1 for r in self.verification_results if r.is_verified),
            "flagged_claims": [
                {
                    "claim": fc.claim,
                    "confidence": fc.confidence,
                }
                for fc in self.flagged_claims
            ],
        }


class FactCheckingService:
    """
    Multi-layer fact-checking to prevent hallucinations.
    1. Claim extraction
    2. Web verification
    3. Context grounding
    4. Confidence scoring
    """
    
    def __init__(self):
        self.llm_service = LLMService()
    
    async def fact_check_post(
        self,
        post: str,
        user_context: Optional[Dict] = None
    ) -> FactCheckResult:
        """Comprehensive fact-checking of generated post."""
        
        # Step 1: Extract claims
        claims = await self._extract_claims(post)
        
        # Step 2: Verify each claim (simplified - in production use web search)
        verification_results = []
        for claim in claims:
            # For now, use LLM to verify (in production, use Tavily + RAG)
            result = await self._verify_claim_with_llm(claim)
            verification_results.append(result)
        
        # Step 3: Flag problematic claims
        flagged = [r for r in verification_results if not r.is_verified]
        
        # Step 4: Score overall confidence
        confidence = self._calculate_confidence(verification_results)
        
        # Step 5: Generate recommendations
        recommendations = await self._generate_recommendations(flagged)
        
        return FactCheckResult(
            post=post,
            claims=claims,
            verification_results=verification_results,
            flagged_claims=flagged,
            confidence_score=confidence,
            recommendations=recommendations,
            is_safe=confidence >= 75,
        )
    
    async def _extract_claims(self, post: str) -> List[str]:
        """Use LLM to identify factual claims in the post."""
        
        prompt = f"""
        Extract ALL factual claims from this LinkedIn post.
        A claim is a statement of fact that can be verified.
        Skip opinions, personal experiences, and rhetorical questions.
        
        Post:
        {post}
        
        Format: One claim per line
        """
        
        response = await self.llm_service.generate(prompt)
        claims_text = response.content
        return [c.strip() for c in claims_text.split("\n") if c.strip()]
    
    async def _verify_claim_with_llm(self, claim: str) -> ClaimVerification:
        """Verify a claim using LLM knowledge (simplified - use web search in production)."""
        
        prompt = f"""
        Is this claim likely to be true based on common knowledge?
        Respond with "True", "False", or "Uncertain" followed by a brief reason.
        
        Claim: {claim}
        
        Response:
        """
        
        response = await self.llm_service.generate(prompt)
        result_text = response.content.lower()
        
        is_verified = result_text.startswith("true")
        confidence = 0.8 if is_verified else 0.3
        
        return ClaimVerification(
            claim=claim,
            is_verified=is_verified,
            confidence=confidence,
        )
    
    def _calculate_confidence(self, results: List[ClaimVerification]) -> float:
        """Calculate overall confidence score (0-100)."""
        
        if not results:
            return 100  # No claims = confident
        
        verified = sum(1 for r in results if r.is_verified)
        total = len(results)
        
        confidence = (verified / total) * 100 if total > 0 else 100
        return min(confidence, 100)
    
    async def _generate_recommendations(self, flagged: List[ClaimVerification]) -> List[str]:
        """Generate recommendations for fixing flagged claims."""
        
        if not flagged:
            return []
        
        recommendations = []
        
        for claim in flagged:
            if claim.confidence == 0:
                recommendations.append(f"Consider removing: '{claim.claim}'")
            else:
                recommendations.append(f"Verify or rephrase: '{claim.claim}'")
        
        return recommendations
