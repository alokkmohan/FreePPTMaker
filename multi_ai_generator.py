
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
        # Try Ollama first (local, free, offline)
        try:
            print("[AI] Trying Ollama (local)...")
            return self._ollama_generate(topic, min_slides, max_slides, style, audience, custom_instructions)
        except Exception as ollama_error:
            print(f"[AI] Ollama failed: {ollama_error}")

            # Fallback to Groq (cloud)
            if not self.groq_key:
                raise Exception("Ollama not available and Groq API key not found. Set GROQ_API_KEY in Streamlit Secrets (cloud) or .env file (local)")

            print("[AI] Using Groq API (cloud fallback)...")
            return self._groq_generate(topic, min_slides, max_slides, style, audience, custom_instructions)

    def _ollama_generate(self, topic, min_slides, max_slides, style, audience, custom_instructions):
        """Generate using Ollama local API (qwen2.5 model)"""
        import requests

        # Check if Ollama is running
        try:
            health = requests.get("http://localhost:11434/", timeout=2)
            if health.status_code != 200:
                raise Exception("Ollama not running")
        except Exception:
            raise Exception("Ollama not running or not accessible")

        print("[AI] Ollama is running, generating content...")

        # Strict prompt for consistent output
        prompt = f"""You are an expert presentation designer. Create a PowerPoint presentation.

TOPIC: {topic}

REQUIREMENTS:
- Create exactly {min_slides} to {max_slides} slides
- Style: Professional {style}
- Audience: {audience}
{f"- Additional: {custom_instructions}" if custom_instructions else ""}

RULES:
- Each slide must have a clear title (5-8 words max)
- Each slide must have 4-5 bullet points
- Each bullet point should be a complete sentence (15-30 words)
- Never break words with spaces
- Be specific with facts and examples
- No emojis, no markdown formatting

OUTPUT FORMAT (JSON only):
{{"title": "Main Title", "subtitle": "Subtitle", "slides": [{{"title": "Slide Title", "content": ["Bullet point 1.", "Bullet point 2.", "Bullet point 3.", "Bullet point 4."], "speaker_notes": "Notes for speaker"}}]}}

Return ONLY valid JSON. No markdown code blocks. No explanations."""

        ollama_model = "qwen2.5"
        response = requests.post(
            "http://localhost:11434/api/generate",
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
            prompt = f"""You are an expert presentation designer creating a HIGH-QUALITY PowerPoint presentation.

**TOPIC:** {topic}

**STRICT REQUIREMENTS:**
1. Create exactly {min_slides} to {max_slides} slides
2. Style: Professional {style}
3. Audience: {audience}
{f"4. Additional: {custom_instructions}" if custom_instructions else ""}

**QUALITY RULES - VERY IMPORTANT:**
- NEVER break words across spaces (write "Consultant" not "Consult ant")
- NEVER truncate sentences mid-word
- Each bullet point MUST be a complete, grammatically correct sentence
- Each bullet should be 15-30 words (not too short, not too long)
- Use proper capitalization and punctuation
- Avoid filler words and generic statements
- Be specific with facts, numbers, and examples
- Each slide title should be clear and descriptive (5-8 words max)

**SLIDE STRUCTURE:**
- Slide 1: Title slide with compelling subtitle
- Slides 2-{max_slides-1}: Content slides with 4-5 bullet points each
- Last slide: Conclusion/Summary

**OUTPUT FORMAT (JSON only, no markdown):**
{{"title": "Main Title", "subtitle": "Engaging Subtitle", "slides": [{{"title": "Clear Slide Title", "content": ["Complete sentence as bullet point 1.", "Complete sentence as bullet point 2.", "Complete sentence as bullet point 3.", "Complete sentence as bullet point 4."], "speaker_notes": "Detailed notes for speaker"}}]}}

Return ONLY valid JSON. No markdown code blocks. No explanations."""

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
