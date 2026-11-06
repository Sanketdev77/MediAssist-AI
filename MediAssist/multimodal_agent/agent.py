
"""Multimodal agent orchestrator for MediAssist AI."""

from pathlib import Path

from langchain_core.documents import Document

from multimodal_agent.router import MultimodalRouter
from multimodal_agent.ocr_processor import OCRProcessor
from multimodal_agent.pdf_processor import PDFProcessor
from multimodal_agent.image_processor import ImageProcessor
from multimodal_agent.content_normalizer import ContentNormalizer


class MultimodalAgent:
    """Coordinate file routing, processing and content normalization."""

    def __init__(self):
        self.router = MultimodalRouter()
        self.ocr_processor = OCRProcessor()
        self.pdf_processor = PDFProcessor(
            ocr_processor=self.ocr_processor
        )
        self.image_processor = ImageProcessor()
        self.normalizer = ContentNormalizer()

    def process_file(
        self,
        file_path: str | Path,
        image_question: str | None = None,
    ) -> list[Document]:
        """
        Process a supported file and return normalized Documents.

        Supported files: PDF, PNG, JPG and JPEG.
        """

        path = Path(file_path)
        file_details = self.router.get_file_details(path)
        file_type = file_details["file_type"]

        if file_type == "pdf":
            documents = self.pdf_processor.process_pdf(path)
            return self.normalizer.normalize_pdf_documents(documents)

        if file_type == "image":
            ocr_result = self.ocr_processor.extract_text_with_metadata(
                path
            )

            documents = []

            # Include literal text detected in the image when available.
            try:
                documents.append(
                    self.normalizer.normalize_ocr_result(ocr_result)
                )
            except ValueError:
                # OCR may not find readable text in a chart or diagram.
                pass

            # Analyze visual content independently of OCR.
            image_result = self.image_processor.analyze_image(
                image_path=path,
                question=image_question,
            )

            documents.append(
                self.normalizer.normalize_image_result(image_result)
            )

            return documents

        if file_type in {"docx", "txt"}:
            raise NotImplementedError(
                f"{file_type.upper()} processing is not connected "
                "to this agent yet. It will be added in a later step."
            )

        raise ValueError(f"Unsupported file type: {file_type}")

    def process_files(
        self,
        file_paths: list[str | Path],
    ) -> list[Document]:
        """Process multiple files and combine their Documents."""

        all_documents = []

        for file_path in file_paths:
            documents = self.process_file(file_path)
            all_documents.extend(documents)

        return all_documents