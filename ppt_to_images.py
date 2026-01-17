#!/usr/bin/env python3
"""
PowerPoint to Images Converter
Converts each slide of a PPT to individual image files
"""

import os
import sys
import subprocess
from pathlib import Path

def ppt_to_images(ppt_file, output_dir="output/slides"):
    """
    Convert PowerPoint slides to images using LibreOffice
    
    Args:
        ppt_file: Path to PowerPoint file
        output_dir: Directory to save slide images
    """
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📊 Converting PPT to images...")
    print(f"📁 Input: {ppt_file}")
    print(f"📂 Output: {output_dir}")
    print("")
    
    # Check if file exists
    if not os.path.exists(ppt_file):
        print(f"❌ Error: File not found: {ppt_file}")
        return False
    
    # Convert using LibreOffice
    try:
        # LibreOffice command to convert to PDF first (better quality)
        pdf_output = os.path.join(output_dir, "temp.pdf")
        
        print("🔄 Step 1: Converting PPT to PDF...")
        cmd_pdf = [
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            ppt_file
        ]
        
        result = subprocess.run(cmd_pdf, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print("⚠️  PDF conversion failed, trying direct PNG conversion...")
            
            # Alternative: Direct conversion to PNG
            print("🔄 Converting PPT slides to PNG...")
            cmd_png = [
                "libreoffice",
                "--headless",
                "--convert-to", "png",
                "--outdir", output_dir,
                ppt_file
            ]
            
            result = subprocess.run(cmd_png, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Slides converted to PNG!")
                return True
            else:
                print(f"❌ Conversion failed: {result.stderr}")
                return False
        
        # Find the generated PDF
        ppt_name = Path(ppt_file).stem
        pdf_file = os.path.join(output_dir, f"{ppt_name}.pdf")
        
        if not os.path.exists(pdf_file):
            print("❌ PDF file not created")
            return False
        
        print("✅ PDF created successfully!")
        
        # Convert PDF to images using pdftoppm or convert
        print("🔄 Step 2: Converting PDF to images...")
        
        # Try using pdftoppm (better quality)
        try:
            cmd_images = [
                "pdftoppm",
                "-png",
                "-r", "300",  # 300 DPI for high quality
                pdf_file,
                os.path.join(output_dir, "slide")
            ]
            
            result = subprocess.run(cmd_images, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Images created with pdftoppm!")
                
                # Rename files to better format
                rename_slide_images(output_dir)
                
                # Clean up PDF
                os.remove(pdf_file)
                
                return True
        except FileNotFoundError:
            print("⚠️  pdftoppm not found, trying ImageMagick...")
        
        # Try using ImageMagick convert
        try:
            cmd_convert = [
                "convert",
                "-density", "300",
                pdf_file,
                os.path.join(output_dir, "slide-%02d.png")
            ]
            
            result = subprocess.run(cmd_convert, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Images created with ImageMagick!")
                
                # Clean up PDF
                os.remove(pdf_file)
                
                return True
        except FileNotFoundError:
            print("⚠️  ImageMagick not found")
        
        print("❌ Could not convert PDF to images. PDF saved at:", pdf_file)
        return False
        
    except subprocess.TimeoutExpired:
        print("❌ Conversion timeout!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def rename_slide_images(output_dir):
    """Rename slide images to a cleaner format"""
    import glob
    
    # Find all slide-*.png files
    files = sorted(glob.glob(os.path.join(output_dir, "slide-*.png")))
    
    for i, old_file in enumerate(files, 1):
        new_file = os.path.join(output_dir, f"slide_{i:02d}.png")
        if os.path.exists(old_file):
            os.rename(old_file, new_file)
            print(f"  ✓ Slide {i} saved")

def list_slides(output_dir="output/slides"):
    """List all slide images"""
    import glob
    
    slides = sorted(glob.glob(os.path.join(output_dir, "slide*.png")))
    
    if slides:
        print(f"\n📸 Total slides converted: {len(slides)}")
        print(f"📁 Location: {output_dir}/")
        for slide in slides:
            size = os.path.getsize(slide) / 1024  # KB
            print(f"   • {os.path.basename(slide)} ({size:.1f} KB)")
    else:
        print("\n❌ No slide images found")

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
            print(f"📌 Using latest PPT: {ppt_file}\n")
        else:
            print("❌ No PowerPoint file found in output folder!")
            print("💡 Usage: python ppt_to_images.py [path/to/presentation.pptx]")
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
        print("\n🎉 Conversion complete!")
    else:
        print("\n⚠️  Conversion completed with warnings or errors")
        print("💡 Make sure LibreOffice is installed:")
        print("   sudo apt install libreoffice")
        print("💡 For better quality, install pdftoppm:")
        print("   sudo apt install poppler-utils")
