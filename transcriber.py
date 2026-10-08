import os
import gc

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

MODEL = "distil-whisper/distil-large-v3"  # lighter footprint than large-v3

_pipe = None


def get_pipe():
    """Load (once) and return the ASR pipeline."""
    global _pipe
    if _pipe is not None:
        return _pipe

    import torch
    from transformers import pipeline

    if "pipe" in dir():
        del pipe
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if device != "cpu" else torch.float32
    if device == "cpu":
        print("WARNING: CUDA not available; running on CPU (very slow).")
    else:
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")

    _pipe = pipeline(
        "automatic-speech-recognition",
        model=MODEL,
        dtype=torch_dtype,
        device=device,
        model_kwargs={"attn_implementation": "sdpa"},
    )
    print("Model loaded on", device)
    return _pipe


def format_ts(seconds):
    if seconds is None:
        seconds = 0
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def result_to_srt(result):
    lines = []
    for i, chunk in enumerate(result["chunks"], start=1):
        start, end = chunk["timestamp"]
        text = chunk["text"].strip()
        lines.append(f"{i}\n{format_ts(start)} --> {format_ts(end)}\n{text}\n")
    return "\n".join(lines)


def transcribe_audio(audio_path):
    """Run the ASR pipeline on an audio file and return (text, srt_text)."""
    pipe = get_pipe()
    # Whisper/distil-whisper do their own 30s long-form chunking when
    # return_timestamps=True. Do not pass chunk_length_s (pipeline warning).
    result = pipe(audio_path, return_timestamps=True)
    return result["text"].strip(), result_to_srt(result)


def transcribe_file(audio_path, output_dir):
    """Transcribe a file and write <stem>.txt / <stem>.srt into output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(audio_path))[0]
    print(f"Transcribing: {audio_path}")

    text, srt_text = transcribe_audio(audio_path)

    txt_path = os.path.join(output_dir, f"{stem}.txt")
    srt_path = os.path.join(output_dir, f"{stem}.srt")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_text)

    print(f"Wrote:\n  {txt_path}\n  {srt_path}")
    return txt_path, srt_path
