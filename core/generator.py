"""
LinkedIn Content Generator - Core Brain
Clean, production-ready architecture.
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import logging

from .prompts import PromptBuilder
from .models import PostRequest, PostResponse, GenerationMode
from .rag import RAGEngine
from .llm import LLMProvider


# ===============================
# STATS TRACKING
# ===============================

@dataclass
class GenerationStats:
    generation_time: float
    mode_used: str
    context_sources: List[str]
    tokens_used: int = 0


# ===============================
# MAIN GENERATOR
# ===============================

class LinkedInGenerator:
    """
    Main LinkedIn content generator with clean SIMPLE vs ADVANCED architecture.
    
    Production optimizations:
    - Lazy RAG initialization (only when needed)
    - Singleton embedding model (shared across instances)
    - Graceful fallbacks
    """

    def __init__(self, mode: GenerationMode = GenerationMode.SIMPLE):
        self.mode = mode

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # ---- LLM INIT ----
        try:
            self.logger.info("🔄 Initializing LLM provider...")
            self.llm = LLMProvider()
            self.llm_available = True
            self.logger.info("✅ LLM provider ready")
        except Exception as e:
            self.logger.warning(f"⚠️ LLM init failed: {e}")
            self.llm = None
            self.llm_available = False

        # ---- LAZY RAG INIT (Production Optimization) ----
        # Don't initialize RAG until actually needed
        # Saves memory and startup time
        self.rag_engine = None
        self.rag_available = False
        self._rag_init_attempted = False

        # Metrics
        self.generation_count = 0
        self.total_generation_time = 0
    
    def _ensure_rag_initialized(self):
        """Lazy RAG initialization - only loads when actually needed."""
        if self._rag_init_attempted:
            return self.rag_available
        
        self._rag_init_attempted = True
        
        try:
            self.logger.info("🔄 Initializing RAG engine (lazy load)...")
            self.rag_engine = RAGEngine()
            self.rag_available = True
            self.logger.info("✅ RAG engine ready")
            return True
        except Exception as e:
            self.logger.warning(f"⚠️ RAG init failed: {e}")
            self.logger.warning("📝 Falling back to SIMPLE mode")
            self.rag_available = False
            return False

    # ===============================
    # PUBLIC GENERATE
    # ===============================

    def generate(self, request: PostRequest) -> PostResponse:

        start_time = datetime.now()

        try:

            # ---- DEMO FALLBACK ----
            if not self.llm_available or not self.llm:
                return self._generate_demo_response(request)

            # Use the mode from the REQUEST (what the user chose in UI),
            # not self.mode (which is the generator default).
            active_mode = request.mode
            self.logger.info(f"🎯 Generation mode: {active_mode.value}")

            context = None
            context_sources = ["direct_prompt"]

            # ---- ADVANCED MODE with LAZY RAG INIT ----
            if active_mode == GenerationMode.ADVANCED:
                # Lazy initialization - only load RAG when needed
                if self._ensure_rag_initialized():
                    try:
                        context = self.rag_engine.retrieve_context(request)
                        context_sources = context.sources_used
                        self.logger.info(f"✅ RAG context retrieved: {len(context.content)} chars, sources: {context_sources}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ RAG failed, fallback to simple: {e}")
                else:
                    self.logger.info("📝 RAG unavailable, using SIMPLE mode")

            # ---- SIMPLE MODE with GitHub URL ----
            # Even in simple mode, if a GitHub URL is provided we should
            # fetch basic context so the post is about the actual repo.
            elif request.github_url:
                self.logger.info("📝 Simple mode with GitHub URL — fetching repo context")
                if self._ensure_rag_initialized():
                    try:
                        context = self.rag_engine.retrieve_context(request)
                        context_sources = context.sources_used
                        self.logger.info(f"✅ Repo context for simple mode: {len(context.content)} chars")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Repo context fetch failed: {e}")

            # ---- BUILD PSYCHOLOGY PROMPT ----
            # Use PromptBuilder with enhanced psychology-driven prompts
            if context and hasattr(context, 'content') and context.content:
                # ADVANCED mode with context
                prompt = PromptBuilder.build_advanced_prompt(
                    request=request,
                    context=context.content,
                    context_sources=context.sources_used
                )
                self.logger.info(f"✅ Using ADVANCED prompt with {len(context.content)} chars of context")
            else:
                # SIMPLE mode without context
                prompt = PromptBuilder.build_simple_prompt(request=request)
                self.logger.info("✅ Using SIMPLE prompt (no context)")

            # ---- GENERATE ----
            result = self.llm.generate(prompt)

            if not result.success or not result.content:
                return self._generate_demo_response(request)

            post, hashtags, caption = self._parse_llm_response(result.content)

            generation_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(generation_time)

            return PostResponse(
                success=True,
                post=post,
                hashtags=hashtags,
                caption=caption,
                context_sources=context_sources,
                tokens_used=result.tokens_used,
                mode_used=active_mode.value,
                generation_time=generation_time
            )

        except Exception as e:
            self.logger.error(f"Generation failed: {str(e)}")
            return PostResponse(
                success=False,
                error_message=str(e),
                post="",
                hashtags="",
                caption=""
            )

    # ===============================
    # PARSER
    # ===============================

    def _parse_llm_response(self, content: str):
        """
        Parse LLM response - handles both structured (with labels) and natural output.
        
        Structured format:
            POST:
            [content]
            HASHTAGS:
            [tags]
            
        Natural format:
            [content with hashtags at bottom]
        """
        
        post, hashtags, caption = "", "", ""
        section = None
        has_labels = False
        
        # Check if content has structured labels
        content_upper = content.upper()
        if "POST:" in content_upper or "HASHTAGS:" in content_upper:
            has_labels = True
        
        if has_labels:
            # Parse structured format (legacy/compatibility)
            for line in content.split("\n"):
                line_stripped = line.strip()

                if line_stripped.upper().startswith("POST:"):
                    section = "post"
                    continue
                elif line_stripped.upper().startswith("HASHTAGS:"):
                    section = "hashtags"
                    continue
                elif line_stripped.upper().startswith("CAPTION:"):
                    section = "caption"
                    continue

                if section == "post":
                    post += line + "\n"
                elif section == "hashtags":
                    hashtags += line_stripped + " "
                elif section == "caption":
                    caption += line + "\n"
        else:
            # Parse natural format (new default)
            lines = content.strip().split("\n")
            post_lines = []
            hashtag_lines = []
            
            # Separate post content from hashtags
            for line in lines:
                line_stripped = line.strip()
                # Check if line is hashtags (starts with # or is all hashtags)
                if line_stripped and (line_stripped.startswith("#") or 
                                     all(word.startswith("#") or word == "" for word in line_stripped.split())):
                    hashtag_lines.append(line_stripped)
                else:
                    # Stop considering lines as post if we've started collecting hashtags
                    # and hit a non-hashtag line (likely meta-commentary)
                    if hashtag_lines and not line_stripped:
                        continue
                    elif hashtag_lines and line_stripped:
                        # Skip meta-commentary after hashtags
                        if any(phrase in line_stripped.lower() for phrase in 
                              ["refinement", "changes made", "improvements", "i've", "note:"]):
                            break
                        post_lines.append(line)
                    else:
                        post_lines.append(line)
            
            post = "\n".join(post_lines).strip()
            hashtags = " ".join(hashtag_lines).strip()
        
        # Fallback: if no post extracted, use entire content
        if not post:
            post = content.strip()
            # Try to extract hashtags from the end
            lines = post.split("\n")
            if lines and lines[-1].strip().startswith("#"):
                hashtags = lines[-1].strip()
                post = "\n".join(lines[:-1]).strip()

        return post.strip(), hashtags.strip(), caption.strip()

    # ===============================
    # DEMO MODE
    # ===============================

    def _generate_demo_response(self, request: PostRequest):

        demo_post = f"""Most people misunderstand {request.topic}.

