import logging
import json
import numpy as np
from pathlib import Path
from app.services.embedding_service import get_embedding_model

logger = logging.getLogger(__name__)

def retrieve_relevant_chunks(video_id: int, question: str, top_k: int = 3):
    """
    Step 4C: FAISS Vector Search.
    Finds the most relevant chunks based on semantic similarity.
    """
    embed_dir = Path("uploads/embeddings")
    embed_file = embed_dir / f"video_{video_id}_embeddings.npy"
    chunk_meta_file = embed_dir / f"video_{video_id}_chunks.json"
    
    if not embed_file.exists() or not chunk_meta_file.exists():
        logger.warning("Embeddings not found for video_id=%s. Cannot retrieve chunks.", video_id)
        return []
        
    try:
        import faiss
    except ImportError:
        logger.error("faiss-cpu is not installed.")
        raise
        
    # Load embeddings and chunk metadata
    embeddings = np.load(str(embed_file))
    with open(chunk_meta_file, "r") as f:
        chunks = json.load(f)
        
    if len(chunks) == 0:
        return []
        
    # Initialize FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Embed the query
    model = get_embedding_model()
    query_vector = model.encode([question], convert_to_numpy=True)
    
    # Search
    k = min(top_k, len(chunks))
    distances, indices = index.search(query_vector, k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(chunks) and idx != -1:
            chunk = chunks[idx]
            results.append({
                "chunk_text": chunk.get("chunk_text"),
                "start_time": chunk.get("start_time"),
                "end_time": chunk.get("end_time"),
                "score": float(distances[0][i])
            })
            
    logger.info("Retrieved %s chunks for query: '%s'", len(results), question)
    return results
