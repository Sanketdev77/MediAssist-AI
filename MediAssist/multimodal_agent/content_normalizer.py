
"""Normalize multimodal processing outputs for MediAssist AI."""

from pathlib import Path
from typing import Any

from langchain_core.documents import Document


class ContentNormalizer:
    """Convert text, PDF, OCR and image outputs into Documents."""

    @staticmethod
    def normalize_text(
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> Document:
        """Convert extracted text into a LangChain Document."""

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Cannot normalize empty text.")

        document_metadata = dict(metadata or {})

        document_metadata.setdefault("file_type", "text")
        document_metadata.setdefault("extraction_method", "text")

        return Document(
            page_content=text.strip(),
            metadata=document_metadata,
        )

    @classmethod
    def normalize_pdf_documents(
        cls,
        documents: list[Document],
    ) -> list[Document]:
        """Validate and standardize documents returned by PDFProcessor."""

        normalized_documents = []

        for document in documents:
            if not document.page_content.strip():
                continue

            metadata = dict(document.metadata)
            metadata.setdefault("file_type", "pdf")
            metadata.setdefault("extraction_method", "native_pdf_text")

            normalized_documents.append(
                cls.normalize_text(
                    text=document.page_content,
                    metadata=metadata,
                )
            )

        return normalized_documents

    @classmethod
    def normalize_ocr_result(
        cls,
        result: dict[str, Any],
    ) -> Document:
        """Convert OCRProcessor output into a Document."""

        text = result.get("extracted_text", "")

        metadata = {
            "source": result.get("file_name", "unknown"),
            "file_path": result.get("file_path", ""),
            "file_type": "image",
            "extraction_method": "ocr",
            "ocr_engine": result.get("ocr_engine", "unknown"),
        }

        return cls.normalize_text(text, metadata)

    @classmethod
    def normalize_image_result(
        cls,
        result: dict[str, Any],
    ) -> Document:
        """Convert ImageProcessor output into a Document."""

        description = result.get("description", "")

        metadata = {
            "source": result.get("file_name", "unknown"),
            "file_path": result.get("file_path", ""),
            "file_type": "image",
            "extraction_method": "vision_llm",
            "vision_model": result.get("model", "unknown"),
        }

        return cls.normalize_text(description, metadata)

    @classmethod
    def normalize_file_text(
        cls,
        file_path: str | Path,
        text: str,
        extraction_method: str = "text",
        page: int | None = None,
    ) -> Document:
        """Normalize text extracted from TXT or DOCX files."""

        path = Path(file_path)

        metadata = {
            "source": path.name,
            "file_path": str(path.resolve()),
            "file_type": path.suffix.lower().lstrip("."),
            "extraction_method": extraction_method,
        }

        if page is not None:
            metadata["page"] = page

        return cls.normalize_text(text, metadata)