#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI-Powered PPT Generator
Uses Google Gemini to structure content intelligently
"""

import os
import json
import shutil
import requests
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Try to import image generator
try:
    from image_generator import get_slide_image, download_image, search_image
    IMAGE_GENERATION_AVAILABLE = True
except ImportError:
    IMAGE_GENERATION_AVAILABLE = False

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def deepseek_generate_content(prompt, system_prompt=None, temperature=0.7, max_tokens=2048):
    """
    Call DeepSeek API for text generation
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        raise Exception(f"DeepSeek API error: {response.status_code} {response.text}")

def ollama_generate_content(prompt, system_prompt=None, temperature=0.7, max_tokens=2048):
    """
    Try to generate content using local Ollama LLM (e.g. llama3)
    """
    try:
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "options": {"temperature": temperature, "num_predict": max_tokens}
        }
        if system_prompt:
            payload["system"] = system_prompt
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
        if response.status_code == 200:
            # Ollama streams output, so we need to parse lines
            lines = response.text.splitlines()
            content = ""
            for line in lines:
                if line.strip():
                    try:
                        obj = json.loads(line)
                        content += obj.get("response", "")
                    except Exception:
                        continue
            return content.strip()
        else:
            raise Exception(f"Ollama error: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Ollama failed: {e}")
        return None

def structure_content_with_ai(script_text, user_instructions="", min_slides=10, max_slides=20):
    """Try Ollama first, fallback to DeepSeek if Ollama fails"""
    try:
        # Add user instructions to prompt if provided
        extra_instructions = ""
        if user_instructions:
            extra_instructions = f"\n\nUser's specific instructions:\n{user_instructions}\n\nPlease incorporate these instructions while structuring the presentation."
        # Detect if script has Hindi content
        has_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in script_text[:500])
        if has_hindi:
            lang_instruction = """भाषा: हिंदी में slides बनाएं
- Title slide: मुख्य शीर्षक और उपशीर्षक
- कम से कम 10 slides, अधिकतम 20 slides
- हर content slide में 4-6 bullet points (अनिवार्य)
- हर bullet में पूर्ण, सार्थक वाक्य (60-120 characters)
- Section dividers का उपयोग करें
- Conclusion slide में मुख्य बिंदु"""
            content_preservation = """महत्वपूर्ण: ORIGINAL CONTENT को preserve करें
- Script में दी गई जानकारी को ज्यों का त्यों रखें
- सिर्फ formatting और organization improve करें
- नई जानकारी न जोड़ें, script में जो है वही use करें
- Bullets में script के exact words और phrases use करें
- बस proper sections बनाएं और clear titles दें"""
        else:
            lang_instruction = """Language: Create slides in English
- Title slide with main title and subtitle
- Minimum 10 slides, maximum 20 slides
- Each content slide: 4-6 bullet points (MANDATORY)
- Each bullet: complete, meaningful sentence (80-150 chars)
- Use section dividers for major topics
- Conclusion slide with key takeaways"""
            content_preservation = """CRITICAL: PRESERVE ORIGINAL CONTENT
- Keep the information from the script AS IS
- Only improve formatting and organization
- DO NOT add new information - use only what's in the script
- Use exact words and phrases from the script in bullets
- Just create proper sections and clear titles"""
        prompt = f"""You are a professional presentation designer. Your task is to RESTRUCTURE (not rewrite) the following script into a well-organized PowerPoint presentation.\n\nScript:\n{script_text}{extra_instructions}\n\n{lang_instruction}\n\n{content_preservation}\n\nIMPORTANT REQUIREMENTS:\n- Extract a clear TITLE from the script content (first line or main topic)\n- Create a relevant SUBTITLE based on script theme\n- MINIMUM {min_slides} slides (excluding title)\n- MAXIMUM {max_slides} slides total\n- Break the script into logical sections\n- Each section gets a clear, descriptive title\n- Convert each section's content into 4-6 bullet points\n- Use the EXACT information from the script - don't invent new content\n- Keep technical terms, names, numbers exactly as given in script\n\nReturn ONLY valid JSON (no markdown):\n{{\n    \"title\": \"Extract or infer main title from script\",\n    \"subtitle\": \"Brief subtitle based on script theme\",\n    \"slides\": [\n        {{\n            \"type\": \"content\",\n            \"title\": \"Section Title (from script context)\",\n            \"bullets\": [\"Point from script\", \"Another point from script\", \"Third point from script\", \"Fourth point from script\"]\n        }},\n        {{\n            \"type\": \"section\",\n            \"title\": \"Major Topic Divider\"\n        }},\n        {{\n            \"type\": \"content\",\n            \"title\": \"Another Section Title\",\n            \"bullets\": [\"Script content 1\", \"Script content 2\", \"Script content 3\", \"Script content 4\"]\n        }}\n    ]\n}}\n\nImportant Rules:\n- PRESERVE original content - only reorganize it\n- Extract title and subtitle from script itself\n- MINIMUM 4 bullets per content slide (ideal 5-6)\n- Each bullet uses information directly from the script\n- Create clear section titles that reflect the content\n- Natural flow following script's structure\n- DO NOT use emojis or special icons (⚠️ ❌ ✅ etc.) - plain text only\n- Return ONLY the JSON, no extra text"""
        # Try Ollama first
        content_text = ollama_generate_content(prompt, system_prompt=None, temperature=0.3, max_tokens=6000)
        if not content_text or len(content_text) < 100:
            # Fallback to DeepSeek
            print("Ollama failed or empty, using DeepSeek...")
            content_text = deepseek_generate_content(prompt, system_prompt=None, temperature=0.3, max_tokens=6000)
        content_text = content_text.replace('```json', '').replace('```', '').strip()
        result = json.loads(content_text)
        return result
    except Exception as e:
        print(f"AI structuring failed: {e}")
        return structure_content_basic(script_text)

