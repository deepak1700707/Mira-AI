"""
Mira-AI - Voice-Activated AI Assistant
Main entry point for the application.
"""
import signal
import sys
import logging
import os
from pathlib import Path

# Load .env file FIRST before any other imports that might use env vars
# Also create .env from env_example.txt if it doesn't exist
try:
    from dotenv import load_dotenv
    
    env_path = Path(__file__).parent / ".env"
    example_path = Path(__file__).parent / "env_example.txt"
    
    # Create .env file if it doesn't exist
    if not env_path.exists() and example_path.exists():
        try:
            with open(example_path, "r", encoding="utf-8") as f:
                content = f.read()
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[INFO] Created .env file from env_example.txt")
        except Exception as e:
            print(f"[WARNING] Could not create .env file: {e}")
    
    # Load .env from project root
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[OK] Loaded .env file from: {env_path}")
    else:
        # Try current directory
        load_dotenv()
        print(f"[WARNING] .env file not found at {env_path}, trying current directory")
except ImportError:
    print("[WARNING] python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"[WARNING] Error loading .env: {e}")

from modules.speech_to_text import transcribe_audio
from modules.text_to_speech import speak
from modules.brain import ask_brain
from utils.mic_record import record_audio
from modules.memory_manager import save_memory
from utils.runtime_paths import ensure_runtime_dirs, get_audio_path, get_log_path, cleanup_old_files
from modules.wake_word import WakeWordDetector
from utils.wake_listener import listen_for_wake_word

# Initialize runtime directories
ensure_runtime_dirs()

# Configure logging with organized path
log_file = get_log_path("mira_ai.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to: {log_file}")

# Global flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    global running
    logger.info("\n🛑 Shutting down gracefully...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    """Main application loop."""
    logger.info("🚀 Mira-AI starting up...")
    logger.info("💡 Press Ctrl+C to exit gracefully")
    
    # Clean up old runtime files (optional, runs once at startup)
    try:
        max_age = int(os.getenv("CLEANUP_MAX_AGE_DAYS", "7"))
        cleanup_old_files(max_age_days=max_age)
    except Exception:
        pass  # Silently fail if cleanup doesn't work
    
    # Initialize wake word detector
    wake_word_enabled = os.getenv("WAKE_WORD_ENABLED", "true").lower() in ("true", "1", "yes")
    wake_word = os.getenv("WAKE_WORD", "hey-mira")
    wake_sensitivity = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.5"))
    
    detector = None
    if wake_word_enabled:
        try:
            detector = WakeWordDetector(wake_word=wake_word, sensitivity=wake_sensitivity)
        except Exception as e:
            logger.warning(f"Could not initialize wake word detector: {e}")
            detector = None
    
    try:
        while running:
            try:
                # Wake word detection (if enabled)
                if wake_word_enabled and detector:
                    if detector.use_porcupine:
                        # Continuous listening with Porcupine
                        print("\n👂 Waiting for wake word... (say 'Hey Mira' or press Ctrl+C)")
                        wake_detected = listen_for_wake_word(detector, timeout=None)
                        if not wake_detected:
                            continue  # Keep listening
                        print("✅ Wake word detected! Starting recording...\n")
                    else:
                        # Fallback: Record short clip and check for wake word in transcription
                        print("\n👂 Say 'Hey Mira' to activate...")
                
                # Record audio (VAD enabled by default, duration from .env or default 60 seconds)
                logger.info("🎙️ Recording...")
                # Get duration from .env file (already loaded at top of file)
                default_duration = int(os.getenv("RECORDING_DURATION", "60"))
                
                # Use organized audio path
                audio_path = get_audio_path("command.wav")
                audio_file = record_audio(str(audio_path), duration=default_duration, use_vad=True)
                
                if not audio_file or not Path(audio_file).exists():
                    logger.warning("⚠️ No audio file created, skipping...")
                    continue
                
                # Transcribe
                try:
                    command = transcribe_audio(audio_file)
                except Exception as e:
                    logger.error(f"❌ Transcription error: {e}")
                    print(f"❌ Could not transcribe audio: {e}")
                    continue
                
                if not command or not command.strip():
                    logger.info("🔇 No speech detected, continuing...")
                    continue
                
                # Check for wake word in transcription (fallback mode)
                if wake_word_enabled and detector and not detector.use_porcupine:
                    if detector.detect_from_text(command):
                        # Wake word detected, remove it from command and continue
                        print("✅ Wake word detected in transcription!")
                        # Remove wake word phrases from command
                        wake_phrases = ["hey mira", "hey mirah", "mira activate", "activate mira"]
                        command_lower = command.lower()
                        for phrase in wake_phrases:
                            if phrase in command_lower:
                                command = command.replace(phrase, "", 1).strip()
                                break
                        
                        # If command is empty after removing wake word, continue listening
                        if not command:
                            logger.info("Wake word detected but no command, continuing...")
                            continue
                    else:
                        # No wake word, skip this recording
                        logger.info("No wake word detected, ignoring...")
                        continue
                
                print(f"\n🗣️ You said: {command}")
                logger.info(f"User input: {command}")
                
                # Let the AI agent handle everything, including tool selection
                # The agent will automatically decide when to use tools (weather, time, search, etc.)
                try:
                    ai_reply = ask_brain(command)
                    print(f"🤖 Mira-AI: {ai_reply}")
                    logger.info(f"AI response: {ai_reply[:100]}...")  # Log first 100 chars
                    
                    # Extract emotion from brain response if available
                    emotion = "neutral"  # Could be extracted from brain response
                    speak(ai_reply, emotion=emotion)
                    save_memory(command, ai_reply)
                    
                except Exception as e:
                    error_msg = f"❌ AI Brain error: {e}"
                    logger.error(error_msg)
                    print(error_msg)
                    speak("Sorry, I encountered an error processing your request.")
                
            except KeyboardInterrupt:
                logger.info("🛑 Interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in main loop: {e}", exc_info=True)
                print(f"❌ Unexpected error: {e}")
                continue
    
    except Exception as e:
        logger.critical(f"💥 Fatal error: {e}", exc_info=True)
        print(f"💥 Fatal error: {e}")
    finally:
        # Cleanup wake word detector
        if detector:
            try:
                detector.cleanup()
            except Exception:
                pass
        
        logger.info("👋 Mira-AI shutting down. Goodbye!")
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
