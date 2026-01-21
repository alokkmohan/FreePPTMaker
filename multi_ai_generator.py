#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multi-AI Content Generator
Support for Deepseek, Gemini, Groq, Hugging Face, and Claude APIs
"""

import os
import json
from typing import Dict, Optional

class MultiAIGenerator:
    """Generate content using multiple AI providers"""
    
    def __init__(self, ai_model: str = "ollama", api_key: str = None):
        """
        Initialize AI generator (Ollama only)
        """
        self.ai_model = "ollama"
        self.api_key = None  # Ollama does not require API key
    
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
        Generate PPT structure from topic using Ollama only
        """
        return self._ollama_generate(topic, min_slides, max_slides, style, audience, custom_instructions)
    def _ollama_generate(self, topic, min_slides, max_slides, style, audience, custom_instructions):
        """Generate using Ollama local API"""
        print(f"🤖 Using Ollama local API for content generation...")
        try:
            import requests
            ollama_model = "llama3"
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
        print(f"🤖 Using Deepseek API for content generation...")
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
                headers={"Authorization": f"Bearer {self.api_key}"},
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
        """Generate using Groq API"""
        print(f"🤖 Using Groq API for content generation...")
        try:
            from groq import Groq
            
            client = Groq(api_key=self.api_key)
            
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

            message = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=4000
            )
            
            content = message.choices[0].message.content
            
            # Clean JSON
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()
            
            return json.loads(content)
        
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
