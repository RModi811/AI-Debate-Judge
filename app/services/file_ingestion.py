from pathlib import Path
from pypdf import PdfReader
from docx import Document

ALLOWED = {".txt", ".pdf", ".docx"}
MAX_BYTES = {".txt": 10 * 1024 * 1024, ".docx": 10 * 1024 * 1024, ".pdf": 25 * 1024 * 1024}

def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED:
        raise ValueError("Unsupported file type. Use TXT, DOCX, or PDF.")
    if len(content) > MAX_BYTES[suffix]:
        raise ValueError("File exceeds the allowed size for its type.")
    if suffix == ".txt":
        text = content.decode("utf-8", errors="replace")
    elif suffix == ".pdf":
        import io
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        import io
        doc = Document(io.BytesIO(content))
        text = "\n".join(p.text for p in doc.paragraphs)
    text = text.replace("\x00", "").strip()
    if not text:
        raise ValueError("No readable text was found in the uploaded file.")
    return text
