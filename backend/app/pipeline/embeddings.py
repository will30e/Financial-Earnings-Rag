from sentence_transformers import SentenceTransformer
from typing import List, Optional
from app.core.config import settings
from app.core.logging_config import logger

_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("loading_embedding_model", model=settings.EMBEDDING_MODEL)
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    model = get_embedding_model()
    embedding = model.encode([query], normalize_embeddings=True, show_progress_bar=False)
    return embedding[0].tolist()
