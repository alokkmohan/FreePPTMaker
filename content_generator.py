#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Content Generator using Groq AI
Generates detailed articles from topics
"""

import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_content_from_topic(topic, user_instructions=""):
    """Generate detailed article content from a topic using Groq AI"""
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Add user instructions if provided
        extra_context = ""
        if user_instructions:
            extra_context = f"\n\nAdditional Requirements:\n{user_instructions}"
        
        prompt = f"""You are an expert content writer. Create a detailed, well-structured article on the following topic:

Topic: {topic}{extra_context}

Write a comprehensive article with:
- Clear introduction
- Multiple main sections with detailed explanations
- Key points and benefits
- Challenges or considerations
- Future trends or implications
- Strong conclusion

Make it informative, engaging, and suitable for a presentation.
Length: 500-800 words minimum
Format: Use clear paragraphs with section headers

Write the complete article now:"""
        
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert content writer who creates detailed, well-structured articles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        return content
        
    except Exception as e:
        print(f"Content generation failed: {e}")
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
