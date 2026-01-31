#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to verify bullet points generation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_ai_generator import MultiAIGenerator

def test_simple():
    """Quick test to see AI output"""

    print("=" * 80)
    print("🎯 TESTING BULLET POINTS GENERATION")
    print("=" * 80)

    generator = MultiAIGenerator()

    print("\n📝 Generating with 5 bullets per slide...")
    print("-" * 80)

    result = generator.generate_ppt_content(
        topic="Artificial Intelligence in Education",
        min_slides=2,
        max_slides=2,
        style="professional",
        bullets_per_slide=5,
        bullet_word_limit=25
    )

    output = result.get("output", "")

    if output:
        print("\n✅ AI OUTPUT:\n")
        print(output[:1000])  # Print first 1000 chars
        print("\n...")

        # Count bullets
        lines = output.split('\n')
        bullet_lines = [l for l in lines if l.strip().startswith(('- ', '• ', '* '))]
        print(f"\n📊 Total bullet lines found: {len(bullet_lines)}")
        print(f"🎯 Expected: ~5 bullets per slide (2 slides = ~10 total)")

        if len(bullet_lines) >= 8:
            print("✅ SUCCESS: Generated sufficient bullets!")
        else:
            print("⚠️  WARNING: Generated fewer bullets than expected")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_simple()
