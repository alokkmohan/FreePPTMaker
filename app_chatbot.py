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
    page_title="SlideCraft AI",
    page_icon="P",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Minimal CSS
st.markdown("""
<style>
    #MainMenu, footer, header {display: none !important;}
    .block-container {padding-top: 1rem !important; padding-bottom: 100px !important;}

    /* Chat styling */
    .stChatMessage {margin-bottom: 0.5rem !important;}

    /* Fixed bottom input */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 60px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 90% !important;
        max-width: 700px !important;
        z-index: 1000 !important;
    }
</style>
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

# Helper functions
def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def is_greeting(text):
    greetings = ['hi', 'hello', 'hey', 'hii', 'hiii', 'namaste', 'namaskar', 'good morning',
                 'good afternoon', 'good evening', 'howdy', 'hola', 'yo', 'kya hal', 'kaise ho']
    text_lower = text.lower().strip()
    for g in greetings:
        if text_lower == g or text_lower.startswith(g + ' ') or text_lower.startswith(g + '!'):
            return True
    return False

def is_yes(text):
    yes_words = ['yes', 'ya', 'yaa', 'haan', 'han', 'ok', 'okay', 'sure', 'theek', 'thik', 'sahi', 'correct', 'proceed', 'go ahead', 'bana do', 'banao']
    return text.lower().strip() in yes_words or text.lower().strip().startswith('yes')

def is_no(text):
    no_words = ['no', 'nahi', 'naa', 'na', 'change', 'modify', 'edit', 'different']
    return text.lower().strip() in no_words

def generate_ppt(content, topic, theme):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join("output", f"output_{timestamp}")
    os.makedirs(output_folder, exist_ok=True)
    safe_title = re.sub(r'[^\w\s-]', '', str(topic))[:50]
    safe_title = re.sub(r'[-\s]+', '_', safe_title) if safe_title else "presentation"
    ppt_path = os.path.join(output_folder, f"{safe_title}.pptx")
    # If content is a list of slides, pass as structured
    if isinstance(content, list) and all(isinstance(slide, dict) for slide in content):
        success = generate_beautiful_ppt(content, ppt_path, color_scheme=theme, use_ai=False, original_topic=topic, min_slides=6, max_slides=6)
    else:
        success = generate_beautiful_ppt(content, ppt_path, color_scheme=theme, use_ai=False, original_topic=topic, min_slides=6, max_slides=6)
    return success, ppt_path

# Header
st.markdown("""
<div style="
    width: 100vw;
    max-width: 100vw;
    margin-left: calc(-50vw + 50%);
    background: linear-gradient(90deg, #667eea 0%, #5a67d8 100%);
    color: #fff;
    padding: 1.2rem 0 0.7rem 0;
    box-shadow: 0 2px 12px 0 rgba(60,60,120,0.07);
    border-radius: 0 0 18px 18px;
    text-align: center;
">
    <h2 style="margin: 0; font-size: 2.1rem; font-weight: 700; letter-spacing: 1px; color: #fff;">SlideCraft AI</h2>
    <p style="margin: 0.5rem 0 0 0; color: #e0e7ff; font-size: 1.08rem; font-weight: 500; letter-spacing: 0.2px;">Create professional presentations through chat</p>
</div>
<style>
@media (max-width: 600px) {
    div[style*='background: linear-gradient'] h2 {
        font-size: 1.3rem !important;
    }
    div[style*='background: linear-gradient'] p {
        font-size: 0.95rem !important;
    }
    div[style*='background: linear-gradient'] {
        padding: 0.7rem 0 0.5rem 0 !important;
        border-radius: 0 0 12px 12px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# File upload - always visible at top
st.markdown("**Language / भाषा चुनें:**")
language = st.selectbox("Select language", ["English", "Hindi"], key="ppt_language", index=0)
st.session_state.language = language

with st.expander("Attach Document (Optional)", expanded=False):
    uploaded_file = st.file_uploader("Upload txt, docx, or pdf", type=["txt", "docx", "pdf"], key="file_upload", label_visibility="collapsed")
    if uploaded_file:
        file_name = uploaded_file.name
        file_content = ""
        if file_name.endswith('.txt'):
            file_content = uploaded_file.read().decode('utf-8')
        elif file_name.endswith('.docx'):
            try:
                from docx import Document
                import io
                doc = Document(io.BytesIO(uploaded_file.read()))
                file_content = '\n'.join([para.text for para in doc.paragraphs])
            except:
                st.error("Could not read DOCX")
        elif file_name.endswith('.pdf'):
            try:
                import PyPDF2
                import io
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                file_content = '\n'.join([page.extract_text() for page in pdf_reader.pages])
            except:
                st.error("Could not read PDF")
        if file_content:
            st.session_state.file_content = file_content
            st.session_state.file_name = file_name.rsplit('.', 1)[0][:50]
            st.success(f"File loaded: {st.session_state.file_name}")

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Show download button if PPT is ready
if st.session_state.stage == 'done' and st.session_state.ppt_path:
    with st.chat_message("assistant"):
        if st.session_state.topic and st.session_state.topic.lower() != 'none':
            st.success(f"Your presentation on {st.session_state.topic} is ready.\n\nPowered by: Alok Mohan\n\nClick the download button below.")
        col1, col2 = st.columns([3, 1])
        with col1:
            with open(st.session_state.ppt_path, "rb") as f:
                st.download_button("Download PPT", f.read(), file_name="presentation.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True, type="primary")
        with col2:
            if st.button("New", use_container_width=True):
                st.session_state.messages = []
                st.session_state.stage = 'idle'
                st.session_state.ppt_path = None
                st.session_state.topic = None
                st.session_state.file_content = None
                st.rerun()

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
                st.session_state.stage = 'generating'
                st.rerun()
        if designation:
            st.session_state.presenter_designation = designation
            st.session_state.stage = 'generating'
            st.rerun()

user_input = st.chat_input("Type your message...")

if user_input:

    add_message("user", user_input)

    # Show loading spinner immediately after user submits
    with st.spinner("Processing your request. Please wait..."):
        # If greeting, show welcome and ask for topic
        if is_greeting(user_input):
            if st.session_state.get('language', 'English') == 'Hindi':
                response = ("नमस्ते!\n\n" 
                            "मैं आपकी मदद से पेशेवर PowerPoint प्रेजेंटेशन बना सकता हूँ।\n\n"
                            "कृपया एक विषय लिखें, या डॉक्युमेंट अपलोड करें, या टेक्स्ट पेस्ट करें।\n\n"
                            "उदाहरण: 'AI in Healthcare', 'Digital India', आदि।")
            else:
                response = ("Hello!\n\n" 
                            "I can help you create a professional PowerPoint presentation.\n\n"
                            "Please enter a topic, upload a document, or paste your text.\n\n"
                            "Example: 'AI in Healthcare', 'Digital India', etc.")
            add_message("assistant", response)
            st.session_state.stage = 'idle'
            st.rerun()

        # If user input is a real topic/text/file, proceed to AI slide generation
        else:
            # 1. Google search
            google_context = ""
            trusted_domains = ["wikipedia.org", ".gov", ".nic.in", ".org"]
            if google_api_key and google_cse_id:
                try:
                    results = search_google(user_input, google_api_key, google_cse_id, num_results=5)
                    # 2. Filter to trusted sources
                    trusted_results = []
                    for r in results:
                        url = r.get('link', '')
                        if any(domain in url for domain in trusted_domains):
                            trusted_results.append(r)
                    # 3. Extract clean text (use snippet, title)
                    snippets = [r.get('snippet', '') for r in trusted_results]
                    titles = [r.get('title', '') for r in trusted_results]
                    google_context = "\n".join(titles + snippets)
                except Exception as e:
                    st.warning(f"Google search failed: {e}")
                    google_context = ""

            # 4. Pass context and language to AI generator
            generator = MultiAIGenerator()
            language = st.session_state.get('language', 'English')
            # Add language and tone to prompt
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
                    # Slide start
                    m = re.match(r"^Slide ?(\d+): ?(.+)$", line)
                    if m:
                        # Save previous slide
                        if current_slide:
                            slides.append(current_slide)
                        current_slide = {"slide_number": int(m.group(1)), "title": m.group(2), "bullets": []}
                    elif line.startswith('Main Title:'):
                        current_slide["main_title"] = line.split(':',1)[1].strip()
                    elif line.startswith('Tagline:'):
                        current_slide["tagline"] = line.split(':',1)[1].strip()
                    elif line.startswith('Subtitle:'):
                        current_slide["subtitle"] = line.split(':',1)[1].strip()
                    elif line.startswith('Presented by:'):
                        current_slide["presented_by"] = line.split(':',1)[1].strip()
                    elif line.startswith('- '):
                        current_slide.setdefault("bullets", []).append(line[2:].strip())
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
                return slides

            ai_output = content_dict.get("output", "")
            if not ai_output:
                ai_output = content_dict.get("error", "No AI output.")
            slides = parse_slides(ai_output)
            # Show the AI output as chat
            add_message("assistant", ai_output)
            # Save slides to session for PPT generation
            st.session_state.parsed_slides = slides
            st.session_state.stage = 'generating'
            st.rerun()

# Generation process
if st.session_state.stage == 'generating':
    with st.chat_message("assistant"):
        progress_placeholder = st.empty()

        try:
            # Show progress
            progress_placeholder.markdown("**Creating your presentation...**\n\nThinking about the structure...")

            # Generate content
            if st.session_state.file_content:
                content = st.session_state.file_content
                ai_source = "Your Document"
                progress_placeholder.markdown("**Creating your presentation...**\n\n Processing your content...")
            else:
                progress_placeholder.markdown("**Creating your presentation...**\n\n Researching the topic...")
                # Use parsed slides from session (structured)
                content = st.session_state.get('parsed_slides', [])
                ai_source = get_last_ai_source()
                progress_placeholder.markdown(f"**Creating your presentation...**\n\n Content generated by: **{ai_source}**")

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

# Welcome message for new users
if not st.session_state.messages and st.session_state.stage == 'idle':
    with st.chat_message("assistant"):
        st.markdown("Welcome to SlideCraft AI! Type a topic or upload a document to begin.")
