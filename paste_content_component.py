import streamlit as st

def paste_content_component(label="Paste your content", key="paste_content_input", placeholder="Paste or type content here..."):
    """
    A reusable paste content textarea for Streamlit forms.
    Returns the pasted/typed value.
    """
    st.markdown("""
    <style>
    .solid-textarea textarea, .stTextArea textarea {
        background: #fff !important;
        color: #23235B !important;
        border: 2.5px solid #5B63D6 !important;
        border-radius: 10px !important;
        font-size: 1.08rem !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 8px rgba(91,99,214,0.10) !important;
        outline: none !important;
    }
    .solid-textarea textarea:focus, .stTextArea textarea:focus {
        border: 2.5px solid #23235B !important;
        box-shadow: 0 0 0 2px #5B63D6 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    value = st.text_area(label, key=key, label_visibility="visible", placeholder=placeholder)
    st.markdown('<div class="solid-textarea"></div>', unsafe_allow_html=True)
    return value
