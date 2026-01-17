#!/bin/bash
# Auto-process script for converting ODT to TXT and generating outputs
# Usage: ./process_script.sh [input_file.odt]

# Set paths
INPUT_DIR="input"
OUTPUT_DIR="output"
VENV_PYTHON=".venv/bin/python"

# Create directories if not exist
mkdir -p "$INPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Check if input file is provided
if [ -z "$1" ]; then
    # Find the latest .odt file in input folder
    INPUT_FILE=$(ls -t "$INPUT_DIR"/*.odt 2>/dev/null | head -1)
    
    if [ -z "$INPUT_FILE" ]; then
        echo "❌ No .odt file found in $INPUT_DIR folder"
        echo "💡 Usage: ./process_script.sh input/YourFile.odt"
        echo "   Or place an .odt file in the input folder"
        exit 1
    fi
else
    INPUT_FILE="$1"
fi

echo "================================================"
echo "  Raw Script to Output Processor"
echo "================================================"
echo ""
echo "📁 Input file: $INPUT_FILE"

# Extract filename without extension
BASENAME=$(basename "$INPUT_FILE" .odt)
TXT_FILE="$INPUT_DIR/${BASENAME}.txt"
YOUTUBE_SCRIPT="$INPUT_DIR/${BASENAME}_youtube.txt"
PPT_FILE="$OUTPUT_DIR/${BASENAME}.pptx"
DOC_FILE="$OUTPUT_DIR/${BASENAME}.docx"

# Step 1: Convert ODT to TXT
echo ""
echo "📝 Step 1: Converting ODT to TXT..."
odt2txt "$INPUT_FILE" > "$TXT_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Converted to: $TXT_FILE"
else
    echo "❌ Conversion failed!"
    exit 1
fi

# Step 2: Generate YouTube script (if needed - for now just copy)
echo ""
echo "📺 Step 2: Preparing YouTube script..."
cp "$TXT_FILE" "$YOUTUBE_SCRIPT"
echo "✅ YouTube script ready: $YOUTUBE_SCRIPT"

# Step 3: Generate PowerPoint
echo ""
echo "🎨 Step 3: Creating PowerPoint presentation..."
"$VENV_PYTHON" create_detailed_ppt.py

if [ $? -eq 0 ]; then
    echo "✅ PowerPoint created!"
else
    echo "❌ PowerPoint generation failed!"
fi

# Step 4: Generate Word Document
echo ""
echo "📄 Step 4: Creating Word document..."
cp "$YOUTUBE_SCRIPT" input_script.txt
node index.js
mv output_document.docx "$DOC_FILE" 2>/dev/null

if [ -f "$DOC_FILE" ]; then
    echo "✅ Word document created: $DOC_FILE"
else
    echo "⚠️  Word document generation skipped or failed"
fi

# Step 5: Generate slide images from PowerPoint
echo ""
echo "📸 Step 5: Converting PPT slides to images..."
"$VENV_PYTHON" ppt_to_images.py

if [ $? -eq 0 ]; then
    echo "✅ Slide images created!"
else
    echo "⚠️  Slide image generation skipped or failed"
fi

# Cleanup
rm -f input_script.txt

# Summary
echo ""
echo "================================================"
echo "  ✅ Processing Complete!"
echo "================================================"
echo ""
echo "📂 Output folder contents:"
ls -lh "$OUTPUT_DIR"
echo ""
echo "📸 Slide images:"
ls -lh "$OUTPUT_DIR/slides/" 2>/dev/null || echo "  (No slide images)"
echo ""
echo "🎉 All done! Check the output folder for your files."
