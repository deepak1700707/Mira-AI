"""
Wake Word Listener
Continuously listens for wake words and triggers recording when detected.
Supports both continuous listening mode and manual trigger.
"""
import sounddevice as sd
import numpy as np
from pathlib import Path
from modules.wake_word import WakeWordDetector, detect_wake_word_keyword
import os

# Load .env if available
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

def listen_for_wake_word(detector: WakeWordDetector, sample_rate: int = 16000, 
                        timeout: float = None) -> bool:
    """
    Continuously listen for wake word using Porcupine (if available).
    
    Args:
        detector: WakeWordDetector instance
        sample_rate: Audio sample rate (Porcupine uses 16000)
        timeout: Maximum time to listen in seconds (None = infinite)
        
    Returns:
        bool: True if wake word detected
    """
    if not detector.use_porcupine:
        return False  # Use text-based detection instead
    
    frame_length = detector.porcupine.frame_length
    
    print("👂 Listening for wake word... (say 'Hey Mira')")
    
    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, 
                           dtype='int16', blocksize=frame_length) as stream:
            frames_collected = 0
            max_frames = int(timeout * sample_rate / frame_length) if timeout else None
            
            while True:
                audio_chunk, overflowed = stream.read(frame_length)
                
                if overflowed:
                    print("[WARNING] Audio buffer overflow")
                
                # Convert to numpy array
                audio_data = np.frombuffer(audio_chunk, dtype=np.int16).flatten()
                
                # Check for wake word
                if detector.detect_from_audio(audio_data):
                    print("✅ Wake word detected!")
                    return True
                
                frames_collected += 1
                if max_frames and frames_collected >= max_frames:
                    return False
                
                # Show listening indicator every 2 seconds
                if frames_collected % (2 * sample_rate // frame_length) == 0:
                    print(".", end="", flush=True)
    
    except KeyboardInterrupt:
        return False
    except Exception as e:
        print(f"[WARNING] Wake word listening error: {e}")
        return False

def quick_wake_check(detector: WakeWordDetector, audio_file: str) -> bool:
    """
    Quick check if audio file contains wake word (for fallback mode).
    Records short audio, transcribes, and checks for wake word.
    
    Args:
        detector: WakeWordDetector instance
        audio_file: Path to save quick check audio
        
    Returns:
        bool: True if wake word detected in transcription
    """
    # Quick 2-second recording for wake word check
    fs = 16000  # Lower sample rate for faster processing
    
    try:
        print("👂 Quick wake word check...")
        duration = 2
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        
        # Save temporarily
        from scipy.io.wavfile import write
        write(audio_file, fs, audio)
        
        # Quick transcription check would go here, but requires Whisper
        # For now, we'll use continuous listening mode instead
        return False
    except Exception:
        return False

