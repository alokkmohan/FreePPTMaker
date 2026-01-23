
# NOTE: Do NOT make Streamlit UI changes in this file.
# For mobile UI fixes, update app.py only.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multi-AI Content Generator
Support for Deepseek, Gemini, Groq, Hugging Face, and Claude APIs
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
        Initialize AI generator (Groq - FREE)
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
        Generate PPT structure using Groq (FREE)
        """
        if not self.groq_key:
            raise Exception("Groq API key not found. Set GROQ_API_KEY in Streamlit Secrets (cloud) or .env file (local)")

        print("[AI] Using Groq API (FREE)...")
        return self._groq_generate(topic, min_slides, max_slides, style, audience, custom_instructions)
    def _ollama_generate(self, topic, min_slides, max_slides, style, audience, custom_instructions):
        """Generate using Ollama local API"""
        print(f"[AI] Using Ollama local API for content generation...")
        try:
            import requests
            ollama_model = "mistral"
            prompt = f"""You are an expert presentation designer. Create a professional PowerPoint presentation structure for this topic:

**TOPIC:** {topic}

**REQUIREMENTS:**
- {min_slides} to {max_slides} slides
- Professional {style} style
- For {audience} audience
- Include specific data and examples
{f'- Custom: {custom_instructions}' if custom_instructions else ''}

**OUTPUT:**
Return valid JSON with:
{{'title': '...', 'subtitle': '...', 'slides': [{{'title': '...', 'content': ['...', '...'], 'speaker_notes': '...'}}]}}

Return ONLY JSON, no markdown."""
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": ollama_model,
                    "prompt": prompt,
                    "options": {"temperature": 0.7},
                    "stream": False
                }
            )
            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "")
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
                return json.loads(content)
            else:
                raise Exception(f"Ollama API error: {response.text}")
        except Exception as e:
            raise Exception(f"Ollama generation failed: {str(e)}")
    
    def _claude_generate(self, topic, min_slides, max_slides, style, audience, custom_instructions):
        """Generate using Claude API"""
        from claude_ppt_generator import create_ppt_from_topic
        
        # Use existing Claude implementation
        print(f"🤖 Using Claude API for content generation...")
        # Note: create_ppt_from_topic expects topic and returns PPT structure
        # We'll create a temporary function to get just the structure
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            content_prompt = f"""You are an expert researcher and content writer. Create comprehensive, factual content on the following topic for a presentation:

**TOPIC:** {topic}

**REQUIREMENTS:**
- Length: Sufficient for {min_slides} to {max_slides} presentation slides
- Include specific facts, statistics, real data
- Provide concrete examples and case studies
- Use authoritative, professional tone
{f"- Additional Requirements: {custom_instructions}" if custom_instructions else ""}

**OUTPUT FORMAT:**
Return a structured presentation outline with:
1. Title
2. Subtitle
3. Array of slides, each with:
   - title
   - content (array of bullet points)
   - speaker_notes

Return as JSON only."""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": content_prompt}]
            )
            
            response_text = message.content[0].text.strip()
            
            # Clean and parse JSON
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
        
        except Exception as e:
            raise Exception(f"Claude generation failed: {str(e)}")
    
    def _deepseek_generate(self, topic, min_slides, max_slides, style, audience, custom_instructions):
        """Generate using Deepseek API"""
        print(f"[AI] Using Deepseek API for content generation...")
        try:
            import requests
            
            prompt = f"""You are an expert presentation designer. Create a professional PowerPoint presentation structure for this topic:

**TOPIC:** {topic}

**REQUIREMENTS:**
- {min_slides} to {max_slides} slides
- Professional {style} style
- For {audience} audience
- Include specific data and examples
{f"- Custom: {custom_instructions}" if custom_instructions else ""}

**OUTPUT:**
Return valid JSON with:
{{"title": "...", "subtitle": "...", "slides": [{{"title": "...", "content": ["...", "..."], "speaker_notes": "..."}}]}}

Return ONLY JSON, no markdown."""

            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {self.deepseek_key}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 4000
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Clean JSON
                if content.startswith("```json"):
                    content = content.split("```json")[1].split("```")[0].strip()
                elif content.startswith("```"):
                    content = content.split("```")[1].split("```")[0].strip()
                
                return json.loads(content)
            else:
                raise Exception(f"Deepseek API error: {response.text}")
        
        except Exception as e:
            raise Exception(f"Deepseek generation failed: {str(e)}")
    
    def _gemini_generate(self, topic, min_slides, max_slides, style, audience, custom_instructions):
        """Generate using Google Gemini API"""
        print(f"🤖 Using Google Gemini API for content generation...")
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-pro")
            
            prompt = f"""You are an expert presentation designer. Create a professional PowerPoint presentation structure for this topic:

**TOPIC:** {topic}

**REQUIREMENTS:**
- {min_slides} to {max_slides} slides
- Professional {style} style
- For {audience} audience
- Include specific data and examples
{f"- Custom: {custom_instructions}" if custom_instructions else ""}

**OUTPUT:**
Return valid JSON with:
{{"title": "...", "subtitle": "...", "slides": [{{"title": "...", "content": ["...", "..."], "speaker_notes": "..."}}]}}

Return ONLY JSON, no markdown."""

            response = model.generate_content(prompt)
            content = response.text
            
            # Clean JSON
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()
            
            return json.loads(content)
        
        except Exception as e:
            raise Exception(f"Gemini generation failed: {str(e)}")
    
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
                print("[AI] Post-processing applied successfully")
            except ImportError:
                print("[WARN] text_processor not available, skipping post-processing")

            return parsed

        except Exception as e:
            raise Exception(f"Groq generation failed: {str(e)}")
    
    def _huggingface_generate(self, topic, min_slides, max_slides, style, audience, custom_instructions):
        """Generate using Hugging Face Inference API"""
        print(f"🤖 Using Hugging Face API for content generation...")
        try:
            import requests
            
            prompt = f"""You are an expert presentation designer. Create a professional PowerPoint presentation structure for this topic:

**TOPIC:** {topic}

**REQUIREMENTS:**
- {min_slides} to {max_slides} slides
- Professional {style} style
- For {audience} audience
{f"- Custom: {custom_instructions}" if custom_instructions else ""}

**OUTPUT (JSON ONLY):**
{{"title": "...", "subtitle": "...", "slides": [{{"title": "...", "content": ["...", "..."], "speaker_notes": "..."}}]}}"""

            response = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"inputs": prompt, "parameters": {"max_length": 4000, "temperature": 0.7}}
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result[0]["generated_text"] if isinstance(result, list) else result.get("generated_text", "")
                
                # Clean JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                # Find JSON in response
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                if start_idx != -1 and end_idx > start_idx:
                    content = content[start_idx:end_idx]
                
                return json.loads(content)
            else:
                raise Exception(f"Hugging Face API error: {response.text}")
        
        except Exception as e:
            raise Exception(f"Hugging Face generation failed: {str(e)}")


# Convenience function for topic-based generation with Ollama only
def generate_ppt_from_topic_with_ai(
    topic: str,
    style: str = "professional",
    min_slides: int = 10,
    max_slides: int = 20,
    audience: str = "general",
    custom_instructions: str = ""
) -> Dict:
    """
    Generate PPT structure from topic using Ollama only
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
