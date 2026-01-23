import streamlit as st
import os
import re
from datetime import datetime
from docx import Document

# Imports
try:
    from ppt_to_images import ppt_to_images
    PPT_TO_IMAGES_AVAILABLE = True
except:
    PPT_TO_IMAGES_AVAILABLE = False

from content_generator import generate_content_from_topic
from ai_ppt_generator import generate_beautiful_ppt

# Page Config
st.set_page_config(
    page_title="PPT Generator",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS for fixed header and bottom input
st.markdown("""
<style>
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Fixed Header */
    .fixed-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    .fixed-header h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
    }
    .fixed-header p {
        margin: 0.2rem 0 0 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }

    /* Main content area */
    .main-content {
        margin-top: 80px;
        margin-bottom: 100px;
        padding: 1rem;
    }

    /* Features box */
    .features-box {
        background: linear-gradient(145deg, #f8f9ff 0%, #ffffff 100%);
        border: 2px solid #e8ecf1;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
    }
    .features-box h3 {
        color: #667eea;
        margin-bottom: 1rem;
    }
    .feature-item {
        display: inline-block;
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin: 0.3rem;
        font-size: 0.9rem;
    }

    /* AI Status */
    .ai-status {
        background: #f0f4ff;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 1rem !important;
        font-size: 1.1rem !important;
        border-radius: 12px !important;
        width: 100% !important;
    }

    /* Bottom input styling */
    .stChatInput {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem;
        background: white;
        border-top: 1px solid #e0e0e0;
        z-index: 1000;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .fixed-header {
            padding: 0.8rem 1rem;
        }
        .fixed-header h1 {
            font-size: 1.2rem;
        }
        .features-box {
            padding: 1rem;
        }
        .feature-item {
            display: block;
            margin: 0.5rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Fixed Header
st.markdown('''
<div class="fixed-header">
    <h1>PPT Generator</h1>
    <p>Enter topic or paste content below</p>
</div>
''', unsafe_allow_html=True)

# Spacer for fixed header
st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True)

# Initialize session state
if 'generating' not in st.session_state:
    st.session_state.generating = False
if 'ppt_ready' not in st.session_state:
    st.session_state.ppt_ready = False
if 'ppt_path' not in st.session_state:
    st.session_state.ppt_path = None
if 'theme' not in st.session_state:
    st.session_state.theme = 'corporate'
if 'show_upload' not in st.session_state:
    st.session_state.show_upload = False
if 'ai_status' not in st.session_state:
    st.session_state.ai_status = None

# Function to generate PPT
def generate_ppt_func(content, topic, theme):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join("output", f"output_{timestamp}")
    os.makedirs(output_folder, exist_ok=True)

    safe_title = re.sub(r'[^\w\s-]', '', str(topic))[:50]
    safe_title = re.sub(r'[-\s]+', '_', safe_title) if safe_title else "presentation"
    ppt_path = os.path.join(output_folder, f"{safe_title}.pptx")

    success = generate_beautiful_ppt(
        content,
        ppt_path,
        color_scheme=theme,
        use_ai=False,
        original_topic=topic,
        min_slides=10,
        max_slides=15
    )
    return success, ppt_path, output_folder

# Main content area
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Show features when not generating
if not st.session_state.generating and not st.session_state.ppt_ready:
    st.markdown('''
    <div class="features-box">
        <h3>AI-Powered PPT Generator</h3>
        <p style="color: #666; margin-bottom: 1rem;">Create professional presentations in seconds</p>
        <div>
            <span class="feature-item">Topic to PPT</span>
            <span class="feature-item">Text to PPT</span>
            <span class="feature-item">Upload Documents</span>
        </div>
        <div style="margin-top: 0.5rem;">
            <span class="feature-item">5 Themes</span>
            <span class="feature-item">10-15 Slides</span>
            <span class="feature-item">Hindi & English</span>
        </div>
        <p style="color: #999; font-size: 0.85rem; margin-top: 1.5rem;">
            Type a topic, paste content, or click + to upload a file
        </p>
    </div>
    ''', unsafe_allow_html=True)

# Upload panel (shown when + is clicked)
if st.session_state.show_upload:
    st.markdown("---")
    st.markdown("**Upload File (txt, docx, pdf, md)**")
    uploaded_file = st.file_uploader("Upload", type=['txt', 'docx', 'md', 'pdf'], label_visibility="collapsed")

    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.docx'):
                import io
                doc = Document(io.BytesIO(uploaded_file.read()))
                content = '\n'.join([p.text for p in doc.paragraphs])
            elif uploaded_file.name.endswith('.pdf'):
                import PyPDF2
                import io
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                content = '\n'.join([page.extract_text() for page in pdf_reader.pages])
            else:
                content = uploaded_file.read().decode('utf-8')

            st.success(f"Loaded: {uploaded_file.name}")

            if st.button("Generate PPT from File", type="primary", use_container_width=True):
                st.session_state.generating = True
                st.session_state.content_to_process = content
                st.session_state.topic_name = uploaded_file.name.rsplit('.', 1)[0]
                st.session_state.show_upload = False
                st.rerun()
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

    if st.button("Close"):
        st.session_state.show_upload = False
        st.rerun()
    st.markdown("---")

# AI Generation Status
if st.session_state.generating:
    topic = st.session_state.get('topic_name', 'Content')

    with st.status("Generating your PPT...", expanded=True) as status:
        st.write("Analyzing content...")

        try:
            # Check if we have content from file or need to generate
            if st.session_state.get('content_to_process'):
                content = st.session_state.content_to_process
                st.write("Processing uploaded content...")
            else:
                st.write("Generating content with AI...")
                content = generate_content_from_topic(topic, "", 10, 15)

            st.write("Creating slides...")
            st.write("Applying theme...")

            success, ppt_path, output_folder = generate_ppt_func(content, topic, st.session_state.theme)

            if success:
                status.update(label="PPT Ready!", state="complete")
                st.session_state.ppt_ready = True
                st.session_state.ppt_path = ppt_path
                st.session_state.output_folder = output_folder
                st.session_state.generating = False
                st.session_state.content_to_process = None
                st.rerun()
            else:
                status.update(label="Generation failed", state="error")
                st.session_state.generating = False

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.generating = False

# PPT Ready - Show download and options
if st.session_state.ppt_ready and st.session_state.ppt_path:
    st.success("Your PPT is ready!")

    # Download button
    with open(st.session_state.ppt_path, "rb") as f:
        st.download_button(
            "Download PPT",
            f.read(),
            file_name="presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True
        )

    # Theme option (optional - after generation)
    with st.expander("Change Theme & Regenerate (Optional)"):
        col1, col2 = st.columns(2)
        with col1:
            new_theme = st.selectbox("Theme", ['corporate', 'ocean', 'forest', 'sunset', 'eg'],
                                    index=['corporate', 'ocean', 'forest', 'sunset', 'eg'].index(st.session_state.theme))
        with col2:
            if st.button("Regenerate with new theme"):
                st.session_state.theme = new_theme
                st.session_state.ppt_ready = False
                st.session_state.generating = True
                st.rerun()

    # Preview
    if PPT_TO_IMAGES_AVAILABLE:
        with st.expander("Preview Slides"):
            try:
                ppt_to_images(st.session_state.ppt_path, output_dir=st.session_state.output_folder)
                images = sorted([f for f in os.listdir(st.session_state.output_folder)
                               if f.startswith("slide_") and f.endswith(".png")])
                if images:
                    cols = st.columns(2)
                    for idx, img in enumerate(images[:6]):
                        with cols[idx % 2]:
                            st.image(os.path.join(st.session_state.output_folder, img), caption=f"Slide {idx+1}")
            except:
                st.info("Preview not available")

    # New PPT button
    if st.button("Create New PPT", use_container_width=True):
        st.session_state.ppt_ready = False
        st.session_state.ppt_path = None
        st.session_state.generating = False
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Spacer for bottom input
st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True)

# Bottom input area
st.markdown("---")
col_plus, col_input = st.columns([1, 12])

with col_plus:
    if st.button("➕", help="Upload file"):
        st.session_state.show_upload = not st.session_state.show_upload
        st.rerun()

with col_input:
    user_input = st.chat_input("Enter topic or paste content here...")

    if user_input:
        # Determine if it's a topic or full content
        word_count = len(user_input.split())

        st.session_state.generating = True

        if word_count > 50:
            # It's full content - use directly
            st.session_state.content_to_process = user_input
            st.session_state.topic_name = user_input.split('\n')[0][:50]
        else:
            # It's a topic - will generate content
            st.session_state.topic_name = user_input
            st.session_state.content_to_process = None

        st.rerun()
