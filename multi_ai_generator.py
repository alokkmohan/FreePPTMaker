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
    """Get secret from environment variable or .env file"""
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
        
        mistral_api_key = get_secret("MISTRAL_API_KEY") or "sXgAOYTxA51tQ0N1C4O5ppFnELJisujD"
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
        mistral_api_key = get_secret("MISTRAL_API_KEY") or "sXgAOYTxA51tQ0N1C4O5ppFnELJisujD"
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
            "BG": "0D1B2A",
            "CARD": "1B2E42",
            "CARD_ALT": "223A52",
            "TITLE": "FFFFFF",
            "BODY": "B0BEC5",
            "ACCENT": "E84545",
            "TEAL": "00BCD4",
            "GOLD": "FFD166",
            "MUTED": "8D99AE",
        },
        "light": {
            "BG": "FFFFFF",
            "CARD": "E8EAF6",
            "CARD_ALT": "DCE1F0",
            "TITLE": "1A1A2E",
            "BODY": "37474F",
            "ACCENT": "E84545",
            "TEAL": "0277BD",
            "GOLD": "F5A623",
            "MUTED": "757575",
        },
    }

    def generate_pptxgenjs_code(
        self,
        topic: str,
        theme: str = "dark",
        web_context: str = "",
        language: str = "English",
        error_context: str = "",
    ) -> Dict:
        """Generate PptxGenJS JavaScript code for a 10-slide presentation."""
        global _last_ai_source

        colors = self.THEME_COLORS.get(theme, self.THEME_COLORS["dark"])
        color_block = "\n".join(f"  {k}: \"{v}\"" for k, v in colors.items())

        web_section = ""
        if web_context:
            web_section = f"USE THIS RESEARCH for accurate, topic-specific content:\n{web_context}\n\n"

        error_section = ""
        if error_context:
            error_section = f"\n\nPREVIOUS ATTEMPT FAILED WITH ERROR:\n{error_context}\nFix the error and generate correct code.\n"

        bg = colors["BG"]
        card = colors["CARD"]
        card_alt = colors["CARD_ALT"]
        title_c = colors["TITLE"]
        body_c = colors["BODY"]
        accent = colors["ACCENT"]
        teal = colors["TEAL"]
        gold = colors["GOLD"]
        muted = colors["MUTED"]

        prompt = f"""{web_section}Generate PptxGenJS code for 10 slides about: {topic}

The code receives `pptx` object (LAYOUT_WIDE). Do NOT use require(). Do NOT call writeFile().
Language: {language}

Colors: BG="{bg}", Card="{card}", Title="{title_c}", Body="{body_c}", Accent="{accent}", Teal="{teal}", Gold="{gold}"

Every slide: slide.background={{fill:"{bg}"}}; + red bar: slide.addShape(pptx.shapes.RECTANGLE,{{x:0,y:0,w:"100%",h:0.15,fill:{{color:"{accent}"}}}});
Title: slide.addText("Title",{{x:0.5,y:0.25,w:12,h:0.7,fontSize:24,fontFace:"Arial",color:"{title_c}",bold:true}});
Card: slide.addShape(pptx.shapes.ROUNDED_RECTANGLE,{{x:X,y:Y,w:W,h:H,fill:{{color:"{card}"}},rectRadius:0.1,line:{{color:"{teal}",width:1}}}});
Card text: slide.addText([{{text:"Icon Title\\n",options:{{fontSize:13,bold:true,color:"{title_c}"}}}},{{text:"Body text.",options:{{fontSize:11,color:"{body_c}"}}}}],{{x:X+0.15,y:Y+0.1,w:W-0.3,h:H-0.2,fontFace:"Calibri",valign:"top"}});

10 slides: 1.Title(fontSize40,centered) 2.Overview(4 cards 2x2) 3.Background(two-column) 4.TopicA(cards) 5.TopicB(two-col) 6.Timeline(circles+lines) 7.Stats(big numbers) 8.Challenges(cards) 9.Future(two-col) 10.ThankYou

Card grid positions: (0.4,1.2,5.8,2.5),(6.7,1.2,5.8,2.5),(0.4,4.0,5.8,2.5),(6.7,4.0,5.8,2.5)
Two-col: left(0.4,1.2,5.8,5.5) right(6.7,1.2,5.8,5.5)
Use emoji in card titles. No images. Card body max 12 words. Title max 35 chars.
{error_section}
Output ONLY JavaScript code. No markdown, no backticks."""

        mistral_api_key = get_secret("MISTRAL_API_KEY") or "sXgAOYTxA51tQ0N1C4O5ppFnELJisujD"
        if not mistral_api_key:
            return {"error": "No Mistral API key found."}

        try:
            import requests
            resp = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {mistral_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "mistral-large-latest",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a PptxGenJS code generator. Output ONLY valid JavaScript code that adds slides to a pptx object. No markdown, no explanations, no backticks.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 10000,
                    "temperature": 0.4,
                },
                timeout=120,
            )
            resp.raise_for_status()
            ai_output = resp.json()["choices"][0]["message"]["content"].strip()
            _last_ai_source = "Mistral"

            # Strip markdown fences if AI added them
            import re
            ai_output = re.sub(r'^```(?:javascript|js)?\s*\n?', '', ai_output)
            ai_output = re.sub(r'\n?```\s*$', '', ai_output)

            return {"output": ai_output, "ai_source": "Mistral"}
        except Exception as e:
            return {"error": f"PptxGenJS code generation failed: {str(e)}"}
