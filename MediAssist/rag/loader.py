from pathlib import Path

import docx2txt
from pypdf import PdfReader
from langchain_core.documents import Document

# Supported document formats
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def load_document(file_path: str | Path) -> list[Document]:
    """
    Load a PDF, DOCX, or TXT file and return its text
    as a list of LangChain Document objects.
    """

    path = Path(file_path)

    # 1. Check whether the file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 2. Check whether the path points to a file
    if not path.is_file():
        raise ValueError(f"Expected a file, got: {path}")

    # 3. Check the file extension
    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # 4. Extract text according to the file type
    if extension == ".pdf":
        text = _load_pdf(path)

    elif extension == ".docx":
        text = _load_docx(path)

    else:
        text = _load_txt(path)

    # 5. Reject files that contain no extractable text
    text = text.strip()

    if not text:
        raise ValueError(
            f"No extractable text found in {path.name}. "
            "The file may be empty, scanned, or image-only."
        )

    # 6. Return text with source metadata
    return [
        Document(
            page_content=text,
            metadata={
                "source": path.name,
                "file_path": str(path.resolve()),
                "file_type": extension.lstrip("."),
            },
        )
    ]


def _load_pdf(path: Path) -> str:
    """Extract text from a PDF file."""

    reader = PdfReader(str(path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        if page_text.strip():
            pages.append(
                f"[Page {page_number}]\n{page_text}"
            )

    return "\n\n".join(pages)


def _load_docx(path: Path) -> str:
    """Extract text from a Word document."""

    return docx2txt.process(str(path)) or ""


def _load_txt(path: Path) -> str:
    """Read a UTF-8 text file, allowing a common BOM."""

    return path.read_text(encoding="utf-8-sig")





