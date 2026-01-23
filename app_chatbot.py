import streamlit as st
import os
import re
from datetime import datetime

# Imports
try:
    from ppt_to_images import ppt_to_images
    PPT_TO_IMAGES_AVAILABLE = True
except:
    PPT_TO_IMAGES_AVAILABLE = False

from content_generator import generate_content_from_topic
from ai_ppt_generator import generate_beautiful_ppt

# Page Config - MUST be first Streamlit command
st.set_page_config(
    page_title="PPT Generator",
    page_icon="P",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobile-first CSS - Hide all Streamlit defaults
st.markdown("""
<style>
    /* FORCE HIDE all Streamlit default elements */
    #MainMenu, footer, header, .stDeployButton,
    [data-testid="stHeader"], [data-testid="stToolbar"],
    .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_ {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    /* Remove top padding that Streamlit adds */
    .stApp > header {
        display: none !important;
    }

    .block-container {
        padding-top: 0 !important;
        padding-bottom: 80px !important;
        max-width: 100% !important;
    }

    /* Custom Header - compact for mobile */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        text-align: center;
        border-radius: 0 0 16px 16px;
        margin: -1rem -1rem 1rem -1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .app-header h1 {
        margin: 0;
        font-size: 1.3rem;
        font-weight: 700;
    }
    .app-header p {
        margin: 4px 0 0 0;
        font-size: 0.8rem;
        opacity: 0.9;
    }

    /* Features box - mobile optimized */
    .features-box {
        background: linear-gradient(145deg, #f8f9ff 0%, #fff 100%);
        border: 1px solid #e8ecf1;
        border-radius: 16px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        text-align: center;
    }
    .features-box h3 {
        color: #667eea;
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }
    .feature-tag {
        display: inline-block;
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 20px;
        padding: 6px 12px;
        margin: 4px;
        font-size: 0.8rem;
        color: #555;
    }

    /* Bottom input container - FIXED at bottom */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 10px 12px;
        border-top: 1px solid #e0e0e0;
        z-index: 9999;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    .input-row {
        display: flex;
        align-items: center;
        gap: 8px;
        max-width: 800px;
        margin: 0 auto;
    }
    .input-row input {
        flex: 1;
        border: 1px solid #ddd;
        border-radius: 24px;
        padding: 12px 16px;
        font-size: 16px;
        outline: none;
    }
    .input-row input:focus {
        border-color: #667eea;
    }
    .btn-plus, .btn-send {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        border: none;
        cursor: pointer;
        font-size: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .btn-plus {
        background: #f0f0f0;
        color: #666;
    }
    .btn-plus:hover {
        background: #e0e0e0;
    }
    .btn-send {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .btn-send:hover {
        opacity: 0.9;
    }

    /* Streamlit button overrides for mobile */
    .stButton > button {
        border-radius: 12px !important;
        padding: 12px 20px !important;
        font-size: 1rem !important;
        min-height: 48px !important;
    }

    /* Primary button style */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px !important;
        font-size: 1rem !important;
        min-height: 52px !important;
    }

    /* Text input in columns - inline style */
    .stTextInput > div > div > input {
        border-radius: 24px !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        border: 1px solid #ddd !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 1px #667eea !important;
    }

    /* Plus button styling */
    .plus-btn button {
        width: 48px !important;
        height: 48px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        font-size: 1.4rem !important;
        background: #f5f5f5 !important;
        border: 1px solid #ddd !important;
        color: #666 !important;
    }
    .plus-btn button:hover {
        background: #e8e8e8 !important;
    }

    /* Send button styling */
    .send-btn button {
        width: 48px !important;
        height: 48px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        font-size: 1.2rem !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
    }

    /* File uploader compact */
    .stFileUploader {
        padding: 0 !important;
    }
    .stFileUploader > div {
        padding: 8px !important;
    }

    /* Success/error messages */
    .stSuccess, .stError, .stInfo {
        padding: 10px 14px !important;
        border-radius: 10px !important;
        font-size: 0.9rem !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        font-size: 0.95rem !important;
        padding: 10px 0 !important;
    }

    /* Mobile specific */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 12px !important;
            padding-right: 12px !important;
        }
        .app-header {
            margin: -1rem -12px 1rem -12px;
            padding: 10px 12px;
        }
        .app-header h1 {
            font-size: 1.2rem;
        }
        .features-box {
            padding: 1rem;
        }
        .feature-tag {
            padding: 5px 10px;
            font-size: 0.75rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Custom Header
st.markdown('''
<div class="app-header">
    <h1>PPT Generator</h1>
    <p>AI-powered presentations in seconds</p>
</div>
''', unsafe_allow_html=True)

# Initialize session state
if 'generating' not in st.session_state:
    st.session_state.generating = False
if 'ppt_ready' not in st.session_state:
    st.session_state.ppt_ready = False
if 'ppt_path' not in st.session_state:
    st.session_state.ppt_path = None
if 'theme' not in st.session_state:
    st.session_state.theme = 'corporate'
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

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

# ============ MAIN CONTENT AREA ============

# Show features when idle
if not st.session_state.generating and not st.session_state.ppt_ready:
    st.markdown('''
    <div class="features-box">
        <h3>Create Professional PPTs</h3>
        <p style="color: #666; margin: 0.5rem 0; font-size: 0.85rem;">Enter a topic or paste your content below</p>
        <div style="margin-top: 0.8rem;">
            <span class="feature-tag">Topic to PPT</span>
            <span class="feature-tag">Text to PPT</span>
            <span class="feature-tag">File Upload</span>
        </div>
        <div style="margin-top: 0.3rem;">
            <span class="feature-tag">5 Themes</span>
            <span class="feature-tag">10-15 Slides</span>
            <span class="feature-tag">Hindi/English</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# Upload panel removed - using text input only

# AI Generation Status
if st.session_state.generating:
    topic = st.session_state.get('topic_name', 'Content')

    with st.status("Generating PPT...", expanded=True) as status:
        st.write("Analyzing content...")

        try:
            if st.session_state.get('content_to_process'):
                content = st.session_state.content_to_process
                st.write("Processing your content...")
            else:
                st.write("Generating with AI...")
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
                status.update(label="Failed", state="error")
                st.session_state.generating = False

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.generating = False

# PPT Ready - Download section
if st.session_state.ppt_ready and st.session_state.ppt_path:
    st.success("Your PPT is ready!")

    with open(st.session_state.ppt_path, "rb") as f:
        st.download_button(
            "Download PPT",
            f.read(),
            file_name="presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True
        )

    with st.expander("Change Theme"):
        new_theme = st.selectbox(
            "Select theme",
            ['corporate', 'ocean', 'forest', 'sunset', 'eg'],
            index=['corporate', 'ocean', 'forest', 'sunset', 'eg'].index(st.session_state.theme),
            label_visibility="collapsed"
        )
        if st.button("Regenerate", use_container_width=True):
            st.session_state.theme = new_theme
            st.session_state.ppt_ready = False
            st.session_state.generating = True
            st.rerun()

    if PPT_TO_IMAGES_AVAILABLE:
        with st.expander("Preview"):
            try:
                ppt_to_images(st.session_state.ppt_path, output_dir=st.session_state.output_folder)
                images = sorted([f for f in os.listdir(st.session_state.output_folder)
                               if f.startswith("slide_") and f.endswith(".png")])
                if images:
                    for idx, img in enumerate(images[:4]):
                        st.image(os.path.join(st.session_state.output_folder, img), caption=f"Slide {idx+1}")
            except:
                st.info("Preview not available")

    if st.button("New PPT", use_container_width=True):
        st.session_state.ppt_ready = False
        st.session_state.ppt_path = None
        st.session_state.generating = False
        st.session_state.user_input = ""
        st.rerun()

# ============ BOTTOM INPUT BAR (WhatsApp Style) ============
st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)

# WhatsApp style CSS for input row
st.markdown("""
<style>
    /* Input container - flex row */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 6px !important;
        flex-wrap: nowrap !important;
    }

    /* Text input styling */
    .stTextInput input {
        border-radius: 24px !important;
        padding: 14px 50px 14px 18px !important;
        font-size: 16px !important;
        height: 50px !important;
        border: 1px solid #ddd !important;
        background: #f5f5f5 !important;
        width: 100% !important;
    }
    .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102,126,234,0.2) !important;
        background: white !important;
    }

    /* Attach button (inside input area - 2nd column) */
    [data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        max-width: 38px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        font-size: 1.1rem !important;
        background: transparent !important;
        border: none !important;
        color: #666 !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover {
        background: #e8e8e8 !important;
    }

    /* Send button (last column) */
    [data-testid="stHorizontalBlock"] > div:last-child button {
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
        min-height: 50px !important;
        max-width: 50px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        font-size: 1.3rem !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-shrink: 0 !important;
    }
    [data-testid="stHorizontalBlock"] > div:last-child button:hover {
        opacity: 0.9 !important;
        transform: scale(1.05) !important;
    }

    /* Hide file uploader visually but keep functional */
    .stFileUploader {
        position: absolute !important;
        opacity: 0 !important;
        width: 38px !important;
        height: 38px !important;
        cursor: pointer !important;
        z-index: 10 !important;
    }
    .stFileUploader > div {
        padding: 0 !important;
    }
    .stFileUploader label {
        display: none !important;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            gap: 4px !important;
        }
        .stTextInput input {
            font-size: 16px !important;
            height: 46px !important;
            padding: 10px 45px 10px 14px !important;
        }
        [data-testid="stHorizontalBlock"] > div:nth-child(2) button {
            width: 34px !important;
            height: 34px !important;
            min-width: 34px !important;
            max-width: 34px !important;
        }
        [data-testid="stHorizontalBlock"] > div:last-child button {
            width: 46px !important;
            height: 46px !important;
            min-width: 46px !important;
            min-height: 46px !important;
            max-width: 46px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Input row: [____input____] [📎] [➤]
col_input, col_attach, col_btn = st.columns([10, 1, 1])

with col_input:
    user_input = st.text_input(
        "Enter topic",
        placeholder="Type topic or paste content...",
        label_visibility="collapsed",
        key="main_input"
    )

with col_attach:
    # File upload with clip icon overlay
    uploaded_file = st.file_uploader("Upload", type=["txt", "docx", "pdf"], key="file_upload", label_visibility="collapsed")
    if not uploaded_file:
        st.button("📎", key="attach_btn", help="Attach file (txt, docx, pdf)")

with col_btn:
    send_clicked = st.button("➤", key="send_btn", help="Generate PPT")

# Handle file upload
if uploaded_file is not None:
    file_content = ""
    file_name = uploaded_file.name

    if file_name.endswith('.txt'):
        file_content = uploaded_file.read().decode('utf-8')
    elif file_name.endswith('.docx'):
        try:
            from docx import Document
            import io
            doc = Document(io.BytesIO(uploaded_file.read()))
            file_content = '\n'.join([para.text for para in doc.paragraphs])
        except:
            st.error("Could not read DOCX file")
    elif file_name.endswith('.pdf'):
        try:
            import PyPDF2
            import io
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            file_content = '\n'.join([page.extract_text() for page in pdf_reader.pages])
        except:
            st.error("Could not read PDF file")

    if file_content:
        st.session_state.generating = True
        st.session_state.content_to_process = file_content
        st.session_state.topic_name = file_name.rsplit('.', 1)[0][:50]
        st.rerun()

# Handle text submission
if send_clicked and user_input:
    word_count = len(user_input.split())
    st.session_state.generating = True

    if word_count > 50:
        st.session_state.content_to_process = user_input
        st.session_state.topic_name = user_input.split('\n')[0][:50]
    else:
        st.session_state.topic_name = user_input
        st.session_state.content_to_process = None

    st.rerun()
