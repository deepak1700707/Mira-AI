

# from langchain_community.llms import Ollama
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.runnables import RunnableWithMessageHistory
# from langchain_core.chat_history import InMemoryChatMessageHistory

# # 1️⃣ Initialize LLM
# llm = Ollama(model="mistral")

# # 2️⃣ Define the chat prompt
# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are Mira, a smart AI assistant. Be helpful and concise."),
#     MessagesPlaceholder(variable_name="history"),
#     ("human", "{input}")
# ])

# # 3️⃣ Create memory store
# store = {}

# def get_session_history(session_id: str):
#     """Return chat history for a given session."""
#     if session_id not in store:
#         store[session_id] = InMemoryChatMessageHistory()
#     return store[session_id]

# # 4️⃣ Combine prompt + model + memory
# conversation = RunnableWithMessageHistory(
#     prompt | llm,
#     get_session_history,
#     input_messages_key="input",
#     history_messages_key="history"
# )

# # 5️⃣ Ask the AI
# def ask_brain(prompt: str, session_id: str = "default") -> str:
#     """Send a message to the model and get the response."""
#     response = conversation.invoke(
#         {"input": prompt},
#         config={"configurable": {"session_id": session_id}}
#     )
#     return response

# # Example test
# if __name__ == "__main__":
#     print(ask_brain("Hello, who are you?"))
#     print(ask_brain("Can you remember what I said before?"))



# from langchain_community.llms import Ollama
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.runnables import RunnableWithMessageHistory
# from langchain_core.chat_history import InMemoryChatMessageHistory

# # 1️⃣ Initialize LLM (you can replace 'mistral' with 'qwen2.5:7b' for Hindi/English mix)
# # llm = Ollama(model="qwen2.5:7b")
# llm = Ollama(model="qwen2.5:7b", options={"temperature": 0.7, "num_predict": 512})

# # 2️⃣ Define the chat prompt
# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are Mira, a smart emotional AI assistant. "
#                "You can speak both Hindi and English naturally and mix them if needed."),
#     MessagesPlaceholder(variable_name="history"),
#     ("human", "{input}")
# ])

# # 3️⃣ Create memory store
# store = {}

# def get_session_history(session_id: str):
#     """Return chat history for a given session."""
#     if session_id not in store:
#         store[session_id] = InMemoryChatMessageHistory()
#     return store[session_id]

# # 4️⃣ Combine prompt + model + memory
# conversation = RunnableWithMessageHistory(
#     prompt | llm,
#     get_session_history,
#     input_messages_key="input",
#     history_messages_key="history"
# )

# # 5️⃣ Ask the AI
# def ask_brain(prompt: str, session_id: str = "default") -> str:
#     """Send a message to the model and get the response."""
#     response = conversation.invoke(
#         {"input": prompt},
#         config={"configurable": {"session_id": session_id}}
#     )
#     return response

# # ✅ Example test
# if __name__ == "__main__":
#     print(ask_brain("Hello Mira, how are you?"))
#     print(ask_brain("तुम्हें याद है मैंने क्या पूछा था पहले?"))


# from langchain_community.llms import Ollama
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.runnables import RunnableWithMessageHistory
# from langchain_core.chat_history import InMemoryChatMessageHistory
# from transformers import pipeline


# from langchain_community.llms import Ollama
# from langchain.tools import tool
# from langchain_core.chat_history import InMemoryChatMessageHistory
# from langchain.agents import initialize_agent, AgentType
# from langchain.agents import create_react_agent, AgentExecutor

# from transformers import pipeline
# from modules import tools

# # 🔥 Emotion detection model
# emotion_classifier = pipeline(
#     "text-classification",
#     model="j-hartmann/emotion-english-distilroberta-base",
#     return_all_scores=False
# )

# # 🧠 Initialize LLM (multilingual)
# llm = Ollama(model="qwen2.5:7b", options={"temperature": 0.7, "num_predict": 512})

# # 🗨️ Base prompt
# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are Mira, an emotionally intelligent bilingual AI assistant. "
#                "You understand English and Hindi both, and can mix them naturally. "
#                "Be empathetic, friendly, and emotionally aware in your tone."),
#     MessagesPlaceholder(variable_name="history"),
#     ("human", "{input}")
# ])


# # ================================
# # 🧠 LLM + Agent Initialization
# # ================================
# llm = Ollama(
#     model="qwen2.5:7b",  # supports Hindi + English mix
#     options={"temperature": 0.7, "num_predict": 512}
# )

