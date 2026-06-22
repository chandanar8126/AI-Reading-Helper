from ocr_module import extract_text

# Test if Tesseract is working
try:
    import pytesseract
    version = pytesseract.get_tesseract_version()
    print(f"✅ Tesseract installed: Version {version}")
except:
    print("❌ Tesseract NOT installed!")
    print("Please install from: https://github.com/UB-Mannheim/tesseract/wiki")