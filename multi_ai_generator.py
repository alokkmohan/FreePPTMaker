# NOTE: Do NOT make Streamlit UI changes in this file.
# For mobile UI fixes, update app.py only.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multi-AI Content Generator
Support for Ollama (local), Groq (cloud fallback), and other APIs
"""

import os
import json
from typing import Dict, Optional

# Global variable to track which AI was used
_last_ai_source = "Unknown"

def get_last_ai_source():
    """Get which AI was used for last generation"""
    global _last_ai_source
    return _last_ai_source

def get_secret(key):
    """Get secret from Streamlit Cloud or .env file"""
    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            try:
                value = st.secrets.get(key, None)
                if value:
                    return value
            except:
                pass
            # Also try direct access
            try:
                if key in st.secrets:
                    return st.secrets[key]
            except:
                pass
    except:
        pass
    # Fall back to environment variable (for local)
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

class MultiAIGenerator:
    """Generate content using multiple AI providers"""

    def __init__(self, ai_model: str = "auto", api_key: str = None):
        """
        Initialize AI generator
        Priority: Ollama (local) -> Groq (cloud)
        """
        from dotenv import load_dotenv
        load_dotenv()
        self.groq_key = get_secret("GROQ_API_KEY")
        self.deepseek_key = get_secret("DEEPSEEK_API_KEY")
        self.ai_model = ai_model
        self.api_key = api_key

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
        Generate PPT structure using Groq (cloud) or Hugging Face (optional fallback).
        All content rules are dynamic and user-driven.
        """
        global _last_ai_source

        # Build dynamic prompt
        prompt = f"""You are an expert presentation content writer. Generate content for a PowerPoint presentation only.

Rules:
- Number of slides: exactly {min_slides}
- Each slide must have:
  - A clear, specific slide title
  - Exactly {bullets_per_slide} bullet points
  - Each bullet point maximum {bullet_word_limit} words
- Tone: {tone}
- Style: {style}
- Audience: {audience}
{f'- Required phrases/keywords: {required_phrases}' if required_phrases else ''}
{f'- Avoid: {forbidden_content}' if forbidden_content else ''}
{f'- Extra instructions: {custom_instructions}' if custom_instructions else ''}
- No paragraphs
- No emojis
- No markdown
- No generic statements, no filler, no repetition

Output format (strict):
Slide 1 Title:
- Bullet point
- Bullet point

Slide 2 Title:
- Bullet point
- Bullet point

Do not include anything outside this format.

TOPIC: {topic}"

        # Try Groq first
        if self.groq_key:
            try:
                print("[AI] Using Groq API (cloud)...")
                result = self._groq_generate(topic, min_slides, max_slides, style, audience, prompt)
                _last_ai_source = "Groq Cloud (Llama 3.3)"
                return result
            except Exception as groq_error:
                print(f"[AI] Groq failed: {groq_error}")
        # Optionally, try Hugging Face as a fallback
        if hasattr(self, '_huggingface_generate') and self.api_key:
            try:
                print("[AI] Using Hugging Face API (fallback)...")
                result = self._huggingface_generate(topic, min_slides, max_slides, style, audience, prompt)
                _last_ai_source = "Hugging Face API"
                return result
            except Exception as hf_error:
                print(f"[AI] Hugging Face failed: {hf_error}")
        raise Exception("No AI provider available or all failed. Set GROQ_API_KEY or Hugging Face API key.")

    def _groq_generate(self, topic, min_slides, max_slides, style, audience, custom_instructions):
        """Generate using Groq API with improved prompting"""
        print(f"[AI] Using Groq API for content generation...")
        try:
            from groq import Groq

            client = Groq(api_key=self.groq_key)

            # Improved prompt with explicit quality instructions
            prompt = f"""You are an expert presentation designer creating a HIGH-QUALITY PowerPoint.

**TOPIC:** {topic}

**CREATE THIS EXACT STRUCTURE:**
1. TITLE SLIDE: Compelling main title + engaging subtitle
2. INTRODUCTION: What is {topic} and why it matters today
3. KEY CONCEPTS (2-3 slides): Core ideas with specific details
4. BENEFITS/IMPORTANCE: Real-world advantages and impact
5. CHALLENGES: Common issues and how to address them
6. EXAMPLES/CASE STUDIES: Real applications with facts
7. FUTURE TRENDS: What's coming next
8. CONCLUSION: Key takeaways and call to action

**STRICT REQUIREMENTS:**
- Create exactly {min_slides} to {max_slides} slides
- Style: Professional {style}
- Audience: {audience}
{f"- Additional: {custom_instructions}" if custom_instructions else ""}

**CRITICAL QUALITY RULES:**
- EVERY slide title MUST be UNIQUE and SPECIFIC (NOT "Overview", "Introduction", "Details")
- Good titles: "5 Ways AI Transforms Healthcare", "Climate Change Impact on Agriculture"
- Bad titles: "Overview", "Key Points", "Details", "More Information"
- Each bullet: Complete sentence with 15-25 words
- Include specific facts, statistics, percentages, real examples
- NEVER break words with spaces
- Be educational and informative, not generic

**OUTPUT FORMAT (JSON only):**
{{"title": "Compelling Topic Title", "subtitle": "Value-Focused Subtitle", "slides": [{{"title": "Unique Descriptive Slide Title", "content": ["Specific informative bullet with facts.", "Another detailed point with examples.", "Third point explaining key concept.", "Fourth point with actionable insight."], "speaker_notes": "Presenter notes"}}]}}

Return ONLY valid JSON. No markdown. No explanations."""

            message = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional presentation designer. Always output valid JSON only. Never break words with spaces. Write complete sentences."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_tokens=6000
            )

            content = message.choices[0].message.content

            # Clean JSON
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()

            # Find JSON in response
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                content = content[start_idx:end_idx]

            parsed = json.loads(content)

            # Post-process to fix any remaining issues
            try:
                from text_processor import post_process_ai_response
                parsed = post_process_ai_response(parsed)
                print("[AI] Groq: Post-processing applied successfully")
            except ImportError:
                print("[WARN] text_processor not available, skipping post-processing")

            return parsed

        except Exception as e:
            raise Exception(f"Groq generation failed: {str(e)}")


# Convenience function for topic-based generation
def generate_ppt_from_topic_with_ai(
    topic: str,
    style: str = "professional",
    min_slides: int = 10,
    max_slides: int = 20,
    audience: str = "general",
    custom_instructions: str = ""
) -> Dict:
    """
    Generate PPT structure from topic.
    Priority: Ollama (local) -> Groq (cloud fallback)
    """
    generator = MultiAIGenerator()
    return generator.generate_ppt_content(
        topic=topic,
        min_slides=min_slides,
        max_slides=max_slides,
        style=style,
        audience=audience,
        custom_instructions=custom_instructions
    )
