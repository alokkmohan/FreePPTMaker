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

# For visitor and ppt count
import json
def get_conversion_stats():
    counter_file = "visitor_count.json"
    try:
        if os.path.exists(counter_file):
            with open(counter_file, 'r') as f:
                data = json.load(f)
                visits = data.get('total_visits', 0)
                ppts = data.get('ppt_generated', 0)
                if visits > 0:
                    conversion_rate = (ppts / visits) * 100
                else:
                    conversion_rate = 0
                return visits, ppts, conversion_rate
    except:
        pass
    return 0, 0, 0

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

# --- Hero Header ---
st.markdown("""
<div class="hero-header">
  <div class="hero-title">SlideCraft AI</div>
  <div class="hero-subtitle">Create professional presentations from topics, text, or documents</div>
</div>
<style>
.hero-header {
    width: 100%;
    min-height: 160px;
    max-height: 180px;
    background: linear-gradient(90deg, #3b82f6 0%, #7c3aed 100%);
    border-radius: 24px;
    margin: 24px auto 32px auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 32px rgba(60, 72, 180, 0.10);
    padding: 32px 12px 28px 12px;
    text-align: center;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 900;
    color: #fff;
    letter-spacing: -1px;
    margin-bottom: 0.5rem;
    line-height: 1.1;
}
.hero-subtitle {
    font-size: 1.25rem;
    font-weight: 400;
    color: #e0e7ff;
    letter-spacing: 0.1px;
    margin-top: 0;
    line-height: 1.4;
}
@media (max-width: 600px) {
    .hero-header {min-height: 120px; max-height: 160px; padding: 18px 4px 16px 4px;}
    .hero-title {font-size: 1.5rem;}
    .hero-subtitle {font-size: 1rem;}
}
</style>
""", unsafe_allow_html=True)
# --- End Hero Header ---

# Initialize session state
if 'generating' not in st.session_state:
    st.session_state.generating = False
if 'ppt_ready' not in st.session_state:
    st.session_state.ppt_ready = False
if 'pending_file_content' not in st.session_state:
    st.session_state.pending_file_content = None
if 'pending_file_name' not in st.session_state:
    st.session_state.pending_file_name = None
if 'ppt_path' not in st.session_state:
    st.session_state.ppt_path = None
if 'theme' not in st.session_state:
    st.session_state.theme = 'corporate'
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'awaiting_topic' not in st.session_state:
    st.session_state.awaiting_topic = False

# Helper functions for chat
def is_greeting(text):
    """Check if text is a greeting"""
    greetings = ['hi', 'hello', 'hey', 'hii', 'hiii', 'namaste', 'namaskar', 'good morning',
                 'good afternoon', 'good evening', 'good night', 'howdy', 'hola', 'yo',
                 'kya hal', 'kaise ho', 'how are you', 'whats up', "what's up", 'sup']
    text_lower = text.lower().strip()
    # Check exact match or starts with greeting
    for g in greetings:
        if text_lower == g or text_lower.startswith(g + ' ') or text_lower.startswith(g + '!'):
            return True
    return False

def is_valid_topic(text):
    """Check if text is a valid topic for PPT generation"""
    text = text.strip()
    # Too short - likely not a topic
    if len(text) < 5:
        return False
    # Only 1-2 words and not descriptive
    words = text.split()
    if len(words) <= 2:
        # Check if it's a meaningful topic (has noun-like structure)
        short_invalid = ['ok', 'yes', 'no', 'ya', 'haan', 'nahi', 'thanks', 'thank you',
                        'bye', 'okay', 'sure', 'fine', 'good', 'nice', 'great', 'cool']
        if text.lower() in short_invalid:
            return False
    return True

def add_chat_message(role, content):
    """Add message to chat history"""
    st.session_state.chat_messages.append({"role": role, "content": content})

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
# ============ FOOTER ============
visits, ppts, _ = get_conversion_stats()
st.markdown(f'''
<style>
.custom-footer {{
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    text-align: center;
    font-size: 0.95rem;
    padding: 10px 0 8px 0;
    z-index: 99999;
    letter-spacing: 0.2px;
    box-shadow: 0 -2px 10px rgba(60,72,180,0.08);
}}
@media (max-width: 600px) {{
    .custom-footer {{font-size: 0.85rem; padding: 8px 0 6px 0;}}
}}
</style>
<div class="custom-footer">
👀 Visitors: <b>{visits}</b> &nbsp;|&nbsp; 📝 PPTs Generated: <b>{ppts}</b>
</div>
''', unsafe_allow_html=True)

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
                # Custom prompt for detailed slides, correct headers, and first slide as topic
                custom_instructions = """
                - First slide should be the topic title and subtitle
                - Each slide must have a relevant, clear header/title
                - Each bullet point should be detailed (2-3 sentences)
                - Speaker notes should be detailed
                """
                content = generate_content_from_topic(topic, custom_instructions, 10, 15)

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
        st.session_state.pending_file_content = None
        st.session_state.pending_file_name = None
        st.session_state.chat_messages = []  # Clear chat
        st.session_state.awaiting_topic = False
        st.rerun()

