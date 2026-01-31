# 🎨 AI Image Generation Setup Guide

## Overview

AI image generation is now **ENABLED** in the PPT Maker. When you generate a PPT, AI will automatically create relevant images for your slides.

---

## 🔧 Setup Required

### Step 1: Get API Keys

You need **two API keys** for AI image generation:

#### 1. Hugging Face API Key (Required)
- Go to: https://huggingface.co/settings/tokens
- Click "New token"
- Give it a name (e.g., "PPT Maker")
- Copy the token

#### 2. Mistral API Key (Optional but recommended)
- Go to: https://console.mistral.ai/
- Create account / Login
- Go to API Keys section
- Create new API key
- Copy the key

**Note:** Without Mistral API key, simple generic prompts will be used for image generation.

---

### Step 2: Add Keys to .env File

Open your `.env` file and add:

```env
# AI Image Generation
HUGGINGFACE_API_KEY=your_actual_huggingface_token_here
MISTRAL_API_KEY=your_actual_mistral_key_here
```

**Important:** Replace `your_actual_*_here` with the actual keys you copied.

---

### Step 3: Restart the App

After adding the keys:

```bash
# Stop the app (Ctrl+C if running)
# Restart it
streamlit run app_chatbot.py
```

---

## ✅ How It Works

When you generate a PPT:

1. **Content Analysis**: AI analyzes each slide's title and content
2. **Prompt Generation**: Mistral AI creates a detailed image prompt
3. **Image Generation**: Hugging Face Stable Diffusion creates the image
4. **PPT Integration**: Image is automatically added to the slide

**Example:**

- Slide Title: "Introduction to Machine Learning"
- AI detects: Concept/Introduction slide
- Generates: Professional illustration of machine learning concept
- Adds: Image to the right side of the slide

---

## 🎯 Which Slides Get Images?

AI automatically adds images to:

- **Concept slides**: Introduction, Overview, What is...
- **Comparison slides**: Charts for data comparison
- **Distribution slides**: Pie charts for percentages
- **Trend slides**: Line charts for growth/timeline

**Skipped:**
- Title slide (Slide 1)
- Thank you slide (Last slide)

---

## 🚫 What if I Don't Want Images?

If you don't want AI images:

1. Leave `HUGGINGFACE_API_KEY` empty in `.env`
2. Images won't be generated
3. PPT will still work normally (text-only slides)

---

## 🐛 Troubleshooting

### Issue: "No images appearing in PPT"

**Check:**
1. Is `HUGGINGFACE_API_KEY` set in `.env`?
2. Did you restart the app after adding keys?
3. Check terminal/console for error messages

**Common errors:**
- `401 Unauthorized`: Invalid Hugging Face API key
- `503 Service Unavailable`: HF API is loading the model (wait 30 seconds, try again)

### Issue: "Images taking too long"

Hugging Face Inference API can take 15-30 seconds per image on first run (cold start). Subsequent images are faster.

**Tip:** Start with a small PPT (3-4 slides) to test.

---

## 💰 API Costs

### Hugging Face
- **FREE tier**: 1000 requests/month
- **Cost**: Free for personal use
- **Rate limit**: ~100 requests/hour

### Mistral AI
- **FREE tier**: Limited free credits
- **Cost**: Very cheap (~$0.001 per prompt)
- **Fallback**: Works without Mistral (basic prompts)

---

## 📊 Example Output

**Before (Text-only):**
```
Slide 2: Machine Learning Basics
• Supervised Learning
• Unsupervised Learning
• Reinforcement Learning
```

**After (With AI Images):**
```
Slide 2: Machine Learning Basics        [AI Generated Image]
• Supervised Learning                    Professional illustration
• Unsupervised Learning                  showing ML concept
• Reinforcement Learning
```

---

## 🎉 Ready!

Once you've added the API keys and restarted the app:

1. Generate any PPT (document upload, paste content, or topic)
2. AI will automatically add images where relevant
3. Download and check your PPT

**Enjoy professional presentations with AI-generated visuals!** 🚀
