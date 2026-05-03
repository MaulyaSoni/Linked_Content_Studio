import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LinkedInService:
    """Service for interacting with the LinkedIn API."""
    
    BASE_URL = "https://api.linkedin.com/v2"
    
    async def publish_post(self, content: str, access_token: str, user_id: str) -> Dict[str, Any]:
        """
        Publish a post to LinkedIn.
        Using the 'posts' endpoint (v2).
        """
        url = f"{self.BASE_URL}/posts"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        
        # LinkedIn v2 'posts' API payload
        payload = {
            "author": f"urn:li:person:{user_id}",
            "commentary": content,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response_data = response.json() if response.text else {}
                
                if response.status_code in [201, 200]:
                    logger.info("Successfully published post to LinkedIn")
                    return {
                        "success": True,
                        "post_urn": response.headers.get("x-restli-id") or response_data.get("id"),
                        "data": response_data
                    }
                else:
                    logger.error(f"Failed to publish to LinkedIn: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": response.text,
                        "status_code": response.status_code
                    }
            except Exception as e:
                logger.exception("Error calling LinkedIn API")
                return {
                    "success": False,
                    "error": str(e)
                }

    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get the authenticated user's profile."""
        url = f"{self.BASE_URL}/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": response.text}
            except Exception as e:
                return {"error": str(e)}
