#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for AI-powered smart title generation
Tests the new generate_smart_title() function
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_ai_generator import MultiAIGenerator

def test_smart_title_generation():
    """Test smart title generation with sample content"""

    print("=" * 80)
    print("🎯 TESTING AI-POWERED SMART TITLE GENERATION")
    print("=" * 80)

    # Initialize generator
    generator = MultiAIGenerator()

    # Test Case 1: English content about AI in Healthcare
    print("\n📝 Test Case 1: AI in Healthcare (English)")
    print("-" * 80)

    sample_content_en = """
    Artificial Intelligence in Healthcare

    Artificial Intelligence (AI) is transforming the healthcare industry by enabling
    better diagnostics, personalized treatment plans, and improved patient outcomes.
    AI-powered systems can analyze medical images with high accuracy, predict disease
    progression, and assist doctors in making informed decisions.

    Key applications include:
    - Medical imaging and diagnostics
    - Drug discovery and development
    - Personalized medicine
    - Virtual health assistants
    - Predictive analytics for patient care
    """

    result_en = generator.generate_smart_title(
        content=sample_content_en,
        language="English",
        style="professional"
    )

    print(f"✅ Success: {result_en.get('success')}")
    print(f"🤖 AI Source: {result_en.get('ai_source', 'Unknown')}")
    print(f"\n📌 Main Title: {result_en.get('main_title')}")
    print(f"💫 Tagline: {result_en.get('tagline')}")
    print(f"📄 Subtitle: {result_en.get('subtitle')}")

    # Test Case 2: Hindi content about Digital India
    print("\n\n📝 Test Case 2: Digital India (Hindi)")
    print("-" * 80)

    sample_content_hi = """
    डिजिटल इंडिया

    डिजिटल इंडिया भारत सरकार की एक महत्वाकांक्षी योजना है जो देश को डिजिटल रूप
    से सशक्त समाज और ज्ञान अर्थव्यवस्था में बदलने के लिए शुरू की गई है। इस
    कार्यक्रम का उद्देश्य सभी नागरिकों को डिजिटल सेवाओं तक पहुंच प्रदान करना है।

    मुख्य उद्देश्य:
    - डिजिटल बुनियादी ढांचे का विकास
    - ई-गवर्नेंस सेवाओं का विस्तार
    - डिजिटल साक्षरता को बढ़ावा
    - ई-कॉमर्स और डिजिटल भुगतान को प्रोत्साहन
    """

    result_hi = generator.generate_smart_title(
        content=sample_content_hi,
        language="Hindi",
        style="corporate"
    )

    print(f"✅ Success: {result_hi.get('success')}")
    print(f"🤖 AI Source: {result_hi.get('ai_source', 'Unknown')}")
    print(f"\n📌 Main Title: {result_hi.get('main_title')}")
    print(f"💫 Tagline: {result_hi.get('tagline')}")
    print(f"📄 Subtitle: {result_hi.get('subtitle')}")

    # Test Case 3: Short topic input
    print("\n\n📝 Test Case 3: Short Topic - Climate Change")
    print("-" * 80)

    sample_content_short = "Climate Change and Global Warming"

    result_short = generator.generate_smart_title(
        content=sample_content_short,
        language="English",
        style="creative"
    )

    print(f"✅ Success: {result_short.get('success')}")
    print(f"🤖 AI Source: {result_short.get('ai_source', 'Unknown')}")
    print(f"\n📌 Main Title: {result_short.get('main_title')}")
    print(f"💫 Tagline: {result_short.get('tagline')}")
    print(f"📄 Subtitle: {result_short.get('subtitle')}")

    # Summary
    print("\n\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    all_success = all([
        result_en.get('success'),
        result_hi.get('success'),
        result_short.get('success')
    ])

    if all_success:
        print("✅ All tests passed!")
        print("🎉 Smart title generation is working correctly!")
    else:
        print("⚠️ Some tests failed. Check the output above.")
        print(f"   English: {'✅' if result_en.get('success') else '❌'}")
        print(f"   Hindi: {'✅' if result_hi.get('success') else '❌'}")
        print(f"   Short: {'✅' if result_short.get('success') else '❌'}")

    print("\n💡 Note: If AI generation failed, fallback titles were used.")
    print("   Check your MISTRAL_API_KEY in .env file for full AI-powered generation.")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_smart_title_generation()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
