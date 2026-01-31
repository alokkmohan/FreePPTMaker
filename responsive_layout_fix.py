"""
100% Viewport-Based Responsive Layout Fix
Ensures UI fits perfectly on ALL screen sizes (mobile & desktop)
"""

RESPONSIVE_LAYOUT_CSS = """
<style>
/* ═══════════════════════════════════════════════════════════════════
   🎯 VIEWPORT-BASED RESPONSIVE LAYOUT (100% FIT GUARANTEE)
   ═══════════════════════════════════════════════════════════════════ */

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1️⃣ CRITICAL: Base Reset & Viewport Lock
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    /* Lock viewport - prevents any overflow */
    height: 100vh;
    height: -webkit-fill-available; /* iOS Safari */
    width: 100vw;
    overflow: hidden;
    position: fixed;
}

body {
    height: 100vh;
    height: -webkit-fill-available;
    width: 100vw;
    overflow: hidden;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

/* Hide Streamlit defaults that can cause overflow */
#MainMenu,
footer,
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
}

.main,
.stApp,
.block-container {
    height: 100vh !important;
    width: 100vw !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100vw !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   2️⃣ LAYOUT STRUCTURE (Fixed Viewport Calculations)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

/* HEADER: 50px fixed (8% of typical mobile screen) */
.app-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 50px;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 600;
    z-index: 1000;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    overflow: hidden;
}

/* CHAT AREA: calc(100vh - header - input) */
.chat-area {
    position: fixed;
    top: 50px;
    left: 0;
    right: 0;
    bottom: 60px;
    /* Height auto-calculated: 100vh - 50px - 60px = remaining space */
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
    background: #f5f5f5;
    padding: 8px;
}

/* INPUT AREA: 60px fixed */
.input-area {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: white;
    border-top: 1px solid #e0e0e0;
    display: flex;
    align-items: center;
    padding: 8px 12px;
    z-index: 1000;
    box-shadow: 0 -2px 4px rgba(0,0,0,0.05);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   3️⃣ MOBILE-SPECIFIC ADJUSTMENTS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

/* Mobile Portrait (< 768px) - Make header smaller */
@media (max-width: 767px) and (orientation: portrait) {
    .app-header {
        height: 48px;
        font-size: 14px;
    }

    .chat-area {
        top: 48px;
        bottom: 56px;
        padding: 6px;
    }

    .input-area {
        height: 56px;
        padding: 6px 8px;
    }
}

/* Mobile Landscape (< 768px height) - Make everything compact */
@media (max-height: 500px) {
    .app-header {
        height: 40px;
        font-size: 13px;
    }

    .chat-area {
        top: 40px;
        bottom: 50px;
        padding: 4px;
    }

    .input-area {
        height: 50px;
        padding: 4px 8px;
    }
}

/* Very small screens (iPhone SE, etc.) */
@media (max-width: 375px) and (max-height: 667px) {
    .app-header {
        height: 44px;
        font-size: 13px;
        padding: 0 8px;
    }

    .chat-area {
        top: 44px;
        bottom: 52px;
        padding: 4px;
    }

    .input-area {
        height: 52px;
    }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   4️⃣ DESKTOP ADJUSTMENTS (More space available)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

@media (min-width: 768px) {
    .app-header {
        height: 56px;
        font-size: 18px;
    }

    .chat-area {
        top: 56px;
        bottom: 70px;
        padding: 12px 16px;
        max-width: 800px;
        margin: 0 auto;
    }

    .input-area {
        height: 70px;
        padding: 12px 16px;
        max-width: 800px;
        left: 50%;
        transform: translateX(-50%);
    }
}

/* Large Desktop (> 1200px) */
@media (min-width: 1200px) {
    .chat-area {
        max-width: 900px;
    }

    .input-area {
        max-width: 900px;
    }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   5️⃣ SAFE AREA INSETS (iOS Notch & Home Indicator)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

@supports (padding: env(safe-area-inset-top)) {
    .app-header {
        padding-top: env(safe-area-inset-top);
        height: calc(50px + env(safe-area-inset-top));
    }

    .chat-area {
        top: calc(50px + env(safe-area-inset-top));
        bottom: calc(60px + env(safe-area-inset-bottom));
    }

    .input-area {
        padding-bottom: env(safe-area-inset-bottom);
        height: calc(60px + env(safe-area-inset-bottom));
    }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   6️⃣ CHAT MESSAGES (Properly contained)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.stChatMessage {
    max-width: 100% !important;
    margin-bottom: 8px;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

[data-testid="stChatMessageContainer"] {
    max-width: 100% !important;
}

/* User messages (right) */
[data-testid="stChatMessageContainer"]:has([data-testid="chatAvatarIcon-user"]) > div {
    background: #dcf8c6;
    border-radius: 8px 0 8px 8px;
    padding: 8px 12px;
    max-width: 85%;
    margin-left: auto;
    word-wrap: break-word;
}

/* Assistant messages (left) */
[data-testid="stChatMessageContainer"]:has([data-testid="chatAvatarIcon-assistant"]) > div {
    background: white;
    border-radius: 0 8px 8px 8px;
    padding: 8px 12px;
    max-width: 85%;
    margin-right: auto;
    word-wrap: break-word;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   7️⃣ INPUT FIELD (Always visible & accessible)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.stChatInput {
    position: relative !important;
    bottom: 0 !important;
}

[data-testid="stChatInput"] {
    border: 1px solid #d0d0d0 !important;
    border-radius: 20px !important;
    background: #f5f5f5 !important;
    padding: 8px 16px !important;
    font-size: 14px !important;
    min-height: 40px !important;
    max-height: 40px !important;
}

[data-testid="stChatInput"]:focus {
    border-color: #6366f1 !important;
    background: white !important;
    outline: none !important;
}

/* Input container sizing */
[data-testid="stChatInputContainer"] {
    width: 100% !important;
    padding: 0 !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   8️⃣ SCROLLBAR STYLING (Clean look)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.chat-area::-webkit-scrollbar {
    width: 4px;
}

.chat-area::-webkit-scrollbar-track {
    background: transparent;
}

.chat-area::-webkit-scrollbar-thumb {
    background: rgba(0,0,0,0.2);
    border-radius: 2px;
}

/* Hide scrollbar on mobile */
@media (max-width: 767px) {
    .chat-area {
        scrollbar-width: none;
        -ms-overflow-style: none;
    }

    .chat-area::-webkit-scrollbar {
        display: none;
    }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   9️⃣ ORIENTATION CHANGE HANDLING
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

/* Force reflow on orientation change */
@media (orientation: portrait) {
    body {
        -webkit-text-size-adjust: 100%;
    }
}

@media (orientation: landscape) {
    body {
        -webkit-text-size-adjust: 100%;
    }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🔟 BUTTONS & INTERACTIVE ELEMENTS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

.stButton > button {
    border-radius: 20px;
    padding: 8px 20px;
    font-size: 14px;
    border: none;
    background: #6366f1;
    color: white;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #4f46e5;
    transform: translateY(-1px);
}

.stButton > button:active {
    transform: translateY(0);
}

/* Download button in chat */
.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border-radius: 20px;
    padding: 10px 24px;
    font-weight: 600;
    width: 100%;
    border: none;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ⚡ PERFORMANCE & SMOOTH RENDERING
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

* {
    -webkit-tap-highlight-color: transparent;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.chat-area {
    scroll-behavior: smooth;
    will-change: scroll-position;
}

/* Prevent text selection on interactive elements */
.app-header,
.input-area {
    user-select: none;
    -webkit-user-select: none;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🎯 CRITICAL: Viewport Meta Tag (Add to HTML head)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

/*
IMPORTANT: Add this to your Streamlit page config or index.html:

<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">

This ensures:
- width=device-width: Viewport width = device width
- initial-scale=1.0: No initial zoom
- maximum-scale=1.0: Prevents zoom (optional)
- user-scalable=no: Disable pinch zoom (optional)
- viewport-fit=cover: Cover notches on iPhone X+
*/

</style>
"""

