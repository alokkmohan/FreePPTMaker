# INTEGRATION GUIDE
# How to integrate Claude-powered PPT generation into your Streamlit app

"""
STEP-BY-STEP INTEGRATION INSTRUCTIONS
=====================================

1. INSTALL REQUIRED PACKAGES
   pip install anthropic pypdf2 python-docx python-pptx

2. SET UP CLAUDE API KEY
   Option A: Environment variable
   export CLAUDE_API_KEY="your-claude-api-key-here"
   
   Option B: In code (for testing only - NOT for production)
   CLAUDE_API_KEY = "your-api-key-here"
   
   Get your API key from: https://console.anthropic.com/

3. COPY FILES TO YOUR PROJECT
   - claude_content_analyzer.py
   - claude_ppt_generator.py

4. UPDATE YOUR app.py
   See code samples below

5. RUN YOUR APP
   streamlit run app.py
"""

# ============================================================================
# SAMPLE CODE FOR app.py INTEGRATION
# ============================================================================

# Add these imports at the top of app.py
from claude_ppt_generator import create_ppt_from_file, create_ppt_from_topic

# ============================================================================
# OPTION 1: Add File Upload Support to Existing App
# ============================================================================

"""
Add this code to your Streamlit app where you want file upload:
"""

def add_file_upload_section():
    """Add file upload section to Streamlit app"""
    st.markdown("### 📤 Upload Document for PPT Generation")
    st.markdown("Upload a Word document, PDF, or text file to create a professional presentation")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['docx', 'pdf', 'txt', 'md'],
        help="Upload Word, PDF, or text files"
    )
    
    if uploaded_file:
        # Save uploaded file temporarily
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # PPT Configuration
        col1, col2 = st.columns(2)
        
        with col1:
            ppt_style = st.selectbox(
                "Presentation Style",
                ["professional", "government", "corporate", "technical"],
                help="Choose the style of your presentation"
            )
            
            min_slides = st.slider("Minimum Slides", 5, 15, 10)
        
        with col2:
            audience = st.selectbox(
                "Target Audience",
                ["general", "executives", "technical", "government"],
                help="Who will view this presentation?"
            )
            
            max_slides = st.slider("Maximum Slides", 10, 25, 15)
        
        custom_instructions = st.text_area(
            "Additional Instructions (Optional)",
            placeholder="E.g., Focus on data analysis, Include case studies, etc.",
            height=100
        )
        
        presenter_name = st.text_input(
            "Presenter Name (Optional)",
            placeholder="Your name"
        )
        
        # Generate button
        if st.button("🎨 Generate Professional PPT", type="primary", use_container_width=True):
            with st.spinner("🤖 Claude is analyzing your document and creating a professional presentation..."):
                
                # Output path
                output_folder = "outputs"
                os.makedirs(output_folder, exist_ok=True)
                output_path = os.path.join(output_folder, f"presentation_{int(time.time())}.pptx")
                
                # Generate PPT using Claude
                success = create_ppt_from_file(
                    file_path=file_path,
                    output_path=output_path,
                    style=ppt_style,
                    min_slides=min_slides,
                    max_slides=max_slides,
                    audience=audience,
                    presenter=presenter_name,
                    custom_instructions=custom_instructions
                )
                
                if success:
                    st.success("✅ Professional PowerPoint created successfully!")
                    
                    # Download button
                    with open(output_path, "rb") as f:
                        ppt_data = f.read()
                    
                    st.download_button(
                        label="📥 Download PowerPoint",
                        data=ppt_data,
                        file_name="professional_presentation.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True,
                        type="primary"
                    )
                    
                    # Preview info
                    st.info("💡 Your presentation has been generated with professional formatting and Claude-enhanced content!")
                
                else:
                    st.error("❌ Failed to generate presentation. Please try again.")


# ============================================================================
# OPTION 2: Enhance Your Existing Topic-Based Generation
# ============================================================================

"""
Replace your existing topic-based generation with Claude-powered version:
"""

