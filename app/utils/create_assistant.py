import asyncio

import httpx
import openai
from app.config.config import settings

client = openai.AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    http_client=httpx.AsyncClient(proxy=settings.PROXY_URL)
)

async def create_assistant():
    assistant = await client.beta.assistants.create(
        name="Value Identifier",
        instructions=(
            "Ты AI-ассистент, который анализирует сообщения пользователя и определяет его ключевые ценности. "
            "Когда ты определил ценность, вызывай `save_value`, передавая найденное значение."
        ),
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "save_value",
                    "description": "Сохраняет ключевую ценность пользователя в базе данных.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string", "description": "Ключевая ценность пользователя"}
                        },
                        "required": ["value"]
                    }
                }
            }
        ],
        model="gpt-4-turbo"
    )
    return assistant.id

async def setup():
    assistant_id = await create_assistant()
    print(f"ID: {assistant_id}")

asyncio.run(setup())