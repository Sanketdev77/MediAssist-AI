
"""OCR processing module for MediAssist AI."""

import os
from pathlib import Path

import cv2
import pytesseract
from pytesseract import TesseractNotFoundError, TesseractError


class OCRProcessor:
    """Extract text from images using Tesseract OCR."""

    SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg"}

    DEFAULT_TESSERACT_PATH = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    def __init__(self, tesseract_path=None):

        # Read executable path from .env or use Windows default.
        executable_path = (
            tesseract_path
            or os.getenv("TESSERACT_CMD")
            or self.DEFAULT_TESSERACT_PATH
        )

        executable_path = Path(executable_path)

        # Verify that Tesseract executable exists.
        if not executable_path.is_file():
            raise FileNotFoundError(
                "Tesseract OCR engine was not found.\n"
                f"Expected location: {executable_path}\n"
                "Please check your TESSERACT_CMD in .env."
            )

        # Configure pytesseract.
        pytesseract.pytesseract.tesseract_cmd = str(
            executable_path
        )

        # Verify that Tesseract can execute.
        try:
            pytesseract.get_tesseract_version()
        except TesseractNotFoundError as error:
            raise RuntimeError(
                "Unable to start Tesseract OCR."
            ) from error

    @classmethod
    def _validate_image(cls, image_path):
        """Validate the image file."""

        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                "The provided path is not a file."
            )

        if path.suffix.lower() not in cls.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported image format: {path.suffix}"
            )

        return path

    @staticmethod
    def preprocess_image(image_path):
        """Preprocess image to improve OCR accuracy."""

        image = cv2.imread(str(image_path))

        if image is None:
            raise ValueError(
                "Unable to read the image."
            )

        # Convert to grayscale.
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # Resize small images.
        height, width = gray.shape

        if width < 1500:
            scale = 1500 / width

            gray = cv2.resize(
                gray,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC
            )

        # Remove noise.
        denoised = cv2.fastNlMeansDenoising(
            gray,
            None,
            10,
            7,
            21
        )

        # Improve text contrast.
        processed = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11
        )

        return processed

    def extract_text(self, image_path):
        """Extract text from an image."""

        path = self._validate_image(image_path)

        try:
            processed_image = self.preprocess_image(path)

            extracted_text = pytesseract.image_to_string(
                processed_image,
                config="--oem 3 --psm 6"
            )

            extracted_text = extracted_text.strip()

            if not extracted_text:
                raise ValueError(
                    f"No readable text found in {path.name}."
                )

            return extracted_text

        except TesseractNotFoundError as error:
            raise RuntimeError(
                "Tesseract OCR executable was not found. "
                "Check TESSERACT_CMD in your .env file."
            ) from error

        except TesseractError as error:
            raise RuntimeError(
                f"Tesseract OCR failed: {error}"
            ) from error

    def extract_text_with_metadata(self, image_path):
        """Extract text and return associated metadata."""

        path = self._validate_image(image_path)

        extracted_text = self.extract_text(path)

        return {
            "file_name": path.name,
            "file_path": str(path.resolve()),
            "file_type": "image",
            "extracted_text": extracted_text,
            "ocr_engine": "Tesseract"
        }
