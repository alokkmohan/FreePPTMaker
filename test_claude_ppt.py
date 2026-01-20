#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TEST SCRIPT - Claude-Powered PPT Generation
Demonstrates how to use the Claude integration
"""

import os
import sys
from claude_ppt_generator import create_ppt_from_topic, create_ppt_from_file

def test_topic_generation():
    """Test 1: Generate PPT from a topic"""
    print("\n" + "="*60)
    print("TEST 1: Topic-based PPT Generation")
    print("="*60)
    
    topic = "Digital Transformation in Government Services"
    output_path = "test_topic_presentation.pptx"
    
    print(f"\n📝 Topic: {topic}")
    print(f"📊 Style: Government")
    print(f"🎯 Audience: Government officials")
    print(f"📄 Slides: 12-15")
    
    success = create_ppt_from_topic(
        topic=topic,
        output_path=output_path,
        style="government",
        min_slides=12,
        max_slides=15,
        audience="government",
        presenter="Alok Mohan",
        custom_instructions="Focus on policy implications, include data from Indian context, highlight Digital India initiatives"
    )
    
    if success:
        print(f"\n✅ SUCCESS! Presentation saved: {output_path}")
        print(f"📊 File size: {os.path.getsize(output_path) / 1024:.2f} KB")
        return True
    else:
        print("\n❌ FAILED to generate presentation")
        return False


def test_file_upload():
    """Test 2: Generate PPT from uploaded file"""
    print("\n" + "="*60)
    print("TEST 2: File-based PPT Generation")
    print("="*60)
    
    # Check if test file exists
    test_file = "test_document.docx"  # Replace with your test file
    
    if not os.path.exists(test_file):
        print(f"\n⚠️  Test file not found: {test_file}")
        print("   Skipping file upload test")
        print("   To test: Create a Word/PDF document and update test_file path")
        return None
    
    output_path = "test_file_presentation.pptx"
    
    print(f"\n📄 Input File: {test_file}")
    print(f"📊 Style: Professional")
    print(f"🎯 Audience: Executives")
    print(f"📄 Slides: 10-12")
    
    success = create_ppt_from_file(
        file_path=test_file,
        output_path=output_path,
        style="professional",
        min_slides=10,
        max_slides=12,
        audience="executives",
        presenter="Alok Mohan"
    )
    
    if success:
        print(f"\n✅ SUCCESS! Presentation saved: {output_path}")
        print(f"📊 File size: {os.path.getsize(output_path) / 1024:.2f} KB")
        return True
    else:
        print("\n❌ FAILED to generate presentation")
        return False


def test_different_styles():
    """Test 3: Generate PPTs with different styles"""
    print("\n" + "="*60)
    print("TEST 3: Multiple Style Variations")
    print("="*60)
    
    topic = "Cloud Computing Basics"
    styles = ["professional", "corporate", "technical"]
    
    results = {}
    
    for style in styles:
        print(f"\n🎨 Generating {style.upper()} style...")
        
        output_path = f"test_{style}_presentation.pptx"
        
        success = create_ppt_from_topic(
            topic=topic,
            output_path=output_path,
            style=style,
            min_slides=8,
            max_slides=10,
            audience="general"
        )
        
        results[style] = success
        
        if success:
            print(f"   ✅ {style}: {output_path}")
        else:
            print(f"   ❌ {style}: Failed")
    
    # Summary
    print("\n📊 Summary:")
    for style, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"   {style.ljust(15)}: {status}")
    
    return all(results.values())


def quick_test():
    """Quick test with minimal slides"""
    print("\n" + "="*60)
    print("QUICK TEST: Fast PPT Generation")
    print("="*60)
    
    topic = "Introduction to Python Programming"
    output_path = "quick_test.pptx"
    
    print(f"\n📝 Topic: {topic}")
    print(f"📄 Slides: 5-7 (quick generation)")
    
    success = create_ppt_from_topic(
        topic=topic,
        output_path=output_path,
        style="professional",
        min_slides=5,
        max_slides=7,
        audience="students"
    )
    
    if success:
        print(f"\n✅ Quick test passed! File: {output_path}")
        return True
    else:
        print("\n❌ Quick test failed")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 CLAUDE-POWERED PPT GENERATOR - TEST SUITE")
    print("="*60)
    
    # Check API key
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: CLAUDE_API_KEY not found in environment")
        print("   Set it with: export CLAUDE_API_KEY='your-key-here'")
        print("   Or it will use the hardcoded key in the script")
    else:
        print(f"\n✅ API Key found: {api_key[:20]}...")
    
    # Menu
    print("\n📋 Available Tests:")
    print("   1. Quick Test (5-7 slides, fast)")
    print("   2. Topic Generation (12-15 slides)")
    print("   3. File Upload (requires test file)")
    print("   4. Multiple Styles (3 presentations)")
    print("   5. Run All Tests")
    print("   0. Exit")
    
    choice = input("\nEnter your choice (0-5): ").strip()
    
    if choice == "1":
        quick_test()
    elif choice == "2":
        test_topic_generation()
    elif choice == "3":
        test_file_upload()
    elif choice == "4":
        test_different_styles()
    elif choice == "5":
        print("\n🏃 Running all tests...\n")
        results = {
            "Quick Test": quick_test(),
            "Topic Generation": test_topic_generation(),
            "File Upload": test_file_upload(),
            "Multiple Styles": test_different_styles()
        }
        
        print("\n" + "="*60)
        print("📊 FINAL RESULTS")
        print("="*60)
        for test_name, result in results.items():
            if result is None:
                status = "⏭️  Skipped"
            elif result:
                status = "✅ Passed"
            else:
                status = "❌ Failed"
            print(f"   {test_name.ljust(20)}: {status}")
    
    elif choice == "0":
        print("\n👋 Goodbye!")
        return
    else:
        print("\n❌ Invalid choice")
        return
    
    print("\n" + "="*60)
    print("✅ Test execution complete!")
    print("="*60)
    print("\nGenerated files:")
    for file in os.listdir('.'):
        if file.endswith('.pptx') and file.startswith('test_'):
            size = os.path.getsize(file) / 1024
            print(f"   📄 {file} ({size:.2f} KB)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
