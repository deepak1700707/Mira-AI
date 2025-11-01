# # from gtts import gTTS
# # import os

# # def speak(text):
# #     tts = gTTS(text)
# #     tts.save("reply.mp3")
# #     os.system("mpg123 reply.mp3")

# from gtts import gTTS
# import os
# import tempfile
# import playsound

# def speak(text, lang="hi"):
#     """
#     Convert text to speech and play it.
#     Automatically supports English, Hindi, or mixed text.
#     """
#     # Detect Hindi or English content to set correct language
#     if any("\u0900" <= ch <= "\u097F" for ch in text):  # Hindi unicode range
#         lang = "hi"
#     else:
#         lang = "en"

#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
#             tts = gTTS(text=text, lang=lang)
#             tts.save(fp.name)
#             playsound.playsound(fp.name)
#     except Exception as e:
#         print(f"🔴 Error in speak(): {e}")
#     finally:
#         try:
#             os.remove(fp.name)
#         except Exception:
#             pass
import asyncio
import tempfile
import pygame
import os
import re
import edge_tts

# ✅ Remove emojis before speaking
def remove_emojis(text):
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # Flags
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

# 🎭 Main async TTS
async def _speak_async(text, lang="en", emotion="neutral"):
    text = remove_emojis(text)

    # 🎙️ Language-based neural voices
    voices = {
        "en": {
            "neutral": "en-US-JennyNeural",
            "happy": "en-US-AnaNeural",
            "sad": "en-US-GuyNeural",
            "angry": "en-US-ChristopherNeural",
        },
        "hi": {
            "neutral": "hi-IN-SwaraNeural",       # Indian female voice
            "happy": "hi-IN-MadhurNeural",        # Cheerful male voice
            "sad": "hi-IN-SwaraNeural",           # Soft tone female
            "angry": "hi-IN-MadhurNeural",        # Firm tone
        }
    }

    # 🎧 Choose the right voice
    lang_voices = voices.get(lang, voices["en"])
    voice = lang_voices.get(emotion, lang_voices["neutral"])

    # 🔊 Adjust speed & pitch slightly based on emotion
    rate_map = {
        "happy": "+15%",   # faster and energetic
        "sad": "-10%",     # slower and calm
        "angry": "+5%",    # firm and slightly faster
        "neutral": "+0%"   # normal rate (fix)
    }
    rate = rate_map.get(emotion, "0%")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        file_path = fp.name

    # Generate & save speech
    tts = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await tts.save(file_path)

    # 🎵 Play audio
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()

    os.remove(file_path)

# 🌐 Wrapper
def speak(text, emotion="neutral"):
    """Automatically detect Hindi/English and use correct accent."""
    lang = "hi" if any("\u0900" <= ch <= "\u097F" for ch in text) else "en"
    asyncio.run(_speak_async(text, lang, emotion))
