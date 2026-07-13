"""OCR extraction module using Tesseract."""
import pytesseract
from PIL import Image, ImageFilter
import platform

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(image_path: str) -> str:
    """Extract text from an image using Tesseract OCR."""
    try:
        img = Image.open(image_path)
        img = img.convert("L")
        img = img.filter(ImageFilter.SHARPEN)
    except Exception as e:
        raise ValueError(f"Image processing failed: {e}")
    try:
        text = pytesseract.image_to_string(img, lang="eng+hin+urd")
    except Exception as e:
        raise ValueError(f"OCR execution failed: {e}")
    stripped_text = text.strip()
    if not stripped_text or len(stripped_text) < 10:
        raise ValueError("OCR returned insufficient text")
    return stripped_text

if __name__ == "__main__":
    print("Tesseract OCR module loaded")