# # Attach tools to Mira (AI Agent)
# agent = initialize_agent(
#     [tools.get_weather, tools.web_search, tools.get_time, tools.open_youtube, tools.open_browser, tools.get_time],
#     llm,
#     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=False
# )

# # 💾 Memory store
# store = {}

# def get_session_history(session_id: str):
#     """Return chat history for a given session."""
#     if session_id not in store:
#         store[session_id] = InMemoryChatMessageHistory()
#     return store[session_id]

# # 🧩 Combine memory + prompt + model
# conversation = RunnableWithMessageHistory(
#     prompt | llm,
#     get_session_history,
#     input_messages_key="input",
#     history_messages_key="history"
# )

# # 🎭 Emotion detection
# def detect_emotion(text: str):
#     """Detect dominant emotion in text."""
#     try:
#         emotion = emotion_classifier(text)[0]["label"].lower()
#         return emotion
#     except Exception:
#         return "neutral"

# # 💬 Tone adaptation
# def tone_instruction(emotion: str):
#     tones = {
#         "joy": "Respond cheerfully and encouragingly 😊",
#         "sadness": "Respond softly, with care and empathy 💙",
#         "anger": "Respond calmly and help the user relax 😌",
#         "fear": "Respond reassuringly and gently 🤝",
#         "surprise": "Respond curiously and positively 😮",
#         "neutral": "Respond naturally and kindly 🙂"
#     }
#     return tones.get(emotion, "Respond naturally and kindly 🙂")

# # 🚀 Main AI call
# def ask_brain(prompt: str, session_id: str = "default") -> str:
#     """Send message to the model and return response with emotional tone."""
#     # emotion = detect_emotion(prompt)
#     # emotional_context = tone_instruction(emotion)

#     # full_input = f"{emotional_context}\nUser: {prompt}"
    
#     # response = conversation.invoke(
#     #     {"input": full_input},
#     #     config={"configurable": {"session_id": session_id}}
#     # )
    
#     # return f"[Emotion: {emotion}] {response}"


#     emotion = detect_emotion(prompt)
#     emotional_context = tone_instruction(emotion)

#     # Emotion prompt + user message
#     full_prompt = f"Emotion: {emotion}\n{emotional_context}\nUser: {prompt}"

#     try:
#         # Agent decides whether to use tools or not
#         response = agent.run(full_prompt)
#         return f"[Emotion: {emotion}] {response}"
#     except Exception as e:
#         return f"🔴 Error: {e}"

# # ✅ Test
# if __name__ == "__main__":
#     print(ask_brain("I am feeling very sad today..."))
#     print(ask_brain("That’s awesome! I just got promoted!"))

# ==========================================
# brain.py — AI Brain using LangGraph ReAct Agent
# ==========================================

from langchain_community.llms import Ollama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import SystemMessage
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
from langchain_community.chat_models import ChatOllama
llm = ChatOllama(model="qwen2.5:7b")

# ============================================
# 🛠️ Define Tools (LangGraph compatible)
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

def get_session_history(session_id: str):
    """Retrieve per-session message history."""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Combine agent with chat memory
conversation = RunnableWithMessageHistory(
    agent,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# ============================================
# 🎭 Emotion Detection + Tone Adaptation
# ============================================
def detect_emotion(text: str):
    """Detect user's emotional tone."""
    try:
        emotion = emotion_classifier(text)[0]["label"].lower()
        return emotion
    except Exception:
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
# 🗨️ Ask Brain
# ============================================
def ask_brain(prompt: str, session_id: str = "default") -> str:
    """Generate emotional and tool-aware responses."""
    emotion = detect_emotion(prompt)
    emotional_context = tone_instruction(emotion)

    # Combine emotional tone and user input
    full_prompt = f"Emotion: {emotion}\n{emotional_context}\nUser: {prompt}"

    try:
        result = conversation.invoke(
            {"input": full_prompt},
            config={"configurable": {"session_id": session_id}}
        )

        # LangGraph agents often return dict with 'output'
        if isinstance(result, dict):
            return f"[Emotion: {emotion}] {result.get('output', str(result))}"
        return f"[Emotion: {emotion}] {result}"

    except Exception as e:
        return f"🔴 Error: {e}"

# ============================================
# ✅ Test Run
# ============================================
if __name__ == "__main__":
    print(ask_brain("I am feeling very sad today..."))
    print(ask_brain("That’s awesome! I just got promoted!"))
