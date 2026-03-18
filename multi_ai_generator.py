"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                     ✨ MULTI-AI CONTENT GENERATOR ✨                          ║
║                                                                               ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                               ║
║  📌 Purpose: Generate PowerPoint content using multiple AI providers         ║
║  🤖 Supported AI: Mistral AI (Cloud API)                                     ║
║  🚀 Features:                                                                 ║
║     • Automatic AI provider selection & fallback                             ║
║     • Dynamic prompt generation with web context                             ║
║     • Customizable slide structure & styling                                 ║
║     • Professional presentation content creation                             ║
║                                                                               ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                               ║
║  📝 Author: TextToPPTMaker Project                                           ║
║  📅 Last Updated: January 25, 2026                                           ║
║  🔧 Version: 2.0                                                              ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════════
# 📦 IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════

import os
import json
from typing import Dict, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# 🌍 GLOBAL VARIABLES
# ═══════════════════════════════════════════════════════════════════════════════

# Track which AI provider was used for the last generation
_last_ai_source = "Unknown"

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_last_ai_source() -> str:
    """
    Get the last AI source/provider that was used for content generation.
    
    Returns:
        str: Name of the AI provider (e.g., 'Mistral', 'Groq', 'Ollama')
    """
    global _last_ai_source
    return _last_ai_source


def get_secret(key: str) -> Optional[str]:
    """Get secret from Streamlit secrets, environment variable, or .env file"""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv(key)

def get_ollama_url():
    """Get Ollama URL - can be local or remote (ngrok/public)"""
    # Check for custom Ollama URL (for remote access via ngrok etc.)
    custom_url = get_secret("OLLAMA_URL")
    if custom_url:
        return custom_url.rstrip('/')
    # Default to localhost
    return "http://localhost:11434"


# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 MULTI-AI GENERATOR CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class MultiAIGenerator:
    """
    🎯 Multi-AI Content Generator
    
    A powerful content generation class that supports multiple AI providers
    with automatic fallback mechanisms. Generates professional PowerPoint
    presentation content with customizable parameters.
    
    Supported AI Providers:
        - Mistral AI (Primary)
        - Groq (Fallback)
        - Ollama (Local option)
    """

    def __init__(self, ai_model: str = "auto", api_key: str = None):
        """
        🚀 Initialize Multi-AI Generator
        
        Args:
            ai_model (str): AI model selection ('auto' for automatic selection)
            api_key (str): Optional API key override
            
        Provider Priority:
            1. Mistral AI (Cloud - Primary)
            2. Groq (Cloud - Fallback)
            3. Ollama (Local - Alternative)
        """
        self.ai_model = ai_model
        self.api_key = api_key

    # ───────────────────────────────────────────────────────────────────────────
    # 📊 MAIN CONTENT GENERATION METHOD
    # ───────────────────────────────────────────────────────────────────────────

    def generate_ppt_content(
        self,
        topic: str,
        min_slides: int = 10,
        max_slides: int = 20,
        style: str = "professional",
        audience: str = "general",
        custom_instructions: str = "",
        bullets_per_slide: int = 4,
        bullet_word_limit: int = 12,
        tone: str = "formal",
        required_phrases: str = "",
        forbidden_content: str = ""
    ) -> Dict:
        """
        🎨 Generate PowerPoint Content Structure
        
        Creates a complete slide-by-slide outline for presentations using AI.
        Supports web research context integration and highly customizable parameters.
        
        Args:
            topic (str): Main presentation topic/title
            min_slides (int): Minimum number of slides (default: 10)
            max_slides (int): Maximum number of slides (default: 20)
            style (str): Presentation style (e.g., 'professional', 'creative')
            audience (str): Target audience type (default: 'general')
            custom_instructions (str): Additional context/web research data
            bullets_per_slide (int): Target bullet points per slide (default: 4)
            bullet_word_limit (int): Word limit per bullet point (default: 12)
            tone (str): Content tone (e.g., 'formal', 'casual')
            required_phrases (str): Phrases that must be included
            forbidden_content (str): Content to avoid
            
        Returns:
            Dict: {'output': str} on success or {'error': str} on failure
            
        Note:
            All content rules are dynamic and user-driven. The AI will use
            web research context if provided to generate unique, topic-specific content.
        """
        global _last_ai_source
        
        # ─────────────────────────────────────────────────────────────────────
        # 🔍 Debug & Context Processing
        # ─────────────────────────────────────────────────────────────────────
        
        if custom_instructions:
            print("\n[DEBUG] Web Research Context passed to AI:\n" + custom_instructions + "\n")

        # ─────────────────────────────────────────────────────────────────────
        # 📝 Build Dynamic AI Prompt
        # ─────────────────────────────────────────────────────────────────────
        web_context = f"WEB RESEARCH CONTEXT (use this information to generate unique, topic-specific slide content):\n{custom_instructions}\n\n" if custom_instructions else ""

        prompt = f"""{web_context}You are an expert presentation content writer. Generate a slide-by-slide outline for a PowerPoint presentation.

STRICT RULES:
- Number of slides: MINIMUM {min_slides} slides, MAXIMUM {max_slides} slides
- Each slide title: MAXIMUM 35 characters. Keep titles short and clear.
- Each bullet: exactly 1 COMPLETE sentence, MAXIMUM 15 words. Never leave a sentence unfinished.
- Never truncate or use "..." — better to write less than to leave incomplete.
- 4 bullet points per slide (no more, no less)
- Each bullet must be a full, meaningful sentence that ends with a period.
- DO NOT write long paragraphs — write SHORT, PUNCHY, COMPLETE sentences.
- No emojis, no markdown, no filler, no repetition

WRONG (too long, will get cut off):
- "The implementation of artificial intelligence in healthcare has significantly improved patient outcomes by enabling early diagnosis and reducing treatment delays across hospitals."

CORRECT (short, complete, impactful):
- "AI enables early diagnosis and reduces treatment delays in hospitals."

- Tone: {tone}
- Style: {style}
- Audience: {audience}
- If writing in Hindi: Write complete short Hindi sentences, not keywords.

Output format:
Slide 1: Title Slide
Main Title: [max 35 chars]
Tagline: [max 50 chars]
Subtitle: [max 50 chars]
Presented by: [optional]

Slide 2: [Short Title max 35 chars]
- Complete sentence, max 15 words.
- Complete sentence, max 15 words.
- Complete sentence, max 15 words.
- Complete sentence, max 15 words.

(Continue for ALL {min_slides} to {max_slides} slides - DO NOT STOP EARLY)

Do not include anything outside this format.

TOPIC: {topic}
"""
        
        # ─────────────────────────────────────────────────────────────────────
        # 🚀 Execute AI Generation with Mistral
        # ─────────────────────────────────────────────────────────────────────
        
        mistral_api_key = get_secret("MISTRAL_API_KEY")
        if mistral_api_key:
            try:
                import requests
                mistral_url = "https://api.mistral.ai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {mistral_api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "mistral-large-latest",
                    "messages": [
                        {"role": "system", "content": "You are an expert presentation content writer. Generate complete slide-by-slide content."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 8000,
                    "temperature": 0.7
                }
                resp = requests.post(mistral_url, headers=headers, json=data, timeout=60)
                resp.raise_for_status()
                result = resp.json()
                ai_output = result["choices"][0]["message"]["content"]
                global _last_ai_source
                _last_ai_source = "Mistral"
                return {"output": ai_output}
            except Exception as e:
                return {"error": f"Mistral AI generation failed: {str(e)}"}
        return {"error": "No valid Mistral API key found. Please set MISTRAL_API_KEY."}

    # ───────────────────────────────────────────────────────────────────────────
    # 🎯 AI-POWERED AUTOMATIC TITLE GENERATION
    # ───────────────────────────────────────────────────────────────────────────

    def generate_smart_title(
        self,
        content: str,
        language: str = "English",
        style: str = "professional"
    ) -> Dict:
        """
        🎨 AI-Powered Smart Title Generator

        Automatically generates attractive, professional titles for presentations
        by analyzing the content using AI. Creates Main Title, Tagline, and Subtitle.

        Args:
            content (str): The presentation content/topic to analyze
            language (str): Language for title generation (default: "English")
            style (str): Title style - 'professional', 'creative', 'corporate', etc.

        Returns:
            Dict: {
                'main_title': str,     # Primary presentation title (max 80 chars)
                'tagline': str,        # Catchy subtitle/tagline (max 100 chars)
                'subtitle': str,       # Additional context (max 100 chars)
                'success': bool,       # Whether generation was successful
                'error': str           # Error message if failed
            }

        Example:
            >>> generator = MultiAIGenerator()
            >>> result = generator.generate_smart_title(
            ...     content="Artificial Intelligence in Healthcare...",
            ...     language="English",
            ...     style="professional"
            ... )
            >>> print(result['main_title'])
            'AI-Powered Healthcare Revolution'
        """
        global _last_ai_source

        # Truncate content for analysis (max 3000 chars for better performance)
        content_preview = content[:3000] if len(content) > 3000 else content

        # Build AI prompt for title generation
        prompt = f"""You are an expert presentation title writer. Analyze the following content and create an attractive, professional presentation title package.

CONTENT TO ANALYZE:
{content_preview}

YOUR TASK:
Generate THREE components for a presentation title slide:

1. MAIN TITLE (max 35 characters):
   - Short, catchy, professional
   - Must capture the essence of the content
   - Style: {style}
   - Language: {language}
   - NO generic words like "Presentation" or "Overview"

2. TAGLINE (max 50 characters):
   - A compelling subtitle that adds context
   - Language: {language}

3. SUBTITLE (max 50 characters):
   - Additional context or focus area
   - Language: {language}

OUTPUT FORMAT (strict - output ONLY these three lines, nothing else):
Main Title: [Your main title here]
Tagline: [Your tagline here]
Subtitle: [Your subtitle here]

IMPORTANT RULES:
- Write in {language} language
- Keep titles concise and impactful
- NO emojis, NO markdown formatting
- NO explanations or extra text
- Just output the three lines in the exact format shown above
"""

        # Try Mistral AI first
        mistral_api_key = get_secret("MISTRAL_API_KEY")
        if mistral_api_key:
            try:
                import requests
                mistral_url = "https://api.mistral.ai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {mistral_api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "mistral-large-latest",
                    "messages": [
                        {"role": "system", "content": "You are an expert presentation title writer. Generate concise, impactful titles."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.8  # Higher temperature for more creative titles
                }
                resp = requests.post(mistral_url, headers=headers, json=data, timeout=30)
                resp.raise_for_status()
                result = resp.json()
                ai_output = result["choices"][0]["message"]["content"].strip()

                _last_ai_source = "Mistral"

                # Parse AI output
                main_title = ""
                tagline = ""
                subtitle = ""

                for line in ai_output.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('main title:'):
                        main_title = line.split(':', 1)[1].strip()[:80]
                    elif line.lower().startswith('tagline:'):
                        tagline = line.split(':', 1)[1].strip()[:100]
                    elif line.lower().startswith('subtitle:'):
                        subtitle = line.split(':', 1)[1].strip()[:100]

                # Fallback if parsing failed
                if not main_title:
                    lines = [l.strip() for l in ai_output.split('\n') if l.strip()]
                    main_title = lines[0][:80] if len(lines) > 0 else "Professional Presentation"
                    tagline = lines[1][:100] if len(lines) > 1 else "Key Insights and Analysis"
                    subtitle = lines[2][:100] if len(lines) > 2 else "Comprehensive Overview"

                return {
                    'main_title': main_title or "Professional Presentation",
                    'tagline': tagline or "Key Insights and Analysis",
                    'subtitle': subtitle or "Comprehensive Overview",
                    'success': True,
                    'ai_source': 'Mistral'
                }

            except Exception as e:
                print(f"[DEBUG] Mistral title generation failed: {str(e)}")

        # Fallback: Generate basic title from content
        # Extract first meaningful line as title
        lines = [l.strip() for l in content.split('\n') if l.strip() and len(l.strip()) > 10]
        if lines:
            main_title = lines[0][:80]
        else:
            main_title = "Professional Presentation"

        return {
            'main_title': main_title,
            'tagline': "Key Insights and Analysis",
            'subtitle': "Comprehensive Overview",
            'success': False,
            'error': "AI title generation not available, using fallback",
            'ai_source': 'Fallback'
        }

    # ───────────────────────────────────────────────────────────────────────────
    # 🎨 PPTXGENJS CODE GENERATION (AI generates JavaScript slide code)
    # ───────────────────────────────────────────────────────────────────────────

    THEME_COLORS = {
        "dark": {
            "BG": "0D1B2A", "CARD": "1B2E42", "CARD_ALT": "223A52",
            "TITLE": "FFFFFF", "BODY": "B0BEC5", "ACCENT": "E84545",
            "TEAL": "00BCD4", "GOLD": "FFD166", "MUTED": "8D99AE",
        },
        "light": {
            "BG": "FFFFFF", "CARD": "E8EAF6", "CARD_ALT": "DCE1F0",
            "TITLE": "1A1A2E", "BODY": "37474F", "ACCENT": "E84545",
            "TEAL": "0277BD", "GOLD": "F5A623", "MUTED": "757575",
        },
        "modern": {
            "BG": "F5F7FA", "CARD": "FFFFFF", "CARD_ALT": "EBF0F7",
            "TITLE": "1C3557", "BODY": "2D3E50", "ACCENT": "1565C0",
            "TEAL": "0097A7", "GOLD": "F57C00", "MUTED": "78909C",
        },
        "corporate": {
            "BG": "EEF2F7", "CARD": "FFFFFF", "CARD_ALT": "D6E4F0",
            "TITLE": "0A2342", "BODY": "1C3557", "ACCENT": "0057A8",
            "TEAL": "0096C7", "GOLD": "E8A020", "MUTED": "607D8B",
        },
        "nature": {
            "BG": "F1F8F1", "CARD": "FFFFFF", "CARD_ALT": "D8EDD8",
            "TITLE": "1B4332", "BODY": "2D6A4F", "ACCENT": "2D6A4F",
            "TEAL": "40916C", "GOLD": "F4A261", "MUTED": "74A57F",
        },
        "bold": {
            "BG": "1A1A1A", "CARD": "2D2D2D", "CARD_ALT": "3A3A3A",
            "TITLE": "FFFFFF", "BODY": "E0E0E0", "ACCENT": "FF3333",
            "TEAL": "FF9800", "GOLD": "FFD700", "MUTED": "9E9E9E",
        },
        "purple": {
            "BG": "F3F0FF", "CARD": "FFFFFF", "CARD_ALT": "E8E0FF",
            "TITLE": "2D0057", "BODY": "4A0080", "ACCENT": "7B2FBE",
            "TEAL": "9C27B0", "GOLD": "FF9800", "MUTED": "9575CD",
        },
    }

    def generate_pptxgenjs_code(
        self,
        topic: str,
        theme: str = "dark",
        web_context: str = "",
        language: str = "English",
        error_context: str = "",
        num_slides: int = 10,
        logo_data: str = None,
        company_name: str = "",
        brand_accent: str = "",
    ) -> Dict:
        """Generate PptxGenJS JavaScript code for a presentation."""
        global _last_ai_source

        colors = self.THEME_COLORS.get(theme, self.THEME_COLORS["dark"])
        color_block = "\n".join(f"  {k}: \"{v}\"" for k, v in colors.items())

        web_section = ""
        if web_context:
            web_section = f"USE THIS RESEARCH for accurate, topic-specific content:\n{web_context}\n\n"

        error_section = ""
        if error_context:
            error_section = f"\n\nPREVIOUS ATTEMPT FAILED WITH ERROR:\n{error_context}\nFix the error and generate correct code.\n"

        logo_section = ""
        if logo_data:
            logo_section = f'\nLOGO: Add logo to top-right of every slide (including title and thank you) using:\nslide.addImage({{data: "{logo_data}", x: 11.8, y: 0.2, w: 1.3, h: 0.5}});\n'

        # Override accent color if custom brand color provided
        if brand_accent and len(brand_accent) == 6:
            accent = brand_accent
            teal   = brand_accent  # use same brand color for teal too

        company_section = ""
        if company_name:
            company_section = f'\nBRANDING: Add company name "{company_name}" as a small footer on every slide (bottom-left) using:\nslide.addText("{company_name}",{{x:0.3,y:7.1,w:4,h:0.3,fontSize:8,color:"{colors["MUTED"]}",fontFace:"Calibri",align:"left"}});\n'

        bg = colors["BG"]
        card = colors["CARD"]
        card_alt = colors["CARD_ALT"]
        title_c = colors["TITLE"]
        body_c = colors["BODY"]
        accent = colors["ACCENT"]
        teal = colors["TEAL"]
        gold = colors["GOLD"]
        muted = colors["MUTED"]

        # Build dynamic slide structure based on num_slides
        content_slides = num_slides - 2  # exclude title + thank you
        all_topics = [
            "Overview (4-BOX): 4 key aspects",
            "Background/History (2-COL): Historical context and origin",
            "Key Topic A (4-BOX): Main aspect details",
            "Key Topic B (2-COL): Another major aspect",
            "Timeline (2-COL): Key events and dates",
            "Statistics/Facts (TABLE): Key data in a comparison table",
            "Challenges (4-BOX): Problems and challenges",
            "Solutions/Strategies (2-COL): How to address challenges",
            "Case Studies (4-BOX): Real examples",
            "Impact/Results (2-COL): Outcomes and achievements",
            "Future Trends (2-COL): What lies ahead",
            "Key Players (4-BOX): Important people or organizations",
            "Technology/Tools (2-COL): Tools and methods used",
            "Recommendations (4-BOX): Suggested actions",
            "Global Perspective (2-COL): International view",
            "Conclusion (2-COL): Summary and final thoughts",
            "Best Practices (4-BOX): Proven approaches",
            "Resources (2-COL): Further reading and references",
        ]
        selected = all_topics[:content_slides]
        slide_structure = "\n".join(
            f"{i+2}. {t} of \"{topic}\"" for i, t in enumerate(selected)
        )

        prompt = f"""{web_section}Generate PptxGenJS JavaScript code for a {num_slides}-slide presentation on: "{topic}"

CRITICAL: Every card, text box, and bullet MUST contain REAL, SPECIFIC content about "{topic}".
DO NOT use placeholder text like "Body text.", "Key point here", "Description", or "Lorem ipsum".
Write actual meaningful sentences about the topic in {language}.

The code receives a `pptx` object (LAYOUT_WIDE 13.33x7.5 inches). Do NOT use require(). Do NOT call writeFile().
CRITICAL: Do NOT declare `const pptx`, `let pptx`, or `var pptx`. The pptx variable is already provided. Use it directly.
CRITICAL: EVERY slide MUST start with: let slide1 = pptx.addSlide(); (use slide1, slide2, slide3... for each slide)
NEVER call pptx.addShape() or pptx.addText() directly. ALWAYS call it on the slide variable: slide1.addShape(), slide1.addText()
NEVER chain: pptx.addSlide().addShape() — ALWAYS assign to a variable first: let slide1 = pptx.addSlide(); then slide1.addShape()
Language: {language}

Colors: BG="{bg}", Card="{card}", Title="{title_c}", Body="{body_c}", Accent="{accent}", Teal="{teal}", Gold="{gold}"

NO EMOJIS anywhere. No emoji icons in any text, titles, or bullets.

EVERY slide must start with these two shapes:
1. Full background: slide.addShape(pptx.shapes.RECTANGLE,{{x:0,y:0,w:13.33,h:7.5,fill:{{color:"{bg}"}},line:{{type:"none"}}}});
2. Accent bar: slide.addShape(pptx.shapes.RECTANGLE,{{x:0,y:0,w:13.33,h:0.15,fill:{{color:"{accent}"}},line:{{type:"none"}}}});

MANDATORY: Every content slide (2-9) MUST have a REAL SLIDE TITLE (not placeholder text) as the first text:
Example for slide about "Overview": slide.addText("Overview of {topic}",{{x:0.5,y:0.25,w:12,h:0.7,fontSize:24,fontFace:"Calibri",color:"{title_c}",bold:true}});
NEVER write "Slide Title Here" — always write the REAL topic-specific title.

--- LAYOUT RULES ---

4-BOX LAYOUT (slides 2, 4, 8): 2x2 grid of 4 boxes. Each box: bold heading + 4 bullet points at 13pt.
Box positions: top-left(0.4,1.1,6.1,2.8) top-right(7.0,1.1,6.1,2.8) bot-left(0.4,4.1,6.1,2.8) bot-right(7.0,4.1,6.1,2.8)
slide.addShape(pptx.shapes.ROUNDED_RECTANGLE,{{x:0.4,y:1.1,w:6.1,h:2.8,fill:{{color:"{card}"}},rectRadius:0.08,line:{{color:"{teal}",width:1}}}});
slide.addText([{{text:"Box Heading\\n",options:{{fontSize:13,bold:true,color:"{title_c}",fontFace:"Calibri"}}}},{{text:"- Real bullet 1 about {topic}\\n",options:{{fontSize:13,color:"{body_c}",fontFace:"Calibri"}}}},{{text:"- Real bullet 2 about {topic}\\n",options:{{fontSize:13,color:"{body_c}",fontFace:"Calibri"}}}},{{text:"- Real bullet 3 about {topic}\\n",options:{{fontSize:13,color:"{body_c}",fontFace:"Calibri"}}}},{{text:"- Real bullet 4 about {topic}",options:{{fontSize:13,color:"{body_c}",fontFace:"Calibri"}}}}],{{x:0.5,y:1.15,w:5.9,h:2.65,fontFace:"Calibri",valign:"top",shrinkText:true}});
(repeat for all 4 box positions)

2-COLUMN LAYOUT (slides 3, 5, 6, 7, 9): 2 columns. Each column: bold heading + 8 bullet points at 13pt.
Column positions: left(0.4,1.1,6.1,5.8) right(7.0,1.1,6.1,5.8)
slide.addShape(pptx.shapes.ROUNDED_RECTANGLE,{{x:0.4,y:1.1,w:6.1,h:5.8,fill:{{color:"{card}"}},rectRadius:0.08,line:{{color:"{teal}",width:1}}}});
slide.addText([{{text:"Left Heading\\n",options:{{fontSize:13,bold:true,color:"{title_c}",fontFace:"Calibri"}}}},{{text:"- Point 1\\n",options:{{fontSize:13,color:"{body_c}",fontFace:"Calibri"}}}},{{text:"- Point 2\\n",options:{{fontSize:13,color:"{body_c}",fontFace:"Calibri"}}}},{{text:"- Point 3\\n",options:{{fontSize:13,color:"{body_c}",fontFace:"Calibri"}}}},{{text:"- Point 4\\n",options:{{fontSize:13,color:"{body_c}",fontFace:"Calibri"}}}},{{text:"- Point 5\\n",options:{{fontSize:13,color:"{body_c}",fontFace:"Calibri"}}}},{{text:"- Point 6\\n",options:{{fontSize:13,color:"{body_c}",fontFace:"Calibri"}}}},{{text:"- Point 7\\n",options:{{fontSize:13,color:"{body_c}",fontFace:"Calibri"}}}},{{text:"- Point 8",options:{{fontSize:13,color:"{body_c}",fontFace:"Calibri"}}}}],{{x:0.5,y:1.15,w:5.9,h:5.65,fontFace:"Calibri",valign:"top",shrinkText:true}});
(repeat with x:7.0 for right column)

TABLE LAYOUT (for statistics/comparison slides): A slide with a data table.
slide.addTable([
  [{{text:"Header1",options:{{bold:true,color:"{title_c}",fill:"{accent}",fontSize:13,fontFace:"Calibri"}}}},{{text:"Header2",options:{{bold:true,color:"{title_c}",fill:"{accent}",fontSize:13,fontFace:"Calibri"}}}},{{text:"Header3",options:{{bold:true,color:"{title_c}",fill:"{accent}",fontSize:13,fontFace:"Calibri"}}}}],
  [{{text:"Row1Col1",options:{{color:"{body_c}",fill:"{card}",fontSize:12,fontFace:"Calibri"}}}},{{text:"Row1Col2",options:{{color:"{body_c}",fill:"{card}",fontSize:12,fontFace:"Calibri"}}}},{{text:"Row1Col3",options:{{color:"{body_c}",fill:"{card}",fontSize:12,fontFace:"Calibri"}}}}],
  [{{text:"Row2Col1",options:{{color:"{body_c}",fill:"{card_alt}",fontSize:12,fontFace:"Calibri"}}}},{{text:"Row2Col2",options:{{color:"{body_c}",fill:"{card_alt}",fontSize:12,fontFace:"Calibri"}}}},{{text:"Row2Col3",options:{{color:"{body_c}",fill:"{card_alt}",fontSize:12,fontFace:"Calibri"}}}}],
],{{x:0.5,y:1.1,w:12.3,h:5.8,rowH:0.45,fontSize:12}});

Slide structure ({num_slides} slides total):
1. TITLE SLIDE: Title at top-center, subtitle below it. Use this exact layout:
   slide1.addText("Real Title About {topic}",{{x:0.5,y:1.2,w:12.3,h:1.5,fontSize:40,bold:true,color:"{title_c}",fontFace:"Calibri",align:"center"}});
   slide1.addText("Real subtitle or tagline about {topic}",{{x:0.5,y:2.9,w:12.3,h:0.8,fontSize:22,color:"{body_c}",fontFace:"Calibri",align:"center"}});
{slide_structure}
{num_slides}. THANK YOU SLIDE (slide{num_slides}): "Thank You" at top-center, "Any Questions?" below it:
    slide{num_slides}.addText("Thank You",{{x:0.5,y:1.5,w:12.3,h:1.5,fontSize:48,bold:true,color:"{title_c}",fontFace:"Calibri",align:"center"}});
    slide{num_slides}.addText("Any Questions?",{{x:0.5,y:3.2,w:12.3,h:0.8,fontSize:28,color:"{gold}",fontFace:"Calibri",align:"center"}});

IMPORTANT: Generate EXACTLY {num_slides} slides. No more, no less.
REMEMBER: NO emojis. All text in {language}. Real specific content about "{topic}". Complete sentences in bullets.

SPEAKER NOTES: After every slide's content, add speaker notes using addNotes(). Write 2-3 meaningful sentences a presenter would say for that slide.
Example: slide1.addNotes("Welcome everyone. Today we will explore {topic} in detail covering key aspects, history, challenges and future outlook.");
{logo_section}{company_section}{error_section}
Output ONLY JavaScript code. No markdown, no backticks, no explanations."""

        import requests, re as _re

        system_msg = "You are a PptxGenJS code generator. Output ONLY valid JavaScript code that adds slides to a pptx object. No markdown, no explanations, no backticks."

        def _clean_output(text):
            text = _re.sub(r'^```(?:javascript|js)?\s*\n?', '', text)
            text = _re.sub(r'\n?```\s*$', '', text)
            return text.strip()

        def _is_truncated(text):
            last = text.rstrip().split('\n')[-1].strip() if text.strip() else ''
            return bool(last) and not last.endswith((';', '}', '//', '*/'))

        apis = [
            {
                "name": "Mistral",
                "url": "https://api.mistral.ai/v1/chat/completions",
                "key": get_secret("MISTRAL_API_KEY"),
                "model": "mistral-small-latest",
                "max_tokens": 16000,
            },
            {
                "name": "Groq",
                "url": "https://api.groq.com/openai/v1/chat/completions",
                "key": get_secret("GROQ_API_KEY"),
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 16000,
            },
        ]

        last_error = "All AI providers failed."
        for api in apis:
            if not api["key"]:
                continue
            try:
                resp = requests.post(
                    api["url"],
                    headers={"Authorization": f"Bearer {api['key']}", "Content-Type": "application/json"},
                    json={
                        "model": api["model"],
                        "messages": [
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": prompt},
                        ],
                        "max_tokens": api["max_tokens"],
                        "temperature": 0.3,
                    },
                    timeout=90,
                )
                resp.raise_for_status()
                ai_output = resp.json()["choices"][0]["message"]["content"].strip()
                ai_output = _clean_output(ai_output)
                if not ai_output:
                    last_error = f"{api['name']}: empty response"
                    continue
                if _is_truncated(ai_output):
                    last_error = f"{api['name']}: output truncated"
                    continue
                _last_ai_source = api["name"]
                return {"output": ai_output, "ai_source": api["name"]}
            except Exception as e:
                last_error = f"{api['name']}: {str(e)}"
                continue

        return {"error": f"PptxGenJS generation failed: {last_error}"}
