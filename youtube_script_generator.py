#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YouTube Script Generator using Groq AI
Converts articles/scripts into engaging YouTube video scripts
"""

import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_youtube_script_with_ai(article_text):
    """Generate engaging YouTube script from article using Groq AI"""
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        prompt = f"""You are an expert YouTube scriptwriter. Convert this article into an engaging, conversational YouTube video script.

Article:
{article_text}

Create a professional YouTube script with:
- Engaging opening hook
- Clear section breaks with ## headers
- Conversational, natural language (like talking to viewers)
- Include phrases like "Hello everyone", "In this video", "Let's explore"
- Use transitions between sections
- Strong conclusion with call-to-action
- Format with proper markdown headers (##)

Make it feel like a person talking to the camera, not reading an article.
Keep the same information but make it more engaging and conversational.
"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert YouTube scriptwriter who creates engaging, conversational scripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=4000
        )
        
        script = response.choices[0].message.content.strip()
        return script
        
    except Exception as e:
        print(f"YouTube script generation failed: {e}")
        return generate_basic_youtube_script(article_text)

def generate_basic_youtube_script(article_text):
    """Fallback basic YouTube script generation"""
    
    lines = [l.strip() for l in article_text.split('\n') if l.strip()]
    
    # Extract title
    title = lines[0] if lines else "Video Topic"
    
    script = f"""# YouTube Script: {title}

---

## OPENING

Hello everyone! Welcome back to the channel. Today we're going to talk about an exciting topic: {title}. 

"""
    
    # Add content sections
    current_section = None
    for line in lines[1:]:
        if ':' in line and len(line) < 100:
            # Likely a section header
            current_section = line.replace(':', '').strip()
            script += f"\n## {current_section.upper()}\n\n"
        else:
            # Content
            script += f"{line} "
            if len(script.split('\n')[-1]) > 300:
                script += "\n\n"
    
    script += """

## CONCLUSION

Thank you so much for watching! If you found this video helpful, please give it a thumbs up and subscribe to the channel for more content. Let me know your thoughts in the comments below. See you in the next video!

---

**Production Notes:**
- Review and adjust pacing
- Add B-roll footage where relevant
- Include text overlays for key points
- Add background music
"""
    
    return script

if __name__ == "__main__":
    sample = "AI in Education: The future is here. AI is transforming learning."
    print(generate_youtube_script_with_ai(sample))
