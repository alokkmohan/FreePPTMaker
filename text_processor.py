#!/usr/bin/env python3
"""
Text Post-Processing for PPT Generation
Fixes common AI output issues like broken words, incomplete sentences, etc.
"""

import re

def fix_broken_words(text):
    """Fix words that are incorrectly broken with spaces"""
    if not text:
        return text

    # Common patterns of broken words (space in middle of word)
    # Pattern: lowercase + space + lowercase (in middle of word)
    # e.g., "Consult ant" -> "Consultant", "Specialis t" -> "Specialist"

    # Fix pattern: word ending with space + 1-3 letters
    text = re.sub(r'(\w+)\s+([a-z]{1,3})(?=\s|$|[.,;:!?])', r'\1\2', text)

    # Fix pattern: capital letter + space + lowercase continuation
    text = re.sub(r'([A-Z][a-z]+)\s+([a-z]{1,4})(?=\s|$|[.,;:!?])', r'\1\2', text)

    # Fix common broken words explicitly
    broken_words = {
        'Consult ant': 'Consultant',
        'Specialis t': 'Specialist',
        'Manage ment': 'Management',
        'Develop ment': 'Development',
        'Govern ment': 'Government',
        'Depart ment': 'Department',
        'Require ment': 'Requirement',
        'Environ ment': 'Environment',
        'Achieve ment': 'Achievement',
        'Improve ment': 'Improvement',
        'Engage ment': 'Engagement',
        'Employ ment': 'Employment',
        'Assess ment': 'Assessment',
        'Invest ment': 'Investment',
        'Treat ment': 'Treatment',
        'Docu ment': 'Document',
        'Ele ment': 'Element',
        'Funda mental': 'Fundamental',
        'Experi mental': 'Experimental',
        'Environ mental': 'Environmental',
        'Govern mental': 'Governmental',
        'Depart mental': 'Departmental',
        'Incre mental': 'Incremental',
        'Supple mental': 'Supplemental',
        'Senti mental': 'Sentimental',
        'Techno logy': 'Technology',
        'Metho dology': 'Methodology',
        'Psycho logy': 'Psychology',
        'Bio logy': 'Biology',
        'Socio logy': 'Sociology',
        'Ideo logy': 'Ideology',
        'Effici ency': 'Efficiency',
        'Suffici ency': 'Sufficiency',
        'Defici ency': 'Deficiency',
        'Profici ency': 'Proficiency',
        'Trans parency': 'Transparency',
        'Compe tency': 'Competency',
        'Consis tency': 'Consistency',
        'Resi liency': 'Resiliency',
        'Organi zation': 'Organization',
        'Imple mentation': 'Implementation',
        'Commu nication': 'Communication',
        'Infor mation': 'Information',
        'Trans formation': 'Transformation',
        'Digi tization': 'Digitization',
        'Auto mation': 'Automation',
        'Optimi zation': 'Optimization',
        'Integra tion': 'Integration',
        'Innova tion': 'Innovation',
        'Collabo ration': 'Collaboration',
        'Coordi nation': 'Coordination',
        'Regula tion': 'Regulation',
        'Opera tion': 'Operation',
        'Administra tion': 'Administration',
        'Applica tion': 'Application',
        'Educa tion': 'Education',
        'Evalua tion': 'Evaluation',
    }

    for broken, fixed in broken_words.items():
        text = text.replace(broken, fixed)
        text = text.replace(broken.lower(), fixed.lower())

    return text


def smart_truncate(text, max_length, suffix="..."):
    """Truncate text at word boundary, not mid-word"""
    if not text or len(text) <= max_length:
        return text

    # Find last space before max_length
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')

    if last_space > max_length * 0.7:  # At least 70% of max length
        truncated = truncated[:last_space]

    # Remove trailing punctuation that looks incomplete
    truncated = truncated.rstrip('.,;:-')

    return truncated.strip() + suffix


def complete_sentence(text):
    """Ensure text ends with complete sentence"""
    if not text:
        return text

    text = text.strip()

    # If already ends with sentence-ending punctuation
    if text[-1] in '.!?':
        return text

    # Find last sentence ending
    last_period = text.rfind('.')
    last_exclaim = text.rfind('!')
    last_question = text.rfind('?')

    last_sentence_end = max(last_period, last_exclaim, last_question)

    # If found a sentence ending after 60% of text, use it
    if last_sentence_end > len(text) * 0.6:
        return text[:last_sentence_end + 1]

    # Otherwise, add period
    return text + "."


def clean_bullet_point(bullet):
    """Clean and fix a single bullet point"""
    if not bullet:
        return bullet

    # Remove leading/trailing whitespace
    bullet = bullet.strip()

    # Remove common bullet prefixes (we add our own)
    bullet = re.sub(r'^[-*•●◦▪▸►]\s*', '', bullet)
    bullet = re.sub(r'^\d+[.)]\s*', '', bullet)

    # Fix broken words
    bullet = fix_broken_words(bullet)

    # Fix multiple spaces
    bullet = re.sub(r'\s+', ' ', bullet)

    # Fix common formatting issues
    bullet = bullet.replace(' ,', ',')
    bullet = bullet.replace(' .', '.')
    bullet = bullet.replace(' :', ':')
    bullet = bullet.replace('( ', '(')
    bullet = bullet.replace(' )', ')')

    # Capitalize first letter
    if bullet and bullet[0].islower():
        bullet = bullet[0].upper() + bullet[1:]

    return bullet


def process_slide_content(title, bullets, max_title_len=70, max_bullet_len=180):
    """Process and clean slide content"""
    # Clean title
    title = fix_broken_words(title.strip()) if title else "Slide"
    title = smart_truncate(title, max_title_len, "")

    # Clean bullets
    cleaned_bullets = []
    for bullet in bullets:
        if not bullet or not bullet.strip():
            continue

        cleaned = clean_bullet_point(bullet)

        # Smart truncate (word boundary)
        if len(cleaned) > max_bullet_len:
            cleaned = smart_truncate(cleaned, max_bullet_len)

        if cleaned and len(cleaned) > 10:  # Skip very short bullets
            cleaned_bullets.append(cleaned)

    return title, cleaned_bullets


def validate_slide_structure(slides):
    """Validate and fix slide structure"""
    valid_slides = []

    for slide in slides:
        if not isinstance(slide, dict):
            continue

        title = slide.get('title', '').strip()
        bullets = slide.get('content', slide.get('bullets', []))

        # Ensure bullets is a list
        if isinstance(bullets, str):
            bullets = [b.strip() for b in bullets.split('\n') if b.strip()]

        # Skip slides with no title and no content
        if not title and not bullets:
            continue

        # Process content
        title, bullets = process_slide_content(title, bullets)

        # Ensure at least 2 bullets per slide
        if len(bullets) < 2:
            continue

        valid_slides.append({
            'title': title,
            'content': bullets,
            'type': slide.get('type', 'content')
        })

    return valid_slides


def post_process_ai_response(content_dict):
    """Post-process entire AI response"""
    if not content_dict or not isinstance(content_dict, dict):
        return content_dict

    # Fix title
    if content_dict.get('title'):
        content_dict['title'] = fix_broken_words(content_dict['title'])

    # Fix subtitle
    if content_dict.get('subtitle'):
        content_dict['subtitle'] = fix_broken_words(content_dict['subtitle'])

    # Fix slides
    if content_dict.get('slides'):
        content_dict['slides'] = validate_slide_structure(content_dict['slides'])

    return content_dict
