import streamlit as st

def text_input_component(label="Your name", key="presenter_name_input", placeholder="Type your name...", help="This will appear on the PPT (optional)"):
    """
    A reusable text input component for Streamlit forms.
    Returns the input value.
    """
    st.markdown("""
    <style>
    .solid-input input, .stTextInput input {
        background: #fff !important;
        color: #23235B !important;
        border: 2.5px solid #5B63D6 !important;
        border-radius: 10px !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 8px rgba(91,99,214,0.10) !important;
        outline: none !important;
    }
    .solid-input input:focus, .stTextInput input:focus {
        border: 2.5px solid #23235B !important;
        box-shadow: 0 0 0 2px #5B63D6 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    value = st.text_input(label, key=key, label_visibility="visible", placeholder=placeholder, help=help)
    st.markdown('<div class="solid-input"></div>', unsafe_allow_html=True)
    return value
