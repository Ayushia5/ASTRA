"""OCR extraction module using Tesseract."""
import pytesseract
from PIL import Image, ImageFilter

def extract_text(image_path: str) -> str:
    """Extract text from an image using OCR (eng+hin+urd) after grayscale and sharpen preprocessing."""
    try:
        img = Image.open(image_path)
        img = img.convert("L")
        img = img.filter(ImageFilter.SHARPEN)
    except Exception as e:
        print(f"[ERROR] extract_text: Failed to open or preprocess image - {e}")
        raise ValueError(f"Image processing failed: {e}")

    try:
        text = pytesseract.image_to_string(img, lang="eng+hin+urd")
    except Exception as e:
        print(f"[ERROR] extract_text: OCR failed - {e}")
        raise ValueError(f"OCR execution failed: {e}")

    stripped_text = text.strip()
    if not stripped_text or len(stripped_text) < 10:
        raise ValueError("OCR returned insufficient text")
    
    return stripped_text

if __name__ == "__main__":
    import os
    test_image = "test_ocr_sample.png"
    if not os.path.exists(test_image):
        print(f"[WARNING] Test image '{test_image}' not found. Please provide a real image path to test.")
    else:
        try:
            print(f"Testing OCR on {test_image}...")
            result = extract_text(test_image)
            print("OCR Result:\n", result)
        except Exception as ex:
            print(f"Test Exception: {ex}")
