#!/usr/bin/env python3
"""
PowerPoint to Images Converter (Pure Python)
Converts each slide of a PPT to individual image files using PyMuPDF and pptx2pdf
No external dependencies required (LibreOffice, Poppler, ImageMagick)
"""

import os
import sys
from pathlib import Path

def ppt_to_images(ppt_file, output_dir="output/slides"):
    """
    Convert PowerPoint slides to images using pure Python libraries
    
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
    
    try:
        # Step 1: Convert PPT to PDF using pptx2pdf
        print("🔄 Step 1: Converting PPT to PDF...")
        from pptx2pdf.convert import convert
        
        ppt_name = Path(ppt_file).stem
        pdf_file = os.path.join(output_dir, f"{ppt_name}.pdf")
        
        try:
            convert(ppt_file, pdf_file)
            print(f"✅ PDF created: {pdf_file}")
        except Exception as e:
            print(f"⚠️ pptx2pdf conversion failed: {e}")
            return False
        
        # Step 2: Convert PDF to images using PyMuPDF
        print("🔄 Step 2: Converting PDF to images...")
        import fitz  # PyMuPDF
        
        if not os.path.exists(pdf_file):
            print(f"❌ PDF file not found: {pdf_file}")
            return False
        
        try:
            # Open PDF
            pdf_document = fitz.open(pdf_file)
            total_pages = pdf_document.page_count
            
            print(f"📄 PDF has {total_pages} pages")
            
            # Convert each page to image
            for page_num in range(total_pages):
                try:
                    # Get page
                    page = pdf_document[page_num]
                    
                    # Render page to image (high quality: 300 DPI equivalent)
                    mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    
                    # Save as PNG
                    image_file = os.path.join(output_dir, f"slide_{page_num + 1:02d}.png")
                    pix.save(image_file)
                    
                    print(f"  ✓ Slide {page_num + 1} saved")
                    
                except Exception as e:
                    print(f"  ❌ Error converting page {page_num + 1}: {e}")
                    continue
            
            pdf_document.close()
            print("✅ All slides converted to images!")
            
            # Clean up PDF
            try:
                os.remove(pdf_file)
                print("✓ Cleaned up temporary PDF")
            except:
                pass
            
            return True
            
        except ImportError:
            print("❌ PyMuPDF (fitz) not installed")
            print("💡 Install it with: pip install PyMuPDF")
            return False
        except Exception as e:
            print(f"❌ Error converting PDF to images: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Required library not found: {e}")
        print("💡 Install required packages:")
        print("   pip install PyMuPDF pptx2pdf")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

# Note: rename_slide_images is no longer needed with pure Python approach

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
    print("  PowerPoint to Images Converter (Pure Python)")
    print("=" * 50)
    print()
    
    # Convert
    success = ppt_to_images(ppt_file)
    
    if success:
        # List generated slides
        list_slides()
        print("\n🎉 Conversion complete!")
    else:
        print("\n⚠️  Conversion failed")
        print("💡 Make sure required packages are installed:")
        print("   pip install PyMuPDF pptx2pdf")
