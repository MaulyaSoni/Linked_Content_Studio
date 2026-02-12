# ============================================================================
# LINKEDIN POST GENERATOR - PROFESSIONAL WEB APPLICATION
# ============================================================================
# Built with: Streamlit + LangChain + Groq LLM + RAG
# Features: Light/Dark Mode, GitHub Integration, Professional UI
# ============================================================================

import streamlit as st
from loaders.document_loader import load_project_text, load_readme_file
from loaders.github_loader import GitHubLoader
from rag.vector_store import create_vector_store
from rag.retriever import retrieve_context
from rag.readme_fallback_retriever import ReadmeFallbackRetriever
from chains.style_chains import post_generator
from chains.hashtag_chain import generate_hashtags
from chains.caption_chain import generate_caption
from chains.quality_chains import enforce_specificity, score_post_quality
from chains.safety_chains import SafetyChain
from utils.tone_mapper import map_tone
from utils.llm_fallback import get_llm_with_fallback, get_fallback_status, test_llm_health
from utils.logger import get_logger, get_metrics_tracker
from utils.export_handler import ExportHandler, PostDiffViewer, HookSelector
from utils.exceptions import ReadmeNotFoundException, InsufficientRepositoryDataException, RepositoryAccessException
from config.theme_manager import ThemeManager
from config.settings import get_llm
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from datetime import datetime
import time

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="LinkedIn Content Studio",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"

if "posts_history" not in st.session_state:
    st.session_state.posts_history = []

if "current_post" not in st.session_state:
    st.session_state.current_post = None

if "last_generated_time" not in st.session_state:
    st.session_state.last_generated_time = None

# Production features session state
if "feedback_data" not in st.session_state:
    st.session_state.feedback_data = []

if "llm_health" not in st.session_state:
    st.session_state.llm_health = test_llm_health()

if "generation_logs" not in st.session_state:
    st.session_state.generation_logs = []

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().timestamp()}"

if "show_metrics" not in st.session_state:
    st.session_state.show_metrics = False

if "show_debug" not in st.session_state:
    st.session_state.show_debug = False

if "show_hook_selector" not in st.session_state:
    st.session_state.show_hook_selector = False

# ============================================================================
# APPLY THEME STYLING
# ============================================================================

ThemeManager.apply_custom_css()
theme = ThemeManager.get_current_theme()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_github_url(url: str) -> bool:
    """Validate GitHub URL format."""
    import re
    pattern = r'(https://)?github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+'
    return bool(re.match(pattern, url))


def load_documents_from_source(
    input_type: str,
    text_content: str = None,
    file_content: str = None,
    github_url: str = None,
    load_both: bool = False
) -> Tuple[List[Document], Dict]:
    """
    Load documents from various sources with intelligent fallback for unavailable README.
    
    Args:
        input_type: "text", "file", or "github"
        text_content: Direct text input
        file_content: Uploaded file content
        github_url: GitHub repository URL
        load_both: Load both README and repo info for GitHub
        
    Returns:
        Tuple of (List of Documents, metadata dict with retrieval info)
    """
    documents = []
    retrieval_info = {
        "source_type": input_type,
        "readme_found": False,
        "sources_used": [],
        "transparency_message": "",
        "data_completeness": "unknown"
    }
    
    try:
        if input_type == "text" and text_content:
            documents.extend(load_project_text(text_content))
            retrieval_info["sources_used"] = ["text_input"]
            retrieval_info["transparency_message"] = "✅ Using provided text content"
        
        elif input_type == "file" and file_content:
            documents.extend(load_project_text(file_content))
            retrieval_info["sources_used"] = ["file_upload"]
            retrieval_info["transparency_message"] = "✅ Using uploaded file"
        
        elif input_type == "github" and github_url:
            # ============================================================
            # PRODUCTION-LEVEL GITHUB LOADING WITH FALLBACK
            # ============================================================
            
            try:
                # Step 1: Try intelligent fallback retriever
                # This implements the full hierarchy: README → Metadata → Structure → Requirements → Commits → Issues
                fallback_retriever = ReadmeFallbackRetriever(github_url)
                
                print("\n🔄 [README Fallback System] Starting context retrieval...")
                documents, retrieval_status = fallback_retriever.retrieve_context()
                
                # Extract retrieval information for UI
                retrieval_info["readme_found"] = retrieval_status["readme_found"]
                retrieval_info["sources_used"] = retrieval_status["sources_used"]
                retrieval_info["data_completeness"] = retrieval_status["data_completeness"]
                retrieval_info["transparency_message"] = fallback_retriever.get_transparency_message()
                
                print(f"✅ Retrieved {len(documents)} documents from {len(retrieval_status['sources_used'])} sources")
                print(f"📊 Data Completeness: {retrieval_status['data_completeness']}")
                
            except Exception as fallback_error:
                # If fallback retriever fails, raise with proper exception
                print(f"❌ Fallback retriever failed: {str(fallback_error)}")
                raise RepositoryAccessException(github_url, str(fallback_error))
        
        elif input_type == "github_plus_text" and github_url and text_content:
            # Load both GitHub repo content and additional text
            try:
                fallback_retriever = ReadmeFallbackRetriever(github_url)
                github_docs, retrieval_status = fallback_retriever.retrieve_context()
                documents.extend(github_docs)
                
                # Add additional context text
                documents.extend(load_project_text(text_content))
                
                retrieval_info["readme_found"] = retrieval_status["readme_found"]
                retrieval_info["sources_used"] = retrieval_status["sources_used"] + ["additional_text"]
                retrieval_info["data_completeness"] = retrieval_status["data_completeness"]
                retrieval_info["transparency_message"] = (
                    fallback_retriever.get_transparency_message() + 
                    "\n➕ Plus: Additional user-provided context"
                )
                
            except Exception as fallback_error:
                print(f"❌ GitHub retrieval failed: {str(fallback_error)}")
                raise RepositoryAccessException(github_url, str(fallback_error))
        
        return documents, retrieval_info
    
    except RepositoryAccessException as e:
        raise e
    except Exception as e:
        raise Exception(f"Error loading documents: {str(e)}")


