import logging
import json
import numpy as np
from pathlib import Path
from app.services.chunking_service import create_chunks

logger = logging.getLogger(__name__)

# Lazy load model to avoid memory overhead until needed
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Fast, small, good enough for MVP RAG
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            logger.error("sentence-transformers is not installed.")
            raise
    return _model

def generate_embeddings(video_id: int) -> bool:
    """
    Step 4B: Generate vector embeddings for transcript chunks.
    Uses a .lock file to prevent race conditions on concurrent requests for the same video.
    """
    embed_dir = Path("uploads/embeddings")
    embed_dir.mkdir(parents=True, exist_ok=True)

    embed_file = embed_dir / f"video_{video_id}_embeddings.npy"
    chunk_meta_file = embed_dir / f"video_{video_id}_chunks.json"
    lock_file = embed_dir / f"video_{video_id}.lock"

    # Check if already generated — fast path
    if embed_file.exists() and chunk_meta_file.exists():
        logger.info("Embeddings already exist for video_id=%s", video_id)
        return True

    # BUG-03 FIX: If another concurrent request is generating for same video, skip.
    if lock_file.exists():
        logger.warning("Embedding generation already in progress for video_id=%s. Skipping.", video_id)
        return False

    try:
        # Acquire lock
        lock_file.touch()

        chunks = create_chunks(video_id)
        if not chunks:
            raise ValueError("No chunks generated")

        model = get_embedding_model()
        texts = [c["chunk_text"] for c in chunks]

        logger.info("Generating embeddings for %s chunks (video_id=%s)", len(texts), video_id)
        embeddings = model.encode(texts, convert_to_numpy=True)

        # BUG-03 FIX: Write to temp files first, then atomically rename.
        # This prevents a partial/corrupt .npy being read by a concurrent retrieval.
        tmp_embed = embed_dir / f"video_{video_id}_embeddings.npy.tmp"
        tmp_meta = embed_dir / f"video_{video_id}_chunks.json.tmp"

        np.save(str(tmp_embed), embeddings)
        with open(tmp_meta, "w") as f:
            json.dump(chunks, f)

        tmp_embed.rename(embed_file)
        tmp_meta.rename(chunk_meta_file)

        logger.info("Successfully generated and saved embeddings for video_id=%s", video_id)
        return True

    except Exception as e:
        logger.error("Failed to generate embeddings: %s", e)
        # Cleanup partial files on failure
        for f in [embed_file, chunk_meta_file]:
            if f.exists():
                f.unlink()
        raise
    finally:
        # Always release the lock regardless of success or failure
        if lock_file.exists():
            lock_file.unlink()
