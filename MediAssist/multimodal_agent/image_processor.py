
"""Image understanding module for MediAssist AI."""

import base64
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from PIL import Image, UnidentifiedImageError


load_dotenv()


class ImageProcessor:
    """Analyze healthcare-related images using a vision-capable LLM."""

    SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg"}
    DEFAULT_MODEL = "qwen/qwen3.8-27b"
    MAX_IMAGE_SIZE_MB = 20
    MAX_IMAGE_DIMENSION = 2048

    SYSTEM_PROMPT = """
You are the image understanding component of MediAssist AI,
an enterprise healthcare information assistant.

Analyze only the visual information present in the supplied image.

Rules:
1. Describe visible objects, charts, diagrams, tables and layouts.
2. Extract and report clearly readable visual information.
3. Do not invent missing values, labels or information.
4. Clearly mention when text or visual details are unclear.
5. Do not make medical diagnoses or treatment recommendations.
6. Do not infer patient information that is not visibly present.
7. Distinguish observations from interpretations.
8. Use clear, professional and concise language.
9. If the image is not healthcare-related, describe it objectively.
"""

    def __init__(self, model_name: str | None = None):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is missing. Add it to your .env file."
            )

        self.model_name = (
            model_name
            or os.getenv("GROQ_VISION_MODEL")
            or self.DEFAULT_MODEL
        )

        self.client = Groq(api_key=api_key)

    @classmethod
    def _validate_image(cls, image_path: str | Path) -> Path:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        if not path.is_file():
            raise ValueError(f"Expected an image file: {path}")

        if path.suffix.lower() not in cls.SUPPORTED_FORMATS:
            raise ValueError(
                "Unsupported image format. Use PNG, JPG or JPEG."
            )

        file_size_mb = path.stat().st_size / (1024 * 1024)

        if file_size_mb > cls.MAX_IMAGE_SIZE_MB:
            raise ValueError(
                f"Image exceeds {cls.MAX_IMAGE_SIZE_MB} MB."
            )

        return path

    @classmethod
    def _encode_image(cls, image_path: Path) -> str:
        """Resize and encode an image as a Base64 JPEG data URI."""

        try:
            with Image.open(image_path) as image:
                image = image.convert("RGB")

                image.thumbnail(
                    (
                        cls.MAX_IMAGE_DIMENSION,
                        cls.MAX_IMAGE_DIMENSION,
                    )
                )

                buffer = BytesIO()
                image.save(buffer, format="JPEG", quality=85)

                encoded_image = base64.b64encode(
                    buffer.getvalue()
                ).decode("utf-8")

                return f"data:image/jpeg;base64,{encoded_image}"

        except UnidentifiedImageError as exc:
            raise ValueError(
                "The supplied file is not a valid image."
            ) from exc

    def analyze_image(
        self,
        image_path: str | Path,
        question: str | None = None,
    ) -> dict:
        """
        Analyze an image and return its visual description.

        Args:
            image_path: Path to the image.
            question: Optional instruction about what to analyze.

        Returns:
            Dictionary containing image details and analysis.
        """

        path = self._validate_image(image_path)
        image_data = self._encode_image(path)

        user_prompt = question or (
            "Describe this image in detail. Identify its important "
            "visual elements, readable text, charts, tables and "
            "diagrams. Organize the response into clear sections."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data,
                                },
                            },
                        ],
                    },
                ],
                temperature=0,
                max_completion_tokens=1500,
            )

            description = (
                response.choices[0].message.content or ""
            ).strip()

            if not description:
                raise RuntimeError(
                    "The vision model returned an empty response."
                )

            return {
                "file_name": path.name,
                "file_path": str(path.resolve()),
                "file_type": "image",
                "description": description,
                "model": self.model_name,
                "processing_method": "vision_llm",
            }

        except Exception as exc:
            raise RuntimeError(
                f"Image analysis failed: {exc}"
            ) from exc