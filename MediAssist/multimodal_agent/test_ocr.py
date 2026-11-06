
from multimodal_agent.ocr_processor import OCRProcessor


def main():
    image_path = "data/uploads/laboratory_report.png"

    ocr = OCRProcessor()

    try:
        result = ocr.extract_text_with_metadata(image_path)

        print("\n========== OCR RESULT ==========")

        print("File:", result["file_name"])
        print("Type:", result["file_type"])
        print("OCR Engine:", result["ocr_engine"])

        print("\nExtracted Text:")
        print(result["extracted_text"])

    except Exception as error:
        print("OCR Processing Error:", error)


if __name__ == "__main__":
    main()
    
