"""
Audio recording module with Voice Activity Detection (VAD) support.
Detects when user is speaking and stops recording automatically.
"""
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os

# Load .env file if available (must be done before reading env vars)
try:
    from dotenv import load_dotenv
    from pathlib import Path
    # Load .env from project root (parent of utils directory)
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try current directory
        load_dotenv()
except ImportError:
    pass  # python-dotenv not installed
except Exception:
    pass  # Ignore errors, will use default values

try:
    import webrtcvad
    VAD_AVAILABLE = True
except ImportError:
    VAD_AVAILABLE = False
    print("⚠️ Warning: webrtcvad not available. Install with: pip install webrtcvad")

def record_audio(filename="command.wav", duration=30, use_vad=True, silence_duration=1.5):
    """
    Record audio from microphone with optional Voice Activity Detection.
    
    Args:
        filename: Output filename for the recording
        duration: Maximum recording duration in seconds (used if VAD disabled or falls back)
        use_vad: Enable Voice Activity Detection for automatic stop
        silence_duration: Seconds of silence before stopping (VAD only)
        
    Returns:
        str: Path to saved audio file
    """
    fs = 44100  # Sample rate
    
    # Get duration from environment if available (override default parameter)
    env_duration = os.getenv("RECORDING_DURATION")
    if env_duration:
        try:
            duration = int(env_duration)
            print(f"📝 Using duration from .env: {duration} seconds")
        except ValueError:
            print(f"⚠️ Warning: Invalid RECORDING_DURATION value: {env_duration}, using default: {duration}")
    else:
        print(f"📝 Using default duration: {duration} seconds (RECORDING_DURATION not set in .env)")
    
    # Check if VAD should be used
    vad_enabled = use_vad
    env_vad = os.getenv("VAD_ENABLED", "true").lower()
    if env_vad in ("false", "0", "no"):
        vad_enabled = False
    
    if vad_enabled and VAD_AVAILABLE:
        return _record_with_vad(filename, fs, silence_duration, max_duration=duration)
    else:
        if not VAD_AVAILABLE and use_vad:
            print("⚠️ VAD not available, using fixed duration recording")
        return _record_fixed_duration(filename, fs, duration)

def _record_fixed_duration(filename, fs, duration):
    """Record audio for a fixed duration."""
    print("🎙️ Recording... Speak now!")
    print(f"⏱️ Recording for {duration} seconds...")
    
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    
    # Check for silence
    if np.max(np.abs(audio)) < 1000:  # Very quiet threshold
        print("⚠️ Warning: Audio seems too quiet. Try speaking louder or closer to mic.")
    
    write(filename, fs, audio)
    print(f"✅ Audio saved as {filename}")
    return filename

def _record_with_vad(filename, fs, silence_duration, max_duration=60):
    """
    Record audio with Voice Activity Detection using simple amplitude-based detection.
    Stops recording after detecting silence.
    
    Args:
        filename: Output filename
        fs: Sample rate
        silence_duration: Seconds of silence before stopping
        max_duration: Maximum recording duration in seconds (default 60)
    """
    print("🎙️ Recording with Voice Activity Detection...")
    print("💬 Speak now! (Will stop automatically after silence)")
    print(f"⏱️ Maximum duration: {max_duration} seconds")
    
    frame_duration = 0.1  # 100ms frames for VAD
    frame_size = int(fs * frame_duration)
    
    audio_frames = []
    last_speech_frame = 0
    silence_threshold_frames = int(silence_duration / frame_duration)
    
    max_frames = int(max_duration / frame_duration)
    
    # Amplitude threshold for speech detection (adjustable - can be tuned via env)
    import os
    env_threshold = os.getenv("VAD_THRESHOLD", "")
    if env_threshold:
        try:
            speech_threshold = int(float(env_threshold) * 32767)  # Convert to int16 range
        except ValueError:
            speech_threshold = 2000
    else:
        speech_threshold = 2000
    
    try:
        with sd.InputStream(samplerate=fs, channels=1, dtype='int16', 
                           blocksize=frame_size) as stream:
            frames_collected = 0
            speech_detected = False
            
            while frames_collected < max_frames:
                # Read audio chunk
                audio_chunk, overflowed = stream.read(frame_size)
                if overflowed:
                    print("⚠️ Audio buffer overflow")
                
                audio_frames.append(audio_chunk)
                frames_collected += 1
                
                # Simple amplitude-based speech detection
                max_amplitude = np.max(np.abs(audio_chunk))
                is_speech = max_amplitude > speech_threshold
                
                if is_speech:
                    if not speech_detected:
                        speech_detected = True
                        print("🗣️ Speech detected...", end="", flush=True)
                    last_speech_frame = frames_collected
                else:
                    # Stop if we've had enough silence after speech was detected
                    if speech_detected and (frames_collected - last_speech_frame) >= silence_threshold_frames:
                        print("\n✅ Recording stopped (silence detected)")
                        break
                    elif frames_collected % 10 == 0:  # Print dots every second
                        print(".", end="", flush=True)
            
            if frames_collected >= max_frames:
                print(f"\n⚠️ Maximum duration ({max_duration}s) reached")
            elif not speech_detected:
                print("\n⚠️ No speech detected, using full recording")
        
        # Combine all frames
        if audio_frames:
            audio = np.concatenate(audio_frames, axis=0)
            write(filename, fs, audio)
            duration = len(audio) / fs
            print(f"✅ Audio saved as {filename} ({duration:.1f}s)")
            return filename
        else:
            print("❌ No audio recorded")
            return None
            
    except Exception as e:
        print(f"⚠️ VAD recording error: {e}")
        print(f"🔄 Falling back to fixed duration recording ({max_duration}s)...")
        return _record_fixed_duration(filename, fs, duration=max_duration)