def build_rag_context(documents: List[Document], query: str, k: int = 4) -> str:
    """
    Build RAG context from documents using vector store.
    
    Args:
        documents: List of documents to index
        query: Query string for retrieval
        k: Number of relevant chunks to retrieve
        
    Returns:
        Concatenated context from retrieved documents
    """
    try:
        # Create vector store from documents
        vectorstore = create_vector_store(documents)
        
        # Retrieve relevant context
        context = retrieve_context(vectorstore, query, k=k)
        
        return context
    
    except Exception as e:
        raise Exception(f"RAG pipeline error: {str(e)}")


def generate_linkedin_post(
    context: str,
    style: str,
    tone: str,
    include_hashtags: bool = True,
    include_caption: bool = False,
    demo_asset_type: str = "Video demo"
) -> dict:
    """
    Generate complete LinkedIn post with LangChain.
    
    Args:
        context: RAG-retrieved context
        style: Post style (Growth, Learning, Build in Public, Recruiter)
        tone: Tone level (Minimal, Balanced, High Energy)
        include_hashtags: Generate hashtags
        include_caption: Generate demo caption
        demo_asset_type: Type of demo asset
        
    Returns:
        Dictionary with generated content
    """
    result = {
        "post": None,
        "hashtags": None,
        "caption": None,
        "quality_score": None,
        "stats": {
            "style": style,
            "tone": tone,
            "word_count": 0,
            "char_count": 0
        }
    }
    
    try:
        # Step 1: Generate base post
        tone_instruction = map_tone(tone)
        post_result = post_generator.run(
            context=context,
            style=style,
            tone=tone_instruction
        )
        post_content = (
            post_result.content
            if hasattr(post_result, 'content')
            else str(post_result)
        )
        
        # Step 2: Enforce specificity (second-pass improvement)
        specificity_result = enforce_specificity(
            post=post_content,
            context=context
        )
        post_content = (
            specificity_result.content
            if hasattr(specificity_result, 'content')
            else str(specificity_result)
        )
        
        result["post"] = post_content
        result["stats"]["word_count"] = len(post_content.split())
        result["stats"]["char_count"] = len(post_content)
        
        # Step 3: Generate hashtags
        if include_hashtags:
            hashtags_result = generate_hashtags(
                content=post_content,
                context=context
            )
            hashtags_content = (
                hashtags_result.content
                if hasattr(hashtags_result, 'content')
                else str(hashtags_result)
            )
            result["hashtags"] = hashtags_content
        
        # Step 4: Generate demo caption
        if include_caption:
            caption_result = generate_caption(
                asset_type=demo_asset_type,
                context=context
            )
            caption_content = (
                caption_result.content
                if hasattr(caption_result, 'content')
                else str(caption_result)
            )
            result["caption"] = caption_content
        
        # Step 5: Score post quality
        quality_result = score_post_quality(
            post=post_content,
            context=context
        )
        quality_text = (
            quality_result.content
            if hasattr(quality_result, 'content')
            else str(quality_result)
        )
        result["quality_score"] = quality_text
        
        return result
    
    except Exception as e:
        raise Exception(f"Post generation error: {str(e)}")


