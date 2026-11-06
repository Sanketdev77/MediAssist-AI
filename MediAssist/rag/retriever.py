
"""Document retrieval for the MediAssist AI RAG pipeline."""

from langchain_core.documents import Document

from rag.vector_store import VectorStore

class DocumentRetriever:
    """Retrieve relevant document chunks from ChromaDB."""

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        top_k: int = 4,
    ) -> None:
        """
        Initialize the retriever.

        Args:
            vector_store: Existing ChromaDB vector store.
            top_k: Maximum number of chunks to retrieve.
        """
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        self.vector_store = vector_store or VectorStore()
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        k: int | None = None,
    ) -> list[Document]:
        """
        Retrieve the most relevant chunks for a user query.

        Args:
            query: User's question.
            k: Optional number of chunks to retrieve.

        Returns:
            A list of LangChain Document objects.
        """
        if not query or not query.strip():
            return []

        number_of_results = self.top_k if k is None else k

        if number_of_results < 1:
            raise ValueError("k must be at least 1.")

        return self.vector_store.similarity_search(
            query=query.strip(),
            k=number_of_results,
        )

    @staticmethod
    def format_context(documents: list[Document]) -> str:
        """
        Format retrieved chunks into context for the RAG chain.
        """
        if not documents:
            return "NO RELEVANT DOCUMENTS FOUND."

        context_parts = []

        for index, document in enumerate(documents, start=1):
            source = document.metadata.get(
                "source",
                document.metadata.get("file_name", "Unknown source"),
            )
            page = document.metadata.get("page")

            source_details = f"Source: {source}"

            if page is not None:
                source_details += f" | Page: {page}"

            context_parts.append(
                f"[Document {index}]\n"
                f"{source_details}\n"
                f"{document.page_content}"
            )

        return "\n\n".join(context_parts)
