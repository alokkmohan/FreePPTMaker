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
from multi_ai_generator import get_last_ai_source

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
    st.session_state.stage = 'idle'  # idle, awaiting_topic, confirming, generating, done
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
    success = generate_beautiful_ppt(content, ppt_path, color_scheme=theme, use_ai=False, original_topic=topic, min_slides=10, max_slides=15)
    return success, ppt_path

# Header
st.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <h2 style="margin: 0; color: #667eea;">SlideCraft AI</h2>
    <p style="margin: 0.3rem 0 0 0; color: #666; font-size: 0.9rem;">Create professional presentations through chat</p>
</div>
""", unsafe_allow_html=True)

# File upload - always visible at top
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
        st.success("Your presentation is ready!")
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
user_input = st.chat_input("Type your message...")

if user_input:
    add_message("user", user_input)

    # State machine for conversation
    if st.session_state.stage == 'idle':
        if is_greeting(user_input):
            response = """Hello! Welcome to **SlideCraft AI**.

I can create professional PowerPoint presentations for you.

**What would you like to do?**
- Tell me a topic (e.g., "AI in Healthcare")
- Paste content directly
- Upload a document using the option above

What topic should I create a presentation on?"""
            add_message("assistant", response)
            st.session_state.stage = 'awaiting_topic'
        elif len(user_input.split()) > 50:
            # Long content - use directly
            st.session_state.topic = user_input.split('\n')[0][:50]
            st.session_state.file_content = user_input
            response = f"""I'll create a presentation from your content.

**Suggested Title:** {st.session_state.topic}
**Subtitle:** A Comprehensive Overview

Should I proceed with this? (Yes/No)"""
            add_message("assistant", response)
            st.session_state.stage = 'confirming'
        elif len(user_input) >= 5:
            # Topic given
            st.session_state.topic = user_input
            response = f"""Great topic! Here's what I'll create:

**Title:** {user_input}
**Subtitle:** A Complete Guide

**Structure:**
1. Introduction
2. Key Concepts
3. Benefits & Advantages
4. Challenges
5. Real-world Examples
6. Future Outlook
7. Conclusion

Should I proceed? (Yes to create, or suggest changes)"""
            add_message("assistant", response)
            st.session_state.stage = 'confirming'
        else:
            response = "I didn't understand that. Please tell me a topic for your presentation, or say **Hi** to start."
            add_message("assistant", response)

    elif st.session_state.stage == 'awaiting_topic':
        if len(user_input) >= 3:
            st.session_state.topic = user_input
            response = f"""Perfect! Here's the plan:

**Title:** {user_input}
**Subtitle:** A Comprehensive Presentation

**Slides I'll create:**
1. Title Slide
2. Introduction - What is {user_input}?
3. Key Concepts & Definitions
4. Benefits & Importance
5. Challenges & Solutions
6. Real Examples & Case Studies
7. Future Trends
8. Conclusion & Takeaways

Ready to create? (Yes/No)"""
            add_message("assistant", response)
            st.session_state.stage = 'confirming'
        else:
            response = "Please provide a more descriptive topic (at least 3 characters)."
            add_message("assistant", response)

    elif st.session_state.stage == 'confirming':
        if is_yes(user_input):
            add_message("assistant", "Starting presentation creation...")
            st.session_state.stage = 'generating'
            st.rerun()
        elif is_no(user_input):
            response = "No problem! What changes would you like? Or tell me a new topic."
            add_message("assistant", response)
            st.session_state.stage = 'awaiting_topic'
        else:
            # Treat as new topic
            st.session_state.topic = user_input
            response = f"""Updated! New plan:

**Title:** {user_input}

Proceed with this? (Yes/No)"""
            add_message("assistant", response)

    elif st.session_state.stage == 'done':
        if is_greeting(user_input):
            response = """Hello again!

Would you like to:
1. Create a **new presentation** - just tell me the topic
2. **Modify** the current one - tell me what to change

What would you like to do?"""
            add_message("assistant", response)
            st.session_state.stage = 'awaiting_topic'
        else:
            # New topic
            st.session_state.topic = user_input
            st.session_state.ppt_path = None
            response = f"""New presentation!

**Title:** {user_input}

Should I create this? (Yes/No)"""
            add_message("assistant", response)
            st.session_state.stage = 'confirming'

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
                content = generate_content_from_topic(st.session_state.topic, "", 10, 15)
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
        st.markdown("""**Welcome to SlideCraft AI!**

I can create professional PowerPoint presentations for you.

**How to use:**
- Type a topic like "Artificial Intelligence" or "Climate Change"
- Or paste your content directly
- Or upload a document above

**Just say Hi or type your topic to begin!**""")
