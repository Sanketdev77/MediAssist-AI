
from multimodal_agent.agent import MultimodalAgent


def main():
    file_path = "data/uploads/sample_report.pdf"

    try:
        agent = MultimodalAgent()
        documents = agent.process_file(file_path)

        print("\n========== MULTIMODAL AGENT RESULT ==========")
        print("Total documents:", len(documents))

        for index, document in enumerate(documents, start=1):
            print(f"\n--- Document {index} ---")
            print("Source:", document.metadata.get("source"))
            print("Type:", document.metadata.get("file_type"))
            print(
                "Method:",
                document.metadata.get("extraction_method"),
            )
            print("Content:")
            print(document.page_content[:1000])

        print("\nMultimodal processing completed.")

    except Exception as error:
        print("Multimodal Agent Error:", error)


if __name__ == "__main__":
    main()
