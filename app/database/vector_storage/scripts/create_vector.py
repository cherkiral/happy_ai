import asyncio
import os

import httpx
import openai

from app.config.config import settings

client = openai.AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    http_client=httpx.AsyncClient(proxy=settings.PROXY_URL)
)

async def add_to_vector_storage():
    vector_store = await client.beta.vector_stores.create(name="Trevognost storage")

    file_paths = [os.path.abspath("../../vector_storage/files/Trevognost_Expanded.docx")]
    file_streams = [open(path, "rb") for path in file_paths]

    file_batch = await client.beta.vector_stores.file_batches.upload_and_poll(
      vector_store_id=vector_store.id, files=file_streams
    )

    print(file_batch.status)
    print(file_batch.file_counts)
    return vector_store.id

async def update_assistant():
    # vector_id = "vs_67cad5d41460819189d2c4fbb46c6de1"
    vector_id = await add_to_vector_storage()

    assistant = await client.beta.assistants.update(
        assistant_id=settings.ASSISTANT_ID,
        tool_resources={"file_search": {"vector_store_ids": [vector_id]}},
    )

    print(assistant)
if __name__ == "__main__":
    asyncio.run(update_assistant())
