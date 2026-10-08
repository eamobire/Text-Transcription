import os

from transcriber import transcribe_file

INPUT_DIR = "C:/Users/agomb/Documents/Audio" # <-- update this path
OUTPUT_DIR = os.path.join(INPUT_DIR, "Output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

exts = (".mp3", ".m4a", ".wav")
audio_files = sorted(f for f in os.listdir(INPUT_DIR) if f.lower().endswith(exts))
print("Found audio files:", audio_files)

for fname in audio_files:
    stem = os.path.splitext(fname)[0]
    if os.path.exists(os.path.join(OUTPUT_DIR, f"{stem}.txt")):
        print(f"Skipping (already done): {fname}")
        continue
    transcribe_file(os.path.join(INPUT_DIR, fname), OUTPUT_DIR)
