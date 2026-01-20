#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Claude Content Analyzer
Professional content analysis and PPT structure generation using Claude API
"""

import anthropic
import os
from typing import Dict, List, Optional
import json
import docx
import PyPDF2
from pathlib import Path

# Claude API configuration
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "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")

class ClaudeContentAnalyzer:
    """Analyze content and generate professional PPT structures using Claude"""
    
    def __init__(self, api_key: str = None):
        """Initialize Claude client"""
        self.api_key = api_key or CLAUDE_API_KEY
        if not self.api_key:
            raise ValueError("Claude API key not found. Set CLAUDE_API_KEY environment variable.")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from uploaded files (Word/PDF/Text)"""
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.docx':
                doc = docx.Document(file_path)
                text = '\n'.join([para.text for para in doc.paragraphs])
                return text
            
            elif file_ext == '.pdf':
                text = ""
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text
            
            elif file_ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        
        except Exception as e:
            raise Exception(f"Error extracting text from file: {str(e)}")
    
    def analyze_for_ppt(
        self, 
        content: str, 
        style: str = "professional",
        min_slides: int = 10,
        max_slides: int = 20,
        audience: str = "general",
        custom_instructions: str = ""
    ) -> Dict:
        """
        Analyze content and generate PPT structure using Claude
        
        Args:
            content: Input text content
            style: PPT style (professional/government/corporate/technical)
            min_slides: Minimum number of slides
            max_slides: Maximum number of slides
            audience: Target audience (general/executives/technical/government)
            custom_instructions: Additional user instructions
        
        Returns:
            Dict with structured PPT content
        """
        
        # Style-specific prompts
        style_guidelines = {
            "professional": "Use clear, concise language. Focus on key points. Professional business tone.",
            "government": "Use formal language. Policy-focused. Include data and statistics. Official tone aligned with government presentations.",
            "corporate": "Business-oriented. ROI-focused. Executive summary style. Data-driven insights.",
            "technical": "Detailed technical explanations. Include diagrams descriptions. Technical terminology appropriate.",
            "academic": "Research-oriented. Citations and references. Scholarly tone."
        }
        
        audience_guidelines = {
            "general": "Explain concepts clearly. Avoid jargon. Accessible to all.",
            "executives": "Focus on high-level insights. Strategic implications. Business impact.",
            "technical": "Technical depth. Implementation details. Architecture and design.",
            "government": "Policy implications. Compliance. Public benefit. Formal structure.",
            "students": "Educational focus. Clear explanations. Learning objectives."
        }
        
        style_guide = style_guidelines.get(style, style_guidelines["professional"])
        audience_guide = audience_guidelines.get(audience, audience_guidelines["general"])
        
        # Build Claude prompt
        prompt = f"""You are an expert presentation designer and content strategist. Analyze the following content and create a professional PowerPoint presentation structure.

**CONTENT TO ANALYZE:**
{content[:15000]}  # Limit for context window

**PRESENTATION REQUIREMENTS:**
- Style: {style.upper()}
- Target Audience: {audience.upper()}
- Number of Slides: {min_slides} to {max_slides} slides
- Style Guidelines: {style_guide}
- Audience Guidelines: {audience_guide}
{f"- Custom Instructions: {custom_instructions}" if custom_instructions else ""}

**YOUR TASK:**
Create a comprehensive, professional presentation structure with the following:

1. **Title Slide**: Catchy, professional title and subtitle
2. **Content Slides**: {min_slides-2} to {max_slides-2} slides covering all key points
3. **Conclusion Slide**: Strong closing with key takeaways

**OUTPUT FORMAT (JSON):**
Return ONLY a valid JSON object with this exact structure:

{{
  "title": "Presentation Title",
  "subtitle": "Presentation Subtitle",
  "slides": [
    {{
      "slide_number": 1,
      "title": "Slide Title",
      "content": [
        "Bullet point 1 - detailed content",
        "Bullet point 2 - detailed content",
        "Bullet point 3 - detailed content"
      ],
      "speaker_notes": "Additional context for presenter (2-3 sentences)"
    }}
  ]
}}

**CRITICAL REQUIREMENTS:**
1. Each slide should have 3-5 bullet points
2. Bullet points should be detailed (10-15 words each), not just short phrases
3. Include specific data, numbers, examples where possible from the source content
4. Maintain logical flow between slides
5. Speaker notes should provide additional context
6. Return ONLY valid JSON - no markdown formatting, no code blocks
7. Ensure {min_slides} to {max_slides} total slides (including title)

Generate the presentation structure now:"""

        try:
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract response
            response_text = message.content[0].text.strip()
            
            # Clean response (remove markdown formatting if present)
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            ppt_structure = json.loads(response_text)
            
            # Validate structure
            if "slides" not in ppt_structure:
                raise ValueError("Invalid response: missing 'slides' key")
            
            return ppt_structure
        
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Claude response as JSON: {str(e)}\nResponse: {response_text[:500]}")
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    def generate_from_topic(
        self,
        topic: str,
        style: str = "professional",
        min_slides: int = 10,
        max_slides: int = 20,
        audience: str = "general",
        custom_instructions: str = ""
    ) -> Dict:
        """
        Generate PPT structure directly from a topic (without file upload)
        
        Args:
            topic: Presentation topic
            style: PPT style
            min_slides: Minimum slides
            max_slides: Maximum slides
            audience: Target audience
            custom_instructions: Additional instructions
        
        Returns:
            Dict with structured PPT content
        """
        
        # First, generate comprehensive content on the topic using Claude
        content_prompt = f"""You are an expert researcher and content writer. Create comprehensive, factual content on the following topic for a presentation:

**TOPIC:** {topic}

**REQUIREMENTS:**
- Length: Sufficient for {min_slides} to {max_slides} presentation slides
- Include specific facts, statistics, real data
- Provide concrete examples and case studies
- Use authoritative, professional tone
- Include actual company names, technologies, specific numbers where relevant
- Cite recent developments and trends
{f"- Additional Requirements: {custom_instructions}" if custom_instructions else ""}

**CONTENT STRUCTURE:**
1. Introduction/Overview
2. Key Concepts/Background
3. Main Points (multiple sections)
4. Applications/Examples
5. Challenges/Considerations
6. Future Outlook
7. Conclusion

Write comprehensive, detailed content covering all these aspects. Each section should be substantial with specific details.

Generate the content now:"""
        
        try:
            # Generate content
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": content_prompt}
                ]
            )
            
            content = message.content[0].text.strip()
            
            # Now analyze this content for PPT structure
            return self.analyze_for_ppt(
                content=content,
                style=style,
                min_slides=min_slides,
                max_slides=max_slides,
                audience=audience,
                custom_instructions=custom_instructions
            )
        
        except Exception as e:
            raise Exception(f"Failed to generate content from topic: {str(e)}")
    
    def enhance_existing_content(
        self,
        existing_content: str,
        improvement_areas: List[str] = None
    ) -> str:
        """
        Enhance existing presentation content
        
        Args:
            existing_content: Current presentation content
            improvement_areas: Areas to improve (e.g., ["clarity", "data", "examples"])
        
        Returns:
            Enhanced content
        """
        
        areas = improvement_areas or ["clarity", "detail", "professionalism"]
        areas_str = ", ".join(areas)
        
        prompt = f"""Improve the following presentation content focusing on: {areas_str}

**CURRENT CONTENT:**
{existing_content}

**IMPROVEMENTS NEEDED:**
- Make content more clear and professional
- Add specific data and statistics where appropriate
- Improve flow and transitions
- Enhance with concrete examples
- Maintain structure while improving quality

Return the enhanced content:"""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text.strip()
        
        except Exception as e:
            raise Exception(f"Failed to enhance content: {str(e)}")


