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
        
        # Detect if topic is in Hindi
        has_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in topic)
        
        if has_hindi:
            prompt = f"""आप एक विशेषज्ञ शोधकर्ता और content writer हैं। निम्नलिखित विषय पर एक विस्तृत, तथ्यात्मक और गहन लेख लिखें:

विषय: {topic}{extra_context}

आवश्यकताएं:
- लंबाई: 2000-2500 शब्द (10-15 slides के लिए पर्याप्त content)
- विशिष्ट तथ्य, आंकड़े, वास्तविक डेटा शामिल करें
- ठोस उदाहरण और case studies प्रदान करें
- आधिकारिक, professional tone का उपयोग करें
- वास्तविक कंपनी के नाम, तकनीकें, विशिष्ट संख्याएं शामिल करें
- हालिया developments और trends का उल्लेख करें

लेख की संरचना:
1. **परिचय** (300-400 शब्द)
   - विषय की पृष्ठभूमि और संदर्भ
   - यह विषय क्यों महत्वपूर्ण है
   - वर्तमान स्थिति और प्रासंगिकता
   - मुख्य बिंदुओं का overview

2. **मुख्य विषय** (1200-1500 शब्द) - 8-10 विस्तृत sections:
   - मूल अवधारणाएं और परिभाषाएं (विस्तार से)
   - वर्तमान trends और नवीनतम developments
   - वास्तविक दुनिया के applications (विशिष्ट उदाहरणों के साथ)
   - लाभ, फायदे और अवसर (detailed points)
   - चुनौतियां, सीमाएं और विचार
   - नवीनतम innovations, technologies, या methodologies
   - Industry impact और market insights
   - Best practices और recommendations
   - सुरक्षा और जोखिम management
   - भविष्य की संभावनाएं

3. **भविष्य का दृष्टिकोण** (300-400 शब्द)
   - भविष्यवाणियां और उभरते trends
   - अपेक्षित developments
   - विकास के अवसर
   - तकनीकी प्रगति

4. **निष्कर्ष** (200-300 शब्द)
   - मुख्य insights का सारांश
   - कार्रवाई योग्य सिफारिशें
   - अंतिम विचार
   - महत्वपूर्ण takeaways

विशिष्ट विवरण, वास्तविक उदाहरण, वास्तविक डेटा और professional depth के साथ लिखें।
कम से कम 10 slides के लिए पर्याप्त content प्रदान करें।

अब पूरा लेख हिंदी में लिखें:"""
        else:
            prompt = f"""You are an expert researcher and content writer. Create a COMPREHENSIVE, FACTUAL, and DETAILED article on the following topic:

Topic: {topic}{extra_context}

REQUIREMENTS:
- Length: 2000-2500 words (enough for 10-15 slides)
- Include SPECIFIC FACTS, STATISTICS, REAL DATA
- Provide CONCRETE EXAMPLES and case studies
- Use authoritative, professional tone
- Include actual company names, technologies, specific numbers
- Cite recent developments and trends

Article Structure:
1. **Introduction** (300-400 words)
   - Comprehensive background and context
   - Why this topic is important
   - Current state and relevance
   - Overview of key points

2. **Main Content** (1200-1500 words) - 8-10 detailed sections:
   - Fundamental concepts and definitions (detailed)
   - Current trends and latest developments
   - Real-world applications with specific examples
   - Benefits, advantages, and opportunities (detailed points)
   - Challenges, limitations, and considerations
   - Latest innovations, technologies, or methodologies
   - Industry impact and market insights
   - Best practices and recommendations
   - Security and risk management
   - Future possibilities

3. **Future Outlook** (300-400 words)
   - Predictions and emerging trends
   - Expected developments
   - Growth opportunities
   - Technological advancements

4. **Conclusion** (200-300 words)
   - Summary of key insights
   - Actionable recommendations
   - Final thoughts
   - Important takeaways

Write with specific details, real examples, actual data, and professional depth.
Provide enough content for at least 10 slides.

Write the complete article now:"""
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": "llama3.2",  # or "llama3.1", "mistral", etc.
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 8000
                }
            },
            timeout=180
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "").strip()
            
            if len(content) < 500:
                print(f"⚠️ Ollama returned insufficient content ({len(content)} chars)")
                return None
                
            print(f"✅ Ollama generated {len(content)} characters of content")
            return content
        else:
            print(f"⚠️ Ollama API returned status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ollama generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_with_groq(topic, user_instructions=""):
    """Generate content using Groq API"""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        extra_context = ""
        if user_instructions:
            extra_context = f"\n\nAdditional Requirements:\n{user_instructions}"
        
        # Detect if topic is in Hindi
        has_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in topic)
        
        if has_hindi:
            prompt = f"""आप एक विशेषज्ञ शोधकर्ता और content writer हैं। निम्नलिखित विषय पर एक विस्तृत, तथ्यात्मक और गहन लेख लिखें:

विषय: {topic}{extra_context}

आवश्यकताएं:
- लंबाई: 2000-2500 शब्द (10-15 slides के लिए)
- विशिष्ट तथ्य, आंकड़े, वास्तविक डेटा
- ठोस उदाहरण और case studies
- आधिकारिक, professional tone
- वास्तविक कंपनी के नाम, तकनीकें, विशिष्ट संख्याएं

संरचना:
1. परिचय (300-400 शब्द)
2. मुख्य विषय (1200-1500 शब्द) - 8-10 sections
3. भविष्य का दृष्टिकोण (300-400 शब्द)
4. निष्कर्ष (200-300 शब्द)

विस्तृत, तथ्यात्मक content लिखें। कम से कम 10 slides के लिए पर्याप्त content दें।

अब पूरा लेख हिंदी में लिखें:"""
        else:
            prompt = f"""You are an expert researcher and content writer with deep knowledge. Create a COMPREHENSIVE, FACTUAL, and DETAILED article on the following topic:

Topic: {topic}{extra_context}

REQUIREMENTS:
- Length: 2000-2500 words (for 10-15 slides)
- Include SPECIFIC FACTS, STATISTICS, REAL DATA with numbers
- Provide CONCRETE EXAMPLES with actual company/product names
- Use authoritative, professional, technical tone
- Include current information and recent developments
- Cite specific technologies, methodologies, frameworks

Article Structure:
1. **Introduction** (300-400 words)
   - Comprehensive background and context
   - Historical perspective if relevant
   - Why this topic is critical now
   - Current state and relevance

2. **Main Content** (1200-1500 words) - 8-10 detailed sections:
   - Core concepts and technical definitions (detailed)
   - Current trends with specific examples (companies, products, stats)
   - Real-world applications and use cases with details
   - Benefits and advantages with quantifiable metrics
   - Challenges and limitations with specific scenarios
   - Latest innovations, technologies, breakthroughs
   - Industry impact, market size, growth data
   - Best practices and recommendations
   - Security and risk considerations
   - Future possibilities and developments

3. **Future Outlook** (300-400 words)
   - Specific predictions with timeframes
   - Emerging trends with examples
   - Growth opportunities and market projections
   - Technological advancements expected

4. **Conclusion** (200-300 words)
   - Summary of critical insights
   - Actionable recommendations
   - Strategic takeaways
   - Key points to remember

IMPORTANT: Be extremely specific. Instead of saying "many companies", name actual companies. Instead of "recent years", give specific years. Instead of "significant growth", provide actual percentages or numbers. Use technical terminology. Provide enough detailed content for at least 10 slides.

Write the complete, detailed article now (2000-2500 words):"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert researcher and technical writer who creates highly detailed, factual, well-researched articles with specific data, real examples, and professional depth. You have extensive knowledge across all domains."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Validate that we got substantial content
        if len(content) < 500:
            print(f"⚠️ Groq returned insufficient content ({len(content)} chars)")
            return None
            
        print(f"✅ Groq generated {len(content)} characters of content")
        return content
        
    except Exception as e:
        print(f"❌ Groq generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_content_from_topic(topic, user_instructions=""):
    """Generate detailed article content from a topic using multiple AI sources"""
    
    print(f"\n{'='*60}")
    print(f"📝 Content Generation Request")
    print(f"Topic: {topic}")
    print(f"Instructions: {user_instructions if user_instructions else 'None'}")
    print(f"{'='*60}\n")
    
    # Try Ollama first if available (better local knowledge)
    if check_ollama_available():
        print("🤖 Using Ollama for enhanced content generation...")
        content = generate_with_ollama(topic, user_instructions)
        if content and len(content) > 500:
            print(f"✅ Ollama success: {len(content)} characters generated")
            return content
        print("⚠️ Ollama failed or returned insufficient content, falling back to Groq...")
    else:
        print("ℹ️ Ollama not available, using Groq API...")
    
    # Fallback to Groq API
    print("🤖 Using Groq API for content generation...")
    content = generate_with_groq(topic, user_instructions)
    if content and len(content) > 500:
        print(f"✅ Groq success: {len(content)} characters generated")
        return content
    
    # Final fallback
    print("\n❌ ERROR: All AI services failed!")
    print("⚠️ Using basic template as last resort...\n")
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
