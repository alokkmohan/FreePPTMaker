import streamlit as st
import os
import glob
import shutil
from datetime import datetime
from docx import Document
from ppt_to_images import ppt_to_images
from create_ppt import process_script
from ai_ppt_generator import generate_beautiful_ppt
from youtube_script_generator import generate_youtube_script_with_ai
from content_generator import generate_content_from_topic

# Page Configuration
st.set_page_config(
    page_title="AI PowerPoint & YouTube Script Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful, mobile-responsive UI
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(to bottom, #f5f7fa 0%, #e8ecf1 100%);
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 25px;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: white;
        margin: 0 0 0.5rem 0;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
        letter-spacing: -1px;
    }
    
    .sub-title {
        font-size: 1.4rem;
        color: #f0f4ff;
        margin: 0;
        font-weight: 400;
        opacity: 0.95;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
        padding: 2rem;
        border-radius: 18px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 2px solid #e8ecf1;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #2d3748;
        margin: 0.5rem 0;
    }
    
    .feature-desc {
        color: #718096;
        font-size: 1rem;
        margin: 0;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 15px;
        font-weight: 600;
        border: 2px solid #e8ecf1;
        padding: 2rem 1.5rem;
        transition: all 0.3s ease;
        font-size: 1.1rem;
        background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
        color: #2d3748;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        white-space: pre-line;
        height: auto;
        line-height: 1.6;
    }
    
    .stButton > button:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2.5rem;
        white-space: normal;
        line-height: normal;
    }
    
    /* File uploader */
    .uploadedFile {
        border-radius: 12px;
        background: #f8f9fa;
        padding: 1rem;
    }
    
    /* Text areas */
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        font-size: 1rem;
        padding: 1rem;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Text inputs */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 0.8rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Info/Success boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 5px solid #667eea;
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Section headers */
    h2, h3 {
        color: #2d3748;
        font-weight: 700;
    }
    
    /* Step indicators */
    .step-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1.2rem;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 1rem;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
    }
    
    /* Theme buttons */
    .theme-button {
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.2rem;
        }
        .sub-title {
            font-size: 1.1rem;
        }
        .header-container {
            padding: 2rem 1.5rem;
        }
        .feature-card {
            padding: 1.5rem;
        }
        .feature-icon {
            font-size: 2.5rem;
        }
        .stButton > button {
            padding: 0.7rem 1.5rem;
            font-size: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        .main-title {
            font-size: 1.8rem;
        }
        .sub-title {
            font-size: 0.95rem;
        }
        .header-container {
            padding: 1.5rem 1rem;
            border-radius: 15px;
        }
        .feature-card {
            padding: 1rem;
        }
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #718096;
        font-size: 0.95rem;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Beautiful Header
st.markdown("""
<div class="header-container">
    <div class="main-title">🎨 AI PowerPoint Generator</div>
    <div class="sub-title">Transform Ideas into Beautiful Presentations & YouTube Scripts</div>
</div>
""", unsafe_allow_html=True)

# Create directories if they don't exist
os.makedirs("input", exist_ok=True)
os.makedirs("output/slides", exist_ok=True)

# Step 1: Input Method
st.markdown('<div class="step-indicator">📝 Step 1: Choose Input Method</div>', unsafe_allow_html=True)
st.markdown("")

# Initialize session state for input method
if 'input_method' not in st.session_state:
    st.session_state['input_method'] = None

col1, col2 = st.columns(2)

with col1:
    if st.button("📁 Upload File\n\nUpload TXT, DOCX, MD files", key="upload_btn", use_container_width=True):
        st.session_state['input_method'] = 'upload'
    
with col2:
    if st.button("✍️ Paste Text\n\nCopy and paste your content", key="paste_btn", use_container_width=True):
        st.session_state['input_method'] = 'paste'

st.markdown("")
script_content = None

if st.session_state.get('input_method') == 'upload':
    st.markdown("### 📁 Upload Your File")
    uploaded_file = st.file_uploader(
        "Choose your file",
        type=["txt", "docx", "md"],
        help="Supported formats: TXT, DOCX, MD"
    )
    if uploaded_file:
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        if file_type in ["txt", "md"]:
            script_content = uploaded_file.read().decode('utf-8')
        elif file_type == "docx":
            temp_path = os.path.join("input", "temp.docx")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())
            doc = Document(temp_path)
            script_content = "\n".join([para.text for para in doc.paragraphs])
        
        if script_content:
            st.success("✅ File uploaded successfully!")
            with st.expander("👀 Preview Content"):
                st.text_area("", script_content, height=200, disabled=True, label_visibility="collapsed")

