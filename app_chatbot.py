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
from multi_ai_generator import MultiAIGenerator, get_last_ai_source
from web_search import search_google

# --- PPT Content Settings (no user input, always use Google Search) ---
num_slides = 8
bullets_per_slide = 4
bullet_word_limit = 10
tone = "formal"
required_phrases = ""
forbidden_content = ""

google_api_key = os.getenv("GOOGLE_API_KEY")
google_cse_id = os.getenv("GOOGLE_CSE_ID")

# Page Config
st.set_page_config(
    page_title="FREE PPT Maker - AI Presentation Generator",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Modern ChatGPT-style CSS
st.markdown("""
<style>
    /* Hide Streamlit defaults (NOT our custom header) */
    #MainMenu, footer, [data-testid="stHeader"] {display: none !important;}

    /* Mobile-specific: Reset any problematic positioning */
    @media (max-width: 768px) {
        .stApp {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        .main .block-container {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
    }

    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 200px !important;
        max-width: 800px !important;
    }

    /* Ensure our header is always visible */
    .main-header {
        display: block !important;
        visibility: visible !important;
        min-height: 60px !important;
    }

    /* Chat message styling */
    .stChatMessage {
        margin-bottom: 0.8rem !important;
        padding: 1rem !important;
        border-radius: 16px !important;
    }

    /* Custom chatbox container */
    .chatbox-wrapper {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to top, #f7f7f8 90%, transparent);
        padding: 1rem 1rem 1.5rem 1rem;
        z-index: 1000;
    }

    .chatbox-container {
        max-width: 760px;
        margin: 0 auto;
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        display: flex;
        align-items: flex-end;
        padding: 8px 12px;
        gap: 8px;
    }

    /* Plus button for upload */
    .upload-btn {
        width: 40px;
        height: 40px;
        min-width: 40px;
        border-radius: 50%;
        border: none;
        background: #f0f0f0;
        color: #666;
        font-size: 24px;
        font-weight: 300;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }
    .upload-btn:hover {
        background: #667eea;
        color: white;
    }

    /* Text area styling */
    .stTextArea > div > div > textarea {
        border: none !important;
        background: transparent !important;
        resize: none !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
        padding: 8px 4px !important;
        min-height: 60px !important;
        max-height: 200px !important;
    }
    .stTextArea > div > div > textarea:focus {
        box-shadow: none !important;
    }
    .stTextArea label {display: none !important;}
    .stTextArea > div {border: none !important; background: transparent !important;}

    /* Send button */
    .send-btn {
        width: 40px;
        height: 40px;
        min-width: 40px;
        border-radius: 50%;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #5a67d8 100%);
        color: white;
        font-size: 18px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }
    .send-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .send-btn:disabled {
        background: #ccc;
        cursor: not-allowed;
    }

    /* File attached indicator */
    .file-attached {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 13px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 8px;
    }
    .file-attached .clear-btn {
        background: none;
        border: none;
        color: #c62828;
        cursor: pointer;
        font-size: 16px;
        padding: 0 4px;
    }

    /* Hide default file uploader styling */
    [data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stFileUploader"] > div > div {
        padding: 0 !important;
    }
    [data-testid="stFileUploader"] label {display: none !important;}
    [data-testid="stFileUploader"] section {border: none !important; padding: 0 !important;}

    /* Placeholder styling */
    .chatbox-placeholder {
        color: #999;
        font-size: 14px;
        text-align: center;
        padding: 8px 0;
    }

    /* Language selector compact */
    .lang-selector {
        display: inline-flex;
        gap: 8px;
        padding: 4px 0;
    }

    /* ════════════════════════════════════════════════════════════════ */
    /* 🌈 COLORFUL HEADER STYLING 🌈 */
    /* ════════════════════════════════════════════════════════════════ */

    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
        padding: 40px 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: slide 20s linear infinite;
    }

    @keyframes slide {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }

    .header-content {
        position: relative;
        z-index: 1;
    }

    .header-title {
        font-size: 48px;
        font-weight: 900;
        color: white;
        margin: 0;
        text-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        animation: fadeInDown 0.8s ease-out;
    }

    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .header-subtitle {
        font-size: 18px;
        color: rgba(255, 255, 255, 0.95);
        margin: 12px 0 0 0;
        font-weight: 500;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .header-features {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 20px;
        flex-wrap: wrap;
    }

    .feature-badge {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 8px 16px;
        border-radius: 20px;
        color: white;
        font-size: 14px;
        font-weight: 600;
        animation: fadeInUp 0.8s ease-out 0.4s both;
    }

    .feature-badge:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# 🌈 COLORFUL HEADER SECTION
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="header-container">
    <div class="header-content">
        <h1 class="header-title">✨ FREE PPT Generator</h1>
        <p class="header-subtitle">🚀 Create Stunning Presentations in Minutes!</p>
        <div class="header-features">
            <div class="feature-badge">⚡ AI-Powered</div>
            <div class="feature-badge">🎨 Beautiful Designs</div>
            <div class="feature-badge">💬 Chat-Based</div>
            <div class="feature-badge">🌍 Multi-Language</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'stage' not in st.session_state:
    st.session_state.stage = 'ask_name'  # ask_name, ask_designation, idle, awaiting_topic, confirming, generating, done
if 'presenter_name' not in st.session_state:
    st.session_state.presenter_name = None
if 'presenter_designation' not in st.session_state:
    st.session_state.presenter_designation = None
if 'topic' not in st.session_state:
    st.session_state.topic = None
if 'suggested_title' not in st.session_state:
    st.session_state.suggested_title = None
if 'ppt_path' not in st.session_state:
    st.session_state.ppt_path = None
if 'theme' not in st.session_state:
    st.session_state.theme = 'corporate'
if 'file_content' not in st.session_state:
    st.session_state.file_content = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None
if 'ai_source' not in st.session_state:
    st.session_state.ai_source = None
if 'num_slides' not in st.session_state:
    st.session_state.num_slides = 6
if 'parsed_slides' not in st.session_state:
    st.session_state.parsed_slides = None

# Helper functions
def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def is_greeting(text):
    # Global greetings - English, Hindi, Spanish, French, German, Arabic, Chinese, Japanese, etc.
    greetings = [
        # English
        'hi', 'hello', 'hey', 'hii', 'hiii', 'hiiii', 'helo', 'hllo', 'hlw', 'hw',
        'good morning', 'good afternoon', 'good evening', 'good night', 'gm', 'gn',
        'howdy', 'yo', 'sup', 'whats up', "what's up", 'wassup', 'wazzup',
        'greetings', 'salutations', 'heya', 'hiya', 'hai',
        # Hindi / Hinglish
        'namaste', 'namaskar', 'pranam', 'pranaam', 'namashkar', 'jai shri krishna',
        'jai hind', 'radhe radhe', 'ram ram', 'jai shri ram', 'jai mata di',
        'kya hal', 'kaise ho', 'kaise hai', 'kaisa hai', 'kya haal hai', 'kya chal raha',
        'aur batao', 'sab theek', 'theek hai', 'haan bhai', 'bhai', 'bro',
        'sat sri akal', 'sasriakal', 'kem cho', 'vanakkam', 'nomoshkar',
        # Spanish
        'hola', 'buenos dias', 'buenas tardes', 'buenas noches', 'que tal',
        # French
        'bonjour', 'bonsoir', 'salut', 'coucou',
        # German
        'hallo', 'guten tag', 'guten morgen', 'guten abend',
        # Italian
        'ciao', 'buongiorno', 'buonasera',
        # Portuguese
        'ola', 'bom dia', 'boa tarde', 'boa noite',
        # Arabic
        'marhaba', 'ahlan', 'salam', 'assalamualaikum', 'as-salamu alaykum', 'salaam',
        # Chinese
        'ni hao', 'nihao',
        # Japanese
        'konnichiwa', 'ohayo', 'konbanwa',
        # Korean
        'annyeong', 'annyeonghaseyo',
        # Russian
        'privet', 'zdravstvuyte',
        # Other
        'aloha', 'shalom', 'sawadee', 'jambo', 'habari'
    ]
    text_lower = text.lower().strip()
    # Remove punctuation for matching
    text_clean = re.sub(r'[^\w\s]', '', text_lower)
    for g in greetings:
        g_clean = re.sub(r'[^\w\s]', '', g)
        if text_clean == g_clean or text_clean.startswith(g_clean + ' '):
            return True
    return False

def is_yes(text):
    yes_words = ['yes', 'ya', 'yaa', 'haan', 'han', 'ok', 'okay', 'sure', 'theek', 'thik', 'sahi', 'correct', 'proceed', 'go ahead', 'bana do', 'banao']
    return text.lower().strip() in yes_words or text.lower().strip().startswith('yes')

def is_no(text):
    no_words = ['no', 'nahi', 'naa', 'na', 'change', 'modify', 'edit', 'different']
    return text.lower().strip() in no_words

def is_valid_topic(text):
    """Check if the input is a valid/meaningful topic for PPT generation"""
    text = text.strip()

    # ISSUE 10: Minimum 10 characters for short inputs
    if len(text) < 10:
        return False, "Please provide more details (at least 10 characters). Example: 'AI in Healthcare' or 'Digital India'."

    # ISSUE 7: Long/structured content is always valid (user pasted content)
    # If text is substantial (> 50 chars), has multiple lines, or has bullet points - accept it
    if len(text) > 50:
        return True, ""

    # Multi-line content is likely structured/pasted content
    if '\n' in text and len(text.split('\n')) >= 2:
        return True, ""

    # Content with bullet markers is structured
    if any(marker in text for marker in ['- ', '• ', '* ', '1. ', '2. ']):
        return True, ""

    # Check for minimum vowels (gibberish often lacks vowels)
    vowels = set('aeiouAEIOU')
    vowel_count = sum(1 for c in text if c in vowels)

    # If mostly consonants with very few vowels, likely gibberish
    if len(text) > 5 and vowel_count < len(text) * 0.15:
        return False, "Yeh samajh nahi aaya. Please ek clear topic likhen jaise 'Artificial Intelligence' ya 'Climate Change'."

    # Check for repeated characters (like "aaaaaaa" or "jjjjj")
    if len(text) > 4:
        for i in range(len(text) - 3):
            if text[i] == text[i+1] == text[i+2] == text[i+3]:
                return False, "Please ek meaningful topic enter karein, random characters nahi."

    # Check if it's just numbers
    if text.replace(' ', '').isdigit():
        return False, "Please topic ka naam likhen, sirf numbers nahi."

    # If text is long enough and has some vowels, probably valid
    if len(text) >= 10 and vowel_count >= 2:
        return True, ""

    return False, "Please ek clear topic batayein (minimum 10 characters). Example: 'Digital India' ya 'AI in Healthcare'."

def generate_ppt(content, topic, theme):
    """Generate PPT with topic-based filename (Issue 9)"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join("output", f"output_{timestamp}")
    os.makedirs(output_folder, exist_ok=True)

    # ISSUE 9: Generate meaningful filename from topic
    # Extract first 3-5 meaningful words from topic
    if topic:
        # Remove special characters and split into words
        words = re.sub(r'[^\w\s]', '', str(topic)).split()
        # Take first 4 words, remove very short words
        meaningful_words = [w for w in words[:5] if len(w) > 2][:4]
        if meaningful_words:
            topic_slug = '_'.join(meaningful_words)
        else:
            topic_slug = 'presentation'
    else:
        topic_slug = 'presentation'

    # Sanitize and limit length
    topic_slug = re.sub(r'[^\w]', '_', topic_slug)[:40]
    topic_slug = re.sub(r'_+', '_', topic_slug).strip('_')

    # Format: TopicSlug_Date.pptx (e.g., AI_Healthcare_20260124.pptx)
    date_str = datetime.now().strftime("%Y%m%d")
    ppt_filename = f"{topic_slug}_{date_str}.pptx"
    ppt_path = os.path.join(output_folder, ppt_filename)

    # If content is a list of slides, pass as structured
    if isinstance(content, list) and all(isinstance(slide, dict) for slide in content):
        success = generate_beautiful_ppt(content, ppt_path, color_scheme=theme, use_ai=False, original_topic=topic, min_slides=6, max_slides=6)
    else:
        success = generate_beautiful_ppt(content, ppt_path, color_scheme=theme, use_ai=False, original_topic=topic, min_slides=6, max_slides=6)
    return success, ppt_path

# Additional CSS for chat styling
st.markdown("""
<style>
.stChatMessage {
    border-radius: 18px !important;
    margin-bottom: 1.1rem !important;
    padding: 0.7rem 1.1rem !important;
    background: #f7f8fd !important;
    box-shadow: 0 2px 8px 0 rgba(90,110,200,0.07);
    font-size: 1.04rem !important;
}
.stChatMessage.user {
    background: #e0e7ff !important;
    color: #2d3748 !important;
    border-top-right-radius: 6px !important;
    border-bottom-left-radius: 22px !important;
}
.stChatMessage.assistant {
    background: #fff !important;
    color: #4a5568 !important;
    border-top-left-radius: 6px !important;
    border-bottom-right-radius: 22px !important;
}
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(90deg, #667eea 0%, #5a67d8 100%) !important;
    color: #fff !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px 0 rgba(90,110,200,0.13);
    padding: 0.5rem 1.2rem !important;
    margin-top: 0.3rem !important;
    margin-bottom: 0.3rem !important;
    border: none !important;
    transition: background 0.2s;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: linear-gradient(90deg, #5a67d8 0%, #667eea 100%) !important;
    color: #fff !important;
    box-shadow: 0 4px 16px 0 rgba(90,110,200,0.18);
}
.stChatInputContainer {
    margin-top: 1.5rem !important;
}
</style>
""", unsafe_allow_html=True)

# Welcome bar at top (helps visibility on mobile - user suggested)

# Remove Streamlit native header and caption; only show custom HTML header

# Language selection and Refresh button (in same row, right aligned)
col_lang, col_spacer, col_refresh = st.columns([2, 2, 1])
with col_lang:
    language = st.selectbox("Language", ["English", "Hindi"], key="ppt_language", index=0, label_visibility="collapsed")
    st.session_state.language = language
with col_refresh:
    if st.button("🔄", key="refresh_chat", help="New Chat - Start fresh"):
        st.session_state.messages = []
        st.session_state.stage = 'idle'
        st.session_state.ppt_path = None
        st.session_state.topic = None
        st.session_state.file_content = None
        st.session_state.file_name = None
        st.session_state.parsed_slides = None
        st.session_state.awaiting_upload_confirm = False
        st.session_state.uploaded_preview = None
        # Add welcome message after refresh
        st.session_state.messages.append({"role": "assistant", "content": "Chat cleared! Ready for a new topic. Type your topic or upload a document."})
        st.rerun()

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Auto-scroll to bottom when new messages appear
if st.session_state.messages:
    st.markdown("""
    <script>
        var chatContainer = window.parent.document.querySelector('[data-testid="stChatMessageContainer"]');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        // Fallback: scroll main container
        var main = window.parent.document.querySelector('.main');
        if (main) {
            main.scrollTop = main.scrollHeight;
        }
    </script>
    """, unsafe_allow_html=True)

# Show download button if PPT is ready
if st.session_state.stage == 'done' and st.session_state.ppt_path:
    with st.chat_message("assistant"):
        if st.session_state.topic and st.session_state.topic.lower() != 'none':
            st.success(f"Your presentation on **{st.session_state.topic}** is ready!")

        # Download and New buttons
        col1, col2 = st.columns([3, 1])
        with col1:
            # ISSUE 9: Use topic-based filename for download
            download_filename = os.path.basename(st.session_state.ppt_path) if st.session_state.ppt_path else "presentation.pptx"
            with open(st.session_state.ppt_path, "rb") as f:
                st.download_button("Download PPT", f.read(), file_name=download_filename,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True, type="primary")
        with col2:
            if st.button("New", use_container_width=True):
                st.session_state.messages = []
                st.session_state.stage = 'idle'
                st.session_state.ppt_path = None
                st.session_state.topic = None
                st.session_state.file_content = None
                st.session_state.parsed_slides = None
                st.rerun()

        # Regenerate options

        # Restore Streamlit native header and caption
        st.markdown("### 📊 FREE PPT Generator")
        st.caption("Create professional presentations through chat")

# Chat input

# Name and designation collection flow
if st.session_state.stage == 'ask_name':
    with st.chat_message("assistant"):
        st.markdown("**Enter your name (for the presentation): (optional)**")
        col1, col2 = st.columns([3,1])
        with col1:
            name = st.text_input("Your name", key="presenter_name_input")
        with col2:
            if st.button("Skip", key="skip_name"):
                st.session_state.presenter_name = None
                st.session_state.stage = 'ask_designation'
                st.rerun()
        if name:
            st.session_state.presenter_name = name
            st.session_state.stage = 'ask_designation'
            st.rerun()
elif st.session_state.stage == 'ask_designation':
    with st.chat_message("assistant"):
        st.markdown("**Enter your designation (for the presentation): (optional)**")
        col1, col2 = st.columns([3,1])
        with col1:
            designation = st.text_input("Your designation", key="presenter_designation_input")
        with col2:
            if st.button("Skip", key="skip_designation"):
                st.session_state.presenter_designation = None
                st.session_state.stage = 'idle'
                # Show personalized welcome
                name = st.session_state.presenter_name
                if name:
                    welcome = f"Welcome {name}! Please tell me a topic for your presentation."
                else:
                    welcome = "Welcome! Please tell me a topic for your presentation."
                add_message("assistant", welcome)
                st.rerun()
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #5a67d8 100%);
        color: #fff;
        padding: 1.2rem 1.2rem 1rem 1.2rem;
        margin: -1rem -1rem 1.2rem -1rem;
        text-align: center;
        border-radius: 0 0 22px 22px;
        box-shadow: 0 6px 24px 0 rgba(102, 126, 234, 0.30), 0 0 0 6px #e0e7ff inset;
        border: 6px solid #5a67d8;
        border-top: none;
        background-clip: padding-box;
    ">
        <h2 style="margin:0;font-size:2.2rem;font-weight:900;letter-spacing:1.2px;text-transform:uppercase;">FREE PPT Generator</h2>
        <p style="margin:0.6rem 0 0 0;font-size:1.12rem;font-weight:500;letter-spacing:0.2px;color:#e0e7ff;">Create professional presentations through chat</p>
    </div>
    <style>
    @media (max-width: 600px) {
        div[style*='background: linear-gradient'] h2 {
            font-size: 1.35rem !important;
        }
        div[style*='background: linear-gradient'] p {
            font-size: 0.98rem !important;
        }
        div[style*='background: linear-gradient'] {
            padding: 0.8rem 0 0.6rem 0 !important;
            border-radius: 0 0 14px 14px !important;
            border-width: 4px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ============ MODERN CHATBOX UI ============
# Initialize show_uploader state
if 'show_uploader' not in st.session_state:
    st.session_state.show_uploader = False

# File attached indicator (show above chatbox)
if st.session_state.file_content:
    col_file, col_clear = st.columns([5, 1])
    with col_file:
        st.markdown(f'''<div class="file-attached">
            <span>📎</span> {st.session_state.get('file_name', 'document')}
        </div>''', unsafe_allow_html=True)
    with col_clear:
        if st.button("✕", key="clear_file", help="Remove file"):
            st.session_state.file_content = None
            st.session_state.file_name = None
            st.session_state.show_uploader = False
            st.rerun()

# Plus button for file upload (above chat input)
col_plus, col_spacer = st.columns([1, 9])
with col_plus:
    if st.button("➕", key="upload_btn", help="Upload PDF / Word / Text document"):
        st.session_state.show_uploader = not st.session_state.show_uploader
        st.rerun()

# Chat input (Enter to send)
user_input = st.chat_input("Send topic, paste content (Hindi/English)...")
send_clicked = user_input is not None

# Initialize upload confirmation state
if 'awaiting_upload_confirm' not in st.session_state:
    st.session_state.awaiting_upload_confirm = False
if 'uploaded_preview' not in st.session_state:
    st.session_state.uploaded_preview = None

# Show file uploader when + is clicked
if st.session_state.show_uploader:
    st.markdown("---")
    st.markdown("**📁 Upload Document** (PDF, Word, Text)")
    quick_file = st.file_uploader(
        "Upload",
        type=["txt", "docx", "pdf", "pptx"],
        key="quick_file_upload",
        label_visibility="collapsed"
    )
    if quick_file:
        file_name = quick_file.name
        file_content = ""
        if file_name.endswith('.txt'):
            file_content = quick_file.read().decode('utf-8')
        elif file_name.endswith('.docx'):
            try:
                from docx import Document
                import io
                doc = Document(io.BytesIO(quick_file.read()))
                file_content = '\n'.join([para.text for para in doc.paragraphs])
            except:
                st.error("Could not read DOCX file")
        elif file_name.endswith('.pdf'):
            try:
                import PyPDF2
                import io
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(quick_file.read()))
                file_content = '\n'.join([page.extract_text() for page in pdf_reader.pages])
            except:
                st.error("Could not read PDF file")
        if file_content:
            st.session_state.file_content = file_content
            st.session_state.file_name = file_name.rsplit('.', 1)[0][:50]
            st.session_state.show_uploader = False
            # ISSUE 6: Show confirmation with preview
            st.session_state.awaiting_upload_confirm = True
            # Extract first 200 chars as preview
            preview = file_content[:200].strip()
            if len(file_content) > 200:
                preview += "..."
            st.session_state.uploaded_preview = preview
            st.rerun()

# ISSUE 6: Document upload confirmation flow
if st.session_state.awaiting_upload_confirm and st.session_state.file_content:
    with st.chat_message("assistant"):
        st.markdown(f"📄 **File loaded: {st.session_state.file_name}**")
        st.markdown("**Preview:**")
        st.markdown(f"```\n{st.session_state.uploaded_preview}\n```")
        st.markdown("---")
        st.markdown("Would you like me to create a PPT from this content?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Generate PPT", key="confirm_upload"):
                st.session_state.awaiting_upload_confirm = False
                # Set topic from file name
                st.session_state.topic = st.session_state.file_name
                # Generate slides from file content using AI
                generator = MultiAIGenerator()
                language = st.session_state.get('language', 'English')
                custom_instructions = f"USER PROVIDED CONTENT (use this as the PRIMARY source):\n{st.session_state.file_content}\n\nLanguage: {language}\nTone: Government / Training"
                content_dict = generator.generate_ppt_content(
                    topic=st.session_state.file_name,
                    min_slides=6,
                    max_slides=6,
                    style=st.session_state.theme,
                    audience="general",
                    custom_instructions=custom_instructions,
                    bullets_per_slide=4,
                    bullet_word_limit=12,
                    tone="government/training",
                    required_phrases="",
                    forbidden_content=""
                )
                ai_output = content_dict.get("output", "")
                # Parse slides
                slides = []
                if ai_output:
                    lines = [l.strip() for l in ai_output.split('\n') if l.strip()]
                    current_slide = {}
                    for line in lines:
                        m = re.match(r"^\*{0,2}Slide\s*(\d+)\s*[:\-]\s*(.+?)\*{0,2}$", line, re.IGNORECASE)
                        if m:
                            if current_slide:
                                slides.append(current_slide)
                            current_slide = {"slide_number": int(m.group(1)), "title": m.group(2).strip(), "bullets": []}
                        elif line.lower().startswith('main title:'):
                            current_slide["main_title"] = line.split(':',1)[1].strip()
                        elif line.lower().startswith('tagline:'):
                            current_slide["tagline"] = line.split(':',1)[1].strip()
                        elif line.lower().startswith('subtitle:'):
                            current_slide["subtitle"] = line.split(':',1)[1].strip()
                        elif line.lower().startswith('presented by:'):
                            current_slide["presented_by"] = line.split(':',1)[1].strip()
                        elif line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                            bullet_text = line[2:].strip()
                            if bullet_text and current_slide:
                                current_slide.setdefault("bullets", []).append(bullet_text)
                        elif re.match(r'^\d+\.\s+', line):
                            bullet_text = re.sub(r'^\d+\.\s+', '', line).strip()
                            if bullet_text and current_slide:
                                current_slide.setdefault("bullets", []).append(bullet_text)
                    if current_slide:
                        slides.append(current_slide)
                st.session_state.parsed_slides = slides
                st.session_state.stage = 'generating'
                add_message("user", f"Generate PPT from uploaded file: {st.session_state.file_name}")
                add_message("assistant", ai_output if ai_output else "Processing your document...")
                st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_upload"):
                st.session_state.awaiting_upload_confirm = False
                st.session_state.file_content = None
                st.session_state.file_name = None
                st.session_state.uploaded_preview = None
                st.rerun()

# Handle chat input (st.chat_input returns text on Enter, None otherwise)
if user_input:

    add_message("user", user_input)

    # Show loading spinner immediately after user submits
    with st.spinner("Processing your request. Please wait..."):
        # If greeting, show welcome and ask for topic
        if is_greeting(user_input):
            name = st.session_state.presenter_name
            name_greeting = f" {name}" if name else ""
            if st.session_state.get('language', 'English') == 'Hindi':
                response = (f"नमस्ते{name_greeting}!\n\n"
                            "मैं आपकी मदद से पेशेवर PowerPoint प्रेजेंटेशन बना सकता हूँ।\n\n"
                            "कृपया एक विषय लिखें, या डॉक्युमेंट अपलोड करें, या टेक्स्ट पेस्ट करें।\n\n"
                            "उदाहरण: 'AI in Healthcare', 'Digital India', आदि।")
            else:
                response = (f"Hello{name_greeting}!\n\n"
                            "I can help you create a professional PowerPoint presentation.\n\n"
                            "Please enter a topic, upload a document, or paste your text.\n\n"
                            "Example: 'AI in Healthcare', 'Digital India', etc.")
            add_message("assistant", response)
            st.session_state.stage = 'idle'
            st.rerun()

        # If user input is a real topic/text/file, proceed to AI slide generation
        else:
            # Validate topic before proceeding
            is_valid, error_msg = is_valid_topic(user_input)
            if not is_valid:
                add_message("assistant", f"{error_msg}\n\nPlease try again with a proper topic.")
                st.session_state.stage = 'idle'
                st.rerun()

            # ISSUE 8: Check if user provided substantial content (pasted text or uploaded file)
            user_provided_content = ""
            use_user_content = False

            # Check if file content is available
            if st.session_state.file_content:
                user_provided_content = st.session_state.file_content
                use_user_content = True
            # Check if user pasted substantial content (> 100 chars suggests they pasted content)
            elif len(user_input) > 100:
                user_provided_content = user_input
                use_user_content = True

            # Only do Google search if user didn't provide substantial content
            google_context = ""
            if not use_user_content:
                trusted_domains = ["wikipedia.org", ".gov", ".nic.in", ".org"]
                if google_api_key and google_cse_id:
                    try:
                        results = search_google(user_input, google_api_key, google_cse_id, num_results=5)
                        # Filter to trusted sources
                        trusted_results = []
                        for r in results:
                            url = r.get('link', '')
                            if any(domain in url for domain in trusted_domains):
                                trusted_results.append(r)
                        # Extract clean text (use snippet, title)
                        snippets = [r.get('snippet', '') for r in trusted_results]
                        titles = [r.get('title', '') for r in trusted_results]
                        google_context = "\n".join(titles + snippets)
                    except Exception as e:
                        st.warning(f"Google search failed: {e}")
                        google_context = ""

            # Pass context and language to AI generator
            generator = MultiAIGenerator()
            language = st.session_state.get('language', 'English')

            # ISSUE 8: Prioritize user content over web search
            if use_user_content:
                custom_instructions = f"USER PROVIDED CONTENT (use this as the PRIMARY source for slide content):\n{user_provided_content}\n\nLanguage: {language}\nTone: Government / Training"
            else:
                custom_instructions = f"{google_context}\n\nLanguage: {language}\nTone: Government / Training"
            content_dict = generator.generate_ppt_content(
                topic=user_input,
                min_slides=6,
                max_slides=6,
                style=st.session_state.theme,
                audience="general",
                custom_instructions=custom_instructions,
                bullets_per_slide=4,
                bullet_word_limit=12,
                tone="government/training",
                required_phrases="",
                forbidden_content=""
            )
            # Parse AI output into slides (robust parser)

            def parse_slides(ai_output):
                slides = []
                if not ai_output:
                    return slides
                lines = [l.strip() for l in ai_output.split('\n') if l.strip()]
                current_slide = {}
                for line in lines:
                    # Slide start - more flexible pattern
                    # Matches: "Slide 1: Title", "Slide1: Title", "**Slide 1: Title**", "Slide 1 - Title", etc.
                    m = re.match(r"^\*{0,2}Slide\s*(\d+)\s*[:\-]\s*(.+?)\*{0,2}$", line, re.IGNORECASE)
                    if m:
                        # Save previous slide
                        if current_slide:
                            slides.append(current_slide)
                        current_slide = {"slide_number": int(m.group(1)), "title": m.group(2).strip(), "bullets": []}
                    elif line.lower().startswith('main title:'):
                        current_slide["main_title"] = line.split(':',1)[1].strip()
                    elif line.lower().startswith('tagline:'):
                        current_slide["tagline"] = line.split(':',1)[1].strip()
                    elif line.lower().startswith('subtitle:'):
                        current_slide["subtitle"] = line.split(':',1)[1].strip()
                    elif line.lower().startswith('presented by:'):
                        current_slide["presented_by"] = line.split(':',1)[1].strip()
                    elif line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                        # Handle various bullet styles
                        bullet_text = line[2:].strip()
                        if bullet_text and current_slide:
                            current_slide.setdefault("bullets", []).append(bullet_text)
                    elif re.match(r'^\d+\.\s+', line):
                        # Handle numbered lists like "1. Point"
                        bullet_text = re.sub(r'^\d+\.\s+', '', line).strip()
                        if bullet_text and current_slide:
                            current_slide.setdefault("bullets", []).append(bullet_text)
                # Add last slide
                if current_slide:
                    slides.append(current_slide)
                # Inject presenter name/designation if not present
                if slides:
                    first = slides[0]
                    if st.session_state.presenter_name:
                        first["presented_by"] = st.session_state.presenter_name
                    if st.session_state.presenter_designation:
                        # Add designation to subtitle if present, else as a new field
                        if first.get("subtitle"):
                            first["subtitle"] = (first.get("subtitle","") + f"\n{st.session_state.presenter_designation}").strip()
                        else:
                            first["subtitle"] = st.session_state.presenter_designation
                # Debug: print parsed slides count
                print(f"[DEBUG] Parsed {len(slides)} slides from AI output")
                return slides

            ai_output = content_dict.get("output", "")
            if not ai_output:
                ai_output = content_dict.get("error", "No AI output.")
            slides = parse_slides(ai_output)
            # Show the AI output as chat
            add_message("assistant", ai_output)
            # Save topic and slides to session for PPT generation
            st.session_state.topic = user_input
            st.session_state.parsed_slides = slides
            print(f"[DEBUG] Topic: {user_input}, Slides count: {len(slides)}")
            st.session_state.stage = 'generating'
            st.rerun()

# Generation process
if st.session_state.stage == 'generating':
    with st.chat_message("assistant"):
        progress_placeholder = st.empty()

        try:
            # Show progress
            progress_placeholder.markdown("**Creating your presentation...**\n\nThinking about the structure...")

            # Use parsed slides (structured data) - this is the primary content
            content = st.session_state.get('parsed_slides', [])
            ai_source = get_last_ai_source()

            if content:
                progress_placeholder.markdown(f"**Creating your presentation...**\n\n Found {len(content)} slides...")
            else:
                progress_placeholder.markdown("**Creating your presentation...**\n\n Processing content...")

            progress_placeholder.markdown("**Creating your presentation...**\n\n Creating Slide 1: Title...")
            progress_placeholder.markdown("**Creating your presentation...**\n\n Creating Slide 2: Introduction...")
            progress_placeholder.markdown("**Creating your presentation...**\n\n Creating Slide 3-5: Key Concepts...")
            progress_placeholder.markdown("**Creating your presentation...**\n\n Creating Slide 6-8: Details...")
            progress_placeholder.markdown("**Creating your presentation...**\n\n Creating Final Slides...")
            progress_placeholder.markdown("**Creating your presentation...**\n\n Applying theme & formatting...")

            # Generate PPT
            success, ppt_path = generate_ppt(content, st.session_state.topic, st.session_state.theme)

            if success:
                st.session_state.ppt_path = ppt_path
                st.session_state.stage = 'done'
                st.session_state.ai_source = ai_source
                # Update PPT generated count
                try:
                    with open("visitor_count.json", 'r') as f:
                        stats = json.load(f)
                    stats["ppt_generated"] = stats.get("ppt_generated", 0) + 1
                    stats["last_ppt"] = datetime.now().isoformat()
                    with open("visitor_count.json", 'w') as f:
                        json.dump(stats, f)
                except:
                    pass
                progress_placeholder.empty()
                add_message("assistant", f"**Done!** Your presentation on **{st.session_state.topic}** is ready.\n\n*Powered by: {ai_source}*\n\nClick the download button below.")
                st.rerun()
            else:
                progress_placeholder.error("Failed to create presentation. Please try again.")
                st.session_state.stage = 'awaiting_topic'

        except Exception as e:
            progress_placeholder.error(f"Error: {str(e)}")
            st.session_state.stage = 'awaiting_topic'
            add_message("assistant", f"Sorry, there was an error. Please try again with a different topic.")
            st.rerun()

# Regeneration process (with new theme/slides)
if st.session_state.stage == 'regenerating':
    with st.chat_message("assistant"):
        progress_placeholder = st.empty()
        try:
            progress_placeholder.markdown("**Regenerating presentation...**\n\nApplying new settings...")

            # Use existing parsed slides or regenerate
            content = st.session_state.get('parsed_slides', [])
            num_slides = st.session_state.get('num_slides', 6)

            # If slide count changed, regenerate content
            if num_slides != len(content):
                progress_placeholder.markdown(f"**Regenerating presentation...**\n\nGenerating {num_slides} slides...")
                generator = MultiAIGenerator()
                language = st.session_state.get('language', 'English')
                custom_instructions = f"Language: {language}\nTone: Government / Training"
                content_dict = generator.generate_ppt_content(
                    topic=st.session_state.topic,
                    min_slides=num_slides,
                    max_slides=num_slides,
                    style=st.session_state.theme,
                    audience="general",
                    custom_instructions=custom_instructions,
                    bullets_per_slide=4,
                    bullet_word_limit=12,
                    tone="government/training",
                    required_phrases="",
                    forbidden_content=""
                )
                ai_output = content_dict.get("output", "")
                # Reparse slides
                lines = [l.strip() for l in ai_output.split('\n') if l.strip()]
                slides = []
                current_slide = {}
                for line in lines:
                    m = re.match(r"^\*{0,2}Slide\s*(\d+)\s*[:\-]\s*(.+?)\*{0,2}$", line, re.IGNORECASE)
                    if m:
                        if current_slide:
                            slides.append(current_slide)
                        current_slide = {"slide_number": int(m.group(1)), "title": m.group(2).strip(), "bullets": []}
                    elif line.lower().startswith('main title:'):
                        current_slide["main_title"] = line.split(':',1)[1].strip()
                    elif line.lower().startswith('tagline:'):
                        current_slide["tagline"] = line.split(':',1)[1].strip()
                    elif line.lower().startswith('subtitle:'):
                        current_slide["subtitle"] = line.split(':',1)[1].strip()
                    elif line.lower().startswith('presented by:'):
                        current_slide["presented_by"] = line.split(':',1)[1].strip()
                    elif line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                        bullet_text = line[2:].strip()
                        if bullet_text and current_slide:
                            current_slide.setdefault("bullets", []).append(bullet_text)
                    elif re.match(r'^\d+\.\s+', line):
                        bullet_text = re.sub(r'^\d+\.\s+', '', line).strip()
                        if bullet_text and current_slide:
                            current_slide.setdefault("bullets", []).append(bullet_text)
                if current_slide:
                    slides.append(current_slide)
                content = slides
                st.session_state.parsed_slides = slides

            progress_placeholder.markdown(f"**Regenerating presentation...**\n\nApplying **{st.session_state.theme}** theme...")

            # Generate PPT with new settings
            success, ppt_path = generate_ppt(content, st.session_state.topic, st.session_state.theme)

            if success:
                st.session_state.ppt_path = ppt_path
                st.session_state.stage = 'done'
                progress_placeholder.empty()
                add_message("assistant", f"**Regenerated!** New presentation with **{st.session_state.theme}** theme and **{len(content)}** slides is ready.")
                st.rerun()
            else:
                progress_placeholder.error("Failed to regenerate. Please try again.")
                st.session_state.stage = 'done'
        except Exception as e:
            progress_placeholder.error(f"Error: {str(e)}")
            st.session_state.stage = 'done'
            st.rerun()

# Welcome message for new users (add to messages so it persists)
if not st.session_state.messages and st.session_state.stage == 'idle':
    st.session_state.messages.append({"role": "assistant", "content": "Welcome! Type a topic or upload a document to create your PPT."})
    st.rerun()

# ============ VISITOR STATS (no footer) ============
import json
stats_file = "visitor_count.json"
try:
    with open(stats_file, 'r') as f:
        stats = json.load(f)
except:
    stats = {"total_visits": 0, "ppt_generated": 0}

# Update visit count (only once per session)
if 'visit_counted' not in st.session_state:
    st.session_state.visit_counted = True
    stats["total_visits"] = stats.get("total_visits", 0) + 1
    stats["last_visit"] = datetime.now().isoformat()
    try:
        with open(stats_file, 'w') as f:
            json.dump(stats, f)
    except:
        pass
