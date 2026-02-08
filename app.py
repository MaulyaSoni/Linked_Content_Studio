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
from chains.style_chains import post_generator
from chains.hashtag_chain import generate_hashtags
from chains.caption_chain import generate_caption
from chains.quality_chains import enforce_specificity, score_post_quality
from utils.tone_mapper import map_tone
from config.theme_manager import ThemeManager
from config.settings import get_llm
from typing import List
from langchain_core.documents import Document

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
) -> List[Document]:
    """
    Load documents from various sources with RAG integration.
    
    Args:
        input_type: "text", "file", or "github"
        text_content: Direct text input
        file_content: Uploaded file content
        github_url: GitHub repository URL
        load_both: Load both README and repo info for GitHub
        
    Returns:
        List of LangChain Documents
    """
    documents = []
    
    try:
        if input_type == "text" and text_content:
            documents.extend(load_project_text(text_content))
        
        elif input_type == "file" and file_content:
            documents.extend(load_project_text(file_content))
        
        elif input_type == "github" and github_url:
            loader = GitHubLoader()
            
            if load_both:
                # Load complete repository information
                documents.extend(loader.load_repo_complete(github_url))
            else:
                # Load only README
                documents.extend(loader.load_readme(github_url))
        
        elif input_type == "github_plus_text" and github_url and text_content:
            # Load both GitHub repo and additional text
            loader = GitHubLoader()
            documents.extend(loader.load_repo_complete(github_url))
            documents.extend(load_project_text(text_content))
        
        return documents
    
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
    st.markdown("### 📊 Quick Info")
    st.info("""
    **RAG Pipeline:**
    - Indexes your documents using FAISS
    - Retrieves most relevant context
    - Generates contextually accurate posts
    
    **LLM Engine:** Groq Llama 3.1
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
                    documents = load_documents_from_source(
                        input_type="text",
                        text_content=text_input
                    )
                elif input_type == "file":
                    documents = load_documents_from_source(
                        input_type="file",
                        file_content=file_content
                    )
                elif input_type == "github":
                    documents = load_documents_from_source(
                        input_type="github",
                        github_url=github_url,
                        load_both=True
                    )
                else:  # github_plus_text
                    documents = load_documents_from_source(
                        input_type="github_plus_text",
                        github_url=github_url,
                        text_content=text_input
                    )
                
                st.success(f"✅ Loaded {len(documents)} document(s)")
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
                post_data = generate_linkedin_post(
                    context=context,
                    style=post_style,
                    tone=tone,
                    include_hashtags=include_hashtags,
                    include_caption=include_caption,
                    demo_asset_type=demo_asset_type if include_caption else "Video demo"
                )
                
                # Store in session state for persistence
                st.session_state.current_post = post_data
                st.session_state.posts_history.append(post_data)
                st.session_state.last_generated_time = st.session_state.get("_time", None)
                
                st.success("✅ Post generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Generation Error: {str(e)}")
                st.error(f"Details: {str(e)}")
                st.stop()
        
        # Display the generated post from session state
        if st.session_state.current_post:
            post_data = st.session_state.current_post
            
            # ====================================================================
            # OUTPUT SECTION
            # ====================================================================
            
            st.markdown("---")
            st.markdown("## 📋 Generated Content")
            
            # Main Post
            st.markdown("### 📄 LinkedIn Post")
            st.markdown(f"""
            <div style="background-color: {theme['tertiary_bg']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {theme['border_color']}; margin-bottom: 1.5rem;">
            {post_data['post']}
            </div>
            """, unsafe_allow_html=True)
            
            # Copy post
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                st.text_area(
                    "Copy post text:",
                    value=post_data['post'],
                    height=120,
                    disabled=True,
                    key="post_copy"
                )
            
            # Hashtags
            if post_data['hashtags']:
                st.markdown("---")
                st.markdown("### #️⃣ Hashtags")
                st.code(post_data['hashtags'], language="text")
                
                st.text_area(
                    "Full post with hashtags:",
                    value=f"{post_data['post']}\n\n{post_data['hashtags']}",
                    height=120,
                    disabled=True,
                    key="full_copy"
                )
            
            # Demo Caption
            if post_data['caption']:
                st.markdown("---")
                st.markdown("### 🎥 Demo Caption")
                st.info(post_data['caption'])
            
            # Statistics
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

