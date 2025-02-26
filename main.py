import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from config import settings
from handlers import router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def main():
    logging.info("Бот запущен")
    await dp.start_polling(bot)

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет, я бот для happyai, отправь мне голосовое сообщение, и я его распоззнаю")

if __name__ == "__main__":
    asyncio.run(main())