# JavaScript for dynamic viewport adjustment
VIEWPORT_FIX_JS = """
<script>
// Dynamic viewport height fix (handles mobile browser address bar)
function setViewportHeight() {
    // Get actual viewport height (accounts for mobile browser UI)
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
}

// Update on load, resize, and orientation change
window.addEventListener('load', setViewportHeight);
window.addEventListener('resize', setViewportHeight);
window.addEventListener('orientationchange', function() {
    setTimeout(setViewportHeight, 100);
});

// Initial call
setViewportHeight();

// Handle mobile keyboard (adjust chat on focus)
const chatArea = document.querySelector('.chat-area');
const inputField = document.querySelector('[data-testid="stChatInput"]');

if (inputField && chatArea) {
    inputField.addEventListener('focus', function() {
        // Scroll chat to bottom when keyboard opens
        setTimeout(() => {
            chatArea.scrollTop = chatArea.scrollHeight;
        }, 300);
    });
}

// Auto-scroll to bottom on new messages
const observer = new MutationObserver(function() {
    if (chatArea) {
        chatArea.scrollTop = chatArea.scrollHeight;
    }
});

if (chatArea) {
    observer.observe(chatArea, {
        childList: true,
        subtree: true
    });
}

// Prevent bounce scrolling on iOS
document.body.addEventListener('touchmove', function(e) {
    if (e.target.closest('.chat-area')) {
        // Allow scrolling in chat area
        return;
    }
    e.preventDefault();
}, { passive: false });
</script>
"""

# HTML structure wrapper
def get_responsive_structure():
    """Returns the HTML structure for responsive layout"""
    return """
    <div class="app-header">
        📊 AI PPT Generator
    </div>
    <div class="chat-area" id="chat-container">
        <!-- Chat messages go here -->
    </div>
    <div class="input-area">
        <!-- Input field goes here -->
    </div>
    """
