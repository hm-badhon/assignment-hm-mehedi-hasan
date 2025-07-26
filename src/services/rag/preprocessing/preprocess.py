"""
Uses llm to convert pdf to text, instead of generic ocr.
"""

import asyncio
import os

from src.services.rag.prompts.prompt import EXTRACT_PROMPT_TEMPLATE
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
SOURCE_FILE_PATH = "data/raw.pdf"
PROCESSED_FILE_PATH = "data/processed.txt"
from google import genai
from google.genai import types

EXTRACT_MODEL_NAME = "gemini-2.5-pro"


async def pdf_to_text(file_path: str) -> str:
    """
    Convert a PDF file to text using a LLM.
    """
    with open(file_path, "rb") as file:
        pdf_bytes = file.read()

    prompt = EXTRACT_PROMPT_TEMPLATE
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
    )

    model = EXTRACT_MODEL_NAME
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(
                    mime_type="application/pdf",
                    data=pdf_bytes,
                ),
                types.Part.from_text(text=prompt),
            ],
        )
    ]
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="text/plain",
        ),
    )
    return response.text


async def process_and_save():
    """
    Process the source PDF file and save the text to the processed file.
    """
    if not os.path.exists(SOURCE_FILE_PATH):
        print(f"Error: Source file {SOURCE_FILE_PATH} not found")
        return
    print(f"Processing PDF: {SOURCE_FILE_PATH}")
    processed_text = await pdf_to_text(SOURCE_FILE_PATH)
    os.makedirs(os.path.dirname(PROCESSED_FILE_PATH), exist_ok=True)
    with open(PROCESSED_FILE_PATH, "w", encoding="utf-8") as file:
        file.write(processed_text)
    print(f"Processed text saved to: {PROCESSED_FILE_PATH}")


if __name__ == "__main__":
    asyncio.run(process_and_save())
