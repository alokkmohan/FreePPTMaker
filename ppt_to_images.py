#!/usr/bin/env python3
"""
PowerPoint to Images Converter (Windows)
Converts each slide of a PPT to individual image files using PowerPoint COM
"""

import os
import sys
from pathlib import Path

def ppt_to_images(ppt_file, output_dir="output/slides"):
    """
    Convert PowerPoint slides to images using Windows COM automation

    Args:
        ppt_file: Path to PowerPoint file
        output_dir: Directory to save slide images
    """

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    print(f"[PPT] Converting PPT to images...")
    print(f"[PPT] Input: {ppt_file}")
    print(f"[PPT] Output: {output_dir}")

    # Check if file exists
    if not os.path.exists(ppt_file):
        print(f"[ERROR] File not found: {ppt_file}")
        return False

    # Get absolute paths
    ppt_file = os.path.abspath(ppt_file)
    output_dir = os.path.abspath(output_dir)

    try:
        # Try Windows COM automation (requires PowerPoint installed)
        import comtypes.client

        print("[PPT] Using PowerPoint COM automation...")

        # Start PowerPoint
        powerpoint = comtypes.client.CreateObject("PowerPoint.Application")
        powerpoint.Visible = 1

        # Open presentation
        presentation = powerpoint.Presentations.Open(ppt_file, WithWindow=False)

        # Export each slide as PNG
        total_slides = presentation.Slides.Count
        print(f"[PPT] Found {total_slides} slides")

        for i in range(1, total_slides + 1):
            slide = presentation.Slides(i)
            image_path = os.path.join(output_dir, f"slide_{i:02d}.png")
            slide.Export(image_path, "PNG", 1280, 720)
            print(f"  [OK] Slide {i} saved")

        # Close presentation
        presentation.Close()
        powerpoint.Quit()

        print("[OK] All slides converted!")
        return True

    except ImportError:
        print("[ERROR] comtypes not installed")
        print("[INFO] Install with: pip install comtypes")
        return False
    except Exception as e:
        error_msg = str(e)
        if "PowerPoint.Application" in error_msg or "class not registered" in error_msg.lower():
            print("[ERROR] Microsoft PowerPoint is not installed")
            print("[INFO] Preview requires PowerPoint to be installed on this machine")
        else:
            print(f"[ERROR] {error_msg}")
        return False


def list_slides(output_dir="output/slides"):
    """List all slide images"""
    import glob

    slides = sorted(glob.glob(os.path.join(output_dir, "slide*.png")))

    if slides:
        print(f"\n[INFO] Total slides converted: {len(slides)}")
        print(f"[INFO] Location: {output_dir}/")
        for slide in slides:
            size = os.path.getsize(slide) / 1024  # KB
            print(f"   - {os.path.basename(slide)} ({size:.1f} KB)")
    else:
        print("\n[INFO] No slide images found")


if __name__ == "__main__":
    # Default PPT file
    ppt_file = "output/buddha_women_freedom.pptx"

    # Check if custom file is provided
    if len(sys.argv) > 1:
        ppt_file = sys.argv[1]

    # Check if file exists
    if not os.path.exists(ppt_file):
        # Try to find latest PPT in output folder
        import glob
        ppts = sorted(glob.glob("output/*.pptx"), key=os.path.getmtime, reverse=True)

        if ppts:
            ppt_file = ppts[0]
            print(f"[INFO] Using latest PPT: {ppt_file}\n")
        else:
            print("[ERROR] No PowerPoint file found in output folder!")
            print("[INFO] Usage: python ppt_to_images.py [path/to/presentation.pptx]")
            sys.exit(1)

    print("=" * 50)
    print("  PowerPoint to Images Converter")
    print("=" * 50)
    print()

    # Convert
    success = ppt_to_images(ppt_file)

    if success:
        # List generated slides
        list_slides()
        print("\n[OK] Conversion complete!")
    else:
        print("\n[WARNING] Conversion failed")
        print("[INFO] Make sure Microsoft PowerPoint is installed")
