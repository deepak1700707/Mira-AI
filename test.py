# import sounddevice as sd
# from scipy.io.wavfile import write
# import numpy as np
# import whisper
# import torch


# def record_audio(filename="command.wav", duration=5, fs=44100):
#     """Record audio from the microphone and save as a WAV file."""
#     print("🎙️ Recording... Speak now!")
#     audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
#     sd.wait()
#     if np.max(np.abs(audio)) > 0:
#         audio = audio / np.max(np.abs(audio))
#     write(filename, fs, (audio * 32767).astype(np.int16))
#     print(f"✅ Audio saved as {filename}")


# def transcribe_audio(audio_file="command.wav", output_file="output.txt"):
#     """Transcribe audio file to text using Whisper with safe settings."""
#     print("🧠 Loading Whisper model...")

#     # Force CPU to avoid CUDA NaN issue
#     device = "cpu"  
#     model = whisper.load_model("base", device=device)

#     print("🎧 Transcribing...")
#     # Disable FP16 to prevent NaN logits
#     result = model.transcribe(audio_file, fp16=False)
#     text = result["text"].strip()

#     print(f"\n📝 Transcription:\n{text}")
#     with open(output_file, "w") as f:
#         f.write(text)
#     print(f"✅ Transcription saved to {output_file}")
#     return text


# if __name__ == "__main__":
#     record_audio(duration=5)
#     transcribe_audio("command.wav")


import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import torch
import whisper

# 🎙️ Record audio
def record_audio(filename="command.wav", duration=5):
    fs = 44100
    print("🎙️ Recording... Speak now!")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    write(filename, fs, audio)
    print(f"✅ Audio saved as {filename}")

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

# 🚀 Run the pipeline
if __name__ == "__main__":
    record_audio(duration=5)
    transcribe_audio("command.wav")
