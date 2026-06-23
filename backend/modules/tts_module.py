from gtts import gTTS
import os

def generate_tts(text, filename="output.mp3"):
    if not text or not text.strip():
        text = "No text provided."
    # Save inside backend/static so Flask can serve it
    os.makedirs("static", exist_ok=True)
    filepath = os.path.join("static", filename)
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(filepath)
    return "/" + filepath.replace("\\", "/")