import logging
from typing import Any, Coroutine

import aiohttp
import httpx
import openai
import base64

from openai.types.chat.chat_completion import Choice

from app.config.config import settings

client = openai.AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    http_client=httpx.AsyncClient(proxy=settings.PROXY_URL)
)


async def download_and_save_image(file_url: str, save_path: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                if response.status == 200:
                    with open(save_path, "wb") as f:
                        f.write(await response.read())
                    logging.info(f"Изображение сохранено: {save_path}")
                else:
                    logging.error(f"Ошибка при скачивании изображения, статус код: {response.status}")
    except Exception as e:
        logging.error(f"Ошибка при скачивании изображения: {e}")

async def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def analyze_photo_with_openai(base64_image: bytes) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Ты эксперт в анализе человеческих эмоций по фото. "
                                "Определи настроение человека по выражению его лица. "
                                "Ответ должен быть одним словом: радость, грусть, удивление, злость, страх, нейтральное.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content.strip()