# Convenience functions for easy integration

def analyze_file_for_ppt(
    file_path: str,
    style: str = "professional",
    min_slides: int = 10,
    max_slides: int = 20,
    audience: str = "general",
    custom_instructions: str = "",
    api_key: str = None
) -> Dict:
    """
    Convenience function: Analyze uploaded file and generate PPT structure
    
    Args:
        file_path: Path to uploaded file (Word/PDF/Text)
        style: PPT style
        min_slides: Minimum slides
        max_slides: Maximum slides
        audience: Target audience
        custom_instructions: Additional instructions
        api_key: Claude API key (optional)
    
    Returns:
        Dict with structured PPT content
    """
    analyzer = ClaudeContentAnalyzer(api_key=api_key)
    content = analyzer.extract_text_from_file(file_path)
    return analyzer.analyze_for_ppt(
        content=content,
        style=style,
        min_slides=min_slides,
        max_slides=max_slides,
        audience=audience,
        custom_instructions=custom_instructions
    )


def generate_ppt_from_topic(
    topic: str,
    style: str = "professional",
    min_slides: int = 10,
    max_slides: int = 20,
    audience: str = "general",
    custom_instructions: str = "",
    api_key: str = None
) -> Dict:
    """
    Convenience function: Generate PPT structure from topic
    
    Args:
        topic: Presentation topic
        style: PPT style
        min_slides: Minimum slides
        max_slides: Maximum slides
        audience: Target audience
        custom_instructions: Additional instructions
        api_key: Claude API key (optional)
    
    Returns:
        Dict with structured PPT content
    """
    analyzer = ClaudeContentAnalyzer(api_key=api_key)
    return analyzer.generate_from_topic(
        topic=topic,
        style=style,
        min_slides=min_slides,
        max_slides=max_slides,
        audience=audience,
        custom_instructions=custom_instructions
    )


# Example usage
if __name__ == "__main__":
    # Test with a topic
    try:
        result = generate_ppt_from_topic(
            topic="Artificial Intelligence in Healthcare",
            style="professional",
            min_slides=12,
            max_slides=15,
            audience="executives"
        )
        
        print("✅ Successfully generated PPT structure:")
        print(f"Title: {result['title']}")
        print(f"Number of slides: {len(result['slides'])}")
        print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
