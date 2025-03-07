import logging
import os
import uuid

from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, BufferedInputFile, ReplyKeyboardMarkup, KeyboardButton
from app.database.crud.users import UserRepository
from app.database.crud.messages import MessageRepository
from app.utils.amplitude import log_event_to_amplitude
from app.utils.utils import transcribe_audio, download_and_save_voice, text_to_speech, process_values, \
    download_and_save_image, encode_image
from app.utils.ai_services import get_assistant_response, analyze_photo_with_openai
from app.config.config import settings


router = Router()

user_repo = UserRepository()
message_repo = MessageRepository()


def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мои последние 10 сообщений")]
        ],
        resize_keyboard=True
    )
    return keyboard

@router.message(F.voice)
async def voice_message_handler(message: Message):
    tg_id = message.from_user.id
    user = await user_repo.create_user(tg_id)

    unique_filename = f"{uuid.uuid4()}.ogg"
    temp_path = os.path.join(settings.TEMP_DIR, unique_filename)

    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"

    await download_and_save_voice(file_url, temp_path)

    transcribed_text = await transcribe_audio(temp_path)
    await message.answer(f"Распознанный текст: {transcribed_text}")

    log_event_to_amplitude("voice_message_sent", tg_id, {"message": transcribed_text})

    await message_repo.save_user_message(tg_id, transcribed_text)

    os.remove(temp_path)
    logging.info(f"Удален временный голосовой файл: {temp_path}")

    waiting_msg = await message.answer("AI генерирует ответ...")

    assistant_response, extracted_value = await get_assistant_response(transcribed_text, user.thread_id)

    await message.answer(assistant_response)
    await waiting_msg.delete()

    if extracted_value:
        valid_values, response_message = await process_values(extracted_value)

        if valid_values:
            await user_repo.update_user_values(user.id, valid_values)
            await message.answer(f"Найдены ваши ценности: {valid_values}")

        await message.answer(response_message)

    waiting_voice_msg = await message.answer("AI создает голосовое сообщение...")

    audio_data = await text_to_speech(assistant_response)
    voice_file = BufferedInputFile(audio_data, filename="response.ogg")

    await message.answer_voice(voice=voice_file)
    await waiting_voice_msg.delete()


@router.message(F.photo)
async def photo_handler(message: Message):
    tg_id = message.from_user.id
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_info.file_path}"

    log_event_to_amplitude("photo_sent", tg_id)

    unique_filename = f"{uuid.uuid4()}.jpg"
    save_path = os.path.join(settings.TEMP_DIR, unique_filename)

    await download_and_save_image(file_url, save_path)

    bs64_photo = await encode_image(save_path)

    waiting_msg = await message.answer("AI пытается определить эмоцию")

    emotion = await analyze_photo_with_openai(bs64_photo)

    await waiting_msg.delete()

    await message.answer(f"Эмоция на фото: {emotion}")

    os.remove(save_path)



@router.message(F.text == "Мои последние 10 сообщений")
async def last_messages_handler(message: Message):
    tg_id = message.from_user.id

    log_event_to_amplitude("request_10_last_messages", tg_id, {"message": "Мои последние 10 сообщений"})

    messages = await message_repo.get_last_messages(tg_id)

    if messages:
        messages_text = "\n".join([f"{i+1}. {msg}" for i, msg in enumerate(messages)])
    else:
        messages_text = "У вас пока нет сохранённых сообщений."

    await message.answer(f"**Ваши последние 10 сообщений:**\n\n{messages_text}")

@router.message(F.text == "Мой thread_id")
async def get_thread_handler(message: Message):
    tg_id = message.from_user.id

    log_event_to_amplitude("request_my_thread_id", tg_id, {"message": "Мой thread_id"})

    user_id = await user_repo.get_or_create_thread(tg_id)

    await message.answer(f"**Ваш thread_id:**\n\n{user_id}")

@router.message(F.text == "Мои ценности")
async def my_values_handler(message: Message):
    tg_id = message.from_user.id

    log_event_to_amplitude("request_user_values", tg_id, {"message": "Мои ценности"})

    values = await user_repo.get_user_values(tg_id)

    await message.answer(f"**Ваши ценности:**\n\n{values}")

@router.message(F.text == "Удалить мои ценности")
async def delete_values_handler(message: Message):
    tg_id = message.from_user.id

    log_event_to_amplitude("request_delete_user_values", tg_id, {"message": "Удалить мои ценности"})

    await user_repo.delete_user_values(tg_id)

    await message.answer(f"**Ваши ценности удалены**")

@router.message(F.text == "Обновить мой thread_id")
async def refresh_thread_handler(message: Message):
    tg_id = message.from_user.id

    log_event_to_amplitude("request_refresh_user_thread_id", tg_id, {"message": "Обновить мой thread_id"})

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да, обновить", callback_data=f"confirm_refresh_{tg_id}")],
            [InlineKeyboardButton(text="Отмена", callback_data="cancel_refresh")]
        ]
    )

    await message.answer(
        "**Вы уверены, что хотите обновить ваш thread_id?**\n"
        "Это приведет к удалению всех ваших ценностей.",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("confirm_refresh_"))
async def confirm_refresh_callback(callback_query):
    tg_id = int(callback_query.data.split("_")[-1])

    new_thread = await user_repo.refresh_user_thread(tg_id)
    await user_repo.delete_user_values(tg_id)

    await callback_query.message.edit_text(f"**Ваш thread_id обновлен:**\n\n{new_thread}")
    await callback_query.answer()


@router.callback_query(F.data == "cancel_refresh")
async def cancel_refresh_callback(callback_query):
    await callback_query.message.edit_text("Обновление thread_id отменено.")
    await callback_query.answer()