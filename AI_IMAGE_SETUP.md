# 🎨 AI Image Generation for PPT - Setup Guide

## Flow Diagram

```
Slide Text (from Mistral)
        ↓
Image Prompt Generation (Mistral AI)
        ↓
Hugging Face Inference API (Stable Diffusion 2.1)
        ↓
Generated AI Image (1024x576, 16:9)
        ↓
Insert into PPT Slide
```

## 📋 Prerequisites

### 1. Hugging Face API Token (REQUIRED)
- Go to: https://huggingface.co/settings/tokens
- Create a new token with "Read" access
- Copy the token

### 2. Mistral API Key (OPTIONAL - for better prompts)
- Go to: https://console.mistral.ai/api-keys
- Create API key
- Copy the key

## ⚙️ Setup

### Step 1: Add API Keys to `.env` file

Create or edit `.env` file in the project root:

```bash
# Required for AI image generation
HUGGINGFACE_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx

# Optional - improves image prompt quality
MISTRAL_API_KEY=xxxxxxxxxxxxxxxxxxxxx
```

### Step 2: Install Dependencies (if needed)

```bash
pip install pillow requests python-dotenv
```

## 🚀 Usage

### Option 1: Test AI Image Generation

```bash
python3 test_ai_images.py
```

This will:
1. Ask if you want AI images or not
2. Generate a sample PPT about "AI in Healthcare"
3. Create images for each slide (if enabled)
4. Save PPT to `test_output/ai_healthcare_demo.pptx`

### Option 2: Use in Your Code

```python
from ai_ppt_generator import generate_beautiful_ppt

slides = [
    {
        "slide_number": 1,
        "title": "Title Slide",
        "main_title": "Your Presentation Title",
        "tagline": "Your tagline",
        "subtitle": "Your subtitle"
    },
    {
        "slide_number": 2,
        "title": "Introduction",
        "bullets": [
            "First point about your topic...",
            "Second point with details...",
            "Third point..."
        ]
    }
    # ... more slides
]

# Generate PPT WITH AI images
generate_beautiful_ppt(
    slides,
    output_path="output.pptx",
    color_scheme="corporate",
    generate_ai_images=True  # ← Enable AI images
)
```

### Option 3: In Streamlit App

The app will automatically use AI images if `HUGGINGFACE_API_TOKEN` is set in `.env`

## 📂 File Structure

```
TextToPPTMaker/
├── ai_image_generator.py          # AI image generation core
├── ai_ppt_generator.py             # PPT generation (updated)
├── test_ai_images.py               # Test script
├── temp_images/                    # Generated images saved here
│   ├── ai_Introduction.jpg
│   ├── ai_Key_Applications.jpg
│   └── ...
└── .env                            # API keys (don't commit!)
```

## 🎨 How It Works

### 1. **Image Prompt Generation** (`ai_image_generator.py`)

```python
generate_image_prompt_from_text(slide_text, slide_title)
```

- Takes slide text and title
- Uses Mistral AI to create a detailed image prompt
- Falls back to simple prompts if Mistral is not available

**Example:**
- Input: "AI in Healthcare - diagnosis, treatment, efficiency"
- Output: "professional medical AI illustration, doctor using AI technology for diagnosis, futuristic hospital setting, modern clean corporate style"

### 2. **Image Generation** (`ai_image_generator.py`)

```python
generate_image_with_huggingface(prompt, output_path)
```

- Calls Hugging Face Inference API
- Uses Stable Diffusion 2.1 model
- Generates 1024x576 image (16:9 aspect ratio for slides)
- Saves as high-quality JPEG

### 3. **PPT Integration** (`ai_ppt_generator.py`)

```python
generate_beautiful_ppt(slides, ..., generate_ai_images=True)
```

- Generates AI images for all content slides
- Skips title and conclusion slides
- Inserts images into PPT using `create_content_slide_with_image()`
- Images are positioned on the right side of slides

## ⚡ Performance

- **With AI Images**: ~30-60 seconds per slide (API dependent)
- **Without AI Images**: ~1-2 seconds total

For a 10-slide presentation:
- No images: ~2 seconds
- With AI images: ~5-10 minutes (first time, model loading)
- Subsequent runs: ~2-3 minutes

## 🐛 Troubleshooting

### Issue: "Model is loading" error

**Solution:** Hugging Face models take time to load on first request. Wait 1-2 minutes and retry.

### Issue: "HUGGINGFACE_API_TOKEN not found"

**Solution:** Add your token to `.env` file:
```bash
HUGGINGFACE_API_TOKEN=hf_your_token_here
```

### Issue: Images not appearing in PPT

**Solution:**
1. Check `temp_images/` folder - are images generated?
2. If yes, check image file paths in console logs
3. Try running test script first to verify setup

### Issue: Poor quality images

**Solution:**
1. Add MISTRAL_API_KEY to improve prompts
2. Manually edit prompts in `ai_image_generator.py`
3. Try different Stable Diffusion models in HF_API_URL

## 🎯 Advanced Configuration

### Change Image Model

Edit `ai_image_generator.py`:

```python
# Default: Stable Diffusion 2.1
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

# Alternative: Stable Diffusion XL
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
```

### Adjust Image Size

Edit `generate_image_with_huggingface()`:

```python
"parameters": {
    "width": 1024,   # Adjust width
    "height": 576,   # Adjust height (keep 16:9 ratio)
    "num_inference_steps": 50,  # More steps = better quality
    "guidance_scale": 7.5       # Higher = follows prompt more
}
```

## 📊 Example Output

### Input Slide:
```
Title: "AI in Healthcare"
Content: "AI is transforming healthcare with predictive
diagnostics, personalized treatment, and virtual assistants"
```

### Generated Prompt:
```
"Modern medical AI technology illustration, doctor using
artificial intelligence for patient diagnosis, futuristic
hospital setting with holographic displays, clean
professional corporate style, blue and white color scheme"
```

### Result:
- High-quality AI-generated image embedded in slide
- 16:9 aspect ratio fits perfectly
- Professional, relevant imagery

## 🎉 Summary

**Files Created:**
1. ✅ `ai_image_generator.py` - Core AI image generation
2. ✅ `test_ai_images.py` - Test & demo script
3. ✅ `AI_IMAGE_SETUP.md` - This setup guide
4. ✅ Updated `ai_ppt_generator.py` - Integration

**To Use:**
1. Add `HUGGINGFACE_API_TOKEN` to `.env`
2. Run `python3 test_ai_images.py`
3. Or set `generate_ai_images=True` in your code

**Features:**
- ✅ Automatic image prompt generation (Mistral)
- ✅ AI image generation (Hugging Face)
- ✅ Smart slide selection (skips title/conclusion)
- ✅ High-quality 16:9 images
- ✅ Easy integration

🎨 **Ready to create beautiful presentations with AI-generated images!**
