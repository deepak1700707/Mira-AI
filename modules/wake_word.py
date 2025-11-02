"""
Wake Word Detection Module
Detects "Hey Mira" or custom wake words before activating the assistant.
Supports both Porcupine (offline) and fallback keyword detection.
"""
import os
from pathlib import Path

# Try to import Porcupine for real wake word detection
PORCUPINE_AVAILABLE = False
try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    pass

def detect_wake_word_keyword(text: str, wake_words: list = None) -> bool:
    """
    Simple keyword-based wake word detection from transcribed text.
    Fallback method when Porcupine is not available.
    
    Args:
        text: Transcribed text to check
        wake_words: List of wake word phrases (default: ["hey mira", "hey mirah"])
        
    Returns:
        bool: True if wake word detected
    """
    if wake_words is None:
        wake_words = ["hey mira", "hey mirah", "mira", "activate"]
    
    text_lower = text.lower().strip()
    for wake_word in wake_words:
        if wake_word in text_lower:
            return True
    return False

class WakeWordDetector:
    """Wake word detector using Porcupine (primary) or keyword fallback."""
    
    def __init__(self, wake_word: str = "hey-mira", sensitivity: float = 0.5):
        """
        Initialize wake word detector.
        
        Args:
            wake_word: Wake word to detect (for Porcupine) or keyword list
            sensitivity: Detection sensitivity (0.0 to 1.0, higher = more sensitive)
        """
        self.wake_word = wake_word
        self.sensitivity = sensitivity
        self.porcupine = None
        self.use_porcupine = False
        
        # Try to initialize Porcupine
        if PORCUPINE_AVAILABLE:
            try:
                # Use built-in wake words (works offline, no API key needed for built-ins)
                # Available: "hey-mira", "hey siri", "alexa", etc.
                self.porcupine = pvporcupine.create(
                    keywords=[wake_word],
                    sensitivities=[sensitivity]
                )
                self.use_porcupine = True
                print(f"[OK] Wake word detection enabled (Porcupine): '{wake_word}'")
            except Exception as e:
                print(f"[WARNING] Porcupine initialization failed: {e}")
                print("[INFO] Falling back to keyword-based detection")
                self.use_porcupine = False
        else:
            print("[INFO] Porcupine not installed, using keyword-based detection")
            print("[TIP] Install with: pip install pvporcupine")
            self.use_porcupine = False
    
    def detect_from_audio(self, audio_data, sample_rate: int = 16000) -> bool:
        """
        Detect wake word from audio data (Porcupine method).
        
        Args:
            audio_data: Audio samples (must match Porcupine sample rate)
            sample_rate: Audio sample rate (Porcupine uses 16000)
            
        Returns:
            bool: True if wake word detected
        """
        if not self.use_porcupine or self.porcupine is None:
            return False
        
        try:
            # Porcupine expects specific frame length
            frame_length = self.porcupine.frame_length
            
            # Process audio in chunks
            if len(audio_data) >= frame_length:
                # Process the first frame_length samples
                keyword_index = self.porcupine.process(audio_data[:frame_length])
                return keyword_index >= 0
        except Exception as e:
            print(f"[WARNING] Wake word detection error: {e}")
        
        return False
    
    def detect_from_text(self, text: str) -> bool:
        """
        Detect wake word from transcribed text (fallback method).
        
        Args:
            text: Transcribed text
            
        Returns:
            bool: True if wake word detected
        """
        wake_words = ["hey mira", "hey mirah", "mira activate", "activate mira"]
        return detect_wake_word_keyword(text, wake_words)
    
    def cleanup(self):
        """Clean up Porcupine resources."""
        if self.porcupine:
            self.porcupine.delete()

