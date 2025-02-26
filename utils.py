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


async def wait_for_completion(thread_id: str, run_id: str) -> None:
    while True:
        run_status = await client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

        if run_status.status == "completed":
            return
        elif run_status.status in ["failed", "cancelled"]:
            raise Exception("Ошибка: Ассистент не смог ответить.")

        await asyncio.sleep(1)

async def get_assistant_response(user_message: str) -> str:
    try:
        thread = await client.beta.threads.create()

        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=settings.ASSISTANT_ID
        )
        logging.info(f"Запущен ассистент ID: {run.id}")

        await wait_for_completion(thread.id, run.id)

        messages = await client.beta.threads.messages.list(thread_id=thread.id)

        if not messages.data:
            return "Ошибка: AI не прислал ответ."

        assistant_response = messages.data[0].content[0].text.value

        logging.info(f"Ответ Assistant API: {assistant_response}")
        return assistant_response

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