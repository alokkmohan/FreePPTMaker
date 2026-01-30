# ui_theme.py
"""
This module contains all the CSS and design for the Streamlit app.
Import and call `set_ui_theme()` at the top of your main app to apply the design.
"""
import streamlit as st

def set_ui_theme():
    st.markdown("""
    <style>
    body, .stApp, .main, .block-container {
        background: #f9f9f9 !important;
        color: #23235B !important;
    }
    .block-container {
        padding-top: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 180px !important;
        max-width: 1000px !important;
        margin: 0 auto !important;
        background: #f9f9f9 !important;
        color: #23235B !important;
    }
    .header-container {
        background: linear-gradient(135deg, #5B63D6 0%, #6B46C1 25%, #E879D9 50%, #2B9BD6 75%, #00B4D8 100%);
        padding: 18px 36px;
        border-radius: 0 0 18px 18px;
        margin-bottom: 28px;
        box-shadow: 0 4px 20px rgba(91, 99, 214, 0.18);
        text-align: center;
        width: 100%;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .header-title {
        font-size: 38px;
        font-weight: 900;
        color: #fff !important;
        margin: 0;
        line-height: 1.1;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
        letter-spacing: 1px;
    }
    [data-testid="stChatMessageContainer"] {
        margin-bottom: 2rem !important;
        min-height: 350px;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        background: #fff !important;
        border-radius: 18px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #e5e5e5;
        padding: 24px 32px;
        color: #23235B !important;
    }
    .stChatMessage {
        margin-bottom: 1.2rem !important;
        padding: 1.2rem !important;
        border-radius: 16px !important;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        font-size: 18px !important;
        color: #222 !important;
        background: #f7f8fd !important;
        box-shadow: 0 2px 8px 0 rgba(90,110,200,0.07);
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
    .stChatInput {
        position: fixed !important;
        bottom: 30px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 90% !important;
        max-width: 900px !important;
        z-index: 100 !important;
        background: #fff !important;
        border: 2px solid #5B63D6 !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 16px rgba(91, 99, 214, 0.2) !important;
        color: #23235B !important;
    }
    .stChatInput textarea {
        min-height: 100px !important;
        font-size: 16px !important;
        padding: 8px !important;
        background: #f9f9f9 !important;
        color: #23235B !important;
        border-radius: 10px !important;
        border: 2px solid #5B63D6 !important;
    }
    .left-action-buttons button {
        background: #f0f2ff !important;
        border: 2px solid #5B63D6 !important;
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        font-size: 20px !important;
        padding: 0 !important;
        box-shadow: 0 2px 10px rgba(91, 99, 214, 0.2) !important;
        cursor: pointer;
        transition: all 0.2s;
        color: #23235B !important;
    }
    [data-testid="stHorizontalBlock"]:has(button[data-testid="stBaseButton-secondary"]) button {
        background: #f0f2ff !important;
        border: 2px solid #5B63D6 !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        font-size: 18px !important;
        padding: 0 !important;
        box-shadow: 0 2px 8px rgba(91, 99, 214, 0.15) !important;
        transition: all 0.2s;
        color: #23235B !important;
    }
    .action-icon-btn {
        background: none;
        border: none;
        font-size: 28px;
        cursor: pointer;
        transition: transform 0.2s, opacity 0.2s;
        padding: 8px;
        color: #23235B !important;
    }
    </style>
    """, unsafe_allow_html=True)
