"""
Mira-AI - Voice-Activated AI Assistant
Main entry point for the application.
"""
import time
import signal
import sys
import logging
import os
from pathlib import Path
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
    wake_word = os.getenv("WAKE_WORD", "jarvis")
    wake_sensitivity = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.5"))
    access_key = os.getenv("ACCESS_KEY", "YOUR_ACCESS_KEY")
    
    detector = None
    if wake_word_enabled:
        try:
            detector = WakeWordDetector(wake_word=wake_word, sensitivity=wake_sensitivity, access_key=access_key)
        except Exception as e:
            logger.warning(f"Could not initialize wake word detector: {e}")
            detector = None
    try:
        mira_awake = False
        last_active_time = 0
        inactivity_timeout = int(os.getenv("INACTIVITY_TIMEOUT", "60"))  # seconds

        while running:
            try:
                # --- 1️⃣ Wake Mode (waiting for wake word) ---
                if not mira_awake:
                    if wake_word_enabled and detector:
                        print("\n👂 Waiting for wake word... (say 'Hey Mira' or press Ctrl+C)")
                        if detector.use_porcupine:
                            wake_detected = listen_for_wake_word(detector, timeout=None)
                            if not wake_detected:
                                continue
                        else:
                            # Fallback text-based wake detection
                            print("\n👂 Say 'Hey Mira' to activate...")
                            audio_path = get_audio_path("wake_listen.wav")
                            audio_file = record_audio(str(audio_path), duration=4, use_vad=True)
                            if not audio_file:
                                continue
                            command = transcribe_audio(audio_file)
                            if not command:
                                continue
                            if not detector.detect_from_text(command):
                                continue
                        
                        # Wake detected
                        print("✅ Wake word detected! Mira is awake.\n")
                        speak("Hello, I'm listening.")
                        mira_awake = True
                        last_active_time = time.time()
                        continue  # go to conversation loop

                # --- 2️⃣ Active Conversation Mode ---
                logger.info("🎙️ Recording command...")
                audio_path = get_audio_path("command.wav")
                audio_file = record_audio(str(audio_path), duration=int(os.getenv("RECORDING_DURATION", "60")), use_vad=True)

                if not audio_file or not Path(audio_file).exists():
                    logger.warning("⚠️ No audio file created, skipping...")
                    continue

                # --- Transcription ---
                try:
                    command = transcribe_audio(audio_file)
                except Exception as e:
                    logger.error(f"❌ Transcription error: {e}")
                    print(f"❌ Could not transcribe audio: {e}")
                    continue

                if not command or not command.strip():
                    logger.info("🔇 No speech detected, continuing...")
                    continue

                command_lower = command.lower()
                print(f"\n🗣️ You said: {command}")
                logger.info(f"User input: {command}")

                # --- 3️⃣ Handle "sleep" / "stop listening" commands ---
                if any(word in command_lower for word in ["sleep", "stop listening", "Good bye", "goodbye", "go to sleep"]):
                    speak("Okay, going to sleep.")
                    mira_awake = False
                    continue

                # --- 4️⃣ Get AI Response ---
                try:
                    ai_reply = ask_brain(command)
                    print(f"🤖 Mira-AI: {ai_reply}")
                    logger.info(f"AI response: {ai_reply[:100]}...")  # Log first 100 chars

                    emotion = "neutral"  # can be extracted later
                    speak(ai_reply, emotion=emotion)
                    save_memory(command, ai_reply)

                    last_active_time = time.time()

                    # After each reply, Mira stays awake and prompts again
                    speak("I'm still listening.")
                    print("🎧 Mira is listening for your next command...\n")

                except Exception as e:
                    error_msg = f"❌ AI Brain error: {e}"
                    logger.error(error_msg)
                    print(error_msg)
                    speak("Sorry, I encountered an error processing your request.")
                    continue

                # --- 5️⃣ Auto sleep if inactive for too long ---
                if mira_awake and (time.time() - last_active_time > inactivity_timeout):
                    speak("I've been idle for too long, going back to sleep.")
                    mira_awake = False
                    continue

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
