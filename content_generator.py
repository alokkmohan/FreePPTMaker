def generate_content_from_topic(topic, user_instructions="", min_slides=10, max_slides=15):
    """Main function to generate content from topic using Ollama only."""
    # Inject high-quality government/policy advisor prompt
    advisor_prompt = f"""
You are a senior government officer and policy advisor with experience in digital governance.

Task:
Create HIGH-QUALITY, meaningful content for a PowerPoint presentation.

Topic:
"{topic}"

Context:
- Audience: Government officers and administrative staff
- Country context: India
- Purpose: Awareness, planning, and decision-making
- Tone: Formal, practical, and policy-oriented
- Avoid generic statements

Content Rules:
- Do NOT write placeholders like "important aspect"
- Do NOT repeat the topic unnecessarily
- Each point must be specific and meaningful
- Use real government-office examples where possible
- Focus on how this topic changes daily office work

Presentation Structure:
1. Introduction
   - Explain the topic in the context of government offices
   - Why it is relevant now
2. Current Use Cases in Government Offices
   - At least 4 concrete examples
   - Example: file processing, grievance redressal, data analysis
3. Benefits
   - Efficiency
   - Transparency
   - Decision support
   - Citizen services
4. Challenges and Risks
   - Data privacy
   - Skill gaps
   - Ethical concerns
   - Infrastructure limitations
5. Way Forward / Recommendations
   - Capacity building
   - Pilot projects
   - Policy safeguards
6. Conclusion
   - Clear summary
   - Future readiness message

Output Format Rules:
- Write slide-wise content
- Each slide must have:
  - A clear title
  - 4–5 bullet points
- Each bullet point should be practical and complete
- Avoid vague or filler language
"""
    # Call Ollama API for content generation (local only)
    from multi_ai_generator import generate_ppt_from_topic_with_ai
    content = generate_ppt_from_topic_with_ai(
        topic=advisor_prompt,
        min_slides=min_slides,
        max_slides=max_slides,
        style="professional",
        audience="government officers",
        custom_instructions=user_instructions
    )
    if content and isinstance(content, dict):
        # Convert dict to formatted string for PPT
        result = []
        if content.get('title'):
            result.append(content['title'])
        if content.get('subtitle'):
            result.append(content['subtitle'])
        result.append("")
        for slide in content.get('slides', []):
            if slide.get('title'):
                result.append(f"\n{slide['title']}")
            for point in slide.get('content', []):
                result.append(f"- {point}")
        return "\n".join(result)
    elif content and len(str(content)) > 500:
        return str(content)
    return generate_basic_content(topic)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Content Generator using Multiple AI APIs
Generates detailed articles from topics using Groq API and Ollama
"""

from dotenv import load_dotenv
load_dotenv()
import os
print("DEBUG: DEEPSEEK_API_KEY =", os.getenv("DEEPSEEK_API_KEY"))

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def generate_basic_content(topic):
    """Fallback basic content generation"""
    return f"""{topic}\n\nIntroduction:\nThis presentation explores the key aspects of {topic}.\n\nMain Points:\nUnderstanding the fundamentals and importance of this topic is crucial in today's world. We will examine various perspectives and practical applications.\n\nKey Benefits:\nThe implementation and understanding of {topic} brings numerous advantages. From efficiency improvements to better outcomes, the impact is significant.\n\nChallenges:\nWhile there are many benefits, it's important to address the challenges and considerations involved. Understanding these helps in better implementation.\n\nFuture Outlook:\nLooking ahead, {topic} will continue to evolve and play an important role. Staying informed about developments is essential.\n\nConclusion:\nIn summary, {topic} represents an important area that deserves attention and understanding. Continued learning and application will yield positive results.\n"""
