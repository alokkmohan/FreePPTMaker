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
        
        prompt = f"""You are a professional presentation designer. Convert the following script into a well-structured PowerPoint presentation.

Script:
{script_text}{extra_instructions}

Create as many slides as needed to properly cover the content. Don't force a fixed number.

Guidelines:
- Title slide with main title and subtitle
- Opening/hook slide if content allows
- Break content into logical sections
- Each content slide: 4-6 bullet points (MANDATORY - never less than 4)
- Each bullet should be substantial and informative (80-150 chars)
- Use section dividers for major topic changes
- Conclusion slide with key takeaways
- Could be 5 slides or 20 slides - depends on content

Return ONLY valid JSON (no markdown):
{{
    "title": "Main presentation title",
    "subtitle": "Brief subtitle or tagline",
    "slides": [
        {{
            "type": "content",
            "title": "Slide Title",
            "bullets": ["Detailed point 1 with full explanation", "Detailed point 2 with context", "Detailed point 3 with examples", "Detailed point 4 with insights"]
        }},
        {{
            "type": "section",
            "title": "Major Topic Name"
        }},
        {{
            "type": "content",
            "title": "Another Topic",
            "bullets": ["Complete sentence 1", "Complete sentence 2", "Complete sentence 3", "Complete sentence 4"]
        }}
    ]
}}

Important Rules:
- MINIMUM 4 bullets per content slide (ideal 5-6)
- Each bullet must be a complete, meaningful sentence
- Keep bullets informative (80-150 chars each)
- Create as many or as few slides as needed for the content
- Don't pad or compress content artificially
- Natural flow and logical grouping
- DO NOT use emojis or special icons (⚠️ ❌ ✅ etc.) - plain text only
- Return ONLY the JSON, no extra text"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a presentation design expert. Create the right number of slides for the content - not too few, not too many. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
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
        
        # Title - adjusted for longer text
        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.4),
            Inches(9), Inches(1.8)
        )
        tf = title_box.text_frame
        tf.text = title
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        
        # Dynamic font size based on title length
        if len(title) > 80:
            p.font.size = Pt(36)  # Smaller for long titles
        elif len(title) > 50:
            p.font.size = Pt(42)  # Medium for moderate titles
        else:
            p.font.size = Pt(48)  # Large for short titles
            
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.font.name = 'Calibri'
        
        # Subtitle
        subtitle_box = slide.shapes.add_textbox(
            Inches(1), Inches(3.2),
            Inches(8), Inches(1)
        )
        tf = subtitle_box.text_frame
        tf.text = subtitle
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        
        # Dynamic subtitle size
        if len(subtitle) > 60:
            p.font.size = Pt(22)
        else:
            p.font.size = Pt(28)
            
        p.font.color.rgb = self.colors["secondary"]
        p.font.name = 'Calibri'
        p.font.italic = True
        
        return slide
    
    def create_section_slide(self, title):
        """Section divider slide"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        
        # Diagonal accent
        accent = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(-2), Inches(-1),
            Inches(14), Inches(7)
        )
        accent.fill.solid()
        accent.fill.fore_color.rgb = self.colors["secondary"]
        accent.line.fill.background()
        accent.rotation = 15
        
        # Title
        title_box = slide.shapes.add_textbox(
            Inches(1), Inches(2),
            Inches(8), Inches(1.5)
        )
        tf = title_box.text_frame
        tf.text = title
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
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
        
        # Title on header
        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.2),
            Inches(9), Inches(0.6)
        )
        tf = title_box.text_frame
        tf.text = title
        p = tf.paragraphs[0]
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
        
        for i, bullet in enumerate(bullets):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            
            p.text = "●  " + bullet
            p.font.size = Pt(20)
            p.font.color.rgb = self.colors["text"]
            p.font.name = 'Calibri'
            p.space_after = Pt(14)
        
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

def generate_beautiful_ppt(script_text, output_path, color_scheme="corporate", use_ai=True, ai_instructions=""):
    """
    Generate beautiful PPT from script
    
    Args:
        script_text: Input script text
        output_path: Output PPT file path
        color_scheme: Color scheme to use
        use_ai: Use AI for content structuring
        ai_instructions: Additional instructions for AI (optional)
    """
    
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
    
    # Title slide
    designer.create_title_slide(content["title"], content["subtitle"])
    
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
