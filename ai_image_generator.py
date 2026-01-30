#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Image Generator for PPT Slides
Uses Hugging Face Inference API + Mistral for prompt generation
Flow: Slide Text → Image Prompt (Mistral) → HF API → Generated Image → PPT
"""

import requests
import os
from typing import Optional, Dict
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Hugging Face Configuration
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")

# Mistral Configuration for prompt generation
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


def generate_image_prompt_from_text(slide_text: str, slide_title: str = "") -> str:
    """
    Step 1: Convert slide text to image generation prompt using Mistral AI

    Args:
        slide_text: The content/bullets of the slide
        slide_title: The title of the slide

    Returns:
        A detailed image generation prompt
    """
    try:
        if not MISTRAL_API_KEY:
            # Fallback: simple prompt if no Mistral API
            return f"professional illustration of {slide_title or slide_text[:100]}, modern, clean, corporate style"

        # Construct prompt for Mistral to generate image description
        mistral_prompt = f"""You are an expert at creating image generation prompts for AI art generators.

Given this slide title and content, create a detailed, descriptive prompt for generating a relevant, professional image.

**Slide Title:** {slide_title}

**Slide Content:** {slide_text[:300]}

**Requirements:**
- Create a prompt for a professional, modern illustration
- Focus on the main concept/theme of the slide
- Keep it visual and descriptive
- Style: Corporate, clean, professional
- Output only the image prompt, nothing else

**Image Prompt:**"""

        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistral-large-latest",
            "messages": [
                {"role": "system", "content": "You are an expert at creating image generation prompts."},
                {"role": "user", "content": mistral_prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }

        response = requests.post(MISTRAL_API_URL, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            image_prompt = result["choices"][0]["message"]["content"].strip()
            print(f"✅ Generated image prompt: {image_prompt[:80]}...")
            return image_prompt
        else:
            print(f"⚠️ Mistral API error: {response.status_code}, using fallback")
            return f"professional illustration of {slide_title}, modern corporate style, clean design"

    except Exception as e:
        print(f"⚠️ Error generating image prompt: {e}")
        # Fallback prompt
        return f"professional illustration of {slide_title or 'business concept'}, modern, clean style"


def generate_image_with_huggingface(prompt: str, output_path: str) -> bool:
    """
    Step 2: Generate image using Hugging Face Inference API

    Args:
        prompt: The image generation prompt
        output_path: Where to save the generated image

    Returns:
        True if successful, False otherwise
    """
    try:
        if not HF_API_TOKEN:
            print("❌ HUGGINGFACE_API_TOKEN not found in environment variables")
            print("💡 Get your token from: https://huggingface.co/settings/tokens")
            return False

        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "width": 1024,
                "height": 576  # 16:9 aspect ratio for slides
            }
        }

        print(f"🎨 Generating image with HF API...")
        print(f"   Prompt: {prompt[:100]}...")

        # Call Hugging Face API
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            # Save image
            image = Image.open(BytesIO(response.content))

            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Save as high-quality JPEG
            image.save(output_path, 'JPEG', quality=95)
            print(f"✅ Image generated and saved: {output_path}")
            return True

        elif response.status_code == 503:
            print("⚠️ Model is loading, please wait and retry...")
            return False
        else:
            print(f"❌ HF API Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error generating image: {e}")
        return False


def generate_slide_image(slide_title: str, slide_content: str, output_dir: str = "temp_images") -> Optional[str]:
    """
    Complete flow: Slide Text → Image Prompt → HF API → Image → Save

    Args:
        slide_title: Title of the slide
        slide_content: Content/bullets of the slide
        output_dir: Directory to save images

    Returns:
        Path to generated image or None if failed
    """
    try:
        # Step 1: Generate image prompt from slide text using Mistral
        print(f"\n📝 Processing slide: {slide_title}")
        image_prompt = generate_image_prompt_from_text(slide_content, slide_title)

        # Step 2: Generate filename
        safe_title = "".join(c for c in slide_title if c.isalnum() or c in (' ', '-', '_'))[:30]
        image_filename = f"ai_{safe_title.replace(' ', '_')}.jpg"
        image_path = os.path.join(output_dir, image_filename)

        # Step 3: Generate image with Hugging Face
        success = generate_image_with_huggingface(image_prompt, image_path)

        if success:
            return image_path
        else:
            return None

    except Exception as e:
        print(f"❌ Error in generate_slide_image: {e}")
        return None


def generate_images_for_all_slides(slides: list, output_dir: str = "temp_images") -> Dict[int, str]:
    """
    Generate AI images for multiple slides

    Args:
        slides: List of slide dictionaries with 'title' and 'bullets'
        output_dir: Directory to save images

    Returns:
        Dictionary mapping slide index to image path
    """
    images = {}

    try:
        os.makedirs(output_dir, exist_ok=True)

        for idx, slide in enumerate(slides):
            # Skip title slide (index 0) and conclusion/thank you slides
            if idx == 0 or idx == len(slides) - 1:
                print(f"⏭️  Skipping slide {idx} (title/conclusion)")
                continue

            title = slide.get('title', f'Slide {idx}')

            # Get content from bullets
            bullets = slide.get('bullets', [])
            content = '\n'.join(bullets) if bullets else ""

            if not content:
                print(f"⏭️  Skipping slide {idx} - no content")
                continue

            print(f"\n{'='*60}")
            print(f"🎨 Generating image for Slide {idx}: {title}")
            print(f"{'='*60}")

            # Generate image
            image_path = generate_slide_image(title, content, output_dir)

            if image_path:
                images[idx] = image_path
                print(f"✅ Image ready for slide {idx}")
            else:
                print(f"⚠️  No image generated for slide {idx}")

        print(f"\n{'='*60}")
        print(f"🎉 Generated {len(images)} images total")
        print(f"{'='*60}")

        return images

    except Exception as e:
        print(f"❌ Error generating images for slides: {e}")
        return {}


# Test function
if __name__ == "__main__":
    print("🧪 Testing AI Image Generator\n")

    # Test slide
    test_slide = {
        "title": "Artificial Intelligence in Healthcare",
        "bullets": [
            "AI is transforming healthcare with predictive diagnostics and personalized treatment",
            "Machine learning models analyze medical images with high accuracy",
            "AI-powered virtual assistants help doctors make informed decisions"
        ]
    }

    print("Test Slide:")
    print(f"  Title: {test_slide['title']}")
    print(f"  Content: {test_slide['bullets'][0][:100]}...\n")

    # Generate image
    image_path = generate_slide_image(
        test_slide['title'],
        '\n'.join(test_slide['bullets']),
        output_dir="test_output"
    )

    if image_path:
        print(f"\n✅ SUCCESS! Image saved to: {image_path}")
    else:
        print("\n❌ FAILED to generate image")
        print("\n💡 Tips:")
        print("   1. Set HUGGINGFACE_API_TOKEN in .env file")
        print("   2. Get token from: https://huggingface.co/settings/tokens")
        print("   3. Optionally set MISTRAL_API_KEY for better prompts")
