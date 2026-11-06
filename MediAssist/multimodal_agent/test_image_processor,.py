
from multimodal_agent.image_processor import ImageProcessor


def main():
    image_path = "data/uploads/sample_image.png"

    try:
        processor = ImageProcessor()

        result = processor.analyze_image(
            image_path=image_path,
            question=(
                "Describe the image, identify any charts or tables, "
                "and extract important visible information."
            ),
        )

        print("\n========== IMAGE ANALYSIS RESULT ==========")
        print("File:", result["file_name"])
        print("Model:", result["model"])
        print("Processing:", result["processing_method"])

        print("\nVisual Description:")
        print(result["description"])

    except Exception as error:
        print("Image Processing Error:", error)


if __name__ == "__main__":
    main()
