#  AI Reading Helper for Dyslexia Students

##  Overview
AI Reading Helper is an AI-powered web application designed to assist dyslexic users by simplifying complex text, extracting text from images, and providing audio support for better comprehension.

---

##  Key Features

### 🔹 AI-Based Text Simplification
- Uses transformer-based models (T5 / FLAN-T5 via HuggingFace)
- Converts complex sentences into simpler, more readable versions

### 🔹 Hybrid Simplification Approach
- Combines:
  - AI-generated simplification
  - Rule-based techniques (word replacement, sentence splitting)
- Ensures better clarity and accuracy

### 🔹 OCR (Image to Text)
- Extracts text from images using Tesseract OCR

### 🔹 Text-to-Speech (TTS)
- Converts simplified text into speech using gTTS

### 🔹 Readability Analysis
Evaluates text using:
- Flesch Reading Ease
- Flesch-Kincaid Grade Level

### 🔹 User System & Progress Tracking
- User login system
- Reading history tracking
- Progress monitoring

### 🔹 Difficulty Detection (In Progress)
- Eye-tracking inspired module
- Logs reading difficulty events

---

##  Tech Stack

**Backend:**
- Flask (Python)

**AI / NLP:**
- HuggingFace Transformers (T5, FLAN-T5)
- PyTorch

**OCR:**
- Tesseract (pytesseract)

**Text Processing:**
- NLTK
- TextStat

**Computer Vision:**
- OpenCV

**Speech:**
- gTTS

**Database:**
- SQLite

---

##  How It Works

1. User inputs text or uploads an image  
2. OCR extracts text (if image is provided)  
3. Text is simplified using:
   - Transformer-based AI model
   - Rule-based processing  
4. Readability metrics are calculated  
5. Output is displayed  
6. Optional: Text is converted to speech  

---

##  How to Run

```bash
pip install -r requirements.txt
python app.py
```
## Future Improvements

- **Fine-tuning transformer models (T5 / FLAN-T5)** on dyslexia-friendly datasets to improve simplification quality and contextual understanding  

- **Enhancing difficulty detection module** by integrating real-time eye-tracking or behavioral signals (e.g., reading pauses, re-reading patterns)  

- **Speech-to-Text integration** to allow users to interact with the system using voice input for improved accessibility  

- **Personalized learning analytics** using user reading history to adapt simplification levels and track progress over time  

- **Deployment and real-world testing** with dyslexic users to evaluate usability and effectiveness  
