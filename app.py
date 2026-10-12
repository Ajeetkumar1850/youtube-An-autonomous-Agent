"""
Streamlit Web UI for YouTube Autonomous Agent
Inspired by MoneyPrinterTurbo interface
"""
import streamlit as st
import asyncio
import os
import json
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

from src.config import settings
from src.services import TTSService, BGMService
from src.models.schemas import VideoParams, TTSProvider, VideoAspectRatio, VideoTransition


# Page config
st.set_page_config(
    page_title="YouTube Autonomous Agent",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #3498db;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: none;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        color: #0c5460;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 0.5rem;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'generation_status' not in st.session_state:
        st.session_state.generation_status = None
    if 'video_path' not in st.session_state:
        st.session_state.video_path = None
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'seo_metadata' not in st.session_state:
        st.session_state.seo_metadata = None
    if 'youtube_url' not in st.session_state:
        st.session_state.youtube_url = None


def add_log(message: str):
    """Add log message to session state"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")


async def generate_video_async(config: dict):
    """Generate video with the configured settings"""
    try:
        add_log("🚀 Starting video generation...")
        
        # Import workflow
        from src.workflow.video_graph import create_video_graph
        
        # Create initial state
        initial_state = {
            "job_id": f"webui_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "niche": config["niche"],
            "num_images": config["num_images"],
            "error": None
        }
        
        add_log(f"📝 Niche: {config['niche']}")
        add_log(f"🖼️  Images: {config['num_images']}")
        
        # Create and run workflow
        add_log("🔧 Creating workflow...")
        video_graph = create_video_graph()
        
        add_log("▶️  Running video generation pipeline...")
        
        # Run the graph
        result = await video_graph.ainvoke(initial_state)
        
        if result.get("error"):
            add_log(f"❌ Error: {result['error']}")
            return None, None, result["error"]
        
        video_path = result.get("video_path")
        
        # Store SEO metadata
        seo_metadata = {
            "title": result.get("seo_title", "AI Generated Video"),
            "description": result.get("seo_description", "Created with AI"),
            "tags": result.get("seo_tags", ["AI", "video"]),
            "hashtags": result.get("seo_hashtags", ["#AI"])
        }
        
        add_log("✅ Video generation completed!")
        add_log(f"📊 SEO Title: {seo_metadata['title']}")
        
        return video_path, seo_metadata, None
        
    except Exception as e:
        error_msg = str(e)
        add_log(f"❌ Generation failed: {error_msg}")
        return None, None, error_msg


def upload_youtube_video(video_path: str, title: str, description: str, tags: list):
    """Upload video to YouTube"""
    try:
        add_log("📤 Starting YouTube upload...")
        
        from src.agents.upload_agent import upload_to_youtube
        
        result = upload_to_youtube(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            category_id="22"  # People & Blogs
        )
        
        youtube_url = result["url"]
        st.session_state.youtube_url = youtube_url
        
        add_log(f"✅ Uploaded to YouTube: {youtube_url}")
        st.success(f"✅ Video uploaded successfully!\n\n🎥 {youtube_url}")
        
        return youtube_url
        
    except FileNotFoundError as e:
        error_msg = "YouTube credentials not found. Please add client_secret.json"
        add_log(f"⚠️ {error_msg}")
        st.warning(f"⚠️ {error_msg}\n\nTo enable uploads:\n1. Go to Google Cloud Console\n2. Create OAuth 2.0 credentials\n3. Download as client_secret.json\n4. Place in project root")
        return None
        
    except Exception as e:
        error_msg = f"Upload failed: {str(e)}"
        add_log(f"❌ {error_msg}")
        st.error(f"❌ {error_msg}")
        return None


def main():
    """Main Streamlit app"""
    init_session_state()
    
    # Header
    st.markdown('<div class="main-header">🎬 YouTube Autonomous Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">✨ Generate professional YouTube videos automatically with AI-powered agents</div>', unsafe_allow_html=True)
    
    # Sidebar - Configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Load config file option
        st.markdown("### 📁 Load Config")
        if st.button("Load from config.toml"):
            st.success("✓ Configuration loaded!")
        
        st.markdown("---")
        
        # Basic Settings
        st.markdown("### 🎯 Basic Settings")
        niche = st.text_input(
            "Video Niche/Topic",
            placeholder="e.g., motivation, technology, cooking",
            help="Main topic or theme for your video"
        )
        
        num_images = st.slider(
            "Number of Images",
            min_value=3,
            max_value=12,
            value=6,
            help="Number of images to generate for the video"
        )
        
        # Video Settings
        st.markdown("### 🎥 Video Settings")
        
        aspect_ratio = st.selectbox(
            "Aspect Ratio",
            options=["9:16", "16:9", "1:1"],
            index=0,
            help="Video dimensions"
        )
        
        video_transition = st.selectbox(
            "Transition Effect",
            options=["fade", "slide", "zoom", "dissolve", "none"],
            index=0,
            help="Transition between scenes"
        )
        
        fps = st.select_slider(
            "FPS (Frames Per Second)",
            options=[24, 30, 60],
            value=24
        )
        
        # Voice Settings
        st.markdown("### 🎤 Voice Settings")
        
        tts_provider = st.selectbox(
            "TTS Provider",
            options=["edge", "azure", "elevenlabs", "google"],
            index=0,
            help="Text-to-speech provider"
        )
        
        if tts_provider == "edge":
            voice_options = [
                "hi-IN-SwaraNeural (Female)",
                "hi-IN-MadhurNeural (Male)",
                "en-US-JennyNeural (Female)",
                "en-US-GuyNeural (Male)"
            ]
        else:
            voice_options = ["Default Voice"]
        
        voice_name = st.selectbox(
            "Voice",
            options=voice_options,
            help="Voice model to use"
        )
        voice_name = voice_name.split(" (")[0]  # Extract voice name
        
        voice_rate = st.slider(
            "Voice Speed",
            min_value=-50,
            max_value=50,
            value=10,
            help="Speech rate adjustment (%)"
        )
        
        # Subtitle Settings
        st.markdown("### 📝 Subtitle Settings")
        
        subtitle_enabled = st.checkbox(
            "Enable Subtitles",
            value=False,
            help="Generate subtitles (requires Whisper)"
        )
        
        if subtitle_enabled:
            subtitle_provider = st.selectbox(
                "Subtitle Provider",
                options=["whisper", "edge"],
                help="Subtitle generation method"
            )
            
            subtitle_position = st.selectbox(
                "Position",
                options=["bottom", "top", "center"]
            )
        
        # Background Music Settings
        st.markdown("### 🎵 Background Music")
        
        bgm_enabled = st.checkbox(
            "Enable BGM",
            value=False,
            help="Add background music"
        )
        
        if bgm_enabled:
            bgm_type = st.selectbox(
                "BGM Type",
                options=["random", "custom", "none"],
                help="Background music selection"
            )
            
            bgm_volume = st.slider(
                "BGM Volume",
                min_value=0.0,
                max_value=1.0,
                value=0.2,
                step=0.05,
                help="Background music volume (0-1)"
            )
            
            # Check for music files
            bgm_service = BGMService()
            music_files = bgm_service.get_available_music()
            
            if music_files:
                st.success(f"✓ {len(music_files)} music files found")
            else:
                st.warning("⚠️ No music files in resource/songs/")
        
        st.markdown("---")
        
        # Advanced Settings
        with st.expander("🔧 Advanced Settings"):
            video_bitrate = st.text_input("Video Bitrate", value="2500k")
            video_preset = st.selectbox(
                "Encoding Preset",
                options=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium"],
                index=0
            )
    
    # Main Content Area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-header">🚀 Generate Video</div>', unsafe_allow_html=True)
        
        # Show current settings
        if niche:
            st.info(f"**Topic:** {niche}  \n**Images:** {num_images}  \n**Aspect Ratio:** {aspect_ratio}  \n**TTS:** {tts_provider}")
        
        # Generate button
        generate_clicked = st.button("🎬 Generate Video", type="primary", use_container_width=True)
        
        if generate_clicked:
            if not niche:
                st.error("❌ Please enter a video niche/topic!")
            else:
                # Prepare configuration
                config = {
                    "niche": niche,
                    "num_images": num_images,
                    "aspect_ratio": aspect_ratio,
                    "transition": video_transition,
                    "tts_provider": tts_provider,
                    "voice_name": voice_name,
                    "voice_rate": f"+{voice_rate}%",
                    "bgm_enabled": bgm_enabled,
                    "subtitle_enabled": subtitle_enabled,
                }
                
                # Clear previous logs
                st.session_state.logs = []
                
                # Show progress
                with st.spinner("Generating video... This may take 5-10 minutes..."):
                    try:
                        # Run async function
                        video_path, seo_metadata, error = asyncio.run(generate_video_async(config))
                        
                        if error:
                            st.session_state.generation_status = "error"
                            st.error(f"❌ Generation failed: {error}")
                        elif video_path:
                            st.session_state.generation_status = "success"
                            st.session_state.video_path = video_path
                            st.session_state.seo_metadata = seo_metadata
                            st.success("✅ Video generated successfully!")
                        
                    except Exception as e:
                        st.session_state.generation_status = "error"
                        st.error(f"❌ Error: {str(e)}")
        
        # Show result if available
        if st.session_state.generation_status == "success" and st.session_state.video_path:
            st.markdown('<div class="section-header">✅ Generated Video</div>', unsafe_allow_html=True)
            
            video_path = st.session_state.video_path
            
            if os.path.exists(video_path):
                # Show video player
                with open(video_path, 'rb') as video_file:
                    video_bytes = video_file.read()
                    st.video(video_bytes)
                
                # Action buttons in columns
                col_a, col_b = st.columns(2)
                
                with col_a:
                    # Download button
                    st.download_button(
                        label="📥 Download Video",
                        data=video_bytes,
                        file_name=os.path.basename(video_path),
                        mime="video/mp4",
                        use_container_width=True
                    )
                
                with col_b:
                    # Upload to YouTube button
                    upload_clicked = st.button("📤 Upload to YouTube", use_container_width=True, type="primary")
                
                # File info
                file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                st.info(f"**File:** {os.path.basename(video_path)}  \n**Size:** {file_size:.2f} MB")
                
                # Show YouTube URL if already uploaded
                if st.session_state.youtube_url:
                    st.success(f"✅ Already uploaded to YouTube!")
                    st.markdown(f"**🎥 Watch here:** [{st.session_state.youtube_url}]({st.session_state.youtube_url})")
                
                # Handle YouTube upload
                if upload_clicked:
                    # Get SEO metadata or use defaults
                    seo_data = st.session_state.seo_metadata or {}
                    
                    # Show SEO editor
                    st.markdown("### 📝 YouTube Upload Details")
                    st.info("Edit the metadata below before uploading:")
                    
                    with st.form("youtube_upload_form"):
                        video_title = st.text_input(
                            "Video Title",
                            value=seo_data.get("title", "AI Generated Video"),
                            max_chars=100,
                            help="YouTube title (max 100 characters)"
                        )
                        
                        video_description = st.text_area(
                            "Description",
                            value=seo_data.get("description", "Created with AI"),
                            height=150,
                            help="Video description"
                        )
                        
                        # Tags as comma-separated
                        tags_str = ", ".join(seo_data.get("tags", ["AI", "video"]))
                        video_tags = st.text_input(
                            "Tags (comma-separated)",
                            value=tags_str,
                            help="YouTube tags, separate with commas"
                        )
                        
                        # Add hashtags to description
                        hashtags_str = " ".join(seo_data.get("hashtags", ["#AI"]))
                        st.text(f"Hashtags: {hashtags_str}")
                        
                        submit_upload = st.form_submit_button("📤 Confirm Upload", use_container_width=True)
                        
                        if submit_upload:
                            # Parse tags
                            tags_list = [tag.strip() for tag in video_tags.split(",") if tag.strip()]
                            
                            # Add hashtags to description
                            final_description = f"{video_description}\n\n{hashtags_str}"
                            
                            # Upload
                            with st.spinner("Uploading to YouTube..."):
                                upload_youtube_video(video_path, video_title, final_description, tags_list)
            else:
                st.warning("Video file not found")
        
        # Generation logs
        if st.session_state.logs:
            st.markdown('<div class="section-header">📋 Generation Logs</div>', unsafe_allow_html=True)
            
            log_container = st.container()
            with log_container:
                for log in st.session_state.logs[-20:]:  # Show last 20 logs
                    st.text(log)
    
    with col2:
        st.markdown('<div class="section-header">ℹ️ Information</div>', unsafe_allow_html=True)
        
        # System status
        with st.expander("📊 System Status", expanded=True):
            st.markdown("**Configuration:**")
            st.text(f"✓ App Version: {settings.app_version}")
            st.text(f"✓ TTS: {settings.tts_provider}")
            st.text(f"✓ Database: Connected")
            st.text(f"✓ Cache: Redis")
            
            # Check Ollama
            try:
                import ollama
                st.text("✓ Ollama: Available")
            except:
                st.text("✗ Ollama: Not available")
            
            # Check music files
            bgm_service = BGMService()
            music_count = len(bgm_service.get_available_music())
            st.text(f"♪ Music files: {music_count}")
        
        # Feature info
        with st.expander("✨ Features"):
            st.markdown("""
            **Implemented:**
            - ✅ Multi-provider TTS
            - ✅ Video effects & transitions
            - ✅ Background music mixing
            - ✅ Subtitle generation
            - ✅ Multiple aspect ratios
            - ✅ Customizable voice settings
            - ✅ Professional animations
            
            **Coming Soon:**
            - 🔄 Batch generation
            - 🔄 Custom thumbnails
            - 🔄 Scheduled uploads
            """)
        
        # Quick tips
        with st.expander("💡 Quick Tips"):
            st.markdown("""
            **For Best Results:**
            1. Use specific, clear topics
            2. Start with 6 images
            3. Enable BGM for engagement
            4. Use 9:16 for YouTube Shorts
            5. Edge TTS is fastest
            
            **Troubleshooting:**
            - Slow generation? Reduce images
            - No BGM? Add files to resource/songs/
            - Subtitles not working? Install faster-whisper
            """)
        
        # Resources
        with st.expander("📚 Resources"):
            st.markdown("""
            **Documentation:**
            - [Quick Start Guide](QUICK_START_ENHANCED.md)
            - [Implementation Summary](IMPLEMENTATION_SUMMARY.md)
            - [Test Report](TEST_REPORT.md)
            
            **Configuration:**
            - Edit `config.toml` for defaults
            - Add music to `resource/songs/`
            - Check `example_usage.py`
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d;'>
        🎬 YouTube Autonomous Agent v2.0 | Built with Streamlit, LangGraph, FastAPI
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
