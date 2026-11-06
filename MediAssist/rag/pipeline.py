
"""Document ingestion pipeline for MediAssist AI."""

from pathlib import Path

from langchain_core.documents import Document

from rag.loader import load_document
from rag.chunker import chunk_documents
from rag.vector_store import VectorStore


class DocumentIngestionPipeline:
    """Load, normalize, chunk, embed, and store documents."""

    MULTIMODAL_EXTENSIONS = {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
    }

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        multimodal_agent=None,
    ):
        self.vector_store = vector_store or VectorStore()
        self._multimodal_agent = multimodal_agent

    def _get_multimodal_agent(self):
        """Initialize the agent only when a multimodal file is processed."""
        if self._multimodal_agent is None:
            from multimodal_agent.agent import MultimodalAgent

            self._multimodal_agent = MultimodalAgent()

        return self._multimodal_agent

    def _load_file(self, path: Path) -> list[Document]:
        """Select the appropriate document processing workflow."""

        if path.suffix.lower() in self.MULTIMODAL_EXTENSIONS:
            agent = self._get_multimodal_agent()
            return agent.process_file(path)

        # Preserve the existing TXT/DOCX loading workflow.
        documents = load_document(path)

        if not documents:
            raise ValueError(
                f"No text extracted from {path.name}."
            )

        return documents

    def ingest_file(self, file_path: str | Path) -> dict:
        """Process a supported file and persist its chunks."""

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Expected a file, but received: {path}"
            )

        supported_extensions = (
            self.MULTIMODAL_EXTENSIONS | {".txt", ".docx"}
        )

        if path.suffix.lower() not in supported_extensions:
            raise ValueError(
                f"Unsupported file format: {path.suffix}. "
                "Supported formats: PDF, TXT, DOCX, PNG, JPG, JPEG."
            )

        # Step 1: Extract text and visual descriptions.
        documents = self._load_file(path)

        if not documents:
            raise ValueError(
                f"No readable content extracted from {path.name}."
            )

        # Step 2: Split extracted content into chunks.
        chunks = chunk_documents(documents)

        if not chunks:
            raise ValueError(
                f"No chunks created from {path.name}."
            )

        # Step 3: Generate embeddings and persist chunks.
        stored_count = self.vector_store.add_documents(chunks)

        return {
            "file_name": path.name,
            "file_type": path.suffix.lower().lstrip("."),
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "chunks_stored": stored_count,
            "storage": "ChromaDB",
        }
