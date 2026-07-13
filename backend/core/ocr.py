"""OCR extraction module using EasyOCR."""
import easyocr

_reader = None

def get_reader():
    """Lazy initialize EasyOCR reader."""
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en', 'hi'])
    return _reader

def extract_text(image_path: str) -> str:
    """Extract text from an image using EasyOCR."""
    try:
        reader = get_reader()
        results = reader.readtext(image_path, detail=0)
        text = ' '.join(results)
        stripped = text.strip()
        if not stripped or len(stripped) < 10:
            raise ValueError("OCR returned insufficient text")
        return stripped
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"OCR execution failed: {e}")

if __name__ == "__main__":
    print("EasyOCR module loaded successfully")