
"""File type detection and processing route selection for MediAssist AI."""

from pathlib import Path


class MultimodalRouter:
    """Identify supported document types and select processing routes."""

    # Supported file extensions grouped by content type.
    SUPPORTED_FORMATS = {
        "pdf": [".pdf"],
        "docx": [".docx"],
        "txt": [".txt"],
        "image": [".png", ".jpg", ".jpeg"],
    }

    # Map each content type to its processing module.
    PROCESSING_ROUTES = {
        "pdf": "pdf_processor",
        "docx": "text_loader",
        "txt": "text_loader",
        "image": "image_processor",
    }

    @classmethod
    def detect_file_type(cls, file_path: str | Path) -> str:
        """
        Detect the uploaded file type using its extension.

        Returns:
            pdf, docx, txt, or image.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Expected a file, but received: {path}"
            )

        extension = path.suffix.lower()

        for file_type, extensions in cls.SUPPORTED_FORMATS.items():
            if extension in extensions:
                return file_type

        raise ValueError(
            f"Unsupported file format: {extension or 'No extension'}. "
            f"Supported formats: PDF, DOCX, TXT, PNG, JPG, JPEG."
        )

    @classmethod
    def get_processing_route(cls, file_path: str | Path) -> str:
        """
        Determine which processing module should handle the file.

        Returns:
            Name of the processing module.
        """
        file_type = cls.detect_file_type(file_path)

        return cls.PROCESSING_ROUTES[file_type]

    @classmethod
    def get_file_details(cls, file_path: str | Path) -> dict:
        """
        Return file information and its selected processing route.
        """
        path = Path(file_path)

        file_type = cls.detect_file_type(path)

        return {
            "file_name": path.name,
            "file_extension": path.suffix.lower(),
            "file_type": file_type,
            "processing_route": cls.PROCESSING_ROUTES[file_type],
        }