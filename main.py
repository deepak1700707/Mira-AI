from modules.speech_to_text import transcribe_audio
from modules.text_to_speech import speak
from modules.brain import ask_brain
# from modules.tools import run_tool
from utils.mic_record import record_audio
from modules.memory_manager import save_memory

while True:
    record_audio("command.wav")
    command = transcribe_audio("command.wav")
    print("🗣️ You said:", command)

    # # Run tool if possible
    # tool_reply = run_tool(command)
    # if tool_reply:
    #     print("🔧 Tool:", tool_reply)
    #     speak(tool_reply)
    #     save_memory(command, tool_reply)
    #     continue

    # Otherwise, use AI brain
    ai_reply = ask_brain(command)
    print("🤖 Jarvis:", ai_reply)
    speak(ai_reply)
    save_memory(command, ai_reply)
