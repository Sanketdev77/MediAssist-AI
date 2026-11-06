import re
import unicodedata
from typing import Sequence

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Created once and reused on every call
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
    keep_separator="end",
)


def clean_text(text: str) -> str:
    """Remove common extraction noise while keeping paragraphs and punctuation."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")  # first, before the filter
    text = "".join(
        c for c in text if c in "\n\t" or unicodedata.category(c) != "Cc"
    )
    text = re.sub(r"[ \t]+", " ", text)    # collapse repeated spaces/tabs
    text = re.sub(r" ?\n ?", "\n", text)   # trim spaces around line breaks
    text = re.sub(r"\n{3,}", "\n\n", text) # at most one blank line
    return text.strip()


def chunk_documents(docs: Sequence[Document]) -> list[Document]:
    """Clean and split loader Documents into chunks ready for embedding."""
    cleaned = [
        Document(page_content=clean_text(d.page_content), metadata=dict(d.metadata))
        for d in docs
        if d.page_content and d.page_content.strip()
    ]

    chunks = _splitter.split_documents(cleaned)  # returns [] for an empty list

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
    return chunks


