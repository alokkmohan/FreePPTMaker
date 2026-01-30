
# --- Gradio Full Feature Migration ---
import gradio as gr
from create_ppt import process_script
from ai_ppt_generator import generate_beautiful_ppt
from youtube_script_generator import generate_youtube_script_with_ai
from content_generator import generate_content_from_topic
from docx import Document
import os
import shutil
from datetime import datetime
import json

def analyze_content(text):
    word_count = len(text.split())
    char_count = len(text)
    estimated_slides = max(5, min(20, word_count // 100))
    return word_count, char_count, estimated_slides

def preview_file(file):
    if file is None:
        return "", 0, 0, 0, ""
    ext = file.name.split(".")[-1].lower()
    if ext in ["txt", "md"]:
        content = file.read().decode("utf-8")
    elif ext == "docx":
        doc = Document(file.name)
        content = "\n".join([para.text for para in doc.paragraphs])
    else:
        content = ""
    word_count, char_count, estimated_slides = analyze_content(content)
    return content, word_count, char_count, estimated_slides, ext

def gradio_full_app():
    with gr.Blocks() as demo:
        gr.Markdown("""# 📊 TEXT to PPT Generator
Transform Your Text into Beautiful PowerPoint Presentations
""")

        with gr.Tab("Upload File"):
            file = gr.File(label="Upload TXT, DOCX, MD file")
            file_content = gr.Textbox(label="Content Preview", lines=10, interactive=False)
            word_count = gr.Number(label="Words", interactive=False)
            char_count = gr.Number(label="Characters", interactive=False)
            estimated_slides = gr.Number(label="Est. Slides", interactive=False)
            ext = gr.Textbox(label="File Type", interactive=False)
            file.upload(preview_file, inputs=file, outputs=[file_content, word_count, char_count, estimated_slides, ext])

        with gr.Tab("Paste Text"):
            paste_text = gr.Textbox(label="Paste your content", lines=10)
            paste_word_count = gr.Number(label="Words", interactive=False)
            paste_char_count = gr.Number(label="Characters", interactive=False)
            paste_estimated_slides = gr.Number(label="Est. Slides", interactive=False)
            paste_text.change(lambda t: analyze_content(t) + (None,), inputs=paste_text, outputs=[paste_word_count, paste_char_count, paste_estimated_slides, gr.State()])

        with gr.Tab("Topic Only (AI)"):
            topic = gr.Textbox(label="Enter your topic", lines=2)
            gr.Markdown("AI will generate a detailed article and create presentation from your topic.")

        # TODO: Add configuration, theme, AI enhancement, and generation steps here

    return demo

if __name__ == "__main__":
    gradio_full_app().launch()
