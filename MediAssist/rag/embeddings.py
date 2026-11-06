import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingModel:
    """Generate text embeddings for the MediAssist AI RAG pipeline."""

    _model_cache: dict[str, SentenceTransformer] = {}

    def __init__(self, model_name: str = MODEL_NAME):
        """Load the pretrained embedding model only when needed."""
        self.model_name = model_name

        if model_name not in self._model_cache:
            self._model_cache[model_name] = SentenceTransformer(model_name)

        self.model = self._model_cache[model_name]

    def encode_texts(self, texts: list[str]) -> np.ndarray:
        """Convert a list of text strings into normalized vectors."""
        if not texts:
            return np.empty(
                (0, self.dimensions),
                dtype=np.float32,
            )

        embeddings = self.model.encode(
            texts,
            batch_size=32,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return np.asarray(embeddings, dtype=np.float32)

    @property
    def dimensions(self) -> int:
        """Return the number of dimensions in each embedding."""
        return self.model.get_embedding_dimension()
