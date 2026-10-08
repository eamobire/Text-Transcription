import os

import gradio as gr

from transcriber import transcribe_file

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Output")


def run_transcription(audio_path, progress=gr.Progress()):
    if not audio_path:
        raise gr.Error("Please upload an audio file first.")

    progress(0, desc="Loading model / transcribing (this can take a while)...")
    txt_path, srt_path = transcribe_file(audio_path, OUTPUT_DIR)
    progress(1, desc="Done")

    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()

    return text, txt_path, srt_path


with gr.Blocks(title="Audio to Text Transcription") as demo:
    gr.Markdown("# Audio to Text Transcription\nUpload an audio file, then click **Transcribe**.")

    audio_input = gr.Audio(label="Audio file", type="filepath", sources=["upload"])
    transcribe_btn = gr.Button("Transcribe", variant="primary")

    transcript_output = gr.Textbox(label="Transcript", lines=15)
    with gr.Row():
        txt_file = gr.File(label="Download .txt")
        srt_file = gr.File(label="Download .srt")

    transcribe_btn.click(
        fn=run_transcription,
        inputs=audio_input,
        outputs=[transcript_output, txt_file, srt_file],
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True)
