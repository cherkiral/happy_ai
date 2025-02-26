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

async def download_and_save_voice(file_url: str, save_path: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                with open(save_path, "wb") as f:
                    f.write(await response.read())
        logging.info(f"Голосовое сообщение сохранено: {save_path}")
    except Exception as e:
        logging.error(f"Ошибка при скачивании голосового сообщения: {e}")


async def transcribe_audio(file_path: str) -> str:
    try:
        with open(file_path, "rb") as file_stream:
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=file_stream,
                language="ru"
            )

        logging.info(f"Ответ Whisper API: {response}")
        return response.text
    except Exception as e:
        logging.error(f"Ошибка при распознавании аудио: {e}")
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

        return f"Ai не смог сгенерировать ответ {run.status}"

    except Exception as e:
        logging.error("Ошибка при получении ответа от Assistant API:", e)
        return "Ошибка при обработке запроса"


async def text_to_speech(text: str) -> bytes:
    try:
        response = await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )

        audio_data = await response.aread()

        if not audio_data or len(audio_data) == 0:
            logging.error("OpenAI TTS вернул пустой аудиофайл!")
            return None

        return audio_data

    except Exception as e:
        logging.error(f"Ошибка при генерации озвучки: {e}")
        return None