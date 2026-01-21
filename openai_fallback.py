import os
import requests

def generate_with_openai(topic, user_instructions="", min_slides=10, max_slides=15):
    """Generate content using OpenAI GPT-3.5/4 API"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found in environment variable OPENAI_API_KEY")
        return None
    prompt = f"You are an expert researcher and content writer. Create a COMPREHENSIVE, FACTUAL, and DETAILED article on the following topic for a presentation.\n\nTopic: {topic}\n{user_instructions}\n\nREQUIREMENTS:\n- Length: enough for {min_slides}-{max_slides} slides/sections\n- Include SPECIFIC FACTS, STATISTICS, REAL DATA\n- Provide CONCRETE EXAMPLES and case studies\n- Use authoritative, professional tone\n- Include actual company names, technologies, specific numbers\n- Cite recent developments and trends\n\nArticle Structure:\n1. Introduction\n2. Main Content\n3. Future Outlook\n4. Conclusion\n\nEach section heading MUST be on its own line followed by a COLON (:). Expand content to cover at least {min_slides} and at most {max_slides} sections/slides. Write the complete article now:"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 3000,
        "temperature": 0.7
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            print(f"✅ OpenAI success: {len(content)} characters generated")
            return content
        else:
            print(f"❌ OpenAI API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ OpenAI Exception: {e}")
        return None
