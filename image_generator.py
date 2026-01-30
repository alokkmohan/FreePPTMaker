#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Image Generator for PPT Slides
Uses Unsplash API to fetch relevant images for slides
"""

import requests
import os
from typing import Optional, List
import json

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except:
    PIL_AVAILABLE = False

# Unsplash API Configuration
UNSPLASH_API_KEY = "YOUR_UNSPLASH_ACCESS_KEY"  # Will be replaced with env variable
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

def get_unsplash_key():
    """Get Unsplash API key from environment"""
    key = os.getenv("UNSPLASH_API_KEY")
    if not key:
        # Try to use a default/demo key (limited requests)
        key = "m_QYdJW0l8y5t8rJhRMUH0_DEH0LPrQcIErmFTGEHMA"
    return key

def search_image(query: str, per_page: int = 1, orientation: str = "landscape") -> Optional[str]:
    """
    Search for an image on Unsplash matching the query
    Returns the image URL with retry mechanism
    """
    try:
        api_key = get_unsplash_key()
        
        # Clean up the query
        query = query.strip()
        if not query or len(query) < 2:
            return None
        
        # Simplify query for better results
        query_simple = query.split()[0] if query else "business"
        
        params = {
            "query": query_simple,
            "per_page": per_page,
            "orientation": orientation,
            "client_id": api_key
        }
        
        # Try with timeout
        response = requests.get(UNSPLASH_API_URL, params=params, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                image_url = data["results"][0]["urls"]["regular"]
                print(f"✅ Found image for: {query_simple}")
                return image_url
            else:
                # Try with more general query if no results
                print(f"⚠️ No results for '{query_simple}', trying generic...")
                params["query"] = "business"
                response = requests.get(UNSPLASH_API_URL, params=params, timeout=8)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("results"):
                        return data["results"][0]["urls"]["regular"]
        elif response.status_code == 429:
            print(f"⚠️ Unsplash API rate limit hit")
            return None
        else:
            print(f"⚠️ Unsplash API Error: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("⚠️ Image search timeout")
        return None
    except Exception as e:
        print(f"⚠️ Error searching for image: {str(e)}")
        return None

def download_image(image_url: str, save_path: str) -> bool:
    """
    Download image from URL and save locally with retry
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Try to download with retries
        for attempt in range(2):
            try:
                response = requests.get(image_url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                    print(f"✅ Downloaded image: {os.path.basename(save_path)}")
                    return True
            except requests.exceptions.Timeout:
                if attempt == 0:
                    print(f"⚠️ Download timeout, retrying...")
                    continue
                else:
                    break
            except requests.exceptions.ConnectionError:
                if attempt == 0:
                    print(f"⚠️ Connection error, retrying...")
                    continue
                else:
                    break
        
        print(f"❌ Failed to download image after retries")
        return False
    except Exception as e:
        print(f"❌ Error downloading image: {str(e)}")
        return False

def get_slide_image(slide_title: str, slide_content: str = "", output_dir: str = "temp_images") -> Optional[str]:
    """
    Get relevant image for a slide based on title and content
    Returns local path to downloaded image
    """
    try:
        # Create temp directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Construct search query from slide title and content
        # Prioritize title but include content keywords
        search_query = slide_title
        if slide_content:
            # Extract key words from content (first 50 chars)
            content_preview = slide_content[:100] if isinstance(slide_content, str) else ""
            search_query = f"{slide_title} {content_preview}"
        
        # Search for image
        image_url = search_image(search_query)
        
        if not image_url:
            return None
        
        # Generate filename from slide title
        safe_title = "".join(c for c in slide_title if c.isalnum() or c in (' ', '-', '_'))[:30]
        image_filename = f"{safe_title.replace(' ', '_')}.jpg"
        image_path = os.path.join(output_dir, image_filename)
        
        # Download image
        if download_image(image_url, image_path):
            return image_path
        else:
            # Fallback: Create placeholder image
            print(f"📍 Creating placeholder image for: {slide_title}")
            if create_placeholder_image(slide_title, image_path):
                return image_path
            return None
            
    except Exception as e:
        print(f"Error getting slide image: {str(e)}")
        return None

def get_images_for_slides(slide_data: List[dict], output_dir: str = "temp_images") -> dict:
    """
    Get images for multiple slides
    Returns dictionary mapping slide index to image path
    
    slide_data format: [
        {"title": "Slide Title", "content": "Slide content/bullets"},
        ...
    ]
    """
    images = {}
    
    try:
        for idx, slide in enumerate(slide_data):
            title = slide.get("title", f"Slide {idx}")
            content = slide.get("content", "")
            
            # Skip title and ending slides (usually don't need images)
            if idx in [0, len(slide_data) - 1]:
                continue
            
            # Get image for this slide
            image_path = get_slide_image(title, content, output_dir)
            if image_path:
                images[idx] = image_path
                print(f"✅ Got image for slide {idx}: {title}")
            else:
                print(f"⚠️ No image found for slide {idx}: {title}")
        
        return images
        
    except Exception as e:
        print(f"Error getting images for slides: {str(e)}")
        return {}

def create_placeholder_image(title: str, save_path: str) -> bool:
    """
    Create a simple placeholder image when network fails
    Uses PIL to generate a colorful background with text
    """
    if not PIL_AVAILABLE:
        return False
    
    try:
        # Create directory if needed
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Color palette
        colors = [
            (102, 126, 234),  # Blue
            (76, 175, 80),    # Green
            (244, 67, 54),    # Red
            (255, 152, 0),    # Orange
            (156, 39, 176),   # Purple
        ]
        
        # Choose color based on title hash
        color = colors[sum(ord(c) for c in title) % len(colors)]
        
        # Create image
        img = Image.new('RGB', (1280, 720), color=color)
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = title[:40] + "..." if len(title) > 40 else title
        
        # Simple text positioning
        bbox = draw.textbbox((0, 0), text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (1280 - text_width) // 2
        y = (720 - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=None)
        
        # Save image
        img.save(save_path, 'JPEG', quality=90)
        print(f"✅ Created placeholder image: {os.path.basename(save_path)}")
        return True
        
    except Exception as e:
        print(f"❌ Could not create placeholder: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the image generator
    test_query = "artificial intelligence"
    print(f"Testing image search for: {test_query}")
    
    image_url = search_image(test_query)
    if image_url:
        print(f"Found image: {image_url}")
        
        # Try to download
        if download_image(image_url, "test_image.jpg"):
            print("✅ Image downloaded successfully!")
        else:
            print("❌ Failed to download image")
    else:
        print("❌ No image found")
