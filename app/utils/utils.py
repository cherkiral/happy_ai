import logging
import aiohttp
import httpx
import openai
from app.config.config import settings
from app.utils.ai_services import validate_value_completion

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

async def process_values(extracted_values: str):
    valid_values = []
    rejected_values = []

    for value in extracted_values.split(", "):
        is_valid = await validate_value_completion(value)
        if is_valid:
            valid_values.append(value)
        else:
            rejected_values.append(value)

    response_message = ""

    if valid_values:
        response_message = f"**Добавлены ценности:** {', '.join(valid_values)}"
    else:
        response_message = "**Все найденные ценности были отклонены.**"

    if rejected_values:
        response_message += f"\n**Отклонены:** {', '.join(rejected_values)}"

    return ", ".join(valid_values), response_message



async def create_thread():
    thread = await client.beta.threads.create()
    return thread.id