import torch
import whisper

# 🧠 Transcribe audio using Whisper
def transcribe_audio(audio_file):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🧠 Loading Whisper model on {device} (float32-safe)...")

    # Force Whisper to use float32 precision to prevent NaN errors
    model = whisper.load_model("base", device=device)
    model = model.to(dtype=torch.float32)

    print("🎧 Transcribing...")
    result = model.transcribe(audio_file, fp16=False)

    print("\n📝 Transcription:")
    print(result["text"])

    # Save transcription
    with open("output.txt", "w") as f:
        f.write(result["text"])
    print("✅ Transcription saved to output.txt")
    return result["text"]