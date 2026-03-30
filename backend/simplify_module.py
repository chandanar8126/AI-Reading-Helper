"""
Dyslexia Friendly AI Text Simplification System
Advanced Version
Author: Chandana Project
"""

import re
import nltk
import pyttsx3
from transformers import pipeline
from textstat import flesch_reading_ease, flesch_kincaid_grade

# download tokenizer
nltk.download('punkt')

# ----------------------------
# TEXT TO SPEECH
# ----------------------------

engine = pyttsx3.init()

def speak_text(text):
    print("\n🔊 Reading text aloud...\n")
    engine.say(text)
    engine.runAndWait()


# ----------------------------
# LOAD AI MODEL
# ----------------------------

def load_simplifier():

    models = [
        "google/flan-t5-base",
        "t5-base",
        "t5-small"
    ]

    for model in models:
        try:
            print(f"Loading model: {model}")
            return pipeline(
                "text2text-generation",
                model=model,
                max_length=256,
                truncation=True
            )
        except:
            pass

    return None


simplifier = load_simplifier()


# ----------------------------
# DYSLEXIA WORD DATASET
# ----------------------------

replacements = {

    # common academic words
    "utilize": "use",
    "facilitate": "help",
    "demonstrate": "show",
    "subsequent": "next",
    "commence": "start",
    "terminate": "end",
    "numerous": "many",
    "possess": "have",
    "purchase": "buy",
    "require": "need",
    "regarding": "about",
    "therefore": "so",
    "furthermore": "also",
    "moreover": "also",
    "consequently": "so",
    "approximately": "about",
    "assistance": "help",
    "beneficial": "helpful",
    "comprehend": "understand",
    "construct": "build",
    "determine": "find",
    "efficient": "fast",
    "fundamental": "basic",
    "identify": "find",
    "indicate": "show",
    "maintain": "keep",
    "obtain": "get",
    "participate": "take part",
    "significant": "important",
    "sufficient": "enough",
    "transform": "change",

    # science words
    "photosynthesis": "how plants make food",
    "evaporation": "water turning into vapor",
    "precipitation": "rain or snow",
    "respiration": "breathing process",

    # tech words
    "algorithm": "step by step method",
    "artificial intelligence": "smart computer system",
    "autonomous": "self driving",
    "computational": "computer based"
}


# ----------------------------
# READABILITY ANALYSIS
# ----------------------------

def calculate_readability(text):

    try:

        flesch = flesch_reading_ease(text)
        grade = flesch_kincaid_grade(text)

        difficulty = "Easy"

        if flesch < 30:
            difficulty = "Hard"

        elif flesch < 60:
            difficulty = "Medium"

        return {
            "flesch_score": round(flesch,2),
            "grade_level": round(grade,2),
            "difficulty": difficulty
        }

    except:

        return {
            "flesch_score":50,
            "grade_level":8,
            "difficulty":"Medium"
        }


# ----------------------------
# WORD SIMPLIFICATION
# ----------------------------

def replace_complex_words(text):

    for complex_word, simple_word in replacements.items():

        pattern = r"\b" + complex_word + r"\b"

        text = re.sub(pattern, simple_word, text, flags=re.IGNORECASE)

    return text


# ----------------------------
# SHORT SENTENCES
# ----------------------------

def shorten_sentences(text,max_words=15):

    sentences = text.split(".")

    new_sentences = []

    for sentence in sentences:

        words = sentence.split()

        if len(words) > max_words:

            mid = len(words)//2

            new_sentences.append(" ".join(words[:mid]))
            new_sentences.append(" ".join(words[mid:]))

        else:

            new_sentences.append(sentence)

    return ". ".join([s.strip() for s in new_sentences if s.strip()])


# ----------------------------
# RULE BASED SIMPLIFICATION
# ----------------------------

def rule_based_simplify(text):

    text = replace_complex_words(text)

    text = shorten_sentences(text)

    text = re.sub(r"\s+"," ",text)

    sentences = text.split(".")

    sentences = [s.capitalize().strip() for s in sentences if s.strip()]

    result = ". ".join(sentences)

    if not result.endswith("."):
        result += "."

    return result


# ----------------------------
# AI SIMPLIFICATION
# ----------------------------

def ai_simplify(text):

    if not simplifier:
        return None

    try:

        prompt = f"Simplify this text for a student with dyslexia: {text}"

        result = simplifier(
            prompt,
            max_length=200,
            min_length=40,
            do_sample=False
        )

        simplified = result[0]["generated_text"]

        if simplified.lower().strip() != text.lower().strip():
            return simplified

    except:

        pass

    return None


# ----------------------------
# MAIN SIMPLIFICATION
# ----------------------------

def simplify_text(text, level='basic'):

    level = (level or 'basic').lower().strip()
    if level not in ['basic', 'intermediate', 'advanced']:
        level = 'basic'

    if len(text) < 10:
        return "Text too short."

    print("\n📊 Checking readability...")

    original_stats = calculate_readability(text)

    print("Original Stats:", original_stats)

    # Level-specific AI prompt guidance
    prompt_text = text
    if level == 'basic':
        prompt_text = f"Simplify this text for a student with dyslexia using short sentences and simple words: {text}"
    elif level == 'intermediate':
        prompt_text = f"Simplify this text for a student with dyslexia while keeping moderate complexity: {text}"
    else:
        prompt_text = f"Simplify complicated words and structure in this text, preserving details for an advanced reader with dyslexia: {text}"

    print(f"\n🤖 Trying AI simplification ({level})...")

    ai_result = ai_simplify(prompt_text)

    if ai_result:
        ai_result = replace_complex_words(ai_result)

        if level == 'basic':
            ai_result = shorten_sentences(ai_result, max_words=12)
        elif level == 'intermediate':
            ai_result = shorten_sentences(ai_result, max_words=16)
        # advanced uses default more verbose sentences

        print("AI Simplification Success")

        return ai_result

    print("Using rule based simplification")

    simplified = rule_based_simplify(text)

    if level == 'advanced':
        # less aggressive for advanced level
        simplified = text
    elif level == 'intermediate':
        simplified = replace_complex_words(text)
        simplified = shorten_sentences(simplified, max_words=18)

    return simplified


# ----------------------------
# TEXT STATISTICS
# ----------------------------

def get_statistics(text):

    words = text.split()

    sentences = text.split(".")

    stats = calculate_readability(text)

    return {

        "word_count": len(words),

        "sentence_count": len(sentences),

        "avg_word_length": round(sum(len(w) for w in words)/len(words),2),

        "readability": stats
    }


# ----------------------------
# MAIN PROGRAM
# ----------------------------

if __name__ == "__main__":

    print("\n🧠 Dyslexia Friendly AI Text Simplifier\n")

    text = input("Enter text to simplify:\n\n")

    print("\n--------------------------------")

    simplified = simplify_text(text)

    print("\n📘 Simplified Text:\n")

    print(simplified)

    stats = get_statistics(simplified)

    print("\n📊 Simplified Text Statistics")

    print(stats)

    speak = input("\n🔊 Do you want the text to be read aloud? (y/n): ")

    if speak.lower() == "y":
        speak_text(simplified)

def get_text_statistics(text):
    from textstat import flesch_reading_ease, flesch_kincaid_grade

    return {
        "word_count": len(text.split()),
        "sentence_count": text.count(".") + text.count("!") + text.count("?"),
        "flesch_reading_ease": round(flesch_reading_ease(text), 2),
        "flesch_kincaid_grade": round(flesch_kincaid_grade(text), 2)
    }