import os
import requests

def generate_with_openai(topic, user_instructions="", min_slides=10, max_slides=15):
    """Generate content using best available OpenAI GPT-4 model"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found in environment variable OPENAI_API_KEY")
        return None
    prompt = topic  # topic now contains the full advisor prompt
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # Try best model first
    for model_name in ["gpt-4-1106-preview", "gpt-4"]:
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 3000,
            "temperature": 0.3
        }
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=90)
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                print(f"✅ OpenAI success ({model_name}): {len(content)} characters generated")
                return content
            else:
                print(f"❌ OpenAI API error ({model_name}): {response.status_code}")
        except Exception as e:
            print(f"❌ OpenAI Exception ({model_name}): {e}")
