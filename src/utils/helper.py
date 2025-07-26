import asyncio

import aiofiles
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.database.chroma_db import ChromaDBManager
from src.services.rag.preprocessing.preprocess import PROCESSED_FILE_PATH
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def initialize_vector_db():
    """
    Initializes the vector database asynchronously.
    """
    chroma_manager = ChromaDBManager()
    collection = await asyncio.to_thread(
        chroma_manager.get_or_create_collection, "assignment"
    )

    count = await asyncio.to_thread(collection.count)
    if count == 0:
        logger.info("ChromaDB collection is empty. Populating with data...")
        async with aiofiles.open(PROCESSED_FILE_PATH, "r", encoding="utf-8") as f:
            data = await f.read()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n"],
            is_separator_regex=False,
        )
        documents = await asyncio.to_thread(text_splitter.split_text, data)

        documents = [doc for doc in documents if doc.strip()]

        await asyncio.to_thread(chroma_manager.add_documents, collection, documents)

        new_count = await asyncio.to_thread(collection.count)
        logger.info(f"ChromaDB populated with {new_count} documents.")
    else:
        logger.info(
            f"ChromaDB collection 'assignment' already populated with {count} documents."
        )