def structure_content_basic(script_text):
    """Basic fallback structuring - flexible slide count based on content"""
    lines = [l.strip() for l in script_text.split('\n') if l.strip()]
    
    if not lines:
        return {
            "title": "Presentation",
            "subtitle": "Generated Content",
            "slides": []
        }
    
    # Extract title and subtitle
    title = lines[0] if lines else "Presentation"
    subtitle = lines[1] if len(lines) > 1 and len(lines[1]) < 100 else "Key Insights"
    
    slides = []
    current_bullets = []
    current_title = None
    
    # Process all content dynamically
    for i, line in enumerate(lines[2:] if len(lines) > 2 else lines):
        # Check if line looks like a heading/section (has colon and shortish)
        is_heading = ':' in line and len(line) < 100
        
        if is_heading:
            # Save previous slide if has enough content (minimum 4 bullets)
            if len(current_bullets) >= 4 and current_title:
                slides.append({
                    "type": "content",
                    "title": current_title,
                    "bullets": current_bullets[:6]
                })
                current_bullets = []
            elif current_bullets and current_title:
                # Store temporarily, will combine with next section
                pass
            
            # Extract new section title
            current_title = line.split(':')[0].strip()
            
            # Content after colon
            after_colon = line.split(':', 1)[1].strip() if ':' in line else ""
            if after_colon and len(after_colon) > 15:
                current_bullets.append(after_colon)
        else:
            # Regular content line
            if len(line) > 15:  # Skip very short lines
                # Set default title if none
                if not current_title:
                    current_title = "Overview"
                
                # Split very long lines into multiple bullets
                if len(line) > 200:
                    # Try to split by sentences
                    parts = line.replace('. ', '.|').split('|')
                    for part in parts:
                        if part.strip() and len(part.strip()) > 20:
                            current_bullets.append(part.strip()[:150])
                else:
                    current_bullets.append(line[:150])
                
                # Create slide when we have 5-6 bullets (good amount)
                if len(current_bullets) >= 5:
                    slides.append({
                        "type": "content",
                        "title": current_title,
                        "bullets": current_bullets[:6]
                    })
                    current_bullets = []
    
    # Add any remaining bullets as final slide(s) - ensure minimum 4 bullets
    if current_bullets:
        # Pad with generic points if less than 4
        while len(current_bullets) < 4:
            current_bullets.append(f"Important aspect of {current_title or 'this topic'}")
        
        slides.append({
            "type": "content",
            "title": current_title or "Summary",
            "bullets": current_bullets[:6]
        })
    
    return {
        "title": title,
        "subtitle": subtitle,
        "slides": slides
    }

