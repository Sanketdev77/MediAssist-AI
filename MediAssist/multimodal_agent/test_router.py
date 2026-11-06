
from multimodal_agent.router import MultimodalRouter
from pathlib import Path
test_files = [
    "sample.pdf",
    "sample.docx",
    "sample.txt",
    "blood_report.png",
    "xray.jpg",
    "medical_image.jpeg",
]

for file_name in test_files:
    try:
        file_type = Path(file_name).suffix.lower()

        # Test classification without requiring actual files.
        for category, extensions in MultimodalRouter.SUPPORTED_FORMATS.items():
            if file_type in extensions:
                print(
                    f"{file_name} -> {category} -> "
                    f"{MultimodalRouter.PROCESSING_ROUTES[category]}"
                )
                break

    except Exception as error:
        print(error)