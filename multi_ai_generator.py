# Function to get the last AI source used
def get_last_ai_source() -> str:
    """Return the last AI source used."""
    global _last_ai_source
    return _last_ai_source
"""
Multi-AI Content Generator
Support for Ollama (local), Groq (cloud fallback), and other APIs
"""

import os
import json
from typing import Dict, Optional

# Global variable to track which AI was used
_last_ai_source = "Unknown"

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

class MultiAIGenerator:
    """Generate content using multiple AI providers"""

    def __init__(self, ai_model: str = "auto", api_key: str = None):
        """
        Initialize AI generator
        Priority: Ollama (local) -> Groq (cloud)
        """
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
        # Debug: print the context being passed
        if custom_instructions:
            print("\n[DEBUG] Web Research Context passed to AI:\n" + custom_instructions + "\n")

        # Build dynamic prompt
        web_context = f"WEB RESEARCH CONTEXT (use this information to generate unique, topic-specific slide content):\n{custom_instructions}\n\n" if custom_instructions else ""

        prompt = f"""{web_context}You are an expert presentation content writer. Generate a detailed, sectioned, slide-by-slide outline for a PowerPoint presentation.

Rules:
- Number of slides: {min_slides} to {max_slides}
- Each slide should have:
    - Slide number and clear title (e.g., Slide 1: Title Slide)
    - Main Title (if Slide 1)
    - Tagline (if Slide 1)
    - Subtitle (if Slide 1)
    - Presented by (if Slide 1)
    - For other slides: a section title and 4-6 detailed, topic-specific bullet points (not generic)
- Use the latest, most relevant data and sources
- Tone: {tone}
- Style: {style}
- Audience: {audience}
- No emojis, no markdown, no filler, no repetition
- Do NOT use any static outline or pre-filled structure. Every slide must be specific to the topic.

Output format (strict):
Slide 1: Title Slide
Main Title: ...
Tagline: ...
Subtitle: ...
Presented by: ...

Slide 2: [Section Title]
- Point 1
- Point 2
- Point 3
- Point 4

Slide 3: [Section Title]
- Point 1
- Point 2
- Point 3
- Point 4

(Continue for all {min_slides} slides)

Do not include anything outside this format.

TOPIC: {topic}
"""
        # The actual AI call logic
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
                    "max_tokens": 4000,
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
