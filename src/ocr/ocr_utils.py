from PIL import Image, ImageFilter
import pytesseract
from pdf2image import convert_from_path
import pdfplumber

def show_image(image):
    image.show()

def ocr_raw(image_path):
    """OCR without preprocessing — raw result."""
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="eng")
    return text

def preprocess_image(image_path):
    """Preprocessing: greyscale → denoise → binarize."""
    img = Image.open(image_path)
    img = img.convert("L")
    img = img.filter(ImageFilter.MedianFilter(size=3))
    img = img.point(lambda x: 0 if x < 90 else 255, "1")
    # show_image(img) 
    return img

def ocr_preprocessed(image_path):
    """OCR with preprocessing — better result."""
    processed = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed, lang="eng")
    return text

def compare_ocr(image_path):
    """Comparison raw vs preprocessed OCR output."""
    print("=== RAW OCR ===")
    raw = ocr_raw(image_path)
    print(raw)
    
    print("\n=== PREPROCESSED OCR ===")
    preprocessed = ocr_preprocessed(image_path)
    print(preprocessed)
    
    return raw, preprocessed

def ocr_scanned_pdf(pdf_path, dpi=300):
    """OCR for scanned PDF — every page separately."""
    
    # Convert PDF pages in PIL images
    pages = convert_from_path(pdf_path, dpi=dpi)
    if (len(pages)==1):
        print(f"PDF has {len(pages)} page")
    else:
        print(f"PDF has {len(pages)} pages")
    
    page_texts = {}
    
    for i, page in enumerate(pages):
        print(f"OCR page {i+1}...")
        
        # Preprocessing
        page = page.convert("L")
        page = page.filter(ImageFilter.MedianFilter(size=3))
        page = page.point(lambda x: 0 if x < 128 else 255, "1")
        
        # OCR
        text = pytesseract.image_to_string(page, lang="eng")
        page_texts[f"page_{i+1}"] = text
    
    return page_texts
if __name__ == "__main__":
    compare_ocr("../../data/raw/images/PMC3931379_830fig1.png")
    with pdfplumber.open("../../data/raw/scanned/DIABETES.pdf") as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            print(f"Page {i+1}: {repr(text)}")

    print("\n---  OCR now ---\n")

    # OCR to take text from images
    texts = ocr_scanned_pdf("../../data/raw/scanned/DIABETES.pdf")
    for page, text in texts.items():
        print(f"\n=== {page} ===")
        print(text)