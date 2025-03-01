import logging
import json
import openai
import httpx
from app.config.config import settings

client = openai.AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    http_client=httpx.AsyncClient(proxy=settings.PROXY_URL)
)

async def get_assistant_response(user_message: str, thread_id: str) -> str:
    try:
        await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=settings.ASSISTANT_ID
        )

        if run.status == "completed":
            messages = await client.beta.threads.messages.list(thread_id=thread_id)

            if messages.data:
                return messages.data[0].content[0].text.value

        return f"Ai не смог сгенерировать ответ {run.status}"

    except Exception as e:
        logging.error("Ошибка при получении ответа от Assistant API:", e)
        return "Ошибка при обработке запроса"


async def extract_assistant_value(thread_id: str):
    try:
        runs = await client.beta.threads.runs.list(thread_id=thread_id)

        if not runs.data:
            return None

        latest_run = runs.data[0]

        if latest_run.status != "requires_action":
            return None

        required_action = latest_run.required_action.dict()
        tool_calls = required_action.get("submit_tool_outputs", {}).get("tool_calls", [])

        tool_outputs = []
        extracted_values = []

        for tool in tool_calls:
            function_name = tool["function"]["name"]
            function_args = tool["function"]["arguments"]

            if function_name == "save_value":
                extracted_value = json.loads(function_args).get("value")
                if extracted_value:
                    extracted_values.append(extracted_value)
                tool_outputs.append({"tool_call_id": tool["id"], "output": json.dumps({"success": True})})

        if tool_outputs:
            await client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=latest_run.id,
                tool_outputs=tool_outputs
            )

        return ", ".join(extracted_values) if extracted_values else None

    except Exception as e:
        logging.error(f"Ошибка при проверке значений Assistant API: {e}")
        return None

async def validate_value_completion(value: str) -> bool:
    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a system that validates if a given word represents a meaningful human value or principle.\n"
                        "A personal value is a concept that guides human behavior, such as 'honesty', 'friendship', or 'freedom'.\n"
                        "Some examples of valid values: дружба (friendship), свобода (freedom), честность (honesty), уважение (respect), "
                        "любовь (love), терпение (patience), ответственность (responsibility), справедливость (justice).\n"
                        "Some examples of INVALID values: телефон (phone), пицца (pizza), компьютер (computer), машина (car), дом (house), интернет (internet).\n"
                        "If the word is an abstract personal value, return ONLY 'True'.\n"
                        "If the word is a physical object, food, or unrelated to personal values, return ONLY 'False'.\n"
                        "DO NOT provide any explanation, return ONLY 'True' or 'False'."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Is '{value}' a valid personal value? Return only True or False.",
                },
            ],
            temperature=0.3,
            max_tokens=5,
        )

        ai_response = response.choices[0].message.content.strip().lower()
        logging.info(f"Validation response for '{value}': {ai_response}")

        return ai_response == "true"

    except Exception as e:
        logging.error(f"Ошибка при валидации значения '{value}': {e}")
        return False
