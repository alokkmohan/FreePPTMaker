"""
WhatsApp-Style UI Components for Streamlit
Provides chat-style buttons, indicators, and messages
"""

import streamlit as st

def show_typing_indicator():
    """Show WhatsApp-style typing indicator (three dots)"""
    st.markdown("""
    <div class="typing-indicator" style="margin: 12px 0;">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    </div>
    """, unsafe_allow_html=True)


def show_processing_message(message="AI is creating your presentation..."):
    """Show processing message with typing indicator in chat"""
    with st.chat_message("assistant"):
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px;">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            <span style="color: #666; font-size: 14px;">{message}</span>
        </div>
        """, unsafe_allow_html=True)


def show_success_message(title="✅ Your presentation is ready!", subtitle=""):
    """Show success message in chat style"""
    with st.chat_message("assistant"):
        st.markdown(f"""
        <div class="success-message">
            <div style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">
                {title}
            </div>
            {f'<div style="font-size: 14px; opacity: 0.9;">{subtitle}</div>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)


def show_chat_option_buttons(options, keys_prefix="option"):
    """
    Show WhatsApp-style option buttons in chat

    Args:
        options: List of tuples [(label, icon, action), ...]
        keys_prefix: Prefix for button keys

    Returns:
        Selected option index or None
    """
    cols = st.columns(len(options))

    for idx, (col, (label, icon)) in enumerate(zip(cols, options)):
        with col:
            if st.button(
                f"{icon} {label}",
                key=f"{keys_prefix}_{idx}",
                use_container_width=True,
                type="secondary"
            ):
                return idx
    return None


def show_download_button_in_chat(file_path, filename="presentation.pptx", auto_download=False):
    """
    Show download button in chat flow

    Args:
        file_path: Path to the file
        filename: Download filename
        auto_download: If True, triggers auto-download
    """
    with st.chat_message("assistant"):
        try:
            with open(file_path, "rb") as f:
                file_data = f.read()

            st.download_button(
                label="⬇️ Download Your PPT",
                data=file_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
                type="primary"
            )

            if auto_download:
                # Trigger auto-download with JavaScript
                st.markdown(f"""
                <script>
                // Auto-download trigger
                setTimeout(function() {{
                    const downloadBtn = document.querySelector('[data-testid="stDownloadButton"]');
                    if (downloadBtn) {{
                        downloadBtn.click();
                    }}
                }}, 500);
                </script>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error loading file: {e}")


def show_slide_preview_thumbnails(image_paths, max_visible=5):
    """
    Show slide preview thumbnails in a horizontal scroll (like WhatsApp media)

    Args:
        image_paths: List of image paths
        max_visible: Maximum thumbnails to show
    """
    if not image_paths:
        return

    with st.chat_message("assistant"):
        st.markdown("""
        <div style="margin-bottom: 8px; font-weight: 500; color: #666;">
            📊 Preview ({} slides)
        </div>
        """.format(len(image_paths)), unsafe_allow_html=True)

        # Create horizontal scrollable container
        cols = st.columns(min(len(image_paths), max_visible))

        for idx, (col, img_path) in enumerate(zip(cols, image_paths[:max_visible])):
            with col:
                try:
                    st.image(img_path, use_container_width=True)
                except Exception as e:
                    st.markdown(f"""
                    <div style="width: 100%; height: 90px; background: #f0f0f0;
                                border-radius: 8px; display: flex; align-items: center;
                                justify-content: center; font-size: 12px; color: #999;">
                        Slide {idx + 1}
                    </div>
                    """, unsafe_allow_html=True)

        if len(image_paths) > max_visible:
            st.caption(f"+ {len(image_paths) - max_visible} more slides")


def add_chat_message(role, content):
    """Add a message to the chat and automatically scroll"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.session_state.messages.append({"role": role, "content": content})

    # Trigger auto-scroll
    st.markdown("""
    <script>
    setTimeout(function() {
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.scrollTo({
                top: chatContainer.scrollHeight,
                behavior: 'smooth'
            });
        }
    }, 100);
    </script>
    """, unsafe_allow_html=True)


def show_welcome_with_options():
    """Show welcome message with WhatsApp-style option buttons"""
    welcome_msg = """**Welcome to AI PPT Generator!** 🎉

I can help you create professional PowerPoint presentations in minutes.

**Choose how you'd like to get started:**"""

    add_chat_message("assistant", welcome_msg)

    with st.chat_message("assistant"):
        st.markdown("""
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px;">
            <button class="chat-option-button" onclick="selectOption('upload')">
                📤 Upload Document
            </button>
            <button class="chat-option-button" onclick="selectOption('paste')">
                📋 Paste Content
            </button>
            <button class="chat-option-button" onclick="selectOption('topic')">
                ✍️ Write Topic
            </button>
        </div>

        <script>
        function selectOption(option) {
            // Store selection in session
            window.selectedOption = option;

            // Highlight selected button
            document.querySelectorAll('.chat-option-button').forEach(btn => {
                btn.style.background = 'white';
                btn.style.color = '#6366f1';
            });
            event.target.style.background = '#6366f1';
            event.target.style.color = 'white';
        }
        </script>
        """, unsafe_allow_html=True)
