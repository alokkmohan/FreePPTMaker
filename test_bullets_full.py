#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full output test to verify bullet points
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_ai_generator import MultiAIGenerator

def test_full_output():
    """See full AI output"""

    print("=" * 80)
    print("🎯 FULL BULLET POINTS TEST")
    print("=" * 80)

    generator = MultiAIGenerator()

    # Test with 5 bullets
    print("\n📝 Test 1: Generating with 5 bullets per slide")
    print("-" * 80)

    result = generator.generate_ppt_content(
        topic="Cloud Computing Basics",
        min_slides=3,  # Title + 2 content slides
        max_slides=3,
        bullets_per_slide=5
    )

    output = result.get("output", "")

    if output:
        print("\n✅ FULL AI OUTPUT:\n")
        print(output)

        # Analyze each slide
        lines = output.split('\n')
        current_slide = None
        slide_bullets = {}

        for line in lines:
            line = line.strip()
            if line.lower().startswith('slide') or line.startswith('**Slide'):
                # Extract slide number
                if 'slide' in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.lower() == 'slide' and i+1 < len(parts):
                            try:
                                num = int(parts[i+1].rstrip(':').rstrip('**'))
                                current_slide = num
                                slide_bullets[num] = 0
                                break
                            except:
                                pass
            elif (line.startswith('- ') or line.startswith('• ') or line.startswith('* ')) and current_slide:
                if current_slide > 1:  # Skip title slide
                    slide_bullets[current_slide] = slide_bullets.get(current_slide, 0) + 1

        print("\n" + "=" * 80)
        print("📊 BULLET COUNT PER SLIDE:")
        print("=" * 80)
        for slide_num, count in sorted(slide_bullets.items()):
            if slide_num > 1:  # Skip title slide
                status = "✅" if count == 5 else "⚠️ "
                print(f"  Slide {slide_num}: {count} bullets {status}")

        total = sum(count for num, count in slide_bullets.items() if num > 1)
        expected = (len([n for n in slide_bullets.keys() if n > 1])) * 5
        print(f"\n  Total: {total} bullets (Expected: {expected})")

        if total == expected:
            print("\n✅ SUCCESS: Generated exactly 5 bullets per slide!")
        else:
            print(f"\n⚠️  Generated {total} bullets, expected {expected}")

    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_full_output()
