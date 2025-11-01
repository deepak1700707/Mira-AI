# # import sounddevice as sd
# # from scipy.io.wavfile import write
# # import numpy as np
# # import soundfile as sf

# # def record_audio(filename="command.wav", duration=5, device_index=0):
# #     fs = 44100  # Standard Whisper sampling rate
# #     print("🎙️ Recording... Speak now!")

# #     # Record audio from selected device
# #     audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32', device=device_index)
# #     sd.wait()

# #     # Check for silence
# #     if np.max(np.abs(audio)) < 0.01:
# #         print("⚠️ Warning: Audio seems too quiet. Try speaking louder or closer to mic.")

# #     # Normalize volume safely
# #     max_val = np.max(np.abs(audio))
# #     if max_val > 0:
# #         audio = audio / max_val

# #     # Save using soundfile (better float precision & metadata)
# #     sf.write(filename, audio, fs)
# #     print(f"✅ Saved recording to {filename}")



# # import whisper
# # import torch
# # import numpy as np
# # import soundfile as sf

# # def record_audio(audio_file):
# #     # Step 1: Load model safely
# #     use_gpu = torch.cuda.is_available()
# #     device = "cuda" if use_gpu else "cpu"
# #     print(f"🧠 Loading Whisper model on {device}...")

# #     # model = whisper.load_model("base", device=device)
# #     model = whisper.load_model("base").to(dtype=torch.float32)  # 👈 full precision

# #     # Force model to run in float32 even on GPU
# #     model = model.to(torch.float32)

# #     # Step 2: Warn if audio too quiet
# #     data, sr = sf.read(audio_file)
# #     if np.abs(data).mean() < 0.01:
# #         print("⚠️ Audio is very quiet. Try speaking louder or closer to mic.")

# #     # Step 3: Transcribe with safe settings
# #     print("🎧 Transcribing...")
# #     try:
# #         result = model.transcribe(audio_file, fp16=False, temperature=0.0)
# #         print("✅ Transcription successful!")
# #         return result["text"]
# #     except Exception as e:
# #         print(f"⚠️ GPU error: {e}")
# #         print("➡️ Retrying on CPU...")
# #         torch.cuda.empty_cache()
# #         model = whisper.load_model("base", device="cpu")
# #         result = model.transcribe(audio_file, fp16=False)
# #         return result["text"]


# import sounddevice as sd
# import numpy as np
# import soundfile as sf
# import whisper
# import torch

# # 🎙️ Record Audio Function
# def record_audio(filename="command.wav", duration=5, device_index=0):
#     fs = 44100  # Whisper standard sampling rate
#     print("🎙️ Recording... Speak now!")

#     # Record from mic
#     audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32', device=device_index)
#     sd.wait()

#     # Silence check
#     if np.max(np.abs(audio)) < 0.01:
#         print("⚠️ Warning: Audio seems too quiet. Try speaking louder or closer to the mic.")

#     # Normalize safely
#     max_val = np.max(np.abs(audio))
#     if max_val > 0:
#         audio = audio / max_val

#     # Save with high-quality precision
#     sf.write(filename, audio, fs)
#     print(f"✅ Saved recording to {filename}")

# # 🎧 Transcription Function (GPU-safe)
# def transcribe_audio(audio_file):
#     print("🧠 Loading Whisper model...")
#     model = whisper.load_model("base")

#     # GPU-safe: use CUDA if available, disable autocast for stability
#     if torch.cuda.is_available():
#         model = model.to("cuda")
#         print("⚙️ Using GPU for transcription (safe mode).")
#         with torch.inference_mode():
#             with torch.cuda.amp.autocast(enabled=False):
#                 result = model.transcribe(audio_file)
#     else:
#         print("⚙️ Using CPU for transcription.")
#         result = model.transcribe(audio_file)

#     text = result["text"].strip()
#     print("\n📝 Transcription:")
#     print(text)

#     # Save to file
#     with open("output.txt", "w", encoding="utf-8") as f:
#         f.write(text)
#     print("✅ Transcription saved to output.txt")


# # 🚀 Main Script
# if __name__ == "__main__":
#     record_audio("command.wav", duration=5, device_index=0)  # change index if needed
#     transcribe_audio("command.wav")



import sounddevice as sd
from scipy.io.wavfile import write


# 🎙️ Record audio
def record_audio(filename="command.wav", duration=5):
    fs = 44100
    print("🎙️ Recording... Speak now!")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    write(filename, fs, audio)
    print(f"✅ Audio saved as {filename}")


# # 🚀 Run the pipeline
# if __name__ == "__main__":
#     record_audio(duration=5)
#     transcribe_audio("command.wav")
