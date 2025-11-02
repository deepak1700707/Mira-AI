
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

# --- Module Imports ---
from modules.speech_to_text import transcribe_audio
from modules.text_to_speech import speak
from modules.brain import ask_brain
from utils.mic_record import record_audio
from modules.memory_manager import save_memory
from utils.runtime_paths import ensure_runtime_dirs, get_audio_path, get_log_path, cleanup_old_files
from modules.wake_word import WakeWordDetector
from utils.wake_listener import listen_for_wake_word
# --- Fix console encoding on Windows ---
if os.name == "nt":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', errors='replace')
    except Exception:
        pass
# --- Initialize runtime directories ---
ensure_runtime_dirs()

# --- Configure Logging ---
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

log_file = get_log_path("mira_ai.log")
# Replace emojis in log messages
def remove_emojis(msg):
    return ''.join(ch for ch in msg if ord(ch) < 10000)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file, encoding='utf-8'),
              logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to: {log_file}")

# --- Global flag for graceful shutdown ---
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

    # --- Cleanup old runtime files once at startup ---
    try:
        max_age = int(os.getenv("CLEANUP_MAX_AGE_DAYS", "7"))
        cleanup_old_files(max_age_days=max_age)
    except Exception:
        pass  # Ignore cleanup errors silently

    # --- Wake word detector setup ---
    wake_word_enabled = os.getenv("WAKE_WORD_ENABLED", "true").lower() in ("true", "1", "yes")
    wake_word = os.getenv("WAKE_WORD", "jarvis")
    wake_sensitivity = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.5"))
    access_key = os.getenv("ACCESS_KEY", "YOUR_ACCESS_KEY")

    detector = None
    if wake_word_enabled:
        try:
            detector = WakeWordDetector(
                wake_word=wake_word,
                sensitivity=wake_sensitivity,
                access_key=access_key
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize wake word detector: {e}")
            detector = None

    # --- Runtime state ---
    mira_awake = False
    last_active_time = 0
    inactivity_timeout = int(os.getenv("INACTIVITY_TIMEOUT", "60"))  # seconds

    try:
        while running:
            # --- 💤 Auto Sleep Check (before recording) ---
            if mira_awake and (time.time() - last_active_time > inactivity_timeout):
                speak("I've been idle for too long, going back to sleep.")
                mira_awake = False
                continue

            # --- 💤 Wake Mode ---
            if not mira_awake:
                if wake_word_enabled and detector:
                    print("\n👂 Waiting for wake word... (say 'Hey Mira' or press Ctrl+C)")
                    wake_detected = listen_for_wake_word(detector, timeout=60)
                    if not wake_detected:
                        continue
                else:
                    # Fallback: short listening window for text-based wake detection
                    print("\n👂 Say 'Hey Mira' to activate...")
                    audio_path = get_audio_path("wake_listen.wav")
                    audio_file = record_audio(str(audio_path), duration=4, use_vad=True)
                    if not audio_file:
                        continue

                    command = transcribe_audio(audio_file)
                    if not command or not detector or not detector.detect_from_text(command):
                        continue

                # --- Wake detected ---
                print("✅ Wake word detected! Mira is awake.\n")
                speak("Hello, I'm listening.")
                mira_awake = True
                last_active_time = time.time()
                continue  # go to conversation mode

            # --- 🎙️ Active Conversation Mode ---
            logger.info("🎙️ Recording command...")
            audio_path = get_audio_path("command.wav")
            audio_file = record_audio(str(audio_path),
                                      duration=int(os.getenv("RECORDING_DURATION", "60")),
                                      use_vad=True)

            if not audio_file or not Path(audio_file).exists():
                logger.warning("⚠️ No audio file created, skipping...")
                continue

            # --- 🧠 Transcription ---
            try:
                command = transcribe_audio(audio_file)
            except Exception as e:
                logger.error(f"❌ Transcription error: {e}")
                print(f"❌ Could not transcribe audio: {e}")
                continue

            if not command or not command.strip():
                logger.info("🔇 No valid speech detected, continuing...")
                continue

            command_lower = command.lower()
            print(f"\n🗣️ You said: {command}")
            logger.info(f"User input: {command}")

            # --- 💤 Sleep Commands ---
            if any(phrase in command_lower for phrase in ["sleep", "stop listening", "goodbye", "go to sleep", "bye", "good bye"]):
                speak("Okay, going to sleep.")
                mira_awake = False
                continue

            # --- 💭 AI Response ---
            try:
                ai_reply = ask_brain(command)
                print(f"🤖 Mira-AI: {ai_reply}")
                logger.info(f"AI response: {ai_reply[:100]}...")

                emotion = "neutral"
                speak(ai_reply, emotion=emotion)
                save_memory(command, ai_reply)

                last_active_time = time.time()
                print("🎧 Listening for your next command...\n")

            except Exception as e:
                logger.error(f"❌ AI Brain error: {e}", exc_info=True)
                speak("Sorry, I encountered an error processing your request.")
                continue

    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")

    except Exception as e:
        logger.critical(f"💥 Fatal error: {e}", exc_info=True)
        print(f"💥 Fatal error: {e}")

    finally:
        # --- Cleanup ---
        if detector:
            try:
                detector.cleanup()
            except Exception:
                pass

        logger.info("👋 Mira-AI shutting down. Goodbye!")
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
