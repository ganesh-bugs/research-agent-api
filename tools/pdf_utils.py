import requests
import fitz  # PyMuPDF
import os
from tqdm import tqdm

def download_pdf(url, save_path="article.pdf"):
    try:
        response = requests.get(url, stream=True, timeout=15)
        if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
            with open(save_path, 'wb') as f:
                for chunk in tqdm(response.iter_content(chunk_size=1024), desc="Downloading PDF"):
                    f.write(chunk)
            return save_path
        else:
            return None
    except Exception as e:
        print(f"❌ PDF download error: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            full_text = ""
            for page in doc:
                full_text += page.get_text()
        return full_text.strip()
    except Exception as e:
        print(f"❌ PDF text extraction error: {e}")
        return ""

def extract_abstract_from_pdf(text):
    """Try to extract abstract section from the full PDF text"""
    lines = text.split('\n')
    abstract_lines = []
    capture = False

    for line in lines:
        line_clean = line.strip().lower()

        if "abstract" in line_clean and not capture:
            capture = True
            continue

        if capture:
            # Heuristically stop at keywords like "introduction", "keywords", etc.
            if any(word in line_clean for word in ["introduction", "keywords", "background", "1.", "i."]):
                break
            if line.strip():
                abstract_lines.append(line.strip())

    return " ".join(abstract_lines).strip() if abstract_lines else None
