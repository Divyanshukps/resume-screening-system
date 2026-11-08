"""Read text out of PDF, DOCX and plain-text resumes."""
import io
import re
from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def _read_pdf(data: bytes) -> str:
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(data)) as pdf:
            text = "\n".join((page.extract_text() or "") for page in pdf.pages)
        if text.strip():
            return text
    except Exception:
        pass
    # fallback parser
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _read_docx(data: bytes) -> str:
    from docx import Document

    doc = Document(io.BytesIO(data))
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            parts.extend(cell.text for cell in row.cells)
    return "\n".join(parts)


def _read_txt(data: bytes) -> str:
    for enc in ("utf-8", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return ""


def extract_text(filename: str, data: bytes) -> str:
    """Return the plain text of a resume, based on its file extension."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return _read_pdf(data)
    if ext == ".docx":
        return _read_docx(data)
    if ext == ".txt":
        return _read_txt(data)
    raise ValueError(f"Unsupported file type: {ext or 'unknown'}")


def guess_candidate_name(text: str, filename: str) -> str:
    """Use the first short, letters-only line as the name; else the file name."""
    for line in text.splitlines()[:6]:
        line = line.strip()
        if 2 <= len(line.split()) <= 4 and re.fullmatch(r"[A-Za-z .'\-]+", line):
            return line.title()
    return Path(filename).stem.replace("_", " ").replace("-", " ").title()