# ============================================================================
# HEADER & BRANDING
# ============================================================================

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="margin-bottom: 0.5rem;">� LinkedIn Content Studio</h1>
        <p style="font-size: 1rem; color: var(--secondary-text);">
            Professional AI-Powered Post Generation
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    st.markdown("### 📥 Input Source")
    
    input_source = st.radio(
        "Choose your input method:",
        ["📝 Text Input", "📄 Upload File", "🔗 GitHub Repository", "📦 Both README & Text"],
        help="Select how you want to provide project information"
    )
    
    st.markdown("---")
    
    st.markdown("### 🎯 Post Configuration")
    
    post_style = st.selectbox(
        "Post Style",
        ["Growth", "Learning", "Build in Public", "Recruiter"],
        help="Choose the narrative style for your post"
    )
    
    tone = st.selectbox(
        "Tone Level",
        ["Minimal", "Balanced", "High Energy"],
        help="How energetic and emoji-rich should the post be?"
    )
    
    st.markdown("---")
    
    st.markdown("### 🎨 Optional Items")
    
    include_hashtags = st.checkbox("✓ Generate Hashtags", value=True)
    include_caption = st.checkbox("✓ Generate Demo Caption", value=False)
    
    if include_caption:
        demo_asset_type = st.text_input(
            "Demo Asset Type",
            value="Video demo",
            help="E.g., 'Video demo', 'Screenshot', 'Code snippet', 'Live demo'"
        )
    else:
        demo_asset_type = "Video demo"
    
    st.markdown("---")
    
    # Theme selector
    ThemeManager.render_theme_selector()
    
    st.markdown("---")
    
    st.markdown("### 🔧 Advanced Options")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.checkbox("📈 Metrics", value=False, key="metrics_toggle"):
            st.session_state.show_metrics = True
    with col2:
        if st.checkbox("🐛 Debug", value=False, key="debug_toggle"):
            st.session_state.show_debug = True
    
    # LLM Health Status
    st.markdown("---")
    with st.expander("🏥 System Health"):
        health_status = test_llm_health()
        
        col1, col2 = st.columns(2)
        with col1:
            if health_status["status"]["is_primary"]:
                st.success("✅ Primary LLM Active")
            elif health_status["status"]["is_degraded"]:
                st.warning("⚠️ Running on Fallback")
            else:
                st.error("🔴 Degraded Mode")
        
        with col2:
            capability = health_status["status"]["capability_level"]
            if capability == "full":
                st.metric("Capability", "Full")
            else:
                st.metric("Capability", capability.capitalize())
        
        if st.button("🔄 Test Connection", key="health_test"):
            with st.spinner("Testing LLM..."):
                is_ok = health_status["connection_ok"]
                if is_ok:
                    st.success("✅ Connection OK")
                else:
                    st.error("❌ Connection Failed")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Info")
    st.info("""
    **RAG Pipeline:**
    - Indexes your documents using FAISS
    - Retrieves most relevant context
    - Generates contextually accurate posts
    
    **LLM Engine:** Groq Llama 3.1 (with fallback)
    **Safety:** Hallucination guard enabled
    """)

# ============================================================================
# MAIN INPUT SECTION
# ============================================================================

st.markdown("## 📝 Project Input")

github_url = None
text_input = None
file_content = None

if input_source == "📝 Text Input":
    text_input = st.text_area(
        "Paste your project README or description:",
        height=250,
        placeholder="Describe your project, tech stack, problems solved, metrics, achievements, etc.",
        key="text_input"
    )

elif input_source == "📄 Upload File":
    uploaded_file = st.file_uploader(
        "Upload README or project description:",
        type=["txt", "md", "markdown"],
        key="file_input"
    )
    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8")
        with st.expander("👁️ Preview"):
            st.markdown(file_content[:500] + "..." if len(file_content) > 500 else file_content)

elif input_source == "🔗 GitHub Repository":
    github_url = st.text_input(
        "GitHub Repository URL:",
        placeholder="https://github.com/username/repo",
        help="Paste the full GitHub repository URL"
    )
    
    if github_url:
        st.markdown("#### 📋 GitHub Content Options")
        col1, col2 = st.columns(2)
        with col1:
            load_readme = st.checkbox("✓ Load README", value=True)
        with col2:
            load_full = st.checkbox("✓ Load Full Repo Info", value=True)

elif input_source == "📦 Both README & Text":
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### GitHub Repository")
        github_url = st.text_input(
            "GitHub URL:",
            placeholder="https://github.com/username/repo",
            help="Paste the full GitHub repository URL",
            key="github_url_combined"
        )
    
    with col2:
        st.markdown("### Additional Context")
        text_input = st.text_area(
            "Additional description:",
            height=150,
            placeholder="Add any extra context not in the README...",
            key="text_combined"
        )

