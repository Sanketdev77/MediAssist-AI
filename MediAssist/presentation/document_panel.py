
import hashlib
import json
import sys
import uuid
from pathlib import Path

import streamlit as st

# Add the MediAssist project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
MANIFEST_PATH = UPLOAD_DIR / "manifest.json"

ALLOWED_TYPES = ["pdf", "docx", "txt"]


def read_uploaded_files():
    """Read the persistent uploaded-document manifest."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    if not MANIFEST_PATH.exists():
        return []

    try:
        return json.loads(
            MANIFEST_PATH.read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, OSError):
        st.error("Unable to read the uploaded document list.")
        return []


def save_uploaded_files(files):
    """Persist the uploaded-document manifest."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    MANIFEST_PATH.write_text(
        json.dumps(files, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def upload_document(uploaded_file):
    """Save, ingest, and register an uploaded document."""
    file_bytes = uploaded_file.getvalue()
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    files = read_uploaded_files()

    # Prevent uploading the same file more than once.
    if any(item.get("sha256") == file_hash for item in files):
        st.info("This document has already been uploaded.")
        return

    original_name = Path(uploaded_file.name).name
    stored_name = f"{uuid.uuid4().hex}_{original_name}"
    stored_path = UPLOAD_DIR / stored_name

    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        stored_path.write_bytes(file_bytes)

        # Run the complete RAG ingestion pipeline.
        with st.spinner(
            "Extracting text, creating embeddings, and indexing document..."
        ):
            from rag.pipeline import DocumentIngestionPipeline

            pipeline = DocumentIngestionPipeline()
            result = pipeline.ingest_file(stored_path)

        # Add the file to the manifest after successful ingestion.
        files.append(
            {
                "id": uuid.uuid4().hex,
                "original_name": original_name,
                "stored_name": stored_name,
                "sha256": file_hash,
                "chunks_stored": result["chunks_stored"],
            }
        )

        save_uploaded_files(files)

        st.success(
            f"Uploaded and indexed successfully: {original_name}"
        )
        st.caption(
            f"Chunks created: {result['chunks_created']} | "
            f"Chunks stored: {result['chunks_stored']}"
        )

    except Exception as error:
        # Remove the uploaded file if ingestion fails.
        if stored_path.exists():
            stored_path.unlink()

        st.error(f"Document ingestion failed: {error}")


def delete_document(file_id):
    """Delete an uploaded document and update its manifest."""
    files = read_uploaded_files()

    selected = next(
        (item for item in files if item["id"] == file_id),
        None,
    )

    if selected is None:
        st.warning("Document not found.")
        return

    stored_path = UPLOAD_DIR / selected["stored_name"]

    try:
        if stored_path.exists():
            stored_path.unlink()

        updated_files = [
            item for item in files
            if item["id"] != file_id
        ]

        save_uploaded_files(updated_files)
        st.rerun()

    except OSError as error:
        st.error(f"Could not delete the document: {error}")


def render_document_panel():
    """Render the document-management section in the dashboard."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    st.header("📁 Documents")
    st.caption("Upload PDF, Word, or text documents.")

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=ALLOWED_TYPES,
        accept_multiple_files=False,
        key="document_uploader",
    )

    if uploaded_file is not None:
        upload_document(uploaded_file)

    st.divider()
    st.subheader("Uploaded documents")

    files = read_uploaded_files()

    if not files:
        st.info("No documents uploaded yet.")
        return

    st.caption(f"{len(files)} document(s)")

    # Preserve the manifest's insertion order.
    for item in files:
        file_col, delete_col = st.columns(
            [5, 1],
            vertical_alignment="center",
        )

        with file_col:
            st.markdown(f"📄 {item['original_name']}")

            if "chunks_stored" in item:
                st.caption(
                    f"{item['chunks_stored']} chunks indexed"
                )

        with delete_col:
            if st.button(
                "🗑️",
                key=f"delete_{item['id']}",
                help=f"Delete {item['original_name']}",
            ):
                delete_document(item["id"])