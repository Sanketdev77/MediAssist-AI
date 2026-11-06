
"""ChromaDB vector storage for the MediAssist AI RAG pipeline."""

import hashlib
from pathlib import Path
from typing import Sequence

import chromadb
from langchain_core.documents import Document

from rag.embeddings import EmbeddingModel

# Store ChromaDB data inside the existing project store directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_PATH = PROJECT_ROOT / "store" / "chroma_db"
COLLECTION_NAME = "mediassist_documents"


class VectorStore:
    """Store document chunks and search them using semantic similarity."""

    def __init__(
        self,
        embedding_model: EmbeddingModel | None = None,
    ) -> None:
        CHROMA_PATH.mkdir(parents=True, exist_ok=True)

        self.embedding_model = embedding_model or EmbeddingModel()

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    @staticmethod
    def _prepare_metadata(metadata: dict) -> dict:
        """Keep metadata compatible with ChromaDB."""
        cleaned = {}

        for key, value in metadata.items():
            if value is None:
                continue

            if isinstance(value, (str, int, float, bool)):
                cleaned[key] = value
            else:
                cleaned[key] = str(value)

        return cleaned

    @staticmethod
    def _generate_id(document: Document, index: int) -> str:
        """Generate a repeatable ID for each chunk."""
        source = str(document.metadata.get("source", "unknown"))
        chunk_index = str(
            document.metadata.get("chunk_index", index)
        )
        page = str(document.metadata.get("page", ""))
        content = document.page_content

        unique_text = (
            f"{source}|{chunk_index}|{page}|{content}"
        )

        return hashlib.sha256(
            unique_text.encode("utf-8")
        ).hexdigest()

    def add_documents(
        self,
        documents: Sequence[Document],
    ) -> int:
        """Embed and store document chunks. Return the chunk count."""
        if not documents:
            return 0

        texts = [doc.page_content for doc in documents]

        embeddings = self.embedding_model.encode_texts(texts)

        ids = [
            self._generate_id(document, index)
            for index, document in enumerate(documents)
        ]

        metadatas = [
            self._prepare_metadata(document.metadata)
            for document in documents
        ]

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
        )

        return len(documents)

    def similarity_search(
        self,
        query: str,
        k: int = 4,
    ) -> list[Document]:
        """Return the most semantically similar document chunks."""
        if not query.strip():
            return []

        if k <= 0:
            return []

        if self.collection.count() == 0:
            return []

        query_embedding = self.embedding_model.encode_texts(
            [query]
        )[0]

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=min(k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        documents = []
        result_texts = results.get("documents") or [[]]
        result_metadata = results.get("metadatas") or [[]]

        for text, metadata in zip(
            result_texts[0],
            result_metadata[0],
        ):
            documents.append(
                Document(
                    page_content=text,
                    metadata=metadata or {},
                )
            )

        return documents

    def delete_collection(self) -> None:
        """Delete all stored chunks in this collection."""
        self.client.delete_collection(COLLECTION_NAME)

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        """Return the total number of stored chunks."""
        return self.collection.count()
