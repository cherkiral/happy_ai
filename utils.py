import asyncio
import io
import logging
import aiohttp
import httpx
import openai
from config import settings

client = openai.AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    http_client=httpx.AsyncClient(proxy=settings.PROXY_URL)
)

async def download_voice(file_url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            return await response.read()

async def transcribe_audio(file_data: bytes) -> str:
    file_stream = io.BytesIO(file_data)
    file_stream.name = "voice.ogg"

    try:
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=file_stream,
            language="ru"
        )
        logging.info(f"Ответ Whisper API: {response}")
        return response.text
    except Exception as e:
        logging.info("Ошибка при распознавании:", e)
        return "Ошибка при распознавании аудио"


async def get_assistant_response(user_message: str) -> str:
    try:
        thread = await client.beta.threads.create()

        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=settings.ASSISTANT_ID
        )

        if run.status == "completed":
            messages = await client.beta.threads.messages.list(thread_id=thread.id)

            if messages.data:
                return messages.data[0].content[0].text.value

        return f"AI пока думает, cтатус: {run.status}"

    except Exception as e:
        logging.error("Ошибка при получении ответа от Assistant API:", e)
        return "Ошибка при обработке запроса"


async def text_to_speech(text: str) -> bytes:
    try:
        response = await client.audio.speech.create(
            model="tts-1-hd",
            voice="alloy",
            input=text
        )

        audio_data = await response.aread()

        return audio_data

    except Exception as e:
        logging.error(f"Ошибка при генерации озвучки: {e}")
        return None