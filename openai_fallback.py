import os
import requests

def generate_with_openai(topic, user_instructions="", min_slides=10, max_slides=15):
    """Generate content using OpenAI GPT-3.5/4 API"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found in environment variable OPENAI_API_KEY")
        return None
    prompt = topic  # topic now contains the full advisor prompt
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
