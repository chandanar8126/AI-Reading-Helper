"""
Advanced OCR Module
For Dyslexia AI Reading Helper
Supports image preprocessing + better OCR accuracy
"""

import cv2
import numpy as np
from PIL import Image
import pytesseract
import platform
import os

# -----------------------------
# Auto Detect Tesseract
# -----------------------------

def configure_tesseract():

    if platform.system() == "Windows":

        possible_paths = [

            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getlogin())
        ]

        for path in possible_paths:

            if os.path.exists(path):

                pytesseract.pytesseract.tesseract_cmd = path

                print(f"✅ Tesseract found at: {path}")

                return True

        print("❌ Tesseract not found. Install from:")
        print("https://github.com/UB-Mannheim/tesseract/wiki")

        return False

    return True


configure_tesseract()


# -----------------------------
# Image Preprocessing
# -----------------------------

def preprocess_image(image_path):

    try:

        img = cv2.imread(image_path)

        if img is None:
            return None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # noise removal
        blur = cv2.GaussianBlur(gray, (5,5), 0)

        # thresholding
        thresh = cv2.adaptiveThreshold(
            blur,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        return thresh

    except Exception as e:

        print("Image preprocessing error:", e)

        return None


# -----------------------------
# OCR Extraction
# -----------------------------

def extract_text(image_path):

    """
    Extract text from image
    """

    try:

        processed = preprocess_image(image_path)

        if processed is None:

            img = Image.open(image_path)

            text = pytesseract.image_to_string(img)

        else:

            text = pytesseract.image_to_string(processed)

        text = text.strip()

        if not text:

            return "⚠️ No readable text detected. Please upload a clearer image."

        return text

    except pytesseract.TesseractNotFoundError:

        return "❌ Tesseract OCR not installed."

    except Exception as e:

        return f"OCR Error: {str(e)}"


# -----------------------------
# OCR Confidence Check
# -----------------------------

def extract_text_with_confidence(image_path):

    try:

        img = cv2.imread(image_path)

        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        words = []

        confidences = []

        for i in range(len(data["text"])):

            word = data["text"][i]

            conf = int(data["conf"][i])

            if conf > 60 and word.strip():

                words.append(word)

                confidences.append(conf)

        text = " ".join(words)

        avg_conf = sum(confidences)/len(confidences) if confidences else 0

        return {

            "text": text,

            "confidence": round(avg_conf,2),

            "word_count": len(words)

        }

    except Exception as e:

        return {

            "text": "",

            "confidence": 0,

            "error": str(e)

        }


# -----------------------------
# OCR + Simplification Pipeline
# -----------------------------

def extract_and_simplify(image_path, simplifier_function):

    """
    Extract text from image and simplify it
    """

    text = extract_text(image_path)

    if not text or text.startswith("❌") or text.startswith("⚠️"):

        return text

    simplified = simplifier_function(text)

    return {

        "original_text": text,

        "simplified_text": simplified
    }


# -----------------------------
# Testing
# -----------------------------

if __name__ == "__main__":

    print("\n🔍 Testing OCR Module")

    path = input("Enter image path: ")

    text = extract_text(path)

    print("\nExtracted Text:\n")

    print(text)

    confidence_data = extract_text_with_confidence(path)

    print("\nOCR Confidence Info:")

    print(confidence_data)

def get_text_statistics(text):
    from textstat import flesch_reading_ease, flesch_kincaid_grade

    return {
        "word_count": len(text.split()),
        "sentence_count": text.count(".") + text.count("!") + text.count("?"),
        "flesch_reading_ease": round(flesch_reading_ease(text), 2),
        "flesch_kincaid_grade": round(flesch_kincaid_grade(text), 2)
    }