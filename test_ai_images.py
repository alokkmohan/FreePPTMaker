#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test AI Image Generation in PPT
Tests the complete flow: Slide Text → Mistral Prompt → HF Image → PPT
"""

from ai_ppt_generator import generate_beautiful_ppt

print("="*70)
print("🎨 TESTING AI IMAGE GENERATION FOR PPT")
print("="*70)

# Sample slides with content
test_slides = [
    {
        "slide_number": 1,
        "title": "Title Slide",
        "main_title": "AI-Powered Healthcare Revolution",
        "tagline": "Transforming Patient Care Through Technology",
        "subtitle": "A Comprehensive Overview",
        "presented_by": "AI PPT Generator"
    },
    {
        "slide_number": 2,
        "title": "Introduction to AI in Healthcare",
        "bullets": [
            "Artificial Intelligence is revolutionizing healthcare by enabling better diagnostics, personalized treatment plans, and improved patient outcomes",
            "AI-powered systems can analyze medical images with high accuracy, predict disease progression, and assist doctors in making informed decisions",
            "The integration of AI in healthcare is improving efficiency, reducing costs, and saving lives across the globe"
        ]
    },
    {
        "slide_number": 3,
        "title": "Key Applications",
        "bullets": [
            "Medical imaging and diagnostics: AI analyzes X-rays, MRIs, and CT scans to detect diseases early",
            "Drug discovery: Machine learning accelerates the development of new medications and treatments",
            "Personalized medicine: AI tailors treatment plans based on individual patient data and genetics",
            "Virtual health assistants: Chatbots provide 24/7 patient support and medical advice"
        ]
    },
    {
        "slide_number": 4,
        "title": "Benefits and Impact",
        "bullets": [
            "Improved diagnostic accuracy reduces medical errors and improves patient outcomes significantly",
            "Cost reduction through automation and efficiency gains in healthcare delivery systems",
            "Enhanced patient experience with personalized care and faster treatment options",
            "Predictive analytics help prevent diseases and enable early intervention strategies"
        ]
    }
]

print("\n📊 Test Slides:")
for slide in test_slides[1:]:  # Skip title slide
    print(f"\n  Slide {slide['slide_number']}: {slide['title']}")
    bullets = slide.get('bullets', [])
    if bullets:
        print(f"    Bullets: {len(bullets)}")

print("\n" + "="*70)
print("⚙️  GENERATION OPTIONS")
print("="*70)

print("\n1. Generate PPT WITHOUT AI images (fast)")
print("2. Generate PPT WITH AI images (requires HF API token)")

choice = input("\nYour choice (1 or 2): ").strip()

if choice == "2":
    generate_images = True
    print("\n✅ AI image generation ENABLED")
    print("\n💡 Make sure you have:")
    print("   - HUGGINGFACE_API_TOKEN in .env file")
    print("   - MISTRAL_API_KEY in .env file (optional, for better prompts)")
else:
    generate_images = False
    print("\n✅ AI image generation DISABLED (fast mode)")

print("\n" + "="*70)
print("🚀 GENERATING PPT...")
print("="*70)

# Generate PPT
success = generate_beautiful_ppt(
    test_slides,
    output_path="test_output/ai_healthcare_demo.pptx",
    color_scheme="corporate",
    generate_ai_images=generate_images
)

print("\n" + "="*70)
if success:
    print("✅ SUCCESS! PPT Generated")
    print("="*70)
    print("\n📁 Output file: test_output/ai_healthcare_demo.pptx")

    if generate_images:
        print("\n🎨 AI Images:")
        print("   - Check temp_images/ folder for generated images")
        print("   - Images are embedded in the PPT slides")
else:
    print("❌ FAILED to generate PPT")
    print("="*70)

print("\n💡 Tips:")
print("   1. Open the PPT to see the results")
print("   2. Each slide has AI-generated images (if enabled)")
print("   3. Check temp_images/ folder to see individual images")
