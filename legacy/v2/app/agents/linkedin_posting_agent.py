"""
LinkedIn Posting Agent
======================
An agent wrapper around LinkedInPoster that enables tool-calling
style posting from within the agent workflow.
"""

import logging
import time
from typing import Dict, Optional

from agents.base_agent import AgentResult, BaseAgent
from tools.linkedin_poster import LinkedInPoster, LinkedInPostResult

logger = logging.getLogger(__name__)


class LinkedInPostingAgent(BaseAgent):
    """
    Posts selected content to LinkedIn using the LinkedInPoster tool.
    Called outside the main 6-agent pipeline — invoked by the user
    after reviewing generated variants.
    """

    def __init__(self, llm_provider=None):
        super().__init__("LinkedInPostingAgent", llm_provider)
        self.poster = LinkedInPoster()

    def run(self, input_data: Dict) -> AgentResult:
        """
        input_data keys:
            post_content  : str   (the post to publish)
            hashtags      : str   (optional hashtag string)
            visibility    : str   ("PUBLIC" or "CONNECTIONS_ONLY")
            scheduled_time: str   (optional ISO datetime for scheduling)
            post_type     : str   (TEXT/IMAGE/VIDEO/DOCUMENT, default TEXT)
        """
        start = time.time()
        post_content = input_data.get("post_content", "")
        hashtags = input_data.get("hashtags", "")
        visibility = input_data.get("visibility", "PUBLIC")
        scheduled_time = input_data.get("scheduled_time")
        post_type = input_data.get("post_type", "TEXT")

        if not post_content:
            return self._failure("No post content provided", time.time() - start)

        self.logger.info("📤 LinkedInPostingAgent: posting to LinkedIn...")

        if scheduled_time:
            result: LinkedInPostResult = self.poster.schedule_post(
                post_content=post_content,
                scheduled_time=scheduled_time,
                hashtags=hashtags,
            )
            action = "scheduled"
        else:
            result = self.poster.post_to_linkedin(
                post_content=post_content,
                hashtags=hashtags,
                visibility=visibility,
                post_type=post_type,
            )
            action = "posted"

        if result.success:
            return self._success(
                output={
                    "post_id": result.post_id,
                    "post_url": result.post_url,
                    "timestamp": result.timestamp,
                    "action": action,
                    "scheduled_time": scheduled_time,
                },
                summary=f"✅ Successfully {action} to LinkedIn. URL: {result.post_url}",
                time=time.time() - start,
            )
        else:
            return self._failure(result.error_message or "LinkedIn posting failed", time.time() - start)
