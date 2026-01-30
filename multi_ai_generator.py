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

        prompt = f"""{web_context}You are an expert presentation content writer. Generate a detailed, sectioned, slide-by-slide outline for a PowerPoint presentation.

CRITICAL RULES:
- Number of slides: MINIMUM {min_slides} slides, MAXIMUM {max_slides} slides
- You MUST generate AT LEAST {min_slides} slides covering all important topics
- Each slide should have:
    - Slide number and clear title (e.g., Slide 1: Title Slide)
    - Main Title (if Slide 1)
    - Tagline (if Slide 1)
    - Subtitle (if Slide 1)
    - Presented by (if Slide 1)
    - For other slides: a section title and 4-6 DETAILED bullet points (flexible based on content complexity)

BULLET POINT RULES (VERY IMPORTANT):
- Generate 4-6 bullet points per slide based on how much detail is needed to explain the topic properly
- MINIMUM 4 bullets per slide, MAXIMUM 6 bullets per slide
- If the topic for a slide is simple: use 4 bullets
- If the topic requires more explanation: use 5-6 bullets to cover all important aspects
- Adjust the number of bullets based on content needs - don't force a fixed number
- Each bullet point MUST be a COMPLETE SENTENCE of 20-35 words (1-2 full lines)
- DO NOT write short phrases like "NEP 2020 implementation" - write full explanatory sentences
- Bullet points should be informative paragraphs that explain the concept clearly
- If writing in Hindi: Write complete Hindi sentences with proper grammar, not just keywords
  Example of WRONG Hindi: "शिक्षा नीति 2020"
  Example of CORRECT Hindi: "राष्ट्रीय शिक्षा नीति 2020 भारत की शिक्षा प्रणाली में व्यापक बदलाव लाने के लिए तैयार की गई एक महत्वपूर्ण नीति है जो छात्रों के समग्र विकास पर केंद्रित है।"

- Tone: {tone}
- Style: {style}
- Audience: {audience}
- No emojis, no markdown, no filler, no repetition
- Cover ALL important topics from the provided content

Output format (flexible bullets per slide based on content):
Slide 1: Title Slide
Main Title: ...
Tagline: ...
Subtitle: ...
Presented by: ...

Slide 2: [Section Title]
- A complete sentence explaining the first key point with relevant details and context (20-35 words)
- A complete sentence explaining the second key point with relevant details and context (20-35 words)
- A complete sentence explaining the third key point with relevant details and context (20-35 words)
- A complete sentence explaining the fourth key point with relevant details and context (20-35 words)
- [Optional 5th bullet if needed] A complete sentence with additional important details (20-35 words)
- [Optional 6th bullet if needed] A complete sentence with additional important details (20-35 words)

Slide 3: [Section Title]
- A complete sentence explaining the first key point with relevant details and context (20-35 words)
- A complete sentence explaining the second key point with relevant details and context (20-35 words)
- A complete sentence explaining the third key point with relevant details and context (20-35 words)
- A complete sentence explaining the fourth key point with relevant details and context (20-35 words)
- [Optional 5th bullet if needed] A complete sentence with additional important details (20-35 words)
- [Optional 6th bullet if needed] A complete sentence with additional important details (20-35 words)

(Continue for ALL {min_slides} to {max_slides} slides - DO NOT STOP EARLY)
REMEMBER: Use 4-6 bullets per slide based on content needs. Don't force a fixed number!

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

1. MAIN TITLE (40-80 characters):
   - Should be catchy, professional, and immediately convey the main topic
   - Must capture the essence of the content
   - Style: {style}
   - Language: {language}
   - NO generic words like "Presentation" or "Overview"
   - Make it impactful and memorable

2. TAGLINE (50-100 characters):
   - A compelling subtitle that adds context
   - Should complement the main title
   - Can be descriptive or aspirational
   - Language: {language}

3. SUBTITLE (50-100 characters):
   - Additional context or focus area
   - Can mention the scope, purpose, or key theme
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
