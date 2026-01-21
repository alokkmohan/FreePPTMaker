def generate_content_from_topic(topic, user_instructions="", min_slides=10, max_slides=15):
    """Main function to generate content from topic using Ollama or fallback to OpenAI."""
    from openai_fallback import generate_with_openai
    # Use only OpenAI for content generation
    content = generate_with_openai(topic, user_instructions, min_slides, max_slides)
    if content and len(content) > 500:
        return content
    # Fallback to basic content if OpenAI also fails
    return generate_basic_content(topic)
def generate_content_from_topic(topic, user_instructions="", min_slides=10, max_slides=15):
    """Main function to generate content from topic using Ollama or fallback."""
    content = generate_with_ollama(topic, user_instructions, min_slides, max_slides)
    if content and len(content) > 500:
        return content
    return generate_basic_content(topic)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Content Generator using Multiple AI APIs
Generates detailed articles from topics using Groq API and Ollama
"""

import os
import requests

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def generate_basic_content(topic):
    """Fallback basic content generation"""
    return f"""{topic}\n\nIntroduction:\nThis presentation explores the key aspects of {topic}.\n\nMain Points:\nUnderstanding the fundamentals and importance of this topic is crucial in today's world. We will examine various perspectives and practical applications.\n\nKey Benefits:\nThe implementation and understanding of {topic} brings numerous advantages. From efficiency improvements to better outcomes, the impact is significant.\n\nChallenges:\nWhile there are many benefits, it's important to address the challenges and considerations involved. Understanding these helps in better implementation.\n\nFuture Outlook:\nLooking ahead, {topic} will continue to evolve and play an important role. Staying informed about developments is essential.\n\nConclusion:\nIn summary, {topic} represents an important area that deserves attention and understanding. Continued learning and application will yield positive results.\n"""
