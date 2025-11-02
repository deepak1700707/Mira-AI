"""
Text-to-speech module using Edge TTS.
Supports bilingual (Hindi/English) speech with emotion-based voice modulation.
"""
import asyncio
import tempfile
import pygame
import os
import re
import edge_tts

def remove_emojis(text):
    """Remove emojis from text before speaking."""
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # Flags
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

async def _speak_async(text, lang="en", emotion="neutral"):
    """
    Async function to convert text to speech.
    
    Args:
        text: Text to speak
        lang: Language code ("en" or "hi")
        emotion: Emotional tone ("neutral", "happy", "sad", "angry")
    """
    text = remove_emojis(text)

    # Language-based neural voices
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

    # Choose the right voice
    lang_voices = voices.get(lang, voices["en"])
    voice = lang_voices.get(emotion, lang_voices["neutral"])

    # Adjust speed & pitch slightly based on emotion
    rate_map = {
        "happy": "+15%",   # faster and energetic
        "sad": "-10%",     # slower and calm
        "angry": "+5%",    # firm and slightly faster
        "neutral": "+0%"   # normal rate
    }
    rate = rate_map.get(emotion, "0%")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        file_path = fp.name

    try:
        # Generate & save speech
        tts = edge_tts.Communicate(text=text, voice=voice, rate=rate)
        await tts.save(file_path)

        # Play audio
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
    finally:
        # Clean up temp file
        try:
            os.remove(file_path)
        except Exception:
            pass

def speak(text, emotion="neutral"):
    """
    Convert text to speech with automatic language detection.
    
    Args:
        text: Text to speak (automatically detects Hindi/English)
        emotion: Emotional tone for voice modulation
    """
    # Automatically detect Hindi/English and use correct accent
    lang = "hi" if any("\u0900" <= ch <= "\u097F" for ch in text) else "en"
    
    try:
        asyncio.run(_speak_async(text, lang, emotion))
    except Exception as e:
        print(f"⚠️ Error in text-to-speech: {e}")
