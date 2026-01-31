"""
WhatsApp-Style Mobile-First CSS for Streamlit PPT Maker
Provides smooth chat experience with proper mobile keyboard handling
"""

WHATSAPP_STYLE_CSS = """
<style>
/* ═══════════════════════════════════════════════════════════════════
   📱 MOBILE-FIRST WHATSAPP-STYLE CHAT UI
   ═══════════════════════════════════════════════════════════════════ */

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1️⃣ VIEWPORT & BASE SETUP (Prevents keyboard push issues)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

html, body {
    height: 100vh;
    height: -webkit-fill-available;
    overflow: hidden;
    position: fixed;
    width: 100%;
    -webkit-overflow-scrolling: touch;
}

/* Hide Streamlit defaults */
#MainMenu, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {
    display: none !important;
}

.main > div:first-child {
    padding-top: 0 !important;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   2️⃣ FIXED BANNER (Always visible at top, never pushed)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.chat-banner {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    z-index: 9999;
    backdrop-filter: blur(10px);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   3️⃣ CHAT CONTAINER (WhatsApp-style scrollable area)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.chat-container {
    position: fixed;
    top: 60px;
    bottom: 70px;
    left: 0;
    right: 0;
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
    background: #f0f2f5;
    padding: 12px;
    scroll-behavior: smooth;
}

/* WhatsApp pattern background */
.chat-container::before {
    content: "";
    position: fixed;
    top: 60px;
    bottom: 70px;
    left: 0;
    right: 0;
    background-image:
        repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,0,0,0.01) 10px, rgba(0,0,0,0.01) 20px);
    pointer-events: none;
    z-index: 0;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   4️⃣ MESSAGE BUBBLES (WhatsApp-style)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.stChatMessage {
    position: relative;
    z-index: 1;
    margin-bottom: 8px;
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* User messages (right side, green) */
[data-testid="stChatMessageContainer"]:has([data-testid="chatAvatarIcon-user"]) {
    justify-content: flex-end !important;
}

[data-testid="stChatMessageContainer"]:has([data-testid="chatAvatarIcon-user"]) > div {
    background: #dcf8c6 !important;
    border-radius: 8px 0px 8px 8px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
    max-width: 80% !important;
    padding: 8px 12px !important;
    margin-left: auto !important;
}

/* Assistant messages (left side, white) */
[data-testid="stChatMessageContainer"]:has([data-testid="chatAvatarIcon-assistant"]) {
    justify-content: flex-start !important;
}

[data-testid="stChatMessageContainer"]:has([data-testid="chatAvatarIcon-assistant"]) > div {
    background: white !important;
    border-radius: 0px 8px 8px 8px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
    max-width: 80% !important;
    padding: 8px 12px !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   5️⃣ INPUT CONTAINER (Fixed at bottom, handles keyboard)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.input-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 70px;
    background: white;
    border-top: 1px solid #e0e0e0;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    z-index: 9998;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.05);
}

/* Mobile keyboard handling */
@supports (-webkit-touch-callout: none) {
    .input-container {
        padding-bottom: env(safe-area-inset-bottom);
    }

    /* When keyboard opens, adjust chat container */
    .chat-container {
        padding-bottom: env(safe-area-inset-bottom);
    }
}

/* Chat input field */
.stChatInput {
    position: relative !important;
    bottom: 0 !important;
}

[data-testid="stChatInput"] {
    border: 1px solid #d0d0d0 !important;
    border-radius: 24px !important;
    background: #f5f5f5 !important;
    padding: 10px 16px !important;
    font-size: 15px !important;
}

[data-testid="stChatInput"]:focus {
    border-color: #6366f1 !important;
    background: white !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.1) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   6️⃣ OPTION BUTTONS (WhatsApp-style action buttons in chat)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.chat-option-button {
    display: inline-block;
    background: white;
    border: 1.5px solid #6366f1;
    border-radius: 20px;
    padding: 10px 20px;
    margin: 6px 4px;
    font-size: 14px;
    font-weight: 500;
    color: #6366f1;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}

.chat-option-button:hover {
    background: #6366f1;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(99,102,241,0.2);
}

.chat-option-button:active {
    transform: translateY(0);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   7️⃣ PROCESSING INDICATOR (Typing dots like WhatsApp)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.typing-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 12px 16px;
    background: white;
    border-radius: 18px;
    width: fit-content;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.typing-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #90949c;
    animation: typing 1.4s infinite;
}

.typing-dot:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: 0.7;
    }
    30% {
        transform: translateY(-10px);
        opacity: 1;
    }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   8️⃣ SUCCESS MESSAGE & DOWNLOAD (In chat flow)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.success-message {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    padding: 16px 20px;
    border-radius: 12px;
    margin: 12px 0;
    box-shadow: 0 4px 12px rgba(16,185,129,0.3);
    animation: successPop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes successPop {
    0% {
        transform: scale(0.8);
        opacity: 0;
    }
    50% {
        transform: scale(1.05);
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}

.download-button {
    display: inline-block;
    background: white;
    color: #6366f1;
    padding: 12px 24px;
    border-radius: 24px;
    font-weight: 600;
    text-decoration: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
    margin: 8px 4px;
}

.download-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(99,102,241,0.3);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   9️⃣ SLIDE PREVIEW (Thumbnails in chat)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.slide-preview-container {
    display: flex;
    overflow-x: auto;
    gap: 8px;
    padding: 12px;
    background: rgba(255,255,255,0.5);
    border-radius: 12px;
    margin: 12px 0;
    -webkit-overflow-scrolling: touch;
}

.slide-preview {
    flex-shrink: 0;
    width: 160px;
    height: 90px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border: 2px solid white;
    transition: transform 0.2s ease;
}

.slide-preview:hover {
    transform: scale(1.05);
}

.slide-preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🔟 MOBILE OPTIMIZATIONS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

@media (max-width: 768px) {
    .chat-banner {
        height: 56px;
        font-size: 16px;
    }

    .chat-container {
        top: 56px;
        bottom: 60px;
        padding: 8px;
    }

    .input-container {
        height: 60px;
        padding: 6px 8px;
    }

    [data-testid="stChatMessageContainer"] > div {
        max-width: 90% !important;
        font-size: 14px !important;
    }

    .chat-option-button {
        padding: 8px 16px;
        font-size: 13px;
        margin: 4px 2px;
    }

    .slide-preview {
        width: 140px;
        height: 79px;
    }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🎯 SMOOTH SCROLL & NO JUMPS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

* {
    -webkit-tap-highlight-color: transparent;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.chat-container::-webkit-scrollbar {
    width: 6px;
}

.chat-container::-webkit-scrollbar-track {
    background: transparent;
}

.chat-container::-webkit-scrollbar-thumb {
    background: rgba(0,0,0,0.2);
    border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
    background: rgba(0,0,0,0.3);
}

/* Prevent layout shift */
.stApp {
    overflow: hidden;
}

/* Hide scrollbar on mobile for cleaner look */
@media (max-width: 768px) {
    .chat-container::-webkit-scrollbar {
        display: none;
    }

    .chat-container {
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
}

</style>
"""

# JavaScript for auto-scroll and keyboard handling
WHATSAPP_AUTOSCROLL_JS = """
<script>
// Auto-scroll to bottom on new messages
function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Smooth scroll with animation
function smoothScrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    }
}

// Handle mobile keyboard
window.addEventListener('resize', function() {
    // When keyboard opens (viewport shrinks), adjust chat
    smoothScrollToBottom();
});

// Auto-scroll on page load and updates
const observer = new MutationObserver(smoothScrollToBottom);
const chatContainer = document.querySelector('.chat-container');
if (chatContainer) {
    observer.observe(chatContainer, { childList: true, subtree: true });
}

// Initial scroll
setTimeout(scrollToBottom, 500);
</script>
"""
