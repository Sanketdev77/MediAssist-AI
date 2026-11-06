
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
IMAGE_MANIFEST_PATH = UPLOAD_DIR / "image_manifest.json"

ALLOWED_TYPES = ["png", "jpg", "jpeg", "pdf"]


def read_uploaded_images():
    """Read the persistent image-upload manifest."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    if not IMAGE_MANIFEST_PATH.exists():
        return []

    try:
        data = json.loads(
            IMAGE_MANIFEST_PATH.read_text(encoding="utf-8")
        )
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        st.error("Unable to read the uploaded image list.")
        return []


def save_uploaded_images(files):
    """Persist the image-upload manifest."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    IMAGE_MANIFEST_PATH.write_text(
        json.dumps(files, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def upload_image_or_pdf(uploaded_file):
    """Save, process, and register an image or scanned PDF."""
    file_bytes = uploaded_file.getvalue()
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    files = read_uploaded_images()

    if any(item.get("sha256") == file_hash for item in files):
        st.info("This image or PDF has already been uploaded.")
        return

    original_name = Path(uploaded_file.name).name
    stored_name = f"{uuid.uuid4().hex}_{original_name}"
    stored_path = UPLOAD_DIR / stored_name

    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        stored_path.write_bytes(file_bytes)

        with st.spinner(
            "Processing visual content, extracting text, "
            "and indexing in the knowledge base..."
        ):
            from rag.pipeline import DocumentIngestionPipeline

            pipeline = DocumentIngestionPipeline()
            result = pipeline.ingest_file(stored_path)

        files.append(
            {
                "id": uuid.uuid4().hex,
                "original_name": original_name,
                "stored_name": stored_name,
                "sha256": file_hash,
                "file_type": result.get("file_type", stored_path.suffix.lower()),
                "chunks_stored": result["chunks_stored"],
            }
        )

        save_uploaded_images(files)

        st.success(f"Processed successfully: {original_name}")
        st.caption(
            f"Chunks created: {result['chunks_created']} | "
            f"Chunks stored: {result['chunks_stored']}"
        )

    except Exception as error:
        if stored_path.exists():
            stored_path.unlink()

        st.error(f"Image/PDF processing failed: {error}")


def delete_uploaded_image(file_id):
    """Delete an uploaded image/PDF and update its manifest."""
    files = read_uploaded_images()

    selected = next(
        (item for item in files if item.get("id") == file_id),
        None,
    )

    if selected is None:
        st.warning("Uploaded file not found.")
        return

    stored_path = UPLOAD_DIR / selected["stored_name"]

    try:
        if stored_path.exists():
            stored_path.unlink()

        updated_files = [
            item for item in files
            if item.get("id") != file_id
        ]

        save_uploaded_images(updated_files)
        st.rerun()

    except OSError as error:
        st.error(f"Could not delete the uploaded file: {error}")


def render_image_upload_panel():
    """Render the image and scanned-PDF upload section."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    st.header("🖼️ Images & Scanned PDFs")
    st.caption(
        "Upload images or PDFs containing scanned pages, "
        "charts, screenshots, and diagrams."
    )

    uploaded_file = st.file_uploader(
        "Upload an image or PDF",
        type=ALLOWED_TYPES,
        accept_multiple_files=False,
        key="image_pdf_uploader",
    )

    if uploaded_file is not None:
        upload_image_or_pdf(uploaded_file)

    st.divider()
    st.subheader("Uploaded images & PDFs")

    files = read_uploaded_images()

    if not files:
        st.info("No images or scanned PDFs uploaded yet.")
        return

    st.caption(f"{len(files)} file(s)")

    for item in files:
        file_col, delete_col = st.columns(
            [5, 1],
            vertical_alignment="center",
        )

        with file_col:
            extension = Path(item["original_name"]).suffix.lower()
            icon = "📕" if extension == ".pdf" else "🖼️"

            st.markdown(f"{icon} {item['original_name']}")

            if "chunks_stored" in item:
                st.caption(
                    f"{item['chunks_stored']} chunks indexed"
                )

        with delete_col:
            if st.button(
                "🗑️",
                key=f"delete_image_{item['id']}",
                help=f"Delete {item['original_name']}",
            ):
                delete_uploaded_image(item["id"])