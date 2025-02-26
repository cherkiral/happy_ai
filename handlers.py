import logging
import os
import uuid

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from utils import transcribe_audio, get_assistant_response, download_and_save_voice, text_to_speech
from config import settings

router = Router()

@router.message(F.voice)
async def voice_message_handler(message: Message):
    unique_filename = f"{uuid.uuid4()}.ogg"
    temp_path = os.path.join(settings.TEMP_DIR, unique_filename)

    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"

    await download_and_save_voice(file_url, temp_path)

    transcribed_text = await transcribe_audio(temp_path)
    await message.answer(f"Распознанный текст: {transcribed_text}")

    os.remove(temp_path)
    logging.info(f"Удален времменый глосовой файл: {temp_path}")

    waiting_msg = await message.answer("ai генерирует ответ...")

    assistant_response = await get_assistant_response(transcribed_text)

    await message.answer(assistant_response)

    await waiting_msg.delete()

    waiting_voice_msg = await message.answer("ai создает голосовое сообщение...")

    audio_data = await text_to_speech(assistant_response)

    voice_file = BufferedInputFile(audio_data, filename="response.ogg")

    await message.answer_voice(voice=voice_file)

    await waiting_voice_msg.delete()