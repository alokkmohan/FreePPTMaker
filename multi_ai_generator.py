
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
        custom_instructions: str = ""
    ) -> Dict:
        """
        Generate PPT structure.
        Priority: Ollama (local) -> Groq (cloud fallback)
        """
        global _last_ai_source

        # Try Ollama first (local, free, offline)
        try:
            print("[AI] Trying Ollama (local)...")
            result = self._ollama_generate(topic, min_slides, max_slides, style, audience, custom_instructions)
            _last_ai_source = "Ollama (Local)"
            return result
        except Exception as ollama_error:
            print(f"[AI] Ollama failed: {ollama_error}")

            # Fallback to Groq (cloud)
            if not self.groq_key:
                raise Exception("Ollama not available and Groq API key not found. Set GROQ_API_KEY in Streamlit Secrets (cloud) or .env file (local)")

            print("[AI] Using Groq API (cloud fallback)...")
            result = self._groq_generate(topic, min_slides, max_slides, style, audience, custom_instructions)
            _last_ai_source = "Groq Cloud (Llama 3.3)"
            return result

    def _ollama_generate(self, topic, min_slides, max_slides, style, audience, custom_instructions):
        """Generate using Ollama API (local or remote via ngrok)"""
        import requests

        # Get Ollama URL (local or remote)
        ollama_url = get_ollama_url()
        print(f"[AI] Checking Ollama at: {ollama_url}")

        # Check if Ollama is running
        try:
            health = requests.get(f"{ollama_url}/", timeout=5)
            if health.status_code != 200:
                raise Exception(f"Ollama not running at {ollama_url}")
        except Exception as e:
            raise Exception(f"Ollama not accessible at {ollama_url}: {str(e)}")

        print(f"[AI] Ollama is running at {ollama_url}, generating content...")

        # Improved prompt for better content quality
        prompt = f"""You are an expert presentation designer creating a professional PowerPoint.

TOPIC: {topic}

CREATE A PRESENTATION WITH THIS EXACT STRUCTURE:
1. TITLE SLIDE: Main title and engaging subtitle
2. INTRODUCTION: What is this topic and why it matters
3. KEY CONCEPTS: Core ideas and definitions (3-4 slides)
4. BENEFITS/ADVANTAGES: Why this is important
5. CHALLENGES/CONSIDERATIONS: What to watch out for
6. REAL EXAMPLES: Practical applications or case studies
7. FUTURE OUTLOOK: What's next in this field
8. CONCLUSION: Summary and key takeaways

STRICT REQUIREMENTS:
- Create exactly {min_slides} to {max_slides} slides
- Style: Professional {style}
- Audience: {audience}
{f"- Additional: {custom_instructions}" if custom_instructions else ""}

CRITICAL RULES:
- EVERY slide MUST have a UNIQUE, SPECIFIC title (NOT generic like "Overview" or "Introduction")
- Title examples: "AI Revolutionizing Healthcare Diagnosis", "Top 5 Climate Change Impacts", "How Solar Energy Works"
- Each slide: 4-5 bullet points with complete sentences (15-25 words each)
- Include specific facts, statistics, real examples
- Be informative and educational, not generic
- No emojis, no markdown

OUTPUT FORMAT (valid JSON only):
{{"title": "Compelling Main Title", "subtitle": "Engaging Subtitle That Explains Value", "slides": [{{"title": "Unique Specific Slide Title", "content": ["Detailed bullet point with specific information.", "Another informative point with facts or examples.", "Third point explaining a key concept clearly.", "Fourth point with actionable or memorable insight."], "speaker_notes": "Detailed notes for the presenter"}}]}}

Return ONLY valid JSON. No code blocks. No explanations."""

        ollama_model = "qwen2.5"
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": ollama_model,
                "prompt": prompt,
                "options": {"temperature": 0.3},
                "stream": False
            },
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "")

            # Clean JSON from response
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

            # Post-process to fix any issues
            try:
                from text_processor import post_process_ai_response
                parsed = post_process_ai_response(parsed)
                print("[AI] Ollama: Post-processing applied successfully")
            except ImportError:
                print("[WARN] text_processor not available, skipping post-processing")

            return parsed
        else:
            raise Exception(f"Ollama API error: {response.text}")

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
