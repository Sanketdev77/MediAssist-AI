
from multimodal_agent.pdf_processor import PDFProcessor


def main():

    pdf_path = "data/uploads/sample_report.pdf"

    processor = PDFProcessor()

    try:
        documents = processor.process_pdf(pdf_path)

        print("\n========== PDF PROCESSING RESULT ==========")

        print("Total extracted pages:", len(documents))

        for document in documents:

            print("\n----------------------------------")
            print("Source:", document.metadata["source"])
            print("Page:", document.metadata["page"])
            print(
                "Extraction method:",
                document.metadata["extraction_method"],
            )

            print("\nExtracted content:")
            print(document.page_content[:1500])

    except Exception as error:
        print("PDF Processing Error:", error)


if __name__ == "__main__":
    main()
