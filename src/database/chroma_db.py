import asyncio
from typing import List

import chromadb
from chromadb.types import Collection

from src.services.rag.utils.llm import GeminiEmbeddingFunction
from src.utils.config import get_settings

settings = get_settings()


class ChromaDBManager:
    """Manages ChromaDB interactions."""

    def __init__(self, path: str = "/app/chroma_data"):
        """Initializes the ChromaDB client."""
        self.client = chromadb.PersistentClient(path=path)

    def get_or_create_collection(self, name: str) -> Collection:
        """
        Gets or creates a ChromaDB collection.
        Args:
            name: The name of the collection.
        Returns:
            The ChromaDB collection.
        """
        embedding_function = GeminiEmbeddingFunction()
        return self.client.get_or_create_collection(
            name=name, embedding_function=embedding_function
        )

    def add_documents(self, collection: Collection, documents: List[str]):
        """
        Adds documents to a ChromaDB collection.
        Args:
            collection: The ChromaDB collection.
            documents: The documents to add.
        """
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_documents = documents[i : i + batch_size]
            collection.add(
                documents=batch_documents,
                ids=[str(j) for j in range(i, i + len(batch_documents))],
            )

    async def query(
        self, collection: Collection, query_texts: List[str], n_results: int = 2
    ) -> List[str]:
        """
        Queries a ChromaDB collection asynchronously.
        Args:
            collection: The ChromaDB collection.
            query_texts: The query texts.
            n_results: The number of results to return.
        Returns:
            The query results.
        """
        results = await asyncio.to_thread(
            collection.query, query_texts=query_texts, n_results=n_results
        )
        return results["documents"][0] if results["documents"] else []
