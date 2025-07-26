from typing import List

from src.database.chroma_db import ChromaDBManager

_db_manager = ChromaDBManager()
_collection = _db_manager.get_or_create_collection("assignment")


async def query(text: str, n_results: int = 2) -> List[str]:
    """Return documents relevant to *text* from ChromaDB."""
    return await _db_manager.query(_collection, [text], n_results=n_results)
