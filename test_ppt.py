#!/usr/bin/env python3
"""
Test script to verify generate_beautiful_ppt function
"""

import sys
import inspect
from ai_ppt_generator import generate_beautiful_ppt

# Check function signature
print("Testing generate_beautiful_ppt function...")
print("-" * 50)

sig = inspect.signature(generate_beautiful_ppt)
print(f"Function signature: {sig}")
print(f"\nParameters:")
for param_name, param in sig.parameters.items():
    print(f"  - {param_name}: {param.default if param.default != inspect.Parameter.empty else 'required'}")

print("\n" + "-" * 50)
print("Testing function call with minimal parameters...")

test_script = """
Title: Test Presentation

Introduction:
This is a test slide.

Conclusion:
Thank you!
"""

try:
    success = generate_beautiful_ppt(
        test_script,
        "test_output.pptx",
        color_scheme="corporate",
        use_ai=False,
        ai_instructions=""
    )
    print(f"✅ Function call successful: {success}")
except Exception as e:
    print(f"❌ Function call failed: {e}")
    import traceback
    traceback.print_exc()
