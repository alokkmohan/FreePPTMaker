import streamlit as st

def document_upload_component(label="Upload Document", key="quick_file_upload", types=["txt", "docx", "pdf", "pptx"]):
    """
    A reusable document upload component for Streamlit.
    Returns (file_name, file_content) or (None, None) if nothing uploaded.
    """
    st.markdown("""
    <style>
    .solid-uploader .stFileUploader {
        background: #fff !important;
        border: 2.5px solid #5B63D6 !important;
        border-radius: 10px !important;
        color: #23235B !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 8px rgba(91,99,214,0.10) !important;
        outline: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    uploaded_files = st.file_uploader(label, type=types, key=key, label_visibility="visible", accept_multiple_files=True)
    st.markdown('<div class="solid-uploader"></div>', unsafe_allow_html=True)
    if uploaded_files:
        files = []
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_content = uploaded_file.read()
            files.append((file_name, file_content))
        return files
    return None