And it’s costing them growth.

Here’s what actually matters:

• Start simple  
• Focus on outcomes  
• Ship consistently  

The difference isn’t talent.

It’s clarity.

What’s your experience with {request.topic}?"""

        return PostResponse(
            success=True,
            post=demo_post,
            hashtags="#AI #Tech #Building #Growth",
            caption=f"Rethinking {request.topic} with clarity.",
            context_sources=["demo_mode"],
            tokens_used=0,
            mode_used="demo"
        )

    # ===============================
    # METRICS
    # ===============================

    def _update_metrics(self, generation_time: float):
        self.generation_count += 1
        self.total_generation_time += generation_time

    @property
    def average_generation_time(self):
        if self.generation_count == 0:
            return 0
        return self.total_generation_time / self.generation_count

    def switch_mode(self, new_mode: GenerationMode):
        self.mode = new_mode
        if new_mode == GenerationMode.ADVANCED and not self.rag_engine:
            self.rag_engine = RAGEngine()
            self.rag_available = True
        self.logger.info(f"Switched to {new_mode.value}")

    # ===============================
    # REFINEMENT
    # ===============================

    def refine_post(self, original_post: str, request: PostRequest) -> PostResponse:
        """
        Humanizer Pass - Make AI content sound like a real person wrote it.
        
        NOT a refinement explainer - just rewrites cleanly.
        No meta-commentary. No analysis. Just the final post.
        """
        
        if not self.llm_available or not self.llm:
            # If LLM unavailable, return original as-is
            return PostResponse(
                success=True,
                post=original_post,
                hashtags="",
                caption="",
                mode_used="refinement_skipped"
            )
        
        tone = getattr(request.tone, 'value', str(request.tone)) if hasattr(request.tone, 'value') else str(request.tone)
        audience = getattr(request.audience, 'value', str(request.audience)) if hasattr(request.audience, 'value') else str(request.audience)
        
        refinement_prompt = f"""Rewrite this LinkedIn post to sound more natural, human, and informational.

                ORIGINAL POST:
                {original_post}

                ⚠️ CRITICAL ANTI-HALLUCINATION RULES:
                🚫 NEVER add fake statistics, percentages, or invented research claims
                🚫 NEVER fabricate "studies show" or "X% of people" claims
                🚫 NEVER add numbers or metrics not in the original
                ✅ Keep original facts intact, just improve the natural flow
                ✅ Add value through clearer explanations and frameworks
                ✅ Write like a knowledgeable professional, not a content machine

                ✅ IMPROVEMENT RULES:
                - Keep the core message and verified insights
                - Remove corporate tone and generic marketing phrases  
                - Remove any exaggerated or unverifiable claims in original
                - Make the hook engaging but honest (max 12 words, no clickbait)
                - Add line breaks for mobile readability (1-2 line paragraphs)
                - Use bullet points (•) for lists if helpful
                - End with genuine question, not salesy CTA
                - Sound conversational like explaining to a colleague
                - Be informational through clear explanations, not fake metrics
                - Tone: {tone}
                - Audience: {audience}

                ❌ STRICTLY FORBIDDEN:
                - Do NOT add fake statistics or percentages
                - Do NOT use "game-changing", "unlock", "the secret to", "revolutionary"
                - Do NOT use "Here's the good news" or "The truth is"
                - Do NOT add corporate buzzwords
                - Do NOT explain what you changed
                - Do NOT add meta-commentary like "Refinements made:" or "Changes:"
                - Do NOT include labels like "POST:" or "HASHTAGS:"
                - Do NOT add "studies show" or "research indicates" without real sources

                🎯 OUTPUT REQUIREMENT:
                Return ONLY the final rewritten post.
                No analysis. No explanations. No headings. No meta-commentary.
                Just write the post naturally as if you were the author.

                        try:
                            result = self.llm.generate(refinement_prompt)
                            
                            if not result.success or not result.content:
                                # Fallback to original
                                return PostResponse(
                                    success=True,
                                    post=original_post,
                                    mode_used="refinement_failed"
                                )
                            
                            post, hashtags, caption = self._parse_llm_response(result.content)
                            
                            return PostResponse(
                                success=True,
                                post=post if post else original_post,
                                hashtags=hashtags,
                                caption=caption,
                                mode_used="refined",
                                tokens_used=result.tokens_used
                            )
                            
                        except Exception as e:
                            self.logger.warning(f"⚠️ Refinement failed: {e}, using original")
                            return PostResponse(
                                success=True,
                                post=original_post,
                                mode_used="refinement_error"
                            )
                """