
"""PDF processing module for MediAssist AI."""

from pathlib import Path
from tempfile import NamedTemporaryFile
import os

import fitz  # PyMuPDF
from langchain_core.documents import Document

from multimodal_agent.ocr_processor import OCRProcessor


class PDFProcessor:
    """Extract text from digital and scanned PDF documents."""

    def __init__(
        self,
        ocr_processor: OCRProcessor | None = None,
        render_dpi: int = 200,
        min_text_chars: int = 30,
    ):
        """
        Initialize the PDF processor.

        Args:
            ocr_processor: Existing OCR processor instance.
            render_dpi: Resolution used to render scanned PDF pages.
            min_text_chars: Minimum extracted characters before OCR fallback.
        """
        if render_dpi < 72:
            raise ValueError("Render DPI must be at least 72.")

        if min_text_chars < 1:
            raise ValueError("Minimum text characters must be positive.")

        self.ocr_processor = ocr_processor or OCRProcessor()
        self.render_dpi = render_dpi
        self.min_text_chars = min_text_chars

    @staticmethod
    def _validate_pdf(pdf_path: str | Path) -> Path:
        """Validate the PDF file."""

        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        if not path.is_file():
            raise ValueError(f"Expected a file: {path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported.")

        return path

    def _extract_page_text(self, page) -> tuple[str, str]:
        """
        Extract text from a PDF page.

        Returns:
            Extracted text and extraction method.
        """

        text = page.get_text("text").strip()

        # Use native PDF text when sufficient text is available.
        if len(text) >= self.min_text_chars:
            return text, "native_pdf_text"

        # Otherwise, render the page and use OCR.
        pixmap = page.get_pixmap(
            dpi=self.render_dpi,
            colorspace=fitz.csRGB,
            alpha=False,
        )

        with NamedTemporaryFile(
            suffix=".png",
            delete=False,
        ) as temporary_file:
            temporary_path = temporary_file.name

        try:
            pixmap.save(temporary_path)

            ocr_text = self.ocr_processor.extract_text(
                temporary_path
            )

            # Preserve any native text extracted from the page.
            combined_text = "\n".join(
                part for part in [text, ocr_text] if part.strip()
            )

            return combined_text, "ocr"

        finally:
            if os.path.exists(temporary_path):
                os.remove(temporary_path)

    def process_pdf(self, pdf_path: str | Path) -> list[Document]:
        """
        Process a PDF and return page-level LangChain Documents.

        Each PDF page becomes a separate Document with source metadata.
        """

        path = self._validate_pdf(pdf_path)

        documents = []

        try:
            with fitz.open(str(path)) as pdf_document:

                if pdf_document.is_encrypted:
                    raise ValueError(
                        "Encrypted PDFs are not supported. "
                        "Please provide an accessible PDF."
                    )

                if pdf_document.page_count == 0:
                    raise ValueError("The PDF contains no pages.")

                for page_index, page in enumerate(pdf_document):

                    extracted_text, extraction_method = (
                        self._extract_page_text(page)
                    )

                    if not extracted_text.strip():
                        continue

                    document = Document(
                        page_content=extracted_text,
                        metadata={
                            "source": path.name,
                            "file_path": str(path.resolve()),
                            "file_type": "pdf",
                            "page": page_index + 1,
                            "extraction_method": extraction_method,
                        },
                    )

                    documents.append(document)

        except (fitz.FileDataError, fitz.EmptyFileError) as exc:
            raise ValueError(
                f"Unable to read the PDF file: {exc}"
            ) from exc

        if not documents:
            raise ValueError(
                "No readable text could be extracted from the PDF."
            )

        return documents