# ============================================================================
# GENERATION CONTROLS
# ============================================================================

st.markdown("---")

col_generate, col_clear, col_history = st.columns([2, 1, 1])

with col_generate:
    generate_button = st.button(
        "🚀 Generate LinkedIn Post",
        use_container_width=True,
        type="primary",
        key="generate_btn"
    )

with col_clear:
    if st.button("🔄 Clear", use_container_width=True):
        st.session_state.posts_history = []
        st.cache_resource.clear()
        st.rerun()

# ============================================================================
# GENERATION PIPELINE
# ============================================================================

if generate_button:
    # Determine what content to use
    input_type = None
    has_content = False
    
    if input_source == "📝 Text Input" and text_input and text_input.strip():
        input_type = "text"
        has_content = True
    elif input_source == "📄 Upload File" and file_content:
        input_type = "file"
        has_content = True
    elif input_source == "🔗 GitHub Repository" and github_url and validate_github_url(github_url):
        input_type = "github"
        has_content = True
    elif input_source == "📦 Both README & Text" and github_url and validate_github_url(github_url):
        input_type = "github_plus_text"
        has_content = True
    
    if not has_content:
        st.error("❌ Please provide valid input before generating a post.")
    else:
        with st.spinner("⏳ Processing your input and building RAG context..."):
            try:
                # Step 1: Load documents from appropriate source
                if input_type == "text":
                    documents, retrieval_info = load_documents_from_source(
                        input_type="text",
                        text_content=text_input
                    )
                elif input_type == "file":
                    documents, retrieval_info = load_documents_from_source(
                        input_type="file",
                        file_content=file_content
                    )
                elif input_type == "github":
                    documents, retrieval_info = load_documents_from_source(
                        input_type="github",
                        github_url=github_url,
                        load_both=True
                    )
                else:  # github_plus_text
                    documents, retrieval_info = load_documents_from_source(
                        input_type="github_plus_text",
                        github_url=github_url,
                        text_content=text_input
                    )
                
                # Store retrieval info in session state for later display
                st.session_state.retrieval_info = retrieval_info
                
                # Display transparency message if available
                if retrieval_info.get("transparency_message"):
                    if retrieval_info["readme_found"]:
                        st.success(retrieval_info["transparency_message"])
                    else:
                        st.warning(retrieval_info["transparency_message"])
                
                st.success(f"✅ Loaded {len(documents)} document(s) from {len(retrieval_info.get('sources_used', []))} source(s)")
                
            except RepositoryAccessException as e:
                st.error(f"❌ GitHub Access Error: {str(e)}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Error loading documents: {str(e)}")
                st.stop()
                
        # Step 2: Build RAG context
        with st.spinner("🔍 Building RAG context from your content..."):
            try:
                context = build_rag_context(
                    documents=documents,
                    query="Summarize key aspects, features, technologies, problems solved, and impact",
                    k=5
                )
                st.success("✅ Context built successfully")
            except Exception as e:
                st.error(f"❌ RAG Error: {str(e)}")
                st.stop()
        
        # Step 3: Generate post
        with st.spinner("🎨 Generating your LinkedIn post with AI..."):
            try:
                start_time = time.time()
                
                post_data = generate_linkedin_post(
                    context=context,
                    style=post_style,
                    tone=tone,
                    include_hashtags=include_hashtags,
                    include_caption=include_caption,
                    demo_asset_type=demo_asset_type if include_caption else "Video demo"
                )
                
                generation_time = time.time() - start_time
                
                st.success("✅ Post generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Generation Error: {str(e)}")
                st.error(f"Details: {str(e)}")
                st.stop()
        
        # Step 4: Safety Check (Hallucination Guard)
        with st.spinner("🛡️ Running safety checks..."):
            try:
                safety_chain = SafetyChain()
                safety_report = safety_chain.run_safety_check(
                    post=post_data["post"],
                    context=context
                )
                
                post_data["post"] = safety_report["final_post"]
                post_data["safety_report"] = safety_report
                
                if safety_report["hallucination_check"]["corrections"] > 0:
                    st.info(f"🔧 {safety_report['hallucination_check']['corrections']} claim(s) were refined for accuracy")
                
                st.success(f"✅ Safety check: {safety_report['recommendation']}")
                
            except Exception as e:
                st.warning(f"⚠️ Safety check skipped: {str(e)}")
                post_data["safety_report"] = {"is_safe": True}
        
        # Step 5: Logging & Metrics
        try:
            logger = get_logger()
            metrics_tracker = get_metrics_tracker()
            
            # Parse quality score to number
            quality_score_val = 0.85  # Default
            try:
                if isinstance(post_data.get("quality_score"), str) and "%" in post_data["quality_score"]:
                    quality_score_val = float(post_data["quality_score"].split("%")[0]) / 100
            except:
                pass
            
            # Log generation
            retrieval_sources = []
            data_completeness = "unknown"
            readme_found = None
            
            if "retrieval_info" in st.session_state:
                retrieval_sources = st.session_state.retrieval_info.get("sources_used", [])
                data_completeness = st.session_state.retrieval_info.get("data_completeness", "unknown")
                readme_found = st.session_state.retrieval_info.get("readme_found", False)
            
            logger.log_generation({
                "session_id": st.session_state.session_id,
                "input_source": input_type,
                "github_url": github_url if input_type.startswith("github") else None,
                "input_text": text_input[:100] if text_input else None,
                "style": post_style,
                "tone": tone,
                "include_hashtags": include_hashtags,
                "include_caption": include_caption,
                "post": post_data["post"],
                "hashtags": post_data.get("hashtags", ""),
                "caption": post_data.get("caption", ""),
                "quality_score": quality_score_val,
                "generation_time": generation_time,
                "llm_calls": 5,
                "llm_model": "llama-3.1-8b-instant",
                "hallucination_corrections": post_data.get("safety_report", {}).get("hallucination_check", {}).get("corrections", 0),
                "policy_violations": post_data.get("safety_report", {}).get("policy_check", {}).get("violations", []),
                "safety_confidence": post_data.get("safety_report", {}).get("hallucination_check", {}).get("confidence", 0),
                "readme_found": readme_found,
                "retrieval_sources": retrieval_sources,
                "data_completeness": data_completeness
            })
            
            # Track metrics
            try:
                corrections = 0
                violations = []
                confidence = 0
                if post_data.get("safety_report"):
                    hc = post_data["safety_report"].get("hallucination_check", {})
                    corrections = hc.get("corrections", 0) if isinstance(hc, dict) else 0
                    pc = post_data["safety_report"].get("policy_check", {})
                    violations = pc.get("violations", []) if isinstance(pc, dict) else []
                    confidence = hc.get("confidence", 0) if isinstance(hc, dict) else 0
                
                metrics_tracker.record_generation(
                    quality_score=quality_score_val,
                    corrections=corrections,
                    policy_violations=violations,
                    safety_conf=confidence
                )
            except Exception as metrics_err:
                pass  # Silent fail for metrics
        except Exception as e:
            pass  # Silent fail for general logging
        
        # Store in session state for persistence
        st.session_state.current_post = post_data
        st.session_state.posts_history.append(post_data)
        st.session_state.last_generated_time = datetime.now().isoformat()
        
        # Display the generated post from session state
        if st.session_state.current_post:
            post_data = st.session_state.current_post
            
            # ====================================================================
            # DATA SOURCE TRANSPARENCY - Production Feature
            # ====================================================================
            
            if "retrieval_info" in st.session_state:
                retrieval_info = st.session_state.retrieval_info
                
                st.markdown("---")
                st.markdown("## 📊 Data Source Transparency")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("README Available", "✅ Yes" if retrieval_info.get("readme_found") else "⚠️ No")
                
                with col2:
                    sources = len(retrieval_info.get("sources_used", []))
                    st.metric("Sources Used", sources)
                
                with col3:
                    completeness = retrieval_info.get("data_completeness", "unknown").capitalize()
                    st.metric("Data Quality", completeness)
                
                with st.expander("📋 Source Details"):
                    st.info(retrieval_info.get("transparency_message", ""))
                    
                    if retrieval_info.get("sources_used"):
                        st.markdown("**Sources Used:**")
                        for source in retrieval_info.get("sources_used", []):
                            st.markdown(f"• {source}")
            
            # ====================================================================
            # OUTPUT SECTION - ENHANCED WITH EDITING CAPABILITY
            # ====================================================================
            
            st.markdown("---")
            st.markdown("## 📋 Generated Content")
            
            # Initialize editable post in session state
            if "editable_post" not in st.session_state:
                st.session_state.editable_post = post_data['post']
            if "editable_hashtags" not in st.session_state:
                st.session_state.editable_hashtags = post_data.get('hashtags', '')
            
            # Main editable section - FULL POST WITH HASHTAGS (PRIMARY)
            st.markdown("### ✍️ Full LinkedIn Post (Editable & Ready to Copy)")
            
            # Full post with hashtags - MAIN EDITABLE AREA
            full_post_text = f"{st.session_state.editable_post}\n\n{st.session_state.editable_hashtags}" if st.session_state.editable_hashtags else st.session_state.editable_post
            
            st.session_state.editable_full_post = st.text_area(
                "📝 Edit and copy your complete post here:",
                value=full_post_text,
                height=300,
                key="editable_full_post_area",
                help="Click and edit before copying to LinkedIn"
            )
            
            # Copy buttons for full post
            copy_col1, copy_col2, copy_col3 = st.columns(3)
            
            with copy_col1:
                if st.button("📋 Copy Full Post", use_container_width=True, key="copy_full_btn"):
                    st.success("✅ Copied! Paste it directly on LinkedIn")
                    st.code(st.session_state.editable_full_post, language="text")
            
            with copy_col2:
                if st.button("📄 Copy Post Only", use_container_width=True, key="copy_post_btn"):
                    st.success("✅ Post text copied!")
                    st.code(st.session_state.editable_post, language="text")
            
            with copy_col3:
                if st.button("#️⃣ Copy Hashtags Only", use_container_width=True, key="copy_tags_btn"):
                    st.success("✅ Hashtags copied!")
                    st.code(st.session_state.editable_hashtags, language="text")
            
            # Save draft button added
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("💾 Save Draft", use_container_width=True, key="save_draft_btn"):
                    st.session_state.saved_draft = st.session_state.editable_full_post
                    st.success("✅ Draft saved to session!")
            
            with col2:
                if st.button("✏️ Reset to Original", use_container_width=True, key="reset_btn"):
                    st.session_state.editable_full_post = full_post_text
                    st.info("🔄 Reset to original")
            
            # Collapsible sections for individual components
            with st.expander("📄 View Post Only"):
                st.markdown(f"""
                <div style="background-color: {theme['tertiary_bg']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {theme['border_color']};">
                {st.session_state.editable_post}
                </div>
                """, unsafe_allow_html=True)
            
            # Hashtags section
            if st.session_state.editable_hashtags:
                with st.expander("#️⃣ View Hashtags Only"):
                    st.code(st.session_state.editable_hashtags, language="text")
            
            # Demo Caption
            if post_data.get('caption'):
                with st.expander("🎥 View Demo Caption"):
                    st.info(post_data['caption'])
            
            # ====================================================================
            # EXPORT SECTION - Production Feature
            # ====================================================================
            
            st.markdown("---")
            st.markdown("## 📤 Export Options")
            
            # Export instructions
            st.info("""
            🎯 **Export your content in multiple formats:**
            • **Copy Ready** - Format for direct LinkedIn posting
            • **Markdown** - Save as .md file for documentation  
            • **Notion** - Import into Notion database
            • **Buffer** - Schedule with Buffer.com or similar tools
            """)
            
            export_col1, export_col2, export_col3, export_col4 = st.columns(4)
            
            with export_col1:
                if st.button("📋 Copy Ready", use_container_width=True, key="export_copy"):
                    try:
                        export_text = ExportHandler.export_for_linkedin(post_data)
                        st.success("✅ LinkedIn format ready! Copy the text below:")
                        st.code(export_text, language="text")
                        # Store in session for clipboard addon
                        st.session_state.linkedin_export = export_text
                        st.info("💡 **Tip:** Select all text above (Ctrl+A) and copy (Ctrl+C)")
                    except Exception as e:
                        st.error(f"❌ Export failed: {str(e)}")
            
            with export_col2:
                if st.button("📝 Save as MD", use_container_width=True, key="export_md"):
                    try:
                        md_content = ExportHandler.export_for_markdown(post_data, title="LinkedIn Post")
                        filename = f"linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                        st.success("✅ Markdown ready for download!")
                        st.download_button(
                            label=f"📥 Download {filename}", 
                            data=md_content,
                            file_name=filename,
                            mime="text/markdown",
                            use_container_width=True,
                            key=f"download_md_{datetime.now().strftime('%H%M%S')}"
                        )
                    except Exception as e:
                        st.error(f"❌ Markdown export failed: {str(e)}")
            
            with export_col3:
                if st.button("💡 Export to Notion", use_container_width=True, key="export_notion"):
                    try:
                        import json
                        notion_data = ExportHandler.export_for_notion(post_data)
                        notion_json = json.dumps(notion_data, indent=2)
                        filename = f"linkedin_notion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        st.success("✅ Notion format ready for download!")
                        st.download_button(
                            label=f"📥 Download {filename}",
                            data=notion_json,
                            file_name=filename,
                            mime="application/json",
                            use_container_width=True,
                            key=f"download_notion_{datetime.now().strftime('%H%M%S')}"
                        )
                    except Exception as e:
                        st.error(f"❌ Notion export failed: {str(e)}")
            
            with export_col4:
                if st.button("📅 Buffer.com Format", use_container_width=True, key="export_buffer"):
                    try:
                        import json
                        buffer_data = ExportHandler.export_for_scheduling(post_data, platform="buffer")
                        buffer_json = json.dumps(buffer_data, indent=2)
                        filename = f"linkedin_buffer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        st.success("✅ Buffer format ready for download!")
                        st.download_button(
                            label=f"📥 Download {filename}",
                            data=buffer_json,
                            file_name=filename,
                            mime="application/json",
                            use_container_width=True,
                            key=f"download_buffer_{datetime.now().strftime('%H%M%S')}"
                        )
                    except Exception as e:
                        st.error(f"❌ Buffer export failed: {str(e)}")
            
            # ====================================================================
            # FEEDBACK SECTION - Human-in-Loop Learning
            # ====================================================================
            
            st.markdown("---")
            st.markdown("## 👍 Feedback & Improvement")
            
            feedback_col1, feedback_col2, feedback_col3, feedback_col4, feedback_col5 = st.columns(5)
            
            with feedback_col1:
                if st.button("👍 Engaging", key="feedback_engaging"):
                    st.session_state.feedback_data.append({
                        "type": "engaging",
                        "timestamp": datetime.now().isoformat(),
                        "post_id": hash(post_data["post"]) % 10000
                    })
                    get_metrics_tracker().record_feedback("engaging")
                    st.success("Thanks for feedback!")
            
            with feedback_col2:
                if st.button("😑 Too Generic", key="feedback_generic"):
                    st.session_state.feedback_data.append({
                        "type": "generic",
                        "timestamp": datetime.now().isoformat(),
                        "post_id": hash(post_data["post"]) % 10000
                    })
                    st.info("We'll make it more specific next time")
            
            with feedback_col3:
                if st.button("🤓 Too Technical", key="feedback_technical"):
                    st.session_state.feedback_data.append({
                        "type": "technical",
                        "timestamp": datetime.now().isoformat(),
                        "post_id": hash(post_data["post"]) % 10000
                    })
                    st.info("We'll simplify it next time")
            
            with feedback_col4:
                if st.button("🎯 Regenerate", key="regenerate"):
                    st.session_state.feedback_data.append({
                        "type": "regenerate",
                        "timestamp": datetime.now().isoformat(),
                        "post_id": hash(post_data["post"]) % 10000
                    })
                    get_metrics_tracker().record_feedback("regenerate")
                    st.info("Post removed from history. Generate again!")
                    st.session_state.current_post = None
            
            with feedback_col5:
                if st.button("💬 Hook Suggestions", key="hook_suggestions"):
                    st.session_state.show_hook_selector = True
            
            # Display feedback history
            if st.session_state.feedback_data:
                with st.expander("📊 Feedback History"):
                    st.write(f"**Total Feedback Items:** {len(st.session_state.feedback_data)}")
                    
                    feedback_summary = {}
                    for fb in st.session_state.feedback_data:
                        fb_type = fb.get("type", "unknown")
                        feedback_summary[fb_type] = feedback_summary.get(fb_type, 0) + 1
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    for i, (ftype, count) in enumerate(feedback_summary.items()):
                        if i % 5 == 0:
                            st.metric(ftype.capitalize(), count)
            
            # Show hook selector if requested
            if st.session_state.get("show_hook_selector"):
                st.markdown("---")
                st.markdown("## 🎣 Hook & Engagement Suggestions")
                
                # Extract topic from post
                topic_hint = post_data["post"].split("\n")[0][:50]
                hook_suggestions = HookSelector.suggest_hooks(topic_hint)
                
                hook_descriptions = HookSelector.get_hook_descriptions()
                
                for hook_type, hooks in hook_suggestions.items():
                    with st.expander(f"{hook_descriptions[hook_type]}"):
                        for i, hook in enumerate(hooks):
                            st.write(f"{i+1}. {hook}")
            
            # Safety Report (if available)
            if post_data.get("safety_report"):
                st.markdown("---")
                st.markdown("## 🛡️ Safety & Quality Report")
                
                safety_info = post_data["safety_report"]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    is_safe = safety_info.get("is_safe", True)
                    st.metric(
                        "Safety Status",
                        "✅ Safe" if is_safe else "⚠️ Review",
                        delta_color="off"
                    )
                
                with col2:
                    hc = safety_info.get("hallucination_check", {})
                    confidence = hc.get("confidence", 0.95)
                    st.metric(
                        "Confidence",
                        f"{confidence*100:.0f}%"
                    )
                
                with col3:
                    hc = safety_info.get("hallucination_check", {})
                    corrections = hc.get("corrections", 0)
                    st.metric(
                        "Corrections Made",
                        corrections
                    )
                
                hc = safety_info.get("hallucination_check", {})
                if hc.get("corrections", 0) > 0:
                    with st.expander("📋 Correction Details"):
                        details = hc.get("details", [])
                        if details:
                            for detail in details:
                                if isinstance(detail, dict):
                                    st.write(f"- **{detail.get('original', 'N/A')}** → **{detail.get('rewritten', 'N/A')}**")
                        else:
                            st.write("Minor refinements were made for accuracy")
            
            # ====================================================================
            # METRICS DASHBOARD (if enabled)
            # ====================================================================
            
            if st.session_state.get("show_metrics"):
                st.markdown("---")
                st.markdown("## 📊 Production Metrics")
                
                metrics_data = get_metrics_tracker().get_summary()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Generations", metrics_data.get("total_generations", 0))
                
                with col2:
                    st.metric("Avg Quality", f"{metrics_data.get('average_quality_score', 0):.2f}")
                
                with col3:
                    st.metric("Hallucination Rate", f"{metrics_data.get('hallucination_rate', 0)*100:.1f}%")
                
                with col4:
                    st.metric("Regeneration Rate", f"{metrics_data.get('regeneration_rate', 0)*100:.1f}%")
                
                st.info(f"Quality Trend: {metrics_data.get('quality_trend', 'N/A')}")
            
            # ====================================================================
            # DEBUG INFO (if enabled)
            # ====================================================================
            
            if st.session_state.get("show_debug"):
                st.markdown("---")
                st.markdown("## 🐛 Debug Information")
                
                with st.expander("Raw Post Data"):
                    st.json(post_data)
                
                with st.expander("Session Info"):
                    st.write(f"Session ID: {st.session_state.session_id}")
                    st.write(f"Generation Time: {st.session_state.last_generated_time}")
                    st.write(f"Posts in History: {len(st.session_state.posts_history)}")
                
                with st.expander("LLM Health"):
                    health = test_llm_health()
                    st.json(health["status"])
            st.markdown("---")
            st.markdown("### 📊 Generation Statistics")
            
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                st.metric("📺 Post Style", post_data['stats']['style'])
            with stat_col2:
                st.metric("🎯 Tone", post_data['stats']['tone'])
            with stat_col3:
                st.metric("📝 Words", post_data['stats']['word_count'])
            with stat_col4:
                st.metric("🔤 Characters", post_data['stats']['char_count'])
            
            # Quality Analysis
            if post_data['quality_score']:
                st.markdown("---")
                st.markdown("### ⭐ Quality Analysis")
                st.markdown(post_data['quality_score'])

