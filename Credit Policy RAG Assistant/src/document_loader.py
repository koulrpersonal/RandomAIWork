"""
Document Loader module.
Parses PDF, Word (.docx), Markdown (.md), and Text (.txt) files.
Extracts text, preserves section/clause metadata, and chunks into manageable units for RAG.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any


def extract_text_from_file(file_path: Path) -> str:
    """Extract plain text from various file formats."""
    suffix = file_path.suffix.lower()

    if suffix in [".md", ".txt"]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    elif suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(file_path))
        text_parts = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            text_parts.append(f"\n--- Page {i+1} ---\n{page_text}")
        return "\n".join(text_parts)

    elif suffix in [".docx", ".doc"]:
        import docx
        doc = docx.Document(str(file_path))
        text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(text_parts)

    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def chunk_text(text: str, filename: str, chunk_size: int = 600, overlap: int = 120) -> List[Dict[str, Any]]:
    """
    Splits text into chunks while preserving clause numbers, section headers, and metadata.
    """
    # Split text into paragraphs
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    
    current_section = "General Policy"
    current_clause = ""
    current_chunk = ""
    
    clause_regex = re.compile(r'\[Clause\s+(\d+\.\d+)\]', re.IGNORECASE)
    section_regex = re.compile(r'##\s+SECTION\s+(\d+[:\s\w\(\)]+)', re.IGNORECASE)

    for para in paragraphs:
        para_clean = para.strip()
        if not para_clean:
            continue

        # Check for section header
        sec_match = section_regex.search(para_clean)
        if sec_match:
            current_section = sec_match.group(0).replace("##", "").strip()

        # Check for clause header
        clause_match = clause_regex.search(para_clean)
        if clause_match:
            current_clause = f"Clause {clause_match.group(1)}"

        # If adding this paragraph exceeds chunk size and we already have content, store current chunk
        if len(current_chunk) + len(para_clean) > chunk_size and len(current_chunk) > 100:
            chunks.append({
                "content": current_chunk.strip(),
                "metadata": {
                    "source": filename,
                    "section": current_section,
                    "clause": current_clause or "General",
                }
            })
            # Overlap: keep the last portion
            current_chunk = current_chunk[-overlap:] + "\n" + para_clean
        else:
            if current_chunk:
                current_chunk += "\n\n" + para_clean
            else:
                current_chunk = para_clean

    # Add remaining text
    if current_chunk.strip():
        chunks.append({
            "content": current_chunk.strip(),
            "metadata": {
                "source": filename,
                "section": current_section,
                "clause": current_clause or "General",
            }
        })

    # Add chunk index to metadata
    for idx, c in enumerate(chunks):
        c["metadata"]["chunk_id"] = f"{filename}_chunk_{idx}"

    return chunks


def load_all_policy_documents(policies_dir: Path, chunk_size: int = 600, overlap: int = 120) -> List[Dict[str, Any]]:
    """
    Scans the policies directory and processes all supported documents into chunks.
    """
    supported_extensions = {".md", ".txt", ".pdf", ".docx"}
    all_chunks = []

    files = [f for f in policies_dir.iterdir() if f.is_file() and f.suffix.lower() in supported_extensions]
    
    for file_path in files:
        try:
            text = extract_text_from_file(file_path)
            file_chunks = chunk_text(text, filename=file_path.name, chunk_size=chunk_size, overlap=overlap)
            all_chunks.extend(file_chunks)
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")

    return all_chunks
