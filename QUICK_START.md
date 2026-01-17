# Article YouTube - Quick Start Guide

## 📁 Folder Structure

```
Article Youtube/
├── input/          # 👈 अपनी raw script यहाँ डालें (.odt files)
├── output/         # 👈 Generated files यहाँ मिलेंगी (.pptx, .docx)
├── process_script.sh  # Auto-process script
└── ...other files
```

## 🚀 Quick Usage

### आसान तरीका (Recommended):

1. **अपनी raw script file (.odt) को `input` folder में डालें**
   ```bash
   cp YourScript.odt input/
   ```

2. **Process करें:**
   ```bash
   ./process_script.sh
   ```

3. **Output files `output` folder में मिल जाएंगी!**
   - PowerPoint (.pptx)
   - Word Document (.docx)
   - Converted text files

### विशिष्ट file process करने के लिए:

```bash
./process_script.sh input/YourFile.odt
```

## 📝 What Gets Generated?

- ✅ **PowerPoint Presentation** - Detailed slides with tables, colorful design
- ✅ **Word Document** - Formatted document for TTS
- ✅ **Slide Images** - Individual PNG images of each slide (300 DPI)
- ✅ **Text Files** - Converted plain text versions

## 🎨 Features

- **Automatic ODT to TXT conversion**
- **Detailed PowerPoint slides** with:
  - Tables for organized data
  - Colorful gradients and decorative elements
  - Proper Hindi font (Noto Sans Devanagari)
  - Read-along friendly content
- **Professional Word documents**
- **Clean folder organization**

## 💡 Tips

- फ़ाइल का नाम Hindi में हो सकता है
- .odt format में script save करें
- Output automatically generate हो जाएगा
- सभी files proper Hindi font में होंगी

## 🔄 Workflow

```
Raw Script (ODT) → input/ → process_script.sh → output/ (PPT + DOCX + Slide Images)
```

**Complete Output:**
- 📊 `output/YourScript.pptx` - PowerPoint presentation
- 📄 `output/YourScript.docx` - Word document
- 📸 `output/slides/slide_01.png, slide_02.png, ...` - Individual slide images

बस अपनी script input folder में डालें और process करें! 🎉
