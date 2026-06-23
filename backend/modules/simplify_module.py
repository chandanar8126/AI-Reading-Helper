"""
Dyslexia Friendly AI Text Simplification System
Author: Chandana R
"""

import re
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# ----------------------------
# LAZY MODEL LOADING
# Why: Loading transformers at startup crashes if torchvision
# has a version conflict. Lazy loading means the model only
# loads when the first simplification request comes in.
# ----------------------------

_simplifier = None

def get_simplifier():
    global _simplifier
    if _simplifier is not None:
        return _simplifier
    try:
        from transformers import pipeline
        models = ["google/flan-t5-base", "t5-base", "t5-small"]
        for model in models:
            try:
                print(f"Loading model: {model}")
                _simplifier = pipeline(
                    "text2text-generation",
                    model=model,
                    max_length=256,
                    truncation=True
                )
                print(f"Model loaded: {model}")
                return _simplifier
            except Exception:
                continue
    except Exception as e:
        print(f"Could not load AI model: {e}")
    return None


# ----------------------------
# DYSLEXIA WORD DICTIONARY
# Why: Some words are hard for dyslexic readers.
# We replace them with simpler alternatives.
# ----------------------------

replacements = {
    # Academic
    "utilize": "use", "facilitate": "help", "demonstrate": "show",
    "subsequent": "next", "commence": "start", "terminate": "end",
    "numerous": "many", "possess": "have", "purchase": "buy",
    "require": "need", "regarding": "about", "therefore": "so",
    "furthermore": "also", "moreover": "also", "consequently": "so",
    "approximately": "about", "assistance": "help", "beneficial": "helpful",
    "comprehend": "understand", "construct": "build", "determine": "find",
    "efficient": "fast", "fundamental": "basic", "identify": "find",
    "indicate": "show", "maintain": "keep", "obtain": "get",
    "participate": "take part", "significant": "important",
    "sufficient": "enough", "transform": "change",
    "implement": "use", "establish": "set up", "individuals": "people",
    "components": "parts", "additional": "more", "however": "but",
    "although": "even though", "necessary": "needed", "previous": "last",
    "currently": "now", "specifically": "exactly", "generally": "usually",
    # Science
    "photosynthesis": "how plants make food",
    "evaporation": "water turning into vapor",
    "precipitation": "rain or snow",
    "respiration": "breathing process",
    "mitochondria": "energy maker in cells",
    "hypothesis": "educated guess",
    "organism": "living thing",
    "environment": "surroundings",
    # Tech
    "algorithm": "step by step method",
    "artificial intelligence": "smart computer system",
    "autonomous": "self driving",
    "computational": "computer based",
    "database": "organized data storage",
    "interface": "screen or display",
    "parameter": "setting or value",
    # Medical
    "diagnosis": "finding out what illness",
    "symptom": "sign of illness",
    "medication": "medicine",
    "physician": "doctor",
    "chronic": "long lasting",
    "acute": "sudden and severe",
}


# ----------------------------
# READABILITY SCORING
# Why: Flesch Reading Ease tells us how hard text is to read.
# Higher score = easier. Below 30 = very hard, above 60 = easy.
# ----------------------------

def calculate_readability(text):
    try:
        flesch = flesch_reading_ease(text)
        grade = flesch_kincaid_grade(text)
        if flesch < 30:
            difficulty = "Hard"
        elif flesch < 60:
            difficulty = "Medium"
        else:
            difficulty = "Easy"
        return {
            "flesch_score": round(flesch, 2),
            "grade_level": round(grade, 2),
            "difficulty": difficulty
        }
    except Exception:
        return {"flesch_score": 50, "grade_level": 8, "difficulty": "Medium"}


# ----------------------------
# WORD REPLACEMENT
# ----------------------------

def replace_complex_words(text):
    for complex_word, simple_word in replacements.items():
        pattern = r"\b" + re.escape(complex_word) + r"\b"
        text = re.sub(pattern, simple_word, text, flags=re.IGNORECASE)
    return text


# ----------------------------
# SENTENCE SPLITTING
# Why: Long sentences are hard for dyslexic readers.
# We use NLTK to split properly instead of cutting at midpoint.
# ----------------------------

def shorten_sentences(text, max_words=15):
    try:
        from nltk.tokenize import sent_tokenize
        sentences = sent_tokenize(text)
    except Exception:
        sentences = text.split(".")

    new_sentences = []
    for sentence in sentences:
        words = sentence.split()
        if len(words) > max_words:
            mid = len(words) // 2
            new_sentences.append(" ".join(words[:mid]))
            new_sentences.append(" ".join(words[mid:]))
        else:
            new_sentences.append(sentence)

    result = ". ".join([s.strip() for s in new_sentences if s.strip()])
    if result and not result.endswith("."):
        result += "."
    return result


# ----------------------------
# RULE BASED SIMPLIFICATION
# ----------------------------

def rule_based_simplify(text):
    text = replace_complex_words(text)
    text = shorten_sentences(text)
    text = re.sub(r"\s+", " ", text)
    sentences = [s.capitalize().strip() for s in text.split(".") if s.strip()]
    result = ". ".join(sentences)
    if not result.endswith("."):
        result += "."
    return result


# ----------------------------
# AI SIMPLIFICATION
# ----------------------------

def ai_simplify(prompt_text):
    simplifier = get_simplifier()
    if not simplifier:
        return None
    try:
        result = simplifier(
            prompt_text,
            max_length=200,
            min_length=40,
            do_sample=False
        )
        simplified = result[0]["generated_text"]
        if simplified.lower().strip() != prompt_text.lower().strip():
            return simplified
    except Exception:
        pass
    return None


# ----------------------------
# MAIN SIMPLIFICATION FUNCTION
# ----------------------------

def simplify_text(text, level='basic'):
    level = (level or 'basic').lower().strip()
    if level not in ['basic', 'intermediate', 'advanced']:
        level = 'basic'

    if len(text) < 10:
        return "Text too short to simplify."

    if level == 'basic':
        prompt = f"Simplify this text for a student with dyslexia using short sentences and simple words: {text}"
    elif level == 'intermediate':
        prompt = f"Simplify this text for a student with dyslexia while keeping moderate complexity: {text}"
    else:
        prompt = f"Simplify complicated words in this text, preserving details for an advanced reader with dyslexia: {text}"

    ai_result = ai_simplify(prompt)

    if ai_result:
        ai_result = replace_complex_words(ai_result)
        if level == 'basic':
            ai_result = shorten_sentences(ai_result, max_words=12)
        elif level == 'intermediate':
            ai_result = shorten_sentences(ai_result, max_words=16)
        return ai_result

    # Fallback to rule based
    if level == 'advanced':
        return replace_complex_words(text)
    elif level == 'intermediate':
        result = replace_complex_words(text)
        return shorten_sentences(result, max_words=18)
    else:
        return rule_based_simplify(text)


# ----------------------------
# STATISTICS — single function, no duplicate
# ----------------------------

def get_text_statistics(text):
    words = text.split()
    if not words:
        return {"word_count": 0, "sentence_count": 0,
                "flesch_reading_ease": 0, "flesch_kincaid_grade": 0}
    stats = calculate_readability(text)
    return {
        "word_count": len(words),
        "sentence_count": text.count(".") + text.count("!") + text.count("?"),
        "flesch_reading_ease": stats["flesch_score"],
        "flesch_kincaid_grade": stats["grade_level"]
    }