elif st.session_state.get('input_method') == 'paste':
    st.markdown("### ✍️ Paste Your Content")
    
    # Initialize session state for content type
    if 'content_type' not in st.session_state:
        st.session_state['content_type'] = None
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("📄 Complete Article\n\nReady content to convert", key="article_btn", use_container_width=True):
            st.session_state['content_type'] = 'article'
    
    with col_b:
        if st.button("🤖 Topic Only\n\nAI generates content for you", key="topic_btn", use_container_width=True):
            st.session_state['content_type'] = 'topic'
    
    st.markdown("")
    
    if st.session_state.get('content_type') == 'topic':
        st.markdown("### 🎯 Enter Your Topic")
        st.markdown("AI will generate a detailed article and create presentation from your topic")
        topic_input = st.text_area(
            "",
            placeholder="Example:\n• Artificial Intelligence in Healthcare\n• Climate Change and Its Effects\n• Future of Electric Vehicles\n• Digital Marketing Strategies 2025",
            help="Enter any topic - AI will create comprehensive content",
            height=150,
            label_visibility="collapsed",
            key="topic_text"
        )
        
        if topic_input and st.button("✅ Confirm Topic and Proceed", type="primary", use_container_width=True):
            st.session_state['confirmed_content'] = f"TOPIC:{topic_input}"
            st.info(f"💡 Topic: **{topic_input}** - AI will create detailed content and presentation")
        
        script_content = st.session_state.get('confirmed_content') if st.session_state.get('confirmed_content', '').startswith('TOPIC:') else None
        
    elif st.session_state.get('content_type') == 'article':
        st.markdown("### 📝 Paste Your Content")
        article_input = st.text_area(
            "",
            height=300,
            placeholder="Paste your content here...\nYou can paste in multiple parts - the text will accumulate.\nSupports multiple languages including Hindi, English, etc.",
            help="Paste your ready-to-convert content. You can paste multiple times before submitting.",
            label_visibility="collapsed",
            key="article_text"
        )
        
        if article_input and st.button("✅ Confirm Content and Proceed", type="primary", use_container_width=True):
            st.session_state['confirmed_content'] = article_input
            st.success(f"✅ Content confirmed ({len(article_input)} characters)")
        
        script_content = st.session_state.get('confirmed_content') if not st.session_state.get('confirmed_content', '').startswith('TOPIC:') else None

