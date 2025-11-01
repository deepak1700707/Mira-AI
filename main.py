import os
import threading
import time
# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from modules.speech_to_text import transcribe_audio, load_whisper_model
from modules.text_to_speech import speak, stop_speaking
from modules.brain import ask_brain
# from modules.tools import run_tool
from utils.mic_record import record_audio
from modules.memory_manager import save_memory

# Pre-load Whisper model for better latency
print("⏳ Loading Whisper model (one-time startup)...")
whisper_model = load_whisper_model()

print("✅ Ready! Speak to start...")
print("💡 Tip: You can interrupt the AI by speaking while it's talking\n")

# Global flag for recording in background
_is_recording = False
_recording_lock = threading.Lock()

def listen_in_background(callback):
    """Continuously listen for user input in background."""
    global _is_recording
    from modules.text_to_speech import _is_speaking
    
    while True:
        # Wait until AI is not speaking
        while _is_speaking.is_set():
            time.sleep(0.1)  # Check every 100ms
        
        # Small delay after AI finishes speaking to prevent feedback
        time.sleep(0.3)
        
        with _recording_lock:
            _is_recording = True
        
        try:
            record_audio("command.wav")
            
            # Check again if AI started speaking during recording
            if _is_speaking.is_set():
                print("⏭️ Skipping transcription - AI is speaking")
                with _recording_lock:
                    _is_recording = False
                continue
            
            command = transcribe_audio("command.wav", whisper_model=whisper_model)
            
            with _recording_lock:
                _is_recording = False
            
            # Only process if there's actual text and it's not the AI's own speech
            if command and command.strip():
                # Basic filter: ignore very short responses that might be echo
                if len(command.strip()) > 3:  # At least 3 characters
                    callback(command)
        except Exception as e:
            print(f"🔴 Error in recording: {e}")
            with _recording_lock:
                _is_recording = False

def process_command(command):
    """Process user command and respond."""
    if not command or not command.strip():
        return
    
    print(f"🗣️ You said: {command}")
    
    # Stop AI if it's speaking
    stop_speaking()
    
    # # Run tool if possible
    # tool_reply = run_tool(command)
    # if tool_reply:
    #     print("🔧 Tool:", tool_reply)
    #     speak(tool_reply)
    #     save_memory(command, tool_reply)
    #     return

    # Otherwise, use AI brain
    ai_reply = ask_brain(command)
    print(f"🤖 Jarvis: {ai_reply}")
    
    # Speak in background so it can be interrupted
    speak(ai_reply, interruptible=True)
    save_memory(command, ai_reply)

# Start background listening thread
listener_thread = threading.Thread(
    target=listen_in_background,
    args=(process_command,),
    daemon=True
)
listener_thread.start()

# Keep main thread alive
try:
    while True:
        import time
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 Shutting down...")
    stop_speaking()
