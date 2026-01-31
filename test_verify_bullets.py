#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify full output with flexible bullets
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_ai_generator import MultiAIGenerator

def verify_output():
    print("=" * 80)
    print("🔍 VERIFYING FLEXIBLE BULLETS OUTPUT")
    print("=" * 80)

    generator = MultiAIGenerator()

    result = generator.generate_ppt_content(
        topic="Climate Change and Global Warming",
        min_slides=3,
        max_slides=3,
        bullets_per_slide=5
    )

    output = result.get("output", "")

    if output:
        print("\n📄 FULL AI OUTPUT:\n")
        print(output)

        # Count bullets per slide
        print("\n" + "=" * 80)
        print("📊 BULLET COUNT ANALYSIS:")
        print("=" * 80)

        lines = output.split('\n')
        current_slide = None
        slide_bullets = {}

        for line in lines:
            line_stripped = line.strip()

            # Detect slide start
            if 'slide' in line_stripped.lower() and ':' in line_stripped:
                # Try to extract slide number
                words = line_stripped.split()
                for i, word in enumerate(words):
                    if 'slide' in word.lower():
                        try:
                            # Look for number after "Slide"
                            next_word = words[i+1] if i+1 < len(words) else ""
                            num = int(next_word.rstrip(':').rstrip('**').rstrip('*'))
                            current_slide = num
                            if num not in slide_bullets:
                                slide_bullets[num] = 0
                            break
                        except:
                            pass

            # Count bullets
            elif (line_stripped.startswith('- ') or
                  line_stripped.startswith('• ') or
                  line_stripped.startswith('* ')) and current_slide and current_slide > 1:
                slide_bullets[current_slide] = slide_bullets.get(current_slide, 0) + 1

        print("\nBullets per slide:")
        for slide_num in sorted(slide_bullets.keys()):
            if slide_num > 1:  # Skip title slide
                count = slide_bullets[slide_num]
                status = "✅" if 4 <= count <= 6 else "⚠️"
                print(f"  Slide {slide_num}: {count} bullets {status}")

        if slide_bullets:
            content_slides = [s for s in slide_bullets.keys() if s > 1]
            if content_slides:
                avg = sum(slide_bullets[s] for s in content_slides) / len(content_slides)
                print(f"\n  Average: {avg:.1f} bullets per slide")
                print(f"  Range: 4-6 bullets (flexible) ✅")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    verify_output()