# Process if content is available
if script_content:
    st.markdown("---")
    st.markdown('<div class="step-indicator">⚙️ Step 2: Configure Options</div>', unsafe_allow_html=True)
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        generate_ppt = st.checkbox("📊 Generate PowerPoint", value=True)
    with col2:
        generate_youtube_script = st.checkbox("🎬 YouTube Script", value=True)
    
    # Always use AI for best results
    use_ai = True
    ai_instructions = ""
    
    # Theme selection
    if generate_ppt:
        st.markdown("####")
        st.markdown("### 🎨 Choose Design Theme")
        
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            if st.button("🌊 Ocean", use_container_width=True, help="Professional blue theme"):
                st.session_state['theme'] = 'ocean'
        with col_b:
            if st.button("🌲 Forest", use_container_width=True, help="Natural green theme"):
                st.session_state['theme'] = 'forest'
        with col_c:
            if st.button("🌅 Sunset", use_container_width=True, help="Warm orange theme"):
                st.session_state['theme'] = 'sunset'
        with col_d:
            if st.button("💼 Corporate", use_container_width=True, help="Classic business theme"):
                st.session_state['theme'] = 'corporate'
        
        selected_theme = st.session_state.get('theme', 'corporate')
        st.info(f"✨ Selected Theme: **{selected_theme.upper()}**")
    
    st.markdown("####")
    if st.button("🚀 Generate Beautiful Files", type="primary", use_container_width=True):
        st.session_state['ai_instructions'] = ai_instructions
        
        # Handle topic mode
        if script_content.startswith("TOPIC:"):
            topic = script_content.replace("TOPIC:", "").strip()
            
            with st.spinner(f"🤖 AI is generating detailed content on: **{topic}**..."):
                try:
                    generated_content = generate_content_from_topic(topic, ai_instructions)
                    script_content = generated_content
                    st.success("✅ Content generated successfully!")
                    
                    with st.expander("📄 View Generated Content"):
                        st.text_area("", generated_content, height=300, label_visibility="collapsed")
                except Exception as e:
                    st.error(f"❌ Content generation failed: {str(e)}")
                    st.stop()
        
        # Create output folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = os.path.join("output", f"output_{timestamp}")
        os.makedirs(output_folder, exist_ok=True)
        
        st.session_state['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['output_folder'] = output_folder
        
        # Save script
        script_path = os.path.join("input", "RawScript.txt")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        
        script_backup = os.path.join(output_folder, "script.txt")
        shutil.copy(script_path, script_backup)
        
        st.markdown("---")
        st.markdown('<div class="step-indicator">📦 Results</div>', unsafe_allow_html=True)
        st.info(f"📁 Files saved in: **{output_folder}**")
        st.markdown("")
        
        # Generate PPT
        if generate_ppt:
            selected_theme = st.session_state.get('theme', 'corporate')
            user_instructions = st.session_state.get('ai_instructions', '')
            
            with st.spinner(f"🎨 Creating beautiful **{selected_theme.upper()}** presentation..."):
                ppt_path = os.path.join(output_folder, "presentation.pptx")
                try:
                    success = generate_beautiful_ppt(
                        script_content, 
                        ppt_path, 
                        color_scheme=selected_theme,
                        use_ai=use_ai,
                        ai_instructions=user_instructions
                    )
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    success = False
                
                if success:
                    st.success("✅ PowerPoint created successfully!")
                    
                    with open(ppt_path, "rb") as f:
                        st.download_button(
                            label="📥 Download PowerPoint (PPTX)",
                            data=f,
                            file_name="presentation.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            use_container_width=True
                        )
                    
                    # Generate images
                    with st.spinner("🖼️ Converting slides to images..."):
                        img_success = ppt_to_images(ppt_path, output_dir=output_folder)
                        images = sorted([f for f in os.listdir(output_folder) if f.startswith("slide_") and f.endswith(".png")])
                        
                        if images:
                            st.success(f"✅ Generated {len(images)} slide images!")
                            
                            st.markdown("### 🖼️ Slide Preview")
                            cols = st.columns(3)
                            for idx, img in enumerate(images):
                                with cols[idx % 3]:
                                    img_path = os.path.join(output_folder, img)
                                    st.image(img_path, caption=f"Slide {idx+1}", use_column_width=True)
                                    with open(img_path, "rb") as f:
                                        st.download_button(
                                            label=f"📥 Slide {idx+1}",
                                            data=f,
                                            file_name=img,
                                            mime="image/png",
                                            key=f"img_{idx}",
                                            use_container_width=True
                                        )
                        else:
                            st.info("ℹ️ Image conversion not available on cloud deployment. Download the PPT file to view slides!")
                else:
                    st.error("❌ PPT generation failed")
        
        # Generate YouTube Script
        if generate_youtube_script:
            with st.spinner("🎬 Creating YouTube script..."):
                youtube_script = generate_youtube_script_with_ai(script_content)
                
                doc_path = os.path.join(output_folder, "youtube_script.docx")
                doc = Document()
                
                title = doc.add_heading("YouTube Script", 0)
                title.alignment = 1
                
                metadata = doc.add_paragraph(f"Generated: {st.session_state.get('timestamp', 'N/A')}")
                metadata.alignment = 1
                doc.add_paragraph()
                doc.add_paragraph("_" * 80)
                doc.add_paragraph()
                
                # Format content
                lines = youtube_script.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith('# '):
                        doc.add_heading(line.replace('# ', ''), 0)
                    elif line.startswith('## '):
                        doc.add_heading(line.replace('## ', ''), 1)
                    elif line.startswith('### '):
                        doc.add_heading(line.replace('### ', ''), 2)
                    elif line.startswith('**') and line.endswith('**'):
                        para = doc.add_paragraph()
                        run = para.add_run(line.strip('*'))
                        run.bold = True
                    elif line.startswith('- ') or line.startswith('• '):
                        doc.add_paragraph(line[2:], style='List Bullet')
                    elif line == '---':
                        doc.add_paragraph('_' * 80)
                    else:
                        if line:
                            doc.add_paragraph(line)
                
                doc.save(doc_path)
                st.success("✅ YouTube script created!")
                
                with st.expander("📺 Preview YouTube Script"):
                    st.markdown(youtube_script)
                
                with open(doc_path, "rb") as f:
                    st.download_button(
                        label="📥 Download YouTube Script (DOCX)",
                        data=f,
                        file_name="youtube_script.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )

# Footer
st.markdown("""
<div class="footer">
    <p><strong>💡 Pro Tip:</strong> Upload any text file or paste content directly. Get professional presentations and YouTube scripts instantly!</p>
    <p style="margin-top: 1rem; color: #a0aec0;">Made with ❤️ by Alok Mohan using Streamlit & Groq AI</p>
</div>
""", unsafe_allow_html=True)
