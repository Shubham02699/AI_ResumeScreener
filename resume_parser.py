"""
resume_parser.py
Extracts plain text from PDF and DOCX resume files.
"""

import pdfplumber
from docx import Document
import os


def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise ValueError(f"Could not read PDF '{os.path.basename(file_path)}': {e}")

    if not text.strip():
        raise ValueError(
            f"No text found in '{os.path.basename(file_path)}'. "
            "This may be a scanned/image-based PDF which cannot be parsed."
        )
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract all text from a DOCX file using python-docx."""
    try:
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n".join(paragraphs)
    except Exception as e:
        raise ValueError(f"Could not read DOCX '{os.path.basename(file_path)}': {e}")

    if not text.strip():
        raise ValueError(f"No text found in '{os.path.basename(file_path)}'.")
    return text.strip()


def extract_text(file_path: str) -> str:
    """
    Auto-detect file type and extract text.
    Supports .pdf and .docx formats.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(
            f"Unsupported file format '{ext}'. Only PDF and DOCX are supported."
        )


def get_candidate_name(file_path: str) -> str:
    """Derive a candidate display name from the filename."""
    base = os.path.basename(file_path)
    name, _ = os.path.splitext(base)
    # Replace underscores/hyphens with spaces and title-case
    return name.replace("_", " ").replace("-", " ").title()
