import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import BotCommand
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from app.config.config import settings
from app.database.crud.users import UserRepository
from app.telegram.handlers import router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
user_repo = UserRepository()

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мои последние 10 сообщений")],
            [KeyboardButton(text="Мой thread_id")],
            [KeyboardButton(text="Мои ценности")],
            [KeyboardButton(text="Удалить мои ценности")],
            [KeyboardButton(text="Обновить мой thread_id")]
        ],
        resize_keyboard=True
    )

async def set_main_menu():
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
    ]
    await bot.set_my_commands(commands)

@dp.message(Command("start"))
async def start_handler(message):
    tg_id = message.from_user.id

    await user_repo.create_user(tg_id)
    await message.answer("Привет! Я AI-бот. Отправь мне голосовое или текст, а я помогу!", reply_markup=get_main_menu())

async def main():
    logging.info("Бот запущен")
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    logging.info("Создана временная директория для голосовых файлов")

    await set_main_menu()

    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