def enhanced_topic_generation():
    """Enhanced topic-based PPT generation using Claude"""
    
    topic = st.text_input(
        "Enter your topic",
        placeholder="E.g., Artificial Intelligence in Healthcare"
    )
    
    if topic:
        col1, col2 = st.columns(2)
        
        with col1:
            ppt_style = st.selectbox(
                "Presentation Style",
                ["professional", "government", "corporate", "technical"]
            )
            
            min_slides = st.slider("Minimum Slides", 5, 15, 10)
        
        with col2:
            audience = st.selectbox(
                "Target Audience",
                ["general", "executives", "technical", "government"]
            )
            
            max_slides = st.slider("Maximum Slides", 10, 25, 15)
        
        custom_instructions = st.text_area(
            "Additional Instructions",
            placeholder="E.g., Include recent statistics, Focus on implementation, etc."
        )
        
        if st.button("🚀 Generate with Claude AI", type="primary"):
            with st.spinner("🤖 Claude is researching and creating your presentation..."):
                
                output_folder = "outputs"
                os.makedirs(output_folder, exist_ok=True)
                output_path = os.path.join(output_folder, f"{topic.replace(' ', '_')}.pptx")
                
                # Generate with Claude
                success = create_ppt_from_topic(
                    topic=topic,
                    output_path=output_path,
                    style=ppt_style,
                    min_slides=min_slides,
                    max_slides=max_slides,
                    audience=audience,
                    custom_instructions=custom_instructions
                )
                
                if success:
                    st.balloons()
                    st.success("✅ Professional presentation created!")
                    
                    with open(output_path, "rb") as f:
                        st.download_button(
                            "📥 Download Presentation",
                            data=f.read(),
                            file_name=f"{topic}.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )


# ============================================================================
# OPTION 3: Add to Your Existing Workflow (Minimal Changes)
# ============================================================================

"""
To integrate into your existing workflow with minimal code changes:

In your app.py, find the section where you call:
    generate_beautiful_ppt(script_content, ppt_path, ...)

Replace it with:
"""

# OLD CODE (comment out or remove):
# success = generate_beautiful_ppt(
#     script_content, 
#     ppt_path, 
#     color_scheme=selected_theme,
#     ...
# )

# NEW CODE (Claude-powered):
from claude_ppt_generator import create_ppt_from_topic

success = create_ppt_from_topic(
    topic=original_topic,  # Your topic variable
    output_path=ppt_path,
    style=selected_theme,  # Map your theme to style
    min_slides=min_slides,
    max_slides=max_slides,
    audience="general",  # Or make this configurable
    custom_instructions=user_instructions
)


# ============================================================================
# TESTING & DEBUGGING
# ============================================================================

"""
Test your integration:

1. Run a simple test:
   python claude_ppt_generator.py

2. Check if Claude API is working:
   python claude_content_analyzer.py

3. Test file upload:
   - Upload a sample Word/PDF file
   - Check if text extraction works
   - Verify PPT generation

4. Monitor errors:
   - Check console for error messages
   - Verify API key is set correctly
   - Ensure file permissions are correct
"""


# ============================================================================
# CUSTOMIZATION OPTIONS
# ============================================================================

"""
You can customize:

1. Color Schemes:
   Edit COLOR_SCHEMES in claude_ppt_generator.py
   Add your own colors

2. Slide Layouts:
   Modify add_content_slide() function
   Change fonts, spacing, alignment

3. Content Quality:
   Adjust Claude prompts in claude_content_analyzer.py
   Add more specific instructions

4. Audience Types:
   Add new audience categories
   Customize tone for each audience

5. File Support:
   Add support for more file types
   Enhance text extraction logic
"""


# ============================================================================
# PRODUCTION CONSIDERATIONS
# ============================================================================

"""
For production deployment:

1. API Key Security:
   - Use environment variables
   - Never commit API keys to git
   - Consider using secrets management

2. Error Handling:
   - Add try-except blocks
   - Provide user-friendly error messages
   - Log errors for debugging

3. Rate Limiting:
   - Monitor API usage
   - Implement request throttling
   - Cache results when appropriate

4. File Cleanup:
   - Delete temporary files
   - Clean up old generated PPTs
   - Manage disk space

5. User Feedback:
   - Show progress indicators
   - Provide estimated time
   - Allow cancellation
"""

print("""
✅ Integration Guide Complete!

Next Steps:
1. Copy claude_content_analyzer.py and claude_ppt_generator.py to your project
2. Install required packages: pip install anthropic pypdf2 python-docx python-pptx
3. Set CLAUDE_API_KEY environment variable
4. Add file upload or enhance topic generation in your app.py
5. Test with a sample file or topic
6. Customize colors, styles, and layouts as needed

For questions or issues, check the code comments and error messages.
Happy coding! 🚀
""")