# ============ BOTTOM INPUT BAR (Claude Style) ============

# Style for chat input
st.markdown("""
<style>
    /* Chat input styling - works on mobile & desktop */
    [data-testid="stChatInput"] {
        background: #f4f4f4 !important;
        border-radius: 24px !important;
        border: 1px solid #ddd !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #667eea !important;
        background: white !important;
    }
    [data-testid="stChatInput"] textarea {
        font-size: 16px !important;
    }

    /* File uploader compact style */
    .stFileUploader {
        margin-bottom: 10px !important;
    }
    .stFileUploader > div > div {
        padding: 10px !important;
    }
    .stFileUploader label {
        font-size: 14px !important;
        color: #666 !important;
    }
</style>
""", unsafe_allow_html=True)

# File uploader (compact, above input)
uploaded_file = st.file_uploader(
    "Attach file (txt, docx, pdf)",
    type=["txt", "docx", "pdf"],
    key="file_upload"
)

# Claude-style chat input - works perfectly on mobile
user_input = st.chat_input("Enter topic or paste content...")
send_clicked = user_input is not None

# Handle file upload - store in pending state (don't auto-process)
if uploaded_file is not None and not st.session_state.generating:
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

    # Store in pending state - wait for user to click send
    if file_content:
        st.session_state.pending_file_content = file_content
        st.session_state.pending_file_name = file_name.rsplit('.', 1)[0][:50]

# Show file ready indicator
if st.session_state.pending_file_content and not st.session_state.generating:
    st.info(f"File ready: {st.session_state.pending_file_name} - Click send or press Enter to generate PPT")

# Display chat messages
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Handle chat input submission
if user_input:
    # Add user message to chat
    add_chat_message("user", user_input)

    # If file is pending, process file
    if st.session_state.pending_file_content:
        add_chat_message("assistant", f"Processing file: {st.session_state.pending_file_name}...")
        st.session_state.generating = True
        st.session_state.content_to_process = st.session_state.pending_file_content
        st.session_state.topic_name = st.session_state.pending_file_name
        st.session_state.pending_file_content = None
        st.session_state.pending_file_name = None
        st.rerun()

    # Check if it's a greeting
    elif is_greeting(user_input):
        response = "Hello! Welcome to SlideCraft AI. I can create professional PowerPoint presentations for you.\n\nPlease tell me the **topic** for your presentation. For example:\n- 'Artificial Intelligence in Healthcare'\n- 'Climate Change and Its Effects'\n- 'Digital Marketing Strategies'"
        add_chat_message("assistant", response)
        st.session_state.awaiting_topic = True
        st.rerun()

    # Check if it's a valid topic
    elif is_valid_topic(user_input):
        word_count = len(user_input.split())
        if word_count > 50:
            # Long content - use as content
            add_chat_message("assistant", f"Starting PPT generation on: **{user_input.split(chr(10))[0][:50]}**...")
            st.session_state.content_to_process = user_input
            st.session_state.topic_name = user_input.split('\n')[0][:50]
        else:
            # Short topic
            add_chat_message("assistant", f"Creating presentation on: **{user_input}**...")
            st.session_state.topic_name = user_input
            st.session_state.content_to_process = None

        st.session_state.generating = True
        st.session_state.awaiting_topic = False
        st.rerun()

    else:
        # Unclear input - ask for clarification
        response = "I didn't quite understand that. Could you please provide a clear topic for your presentation?\n\nFor example:\n- 'Machine Learning Basics'\n- 'History of India'\n- 'Solar Energy Benefits'\n\nOr you can paste/upload content directly."
        add_chat_message("assistant", response)
        st.rerun()

# Also handle case: file is pending and user just presses Enter with empty input
# (st.chat_input returns None for empty, but we can add a generate button)
if st.session_state.pending_file_content and not st.session_state.generating:
    if st.button("Generate PPT from file", use_container_width=True, type="primary"):
        st.session_state.generating = True
        st.session_state.content_to_process = st.session_state.pending_file_content
        st.session_state.topic_name = st.session_state.pending_file_name
        st.session_state.pending_file_content = None
        st.session_state.pending_file_name = None
        st.rerun()
