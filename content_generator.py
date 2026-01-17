#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Content Generator using Multiple AI APIs
Generates detailed articles from topics using Groq API and Ollama
"""

import os
import requests
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OLLAMA_BASE_URL = "http://localhost:11434"

def check_ollama_available():
    """Check if Ollama is available locally"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def generate_with_ollama(topic, user_instructions=""):
    """Generate content using Ollama (local AI with better knowledge)"""
    try:
        extra_context = ""
        if user_instructions:
            extra_context = f"\n\nAdditional Requirements:\n{user_instructions}"
        
        prompt = f"""You are an expert researcher and content writer. Create a COMPREHENSIVE, FACTUAL, and DETAILED article on the following topic:

Topic: {topic}{extra_context}

REQUIREMENTS:
- Length: 1000-1500 words
- Include SPECIFIC FACTS, STATISTICS, REAL DATA
- Provide CONCRETE EXAMPLES and case studies
- Use authoritative, professional tone
- Include actual company names, technologies, specific numbers
- Cite recent developments and trends

Article Structure:
1. **Introduction** (200-250 words)
   - Comprehensive background and context
   - Why this topic is important
   - Current state and relevance

2. **Main Content** (600-900 words) - 5-6 detailed sections:
   - Fundamental concepts and definitions
   - Current trends and latest developments
   - Real-world applications with specific examples
   - Benefits, advantages, and opportunities
   - Challenges, limitations, and considerations
   - Latest innovations, technologies, or methodologies
   - Industry impact and market insights

3. **Future Outlook** (150-200 words)
   - Predictions and emerging trends
   - Expected developments
   - Growth opportunities

4. **Conclusion** (100-150 words)
   - Summary of key insights
   - Actionable recommendations
   - Final thoughts

Write with specific details, real examples, actual data, and professional depth.

Write the complete article now:"""
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": "llama3.2",  # or "llama3.1", "mistral", etc.
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 4000
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            return None
            
    except Exception as e:
        print(f"Ollama generation failed: {e}")
        return None

def generate_with_groq(topic, user_instructions=""):
    """Generate content using Groq API"""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        extra_context = ""
        if user_instructions:
            extra_context = f"\n\nAdditional Requirements:\n{user_instructions}"
        
        prompt = f"""You are an expert researcher and content writer with deep knowledge. Create a COMPREHENSIVE, FACTUAL, and DETAILED article on the following topic:

Topic: {topic}{extra_context}

REQUIREMENTS:
- Length: 1000-1500 words (extensive detail)
- Include SPECIFIC FACTS, STATISTICS, REAL DATA with numbers
- Provide CONCRETE EXAMPLES with actual company/product names
- Use authoritative, professional, technical tone
- Include current information and recent developments
- Cite specific technologies, methodologies, frameworks

Article Structure:
1. **Introduction** (200-250 words)
   - Comprehensive background and context
   - Historical perspective if relevant
   - Why this topic is critical now
   - Current state and relevance

2. **Main Content** (600-900 words) - 5-6 detailed sections:
   - Core concepts and technical definitions
   - Current trends with specific examples (companies, products, stats)
   - Real-world applications and use cases with details
   - Benefits and advantages with quantifiable metrics
   - Challenges and limitations with specific scenarios
   - Latest innovations, technologies, breakthroughs
   - Industry impact, market size, growth data

3. **Future Outlook** (150-200 words)
   - Specific predictions with timeframes
   - Emerging trends with examples
   - Growth opportunities and market projections

4. **Conclusion** (100-150 words)
   - Summary of critical insights
   - Actionable recommendations
   - Strategic takeaways

IMPORTANT: Be extremely specific. Instead of saying "many companies", name actual companies. Instead of "recent years", give specific years. Instead of "significant growth", provide actual percentages or numbers. Use technical terminology.

Write the complete, detailed article now:"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert researcher and technical writer who creates highly detailed, factual, well-researched articles with specific data, real examples, and professional depth. You have extensive knowledge across all domains."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content.strip()
        return content
        
    except Exception as e:
        print(f"Groq generation failed: {e}")
        return None

def generate_content_from_topic(topic, user_instructions=""):
    """Generate detailed article content from a topic using multiple AI sources"""
    
    # Try Ollama first if available (better local knowledge)
    if check_ollama_available():
        print("🤖 Using Ollama for enhanced content generation...")
        content = generate_with_ollama(topic, user_instructions)
        if content:
            return content
        print("⚠️ Ollama failed, falling back to Groq...")
    
    # Fallback to Groq API
    print("🤖 Using Groq API for content generation...")
    content = generate_with_groq(topic, user_instructions)
    if content:
        return content
    
    # Final fallback
    print("⚠️ All AI services failed, using basic template...")
    return generate_basic_content(topic)

def generate_basic_content(topic):
    """Fallback basic content generation"""
    
    return f"""{topic}

Introduction:
This presentation explores the key aspects of {topic}.

Main Points:
Understanding the fundamentals and importance of this topic is crucial in today's world. We will examine various perspectives and practical applications.

Key Benefits:
The implementation and understanding of {topic} brings numerous advantages. From efficiency improvements to better outcomes, the impact is significant.

Challenges:
While there are many benefits, it's important to address the challenges and considerations involved. Understanding these helps in better implementation.

Future Outlook:
Looking ahead, {topic} will continue to evolve and play an important role. Staying informed about developments is essential.

Conclusion:
In summary, {topic} represents an important area that deserves attention and understanding. Continued learning and application will yield positive results.
"""

if __name__ == "__main__":
    test_topic = "AI in Healthcare"
    content = generate_content_from_topic(test_topic)
    print(content)
