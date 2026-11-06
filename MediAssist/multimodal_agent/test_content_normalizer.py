
from multimodal_agent.content_normalizer import ContentNormalizer


def main():
    # Simulate the output returned by ImageProcessor.
    image_result = {
        "file_name": "appointment_chart.png",
        "file_path": "data/uploads/appointment_chart.png",
        "file_type": "image",
        "description": (
            "The chart displays monthly appointment counts. "
            "The values should be verified against the original chart."
        ),
        "model": "vision-model",
        "processing_method": "vision_llm",
    }

    document = ContentNormalizer.normalize_image_result(
        image_result
    )

    print("========== NORMALIZED DOCUMENT ==========")
    print("\nPage Content:")
    print(document.page_content)

    print("\nMetadata:")
    print(document.metadata)

    assert document.page_content
    assert document.metadata["file_type"] == "image"
    assert document.metadata["extraction_method"] == "vision_llm"

    print("\nNormalizer test passed!")


if __name__ == "__main__":
    main()
