# tts_module.py
from gtts import gTTS
import os

def generate_tts(text, filename="output.mp3"):
    if not text:
        text = "No text provided."
    os.makedirs("static", exist_ok=True)
    filepath = os.path.join("static", filename)
    tts = gTTS(text)
    tts.save(filepath)
    return "/" + filepath.replace("\\", "/")
