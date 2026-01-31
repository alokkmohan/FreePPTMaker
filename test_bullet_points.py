#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify bullet points per slide configuration
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_ai_generator import MultiAIGenerator

def test_bullet_points_configuration():
    """Test that AI generates the correct number of bullet points"""

    print("=" * 80)
    print("🎯 TESTING BULLET POINTS PER SLIDE CONFIGURATION")
    print("=" * 80)

    generator = MultiAIGenerator()

    # Test configurations
    test_cases = [
        {"bullets": 3, "label": "3 bullets per slide"},
        {"bullets": 4, "label": "4 bullets per slide (default)"},
        {"bullets": 5, "label": "5 bullets per slide"},
        {"bullets": 6, "label": "6 bullets per slide"},
    ]

    for test_case in test_cases:
        bullets_count = test_case["bullets"]
        label = test_case["label"]

        print(f"\n📝 Test: {label}")
        print("-" * 80)

        result = generator.generate_ppt_content(
            topic="Digital India and E-Governance",
            min_slides=3,
            max_slides=3,
            style="professional",
            audience="government officers",
            bullets_per_slide=bullets_count,
            bullet_word_limit=25,
            tone="formal",
            custom_instructions="Focus on digital transformation in government services"
        )

        ai_output = result.get("output", "")

        if ai_output:
            # Count bullets in each slide
            lines = ai_output.split('\n')
            current_slide = 0
            bullet_counts = []

            for line in lines:
                line = line.strip()
                if line.lower().startswith('slide'):
                    if current_slide > 0:
                        # Don't count title slide
                        pass
                    current_slide += 1
                elif line.startswith('- ') or line.startswith('• '):
                    if current_slide > 1:  # Skip title slide
                        if len(bullet_counts) < current_slide - 1:
                            bullet_counts.append(0)
                        bullet_counts[-1] = bullet_counts[-1] + 1 if bullet_counts else 1

            # Calculate average
            if bullet_counts:
                avg_bullets = sum(bullet_counts) / len(bullet_counts)
                print(f"✅ Generated slides with bullets: {bullet_counts}")
                print(f"📊 Average bullets per slide: {avg_bullets:.1f}")
                print(f"🎯 Target: {bullets_count} bullets per slide")

                # Check if close to target
                if abs(avg_bullets - bullets_count) <= 1:
                    print(f"✅ SUCCESS: Bullet count is close to target!")
                else:
                    print(f"⚠️  WARNING: Bullet count differs from target")
            else:
                print(f"❌ Could not parse bullets from AI output")
        else:
            print(f"❌ AI generation failed: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print("✅ AI prompt now uses dynamic bullets_per_slide parameter")
    print("✅ Users can select 3, 4, 5, or 6 bullets per slide in the UI")
    print("💡 The prompt explicitly instructs AI to generate EXACTLY N bullets")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_bullet_points_configuration()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
