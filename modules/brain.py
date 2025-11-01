from langchain_community.llms import Ollama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableWithMessageHistory
from transformers import pipeline
from langchain.agents import create_agent
from modules.tools import get_weather  # your existing custom tools file

# ============================================
# 🔥 Emotion Detection (Hugging Face)
# ============================================
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=False
)

# ============================================
# 🧠 Initialize LLM (Bilingual - Hindi + English)
# ============================================
# llm = Ollama(model="qwen2.5:7b")
from langchain_ollama import ChatOllama
# Using smaller model for better memory efficiency
# Options: qwen2.5:1.5b (smallest), qwen2.5:3b, qwena2.5:7b (if you have enough RAM)
llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0.7,
    num_predict=512
)

# ============================================
# 🛠 Define Tools (LangGraph compatible)
# ============================================
search_tool = DuckDuckGoSearchRun()
custom_tools = [get_weather]

# combine both built-in + custom
tools_list = [search_tool] + custom_tools

# ============================================
# 🤖 Create ReAct Agent (New LangGraph)
# ============================================
agent = create_agent(llm, tools_list)

# ============================================
# 💾 Memory Management
# ============================================
store = {}

def get_session_messages(session_id: str):
    """Retrieve per-session message history."""
    if session_id not in store:
        store[session_id] = []
    return store[session_id]

# ============================================
# 🎭 Emotion Detection + Tone Adaptation
# ============================================
def detect_emotion(text: str):
    """Detect user's emotional tone."""
    try:
        if not text or not text.strip():
            return "neutral"
        result = emotion_classifier(text)
        if result and len(result) > 0:
            emotion = result[0]["label"].lower()
            # Map emotion labels to our supported emotions
            emotion_map = {
                "joy": "joy",
                "happiness": "joy",
                "sadness": "sadness",
                "sad": "sadness",
                "anger": "anger",
                "angry": "anger",
                "fear": "fear",
                "afraid": "fear",
                "surprise": "surprise",
                "surprised": "surprise",
                "neutral": "neutral"
            }
            return emotion_map.get(emotion, "neutral")
        return "neutral"
    except Exception as e:
        # Debug: print error but return neutral
        # print(f"Emotion detection error: {e}")
        return "neutral"

def tone_instruction(emotion: str):
    """Map emotion → appropriate tone."""
    tones = {
        "joy": "Respond cheerfully and encouragingly 😊",
        "sadness": "Respond softly, with care and empathy 💙",
        "anger": "Respond calmly and help the user relax 😌",
        "fear": "Respond reassuringly and gently 🤝",
        "surprise": "Respond curiously and positively 😮",
        "neutral": "Respond naturally and kindly 🙂"
    }
    return tones.get(emotion, "Respond naturally and kindly 🙂")

# ============================================
# 🗨 Ask Brain
# ============================================
def ask_brain(prompt: str, session_id: str = "default") -> str:
    """Generate emotional and tool-aware responses."""
    emotion = detect_emotion(prompt)
    emotional_context = tone_instruction(emotion)

    # Combine emotional tone and user input
    full_prompt = f"Emotion: {emotion}\n{emotional_context}\nUser: {prompt}"

    try:
        # Get conversation history
        history = get_session_messages(session_id)
        
        # Build messages list with history
        messages = history + [HumanMessage(content=full_prompt)]
        
        # Invoke agent directly
        result = agent.invoke({"messages": messages})
        
        # Extract the last AI message from the result
        if isinstance(result, dict):
            result_messages = result.get("messages", [])
            if result_messages:
                # Find the last AI message
                for msg in reversed(result_messages):
                    if isinstance(msg, AIMessage) and msg.content:
                        # Update history with all new messages
                        store[session_id] = result_messages
                        # Return just the content without emotion prefix
                        return msg.content
            
            return result.get('output', str(result))
        
        # If result is a list of messages
        if isinstance(result, list) and len(result) > 0:
            # Update history
            store[session_id] = result
            # Find last AI message
            for msg in reversed(result):
                if isinstance(msg, AIMessage) and msg.content:
                    # Return just the content without emotion prefix
                    return msg.content
        
        return str(result)

    except ConnectionRefusedError:
        return "🔴 Error: Cannot connect to Ollama. Please make sure Ollama is running:\n   Run: ollama serve"
    except Exception as e:
        error_msg = str(e)
        if "Connection refused" in error_msg or "[Errno 61]" in error_msg:
            return "🔴 Error: Cannot connect to Ollama. Please make sure Ollama is running:\n   Run: ollama serve"
        if "system memory" in error_msg.lower() or "unable to load" in error_msg.lower():
            return "🔴 Error: Model requires too much memory. Try using a smaller model like 'qwen2.5:1.5b' or 'qwen2.5:3b'.\n   Update model in modules/brain.py"
        return f"🔴 Error: {e}"

# ============================================
# ✅ Test Run
# ============================================
if __name__ == "_main_":
    print(ask_brain("I am feeling very sad today..."))
    print(ask_brain("That’s awesome! I just got promoted!"))