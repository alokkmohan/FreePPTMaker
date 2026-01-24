"""
AI-Powered PPT Generator
Uses OpenAI to structure content intelligently
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

# Try to import text processor for smart truncation
try:
    from text_processor import smart_truncate, fix_broken_words, clean_bullet_point
    TEXT_PROCESSOR_AVAILABLE = True
except ImportError:
    TEXT_PROCESSOR_AVAILABLE = False
    def smart_truncate(text, max_len, suffix="..."):
        """Fallback smart truncation at word boundary"""
        if not text or len(text) <= max_len:
            return text
        truncated = text[:max_len]
        last_space = truncated.rfind(' ')
        if last_space > max_len * 0.7:
            return truncated[:last_space].rstrip('.,;:-') + suffix
        return truncated.rstrip('.,;:-') + suffix
    def fix_broken_words(text):
        return text if text else ""
    def clean_bullet_point(text):
        return text.strip() if text else ""

# Try to import image generator
try:
    from image_generator import get_slide_image, download_image, search_image
    IMAGE_GENERATION_AVAILABLE = True
except ImportError:
    IMAGE_GENERATION_AVAILABLE = False



def structure_content_with_ai(script_text, user_instructions="", min_slides=10, max_slides=20):
    """Use Ollama to structure content for slides (Ollama only)"""
    # Call Ollama API for structuring content (replace this with your actual Ollama call)
    result = ollama_structure_content(script_text, user_instructions, min_slides, max_slides)
    return result

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
    
    def create_title_slide(self, main_title, tagline=None, subtitle=None, presented_by=None):
        """Beautiful title slide with separate fields to prevent overflow"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        # Add decorative shape at top
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(0),
            Inches(10), Inches(1.2)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = self.colors["primary"]
        shape.line.fill.background()

        y = 1.3
        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(y), Inches(9), Inches(1.2))
        tf = title_box.text_frame
        tf.text = main_title or "Presentation"
        p = tf.paragraphs[0]
        p.font.size = Pt(40)
        p.font.bold = True
        p.font.color.rgb = self.colors["text"]
        p.font.name = 'Calibri'
        y += 1.1

        # Tagline (if present)
        if tagline:
            tagline_box = slide.shapes.add_textbox(Inches(0.5), Inches(y), Inches(9), Inches(0.7))
            tf_tag = tagline_box.text_frame
            tf_tag.text = tagline
            p_tag = tf_tag.paragraphs[0]
            p_tag.font.size = Pt(24)
            p_tag.font.color.rgb = self.colors["secondary"]
            p_tag.font.name = 'Calibri'
            p_tag.font.italic = True
            y += 0.7

        # Subtitle (if present)
        if subtitle:
            subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(y), Inches(9), Inches(0.7))
            tf_sub = subtitle_box.text_frame
            tf_sub.text = subtitle
            p_sub = tf_sub.paragraphs[0]
            p_sub.font.size = Pt(20)
            p_sub.font.color.rgb = self.colors["secondary"]
            p_sub.font.name = 'Calibri'
            y += 0.7

        # Presented by (if present)
        if presented_by:
            pb_box = slide.shapes.add_textbox(Inches(0.5), Inches(y), Inches(9), Inches(0.6))
            tf_pb = pb_box.text_frame
            tf_pb.text = f"Presented by: {presented_by}"
            p_pb = tf_pb.paragraphs[0]
            p_pb.font.size = Pt(18)
            p_pb.font.color.rgb = self.colors["text"]
            p_pb.font.name = 'Calibri'
            y += 0.6
        return slide
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

            # Clean and fix broken words first
            bullet_text = fix_broken_words(clean_bullet_point(bullet))

            # Smart truncate at word boundary (not mid-word)
            if len(bullet_text) > max_chars:
                bullet_text = smart_truncate(bullet_text, max_chars)

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
        
        # Title (with smart truncation)
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.15), Inches(9), Inches(0.7))
        tf = title_box.text_frame
        clean_title = fix_broken_words(title)
        tf.text = smart_truncate(clean_title, 70, "") if len(clean_title) > 70 else clean_title
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
            # Clean and smart truncate
            clean_text = fix_broken_words(clean_bullet_point(bullet))
            p.text = "● " + (smart_truncate(clean_text, 150) if len(clean_text) > 150 else clean_text)
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
    print(f"[INFO] Using template: {template_path}")
    
    # Structure content
    if use_ai:
        print("[AI] Using AI to structure content...")
        content = structure_content_with_ai(script_text, ai_instructions, min_slides, max_slides)
    else:
        print("[INFO] Using basic structuring...")
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
    print(f"[OK] PPT created from template: {output_path}")
    
    return True

def generate_beautiful_ppt(slides_or_text, output_path, color_scheme="corporate", use_ai=True, ai_instructions="", original_topic=None, template_path=None, min_slides=10, max_slides=20):
    """
    Generate beautiful PPT from structured slides or script text
    """
    print(f"DEBUG: Function called with original_topic={original_topic}, template_path={template_path}, slides={min_slides}-{max_slides}")
    # If input is a list of slides (structured)
    if isinstance(slides_or_text, list) and all(isinstance(slide, dict) for slide in slides_or_text):
        slides = slides_or_text
        designer = ModernPPTDesigner(scheme=color_scheme)
        # Title slide (use all available fields, pass separately)
        first = slides[0] if slides else {}
        main_title = first.get("main_title") or first.get("title") or original_topic or "Presentation"
        tagline = first.get("tagline") or ""
        subtitle = first.get("subtitle") or ""
        presented_by = first.get("presented_by") or ""
        designer.create_title_slide(main_title, tagline, subtitle, presented_by)
        # Content slides
        for slide in slides[1:]:
            designer.create_content_slide_with_image(slide.get("title", ""), slide.get("bullets", []), None)
        designer.create_end_slide()
        designer.save(output_path)
        print(f"[OK] Beautiful PPT created: {output_path}")
        return True
    # Otherwise, fallback to old logic
    # ...existing code...

if __name__ == "__main__":
    # Test
    sample_script = """
Uttar Pradesh's education system is undergoing major transformations.
The state is focusing on accessibility, technology, and skill development.
Operation Kayakalp aims to modernize schools.
Vocational education is being mandated in Classes 9 and 11.
    """
    
    generate_beautiful_ppt(sample_script, "test_beautiful.pptx", use_ai=False)