class ModernPPTDesigner:
    """Creates beautiful, modern PPT designs"""
    
    # Professional Color Schemes
    COLOR_SCHEMES = {
        "ocean": {
            "primary": RGBColor(13, 71, 161),      # Deep Blue
            "secondary": RGBColor(3, 169, 244),    # Light Blue
            "accent": RGBColor(255, 193, 7),       # Amber
            "text": RGBColor(33, 33, 33),          # Dark Gray
            "bg": RGBColor(250, 250, 250),         # Light Gray
        },
        "forest": {
            "primary": RGBColor(27, 94, 32),       # Dark Green
            "secondary": RGBColor(76, 175, 80),    # Green
            "accent": RGBColor(255, 152, 0),       # Orange
            "text": RGBColor(33, 33, 33),
            "bg": RGBColor(250, 250, 250),
        },
        "sunset": {
            "primary": RGBColor(183, 28, 28),      # Deep Red
            "secondary": RGBColor(244, 67, 54),    # Red
            "accent": RGBColor(255, 235, 59),      # Yellow
            "text": RGBColor(33, 33, 33),
            "bg": RGBColor(250, 250, 250),
        },
        "corporate": {
            "primary": RGBColor(26, 35, 126),      # Indigo
            "secondary": RGBColor(92, 107, 192),   # Light Indigo
            "accent": RGBColor(0, 188, 212),       # Cyan
            "text": RGBColor(33, 33, 33),
            "bg": RGBColor(255, 255, 255),
        },
        "eg": {
            "primary": RGBColor(255, 47, 47),      # Bright Red (EG Template Title)
            "secondary": RGBColor(200, 30, 30),    # Darker Red
            "accent": RGBColor(255, 100, 100),     # Light Red
            "text": RGBColor(38, 38, 38),          # Dark Gray (EG Template Text)
            "bg": RGBColor(255, 255, 255),         # White
        }
    }
    
    def __init__(self, scheme="corporate"):
        self.colors = self.COLOR_SCHEMES.get(scheme, self.COLOR_SCHEMES["corporate"])
        self.prs = Presentation()
        self.prs.slide_width = Inches(10)
        self.prs.slide_height = Inches(5.625)
    
    def add_gradient_background(self, slide, style="light"):
        """Add gradient background to slide"""
        # Note: python-pptx doesn't support gradients directly
        # We'll use shapes to create a layered effect
        bg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(0),
            Inches(10), Inches(5.625)
        )
        bg.fill.solid()
        bg.fill.fore_color.rgb = self.colors["bg"]
        bg.line.fill.background()
        
        # Send to back
        slide.shapes._spTree.remove(bg._element)
        slide.shapes._spTree.insert(2, bg._element)
    
    def create_title_slide(self, title, subtitle):
        """Beautiful title slide"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        
        # Add decorative shape at top
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(0),
            Inches(10), Inches(2.5)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = self.colors["primary"]
        shape.line.fill.background()
        
        # Accent stripe
        stripe = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(2.5),
            Inches(10), Inches(0.2)
        )
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = self.colors["accent"]
        stripe.line.fill.background()
        
        # Title - adjusted for longer text with better constraints
        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.3),
            Inches(9), Inches(2)
        )
        tf = title_box.text_frame
        # Truncate very long titles
        if len(title) > 120:
            tf.text = title[:117] + "..."
        else:
            tf.text = title
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        
        # More aggressive dynamic font sizing for titles
        if len(title) > 100:
            p.font.size = Pt(24)  # Very small for very long titles
        elif len(title) > 80:
            p.font.size = Pt(28)  # Smaller for long titles
        elif len(title) > 60:
            p.font.size = Pt(32)  # Medium-small for moderate titles
        elif len(title) > 40:
            p.font.size = Pt(36)  # Medium for shorter titles
        else:
            p.font.size = Pt(40)  # Large for short titles
            
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.font.name = 'Calibri'
        
        # Subtitle with better positioning
        subtitle_box = slide.shapes.add_textbox(
            Inches(1), Inches(3),
            Inches(8), Inches(1.5)
        )
        tf = subtitle_box.text_frame
        # Truncate very long subtitles
        if len(subtitle) > 100:
            tf.text = subtitle[:97] + "..."
        else:
            tf.text = subtitle
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        
        # More aggressive dynamic subtitle sizing
        if len(subtitle) > 80:
            p.font.size = Pt(18)
        elif len(subtitle) > 60:
            p.font.size = Pt(20)
        else:
            p.font.size = Pt(24)
            
        p.font.color.rgb = self.colors["secondary"]
        p.font.name = 'Calibri'
        p.font.italic = True
        
        return slide
    
    def create_section_slide(self, title):
        """Section divider slide"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        
        # Background with gradient effect using two rectangles
        bg_bottom = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(0),
            Inches(10), Inches(5.625)
        )
        bg_bottom.fill.solid()
        bg_bottom.fill.fore_color.rgb = RGBColor(250, 250, 250)
        bg_bottom.line.fill.background()
        
        # Diagonal accent (properly contained within slide)
        accent = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(0),
            Inches(10), Inches(3.5)
        )
        accent.fill.solid()
        accent.fill.fore_color.rgb = self.colors["secondary"]
        accent.line.fill.background()
        accent.rotation = 0  # Keep it horizontal, no overflow
        
        # Title with dynamic sizing
        title_box = slide.shapes.add_textbox(
            Inches(1), Inches(2),
            Inches(8), Inches(1.5)
        )
        tf = title_box.text_frame
        # Truncate very long section titles
        if len(title) > 80:
            tf.text = title[:77] + "..."
        else:
            tf.text = title
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        
        # Dynamic font sizing for section titles
        if len(title) > 60:
            p.font.size = Pt(36)
        elif len(title) > 40:
            p.font.size = Pt(42)
        else:
            p.font.size = Pt(48)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.font.name = 'Calibri'
        
        return slide
    
    def create_content_slide(self, title, bullets):
        """Modern content slide with bullets"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        
        # Header bar
        header = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(0),
            Inches(10), Inches(1)
        )
        header.fill.solid()
        header.fill.fore_color.rgb = self.colors["primary"]
        header.line.fill.background()
        
        # Title on header with dynamic sizing
        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.15),
            Inches(9), Inches(0.7)
        )
        tf = title_box.text_frame
        # Truncate very long content slide titles
        if len(title) > 70:
            tf.text = title[:67] + "..."
        else:
            tf.text = title
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        # Dynamic font sizing for content slide titles
        if len(title) > 50:
            p.font.size = Pt(28)
        elif len(title) > 35:
            p.font.size = Pt(32)
        else:
            p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.font.name = 'Calibri'
        
        # Side accent bar
        side_bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0.3), Inches(1.3),
            Inches(0.15), Inches(3.8)
        )
        side_bar.fill.solid()
        side_bar.fill.fore_color.rgb = self.colors["accent"]
        side_bar.line.fill.background()
        
        # Content
        content_box = slide.shapes.add_textbox(
            Inches(0.8), Inches(1.3),
            Inches(8.7), Inches(4)
        )
        tf = content_box.text_frame
        tf.word_wrap = True
        
        # Calculate appropriate font size based on content
        total_chars = sum(len(bullet) for bullet in bullets)
        num_bullets = len(bullets)
        
        # Detect if text contains Hindi/Devanagari characters
        has_hindi = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for bullet in bullets for char in bullet)
        
        # Dynamic font sizing - more aggressive for Hindi
        if has_hindi:
            # Hindi text takes more space, use smaller limits
            if total_chars > 450 or num_bullets > 6:
                font_size = 12
                space_after = 6
                max_chars = 80
            elif total_chars > 300 or num_bullets > 5:
                font_size = 14
                space_after = 8
                max_chars = 100
            else:
                font_size = 16
                space_after = 10
                max_chars = 120
        else:
            # English text - more aggressive limits
            if total_chars > 700 or num_bullets > 6:
                font_size = 14
                space_after = 8
                max_chars = 150
            elif total_chars > 500 or num_bullets > 5:
                font_size = 16
                space_after = 10
                max_chars = 180
            else:
                font_size = 18
                space_after = 12
                max_chars = 200
        
        for i, bullet in enumerate(bullets):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            
            # Truncate very long bullets based on language
            bullet_text = bullet[:max_chars] + "..." if len(bullet) > max_chars else bullet
            
            p.text = "●  " + bullet_text
            p.font.size = Pt(font_size)
            p.font.color.rgb = self.colors["text"]
            p.font.name = 'Calibri'
            p.space_after = Pt(space_after)
        
        return slide
    
    def create_content_slide_with_image(self, title, bullets, image_path=None):
        """Content slide with image on right side"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        
        # Header bar
        header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(1))
        header.fill.solid()
        header.fill.fore_color.rgb = self.colors["primary"]
        header.line.fill.background()
        
        # Title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.15), Inches(9), Inches(0.7))
        tf = title_box.text_frame
        tf.text = title[:67] + "..." if len(title) > 70 else title
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.font.size = Pt(28 if len(title) > 50 else 32 if len(title) > 35 else 36)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        
        # Side bar
        side_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.3), Inches(1.3), Inches(0.15), Inches(3.8))
        side_bar.fill.solid()
        side_bar.fill.fore_color.rgb = self.colors["accent"]
        side_bar.line.fill.background()
        
        # Add image if available
        content_width = 8.7
        if image_path and os.path.exists(image_path):
            try:
                slide.shapes.add_picture(image_path, Inches(5.2), Inches(1.3), width=Inches(4.3), height=Inches(4))
                content_width = 4.5
            except:
                pass
        
        # Content
        content_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(content_width), Inches(4))
        tf = content_box.text_frame
        tf.word_wrap = True
        
        total_chars = sum(len(b) for b in bullets)
        font_size = 14 if total_chars > 600 else 16 if total_chars > 400 else 18
        
        for i, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = "● " + (bullet[:150] + "..." if len(bullet) > 150 else bullet)
            p.font.size = Pt(font_size)
            p.font.color.rgb = self.colors["text"]
            p.space_after = Pt(10)
        
        return slide
    
    def create_end_slide(self):
        """Beautiful thank you slide"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        
        # Background
        bg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(0),
            Inches(10), Inches(5.625)
        )
        bg.fill.solid()
        bg.fill.fore_color.rgb = self.colors["primary"]
        bg.line.fill.background()
        
        # Circle decoration
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(3), Inches(1),
            Inches(4), Inches(4)
        )
        circle.fill.solid()
        circle.fill.fore_color.rgb = self.colors["secondary"]
        circle.line.fill.background()
        
        # Thank you text
        text_box = slide.shapes.add_textbox(
            Inches(2), Inches(2.3),
            Inches(6), Inches(1)
        )
        tf = text_box.text_frame
        tf.text = "Thank You!"
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(60)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.font.name = 'Calibri'
        
        return slide
    
    def save(self, filepath):
        """Save presentation"""
        self.prs.save(filepath)

def generate_ppt_from_template(script_text, output_path, template_path, use_ai=True, ai_instructions="", original_topic=None, min_slides=10, max_slides=20):
    """
    Generate PPT using a template file
    
    Args:
        script_text: Input script text
        output_path: Output PPT file path
        template_path: Path to template PPTX file
        use_ai: Use AI for content structuring
        ai_instructions: Additional instructions for AI (optional)
        original_topic: Original topic title to use (optional)
        min_slides: Minimum number of slides (optional)
        max_slides: Maximum number of slides (optional)
    """
    print(f"📋 Using template: {template_path}")
    
    # Structure content
    if use_ai:
        print("🤖 Using AI to structure content...")
        content = structure_content_with_ai(script_text, ai_instructions, min_slides, max_slides)
    else:
        print("📝 Using basic structuring...")
        content = structure_content_basic(script_text)
    
    # Load template
    prs = Presentation(template_path)
    
    # Use original topic if provided
    title_to_use = original_topic if original_topic else content["title"]
    
    # Try to find title slide (usually layout 0 or a slide with title placeholder)
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    
    # Fill in title and subtitle if placeholders exist
    if title_slide.shapes.title:
        title_slide.shapes.title.text = title_to_use
    
    # Try to add subtitle if placeholder exists
    for shape in title_slide.placeholders:
        if shape.placeholder_format.idx == 1:  # Usually subtitle placeholder
            shape.text = content.get("subtitle", "")
            break
    
    # Add content slides using template layout
    # Try to use layout 1 (usually content layout) or fallback to layout 0
    content_layout_idx = 1 if len(prs.slide_layouts) > 1 else 0
    
    for slide_data in content.get("slides", []):
        slide_type = slide_data.get("type", "content")
        
        if slide_type == "section":
            # For section slides, try to use section header layout if available
            section_layout_idx = 2 if len(prs.slide_layouts) > 2 else content_layout_idx
            slide = prs.slides.add_slide(prs.slide_layouts[section_layout_idx])
            if slide.shapes.title:
                slide.shapes.title.text = slide_data["title"]
        else:
            # Regular content slide
            slide = prs.slides.add_slide(prs.slide_layouts[content_layout_idx])
            
            # Set title
            if slide.shapes.title:
                slide.shapes.title.text = slide_data["title"]
            
            # Add bullets to content placeholder
            bullets = slide_data.get("bullets", [])
            if bullets:
                # Find the content placeholder (usually idx 1)
                for shape in slide.placeholders:
                    if shape.placeholder_format.idx == 1 and shape.has_text_frame:
                        text_frame = shape.text_frame
                        text_frame.clear()
                        
                        for i, bullet in enumerate(bullets):
                            if i == 0:
                                p = text_frame.paragraphs[0]
                            else:
                                p = text_frame.add_paragraph()
                            p.text = bullet
                            p.level = 0
                        break
    
    # Add thank you slide using last layout
    end_layout_idx = len(prs.slide_layouts) - 1
    end_slide = prs.slides.add_slide(prs.slide_layouts[end_layout_idx])
    if end_slide.shapes.title:
        end_slide.shapes.title.text = "Thank You!"
    
    # Save
    prs.save(output_path)
    print(f"✅ PPT created from template: {output_path}")
    
    return True

def generate_beautiful_ppt(script_text, output_path, color_scheme="corporate", use_ai=True, ai_instructions="", original_topic=None, template_path=None, min_slides=10, max_slides=20):
    """
    Generate beautiful PPT from script
    
    Args:
        script_text: Input script text
        output_path: Output PPT file path
        color_scheme: Color scheme to use
        use_ai: Use AI for content structuring
        ai_instructions: Additional instructions for AI (optional)
        original_topic: Original topic title to use (optional)
        template_path: Path to template PPTX file (optional)
        min_slides: Minimum number of slides (optional, default 10)
        max_slides: Maximum number of slides (optional, default 20)
    """
    print(f"DEBUG: Function called with original_topic={original_topic}, template_path={template_path}, slides={min_slides}-{max_slides}")
    
    # If template is provided, use template-based generation
    if template_path and os.path.exists(template_path):
        return generate_ppt_from_template(script_text, output_path, template_path, use_ai, ai_instructions, original_topic, min_slides, max_slides)
    
    # Structure content
    if use_ai:
        print("🤖 Using AI to structure content...")
        content = structure_content_with_ai(script_text, ai_instructions, min_slides, max_slides)
    else:
        print("📝 Using basic structuring...")
        content = structure_content_basic(script_text)
    
    # Create presentation
    print("🎨 Creating beautiful presentation...")
    designer = ModernPPTDesigner(scheme=color_scheme)
    
    # Title slide
    title_to_use = original_topic if original_topic else content["title"]
    designer.create_title_slide(title_to_use, content["subtitle"])
    
    # Prepare temp directory for images
    import time
    temp_img_dir = os.path.join("temp_images", f"ppt_{int(time.time())}")
    
    # Content slides
    slide_count = 0
    total_slides = len(content.get("slides", []))
    images_added = 0
    
    for idx, slide_data in enumerate(content.get("slides", [])):
        slide_type = slide_data.get("type", "content")
        
        if slide_type == "section":
            designer.create_section_slide(slide_data["title"])
        elif slide_type in ["content", "image_placeholder"]:
            # Try to get image for this slide
            image_path = None
            slide_title = slide_data["title"]
            slide_content = " ".join(slide_data.get("bullets", []))
            
            # Add images to content slides (skip first and last few)
            if IMAGE_GENERATION_AVAILABLE:
                skip_image = (idx < 1) or (idx >= total_slides - 1)  # Skip title-like and ending slides
                
                if not skip_image:
                    try:
                        print(f"🖼️ Fetching image for slide {idx}: {slide_title[:40]}...")
                        image_path = get_slide_image(slide_title, slide_content, temp_img_dir)
                        if image_path:
                            print(f"✅ Added image for slide {idx}")
                            images_added += 1
                        else:
                            print(f"ℹ️ No image found for slide {idx}")
                    except Exception as e:
                        print(f"⚠️ Image generation error for slide {idx}: {str(e)}")
            
            # Use content slide with image support
            designer.create_content_slide_with_image(
                slide_data["title"],
                slide_data.get("bullets", []),
                image_path
            )
            slide_count += 1
    
    # Log summary
    print(f"📸 Image summary: {images_added} images added to {total_slides} slides")
    
    # End slide
    designer.create_end_slide()
    
    # Save
    designer.save(output_path)
    print(f"✅ Beautiful PPT created: {output_path}")
    
    return True

if __name__ == "__main__":
    # Test
    sample_script = """
Uttar Pradesh's education system is undergoing major transformations.
The state is focusing on accessibility, technology, and skill development.
Operation Kayakalp aims to modernize schools.
Vocational education is being mandated in Classes 9 and 11.
    """
    
    generate_beautiful_ppt(sample_script, "test_beautiful.pptx", use_ai=False)
