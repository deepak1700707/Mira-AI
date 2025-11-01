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

from gtts import gTTS
import os
import tempfile
import pygame

def speak(text, emotion="neutral"):
    """
    Convert AI text to speech and play with emotion-aware tone.
    Works on Python 3.13+ without playsound.
    """
    # Auto-detect Hindi or English
    lang = "hi" if any("\u0900" <= ch <= "\u097F" for ch in text) else "en"

    # Adjust speaking rate
    slow = emotion in ["sadness", "fear"]

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(fp.name)

        # Play using pygame
        pygame.mixer.init()
        pygame.mixer.music.load(fp.name)
        pygame.mixer.music.play()

        # Wait until finished
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.quit()

    except Exception as e:
        print(f"🔴 Error in speak(): {e}")
    finally:
        if os.path.exists(fp.name):
            os.remove(fp.name)