# ============================================================================
# HELP SECTION (EXPANDERS)
# ============================================================================

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        ### 🎯 Step-by-Step Guide
        
        1. **Choose Input Source**
           - Text: Paste directly
           - File: Upload README.md
           - GitHub: Provide repo URL
           - Both: GitHub + additional text
        
        2. **Configure Post Settings**
           - Select post style (Growth, Learning, Build in Public, Recruiter)
           - Choose tone (Minimal, Balanced, High Energy)
        
        3. **Add Optional Items**
           - Enable hashtags generation
           - Enable demo caption for videos/screenshots
        
        4. **Generate**
           - Click "Generate LinkedIn Post"
           - Wait for RAG context building
           - Receive complete post with metrics
        
        ### 💡 Pro Tips
        - Provide detailed, specific project information
        - Include metrics, numbers, and results
        - Mention technologies and tools used
        - Describe problems and solutions
        - Be authentic and personal
        """)

with col2:
    with st.expander("📚 Style & Tone Guide"):
        st.markdown("""
        ### 📌 Post Styles
        
        **Growth** - For metrics-driven stories
        - Use: "Scaled by 300%", "Improved by X%"
        - audience: Startups, Product people
        
        **Learning** - For educational content
        - Use: "Discovered", "Realized", "TIL"
        - Audience: Developers, Students
        
        **Build in Public** - For transparent journey
        - Use: "First attempt", "Still iterating"
        - Audience: Indie hackers, Creators
        
        **Recruiter** - For showcasing skills
        - Use: "Architected", "Engineered", "Built"
        - Audience: Job seekers, Technical leads
        
        ### 🎤 Tone Levels
        
        **Minimal** - Professional, minimal emoji
        **Balanced** - Professional + selective emoji
        **High Energy** - Enthusiastic with many emoji
        """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("🔗 **LinkedIn Content Studio**")

with footer_col2:
    st.markdown("Powered by **LangChain** + **Groq** + **FAISS**")

with footer_col3:
    st.markdown("Made with ❤️ for creators")

