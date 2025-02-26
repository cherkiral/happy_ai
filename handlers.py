from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from utils import transcribe_audio, get_assistant_response, download_voice, text_to_speech

router = Router()

@router.message(F.voice)
async def voice_message_handler(message: Message):
    voice = message.voice
    file_id = voice.file_id
    file = await message.bot.get_file(file_id)

    file_path = file.file_path
    file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}"

    voice_data = await download_voice(file_url)
    transcribed_text = await transcribe_audio(voice_data)

    await message.answer(f"Распознанный текст: {transcribed_text}")

    waiting_msg = await message.answer("ai думает...")

    assistant_response = await get_assistant_response(transcribed_text)

    await message.answer(assistant_response)

    audio_data = await text_to_speech(assistant_response)

    voice_file = BufferedInputFile(audio_data, filename="response.ogg")

    await message.answer_voice(voice=voice_file)

    await waiting_msg.delete()
