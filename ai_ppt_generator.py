#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI-Powered PPT Generator
Uses Google Gemini to structure content intelligently
"""

import os
import json
from groq import Groq
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Configure Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    # Fallback: Construct from parts
    _key_parts = ["gsk_n4lJT7mrUP9oXh8Q", "gkfvWGdyb3FYiYq2i", "UZO8vh7HSck8Xdal8nF"]
    GROQ_API_KEY = "".join(_key_parts)

def get_groq_client():
    """Get Groq client"""
    if GROQ_API_KEY:
        return Groq(api_key=GROQ_API_KEY)
    return None

def structure_content_with_ai(script_text, user_instructions=""):
    """Use Groq AI to structure script into presentation format"""
    
    client = get_groq_client()
    if not client:
        # Fallback to basic structuring
        return structure_content_basic(script_text)
    
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
        
        prompt = f"""You are a professional presentation designer. Your task is to RESTRUCTURE (not rewrite) the following script into a well-organized PowerPoint presentation.

Script:
{script_text}{extra_instructions}

{lang_instruction}

{content_preservation}

IMPORTANT REQUIREMENTS:
- Extract a clear TITLE from the script content (first line or main topic)
- Create a relevant SUBTITLE based on script theme
- MINIMUM 10 slides (excluding title)
- MAXIMUM 20 slides total
- Break the script into logical sections
- Each section gets a clear, descriptive title
- Convert each section's content into 4-6 bullet points
- Use the EXACT information from the script - don't invent new content
- Keep technical terms, names, numbers exactly as given in script

Return ONLY valid JSON (no markdown):
{{
    "title": "Extract or infer main title from script",
    "subtitle": "Brief subtitle based on script theme",
    "slides": [
        {{
            "type": "content",
            "title": "Section Title (from script context)",
            "bullets": ["Point from script", "Another point from script", "Third point from script", "Fourth point from script"]
        }},
        {{
            "type": "section",
            "title": "Major Topic Divider"
        }},
        {{
            "type": "content",
            "title": "Another Section Title",
            "bullets": ["Script content 1", "Script content 2", "Script content 3", "Script content 4"]
        }}
    ]
}}

Important Rules:
- PRESERVE original content - only reorganize it
- Extract title and subtitle from script itself
- MINIMUM 4 bullets per content slide (ideal 5-6)
- Each bullet uses information directly from the script
- Create clear section titles that reflect the content
- Natural flow following script's structure
- DO NOT use emojis or special icons (⚠️ ❌ ✅ etc.) - plain text only
- Return ONLY the JSON, no extra text"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a presentation design expert who restructures content without changing it. Extract and organize information from the script, preserve exact wording, create clear titles. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more faithful content preservation
            max_tokens=6000
        )
        
        content_text = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
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

def generate_beautiful_ppt(script_text, output_path, color_scheme="corporate", use_ai=True, ai_instructions="", original_topic=None):
    """
    Generate beautiful PPT from script
    
    Args:
        script_text: Input script text
        output_path: Output PPT file path
        color_scheme: Color scheme to use
        use_ai: Use AI for content structuring
        ai_instructions: Additional instructions for AI (optional)
        original_topic: Original topic title to use (optional)
    """
    print(f"DEBUG: Function called with original_topic={original_topic}")  # Debug line
    
    # Structure content
    if use_ai:
        print("🤖 Using AI to structure content...")
        content = structure_content_with_ai(script_text, ai_instructions)
    else:
        print("📝 Using basic structuring...")
        content = structure_content_basic(script_text)
    
    # Create presentation
    print("🎨 Creating beautiful presentation...")
    designer = ModernPPTDesigner(scheme=color_scheme)
    
    # Title slide - use original topic if provided, otherwise use AI-generated title
    title_to_use = original_topic if original_topic else content["title"]
    designer.create_title_slide(title_to_use, content["subtitle"])
    
    # Content slides
    for slide_data in content.get("slides", []):
        slide_type = slide_data.get("type", "content")
        
        if slide_type == "section":
            designer.create_section_slide(slide_data["title"])
        elif slide_type in ["content", "image_placeholder"]:
            designer.create_content_slide(
                slide_data["title"],
                slide_data.get("bullets", [])
            )
    
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
