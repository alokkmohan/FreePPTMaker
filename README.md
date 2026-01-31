# 🎨 AI PowerPoint Generator

Transform your ideas into beautiful presentations instantly! This Streamlit-based web application uses DeepSeek AI to generate professional PowerPoint presentations and YouTube scripts from your content.

## ✨ Features

- 📝 **Multiple Input Methods**: Upload files (TXT, DOCX, MD) or paste text directly
- 🤖 **AI Content Generation**: Just provide a topic - AI generates the full content
- 🎨 **Beautiful Themes**: Choose from 4 professional color schemes (Ocean, Forest, Sunset, Corporate)
- 🖼️ **AI Image Generation**: Automatically generates relevant images for slides using Hugging Face AI (see [AI_IMAGE_GENERATION_SETUP.md](AI_IMAGE_GENERATION_SETUP.md))
- 🎯 **Theme Switcher**: Change design/theme after PPT generation with one click
- 📊 **Smart Structuring**: AI intelligently organizes content into well-structured slides
- 🎬 **YouTube Script Generation**: Automatically converts content to engaging YouTube scripts
- 📸 **Slide Images**: Converts PPT slides to PNG images
- 📱 **Mobile Responsive**: Beautiful UI that works on all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- LibreOffice (for PPT to image conversion)
DeepSeek API Key

### Installation

1. **Clone the repository**
   \`\`\`bash
   git clone https://github.com/alokkmohan/TextToPPTMaker.git
   cd TextToPPTMaker
   \`\`\`

2. **Create virtual environment**
   \`\`\`bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   \`\`\`

3. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. **Set up environment variables**
   \`\`\`bash
   export DEEPSEEK_API_KEY=your_deepseek_api_key_here
   \`\`\`

5. **Run the application**
   \`\`\`bash
   streamlit run app.py
   \`\`\`

6. **Open in browser**: http://localhost:8501

## 📦 Output

Each generation creates a unique timestamped folder containing:
- 📄 PowerPoint presentation (.pptx)
- 🖼️ PNG images of all slides
- 🎬 YouTube script (optional, .docx)
- 📝 Original script backup

## 🌟 Features

- **AI Content Structuring**: Intelligent slide organization with 4-6 bullets per slide
- **Mobile-Friendly Design**: Responsive layouts with beautiful gradient themes
- **YouTube Script Generation**: Conversational scripts with engaging hooks

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👨‍💻 Author

**Alok Mohan** - [@alokkmohan](https://github.com/alokkmohan)

---

Made with ❤️ using Streamlit & DeepSeek AI
