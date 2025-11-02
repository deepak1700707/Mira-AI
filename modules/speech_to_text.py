"""
Speech-to-text module using OpenAI Whisper.
Caches the model to avoid reloading on each transcription.
"""
import torch
import whisper
from utils.runtime_paths import get_transcript_path

# Global model cache
_whisper_model = None
_device = None

def get_whisper_model():
    """Get or load Whisper model (cached for performance)."""
    global _whisper_model, _device
    
    if _whisper_model is None:
        _device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🧠 Loading Whisper model on {_device} (float32-safe)...")
        
        # Force Whisper to use float32 precision to prevent NaN errors
        _whisper_model = whisper.load_model("base", device=_device)
        _whisper_model = _whisper_model.to(dtype=torch.float32)
        print("✅ Whisper model loaded and cached")
    
    return _whisper_model

def transcribe_audio(audio_file):
    """
    Transcribe audio file to text using Whisper.
    
    Args:
        audio_file: Path to audio file to transcribe
        
    Returns:
        str: Transcribed text
    """
    model = get_whisper_model()
    
    print("🎧 Transcribing...")
    result = model.transcribe(audio_file, fp16=False)
    
    text = result["text"].strip()
    print(f"\n📝 Transcription: {text}")
    
    # Save transcription to organized location
    try:
        transcript_path = get_transcript_path("output.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Transcription saved to {transcript_path}")
    except Exception as e:
        print(f"⚠️ Warning: Could not save transcription: {e}")
    
    return text