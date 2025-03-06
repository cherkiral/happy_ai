from amplitude import Amplitude, BaseEvent
from concurrent.futures import ThreadPoolExecutor

from app.config.config import settings

executor = ThreadPoolExecutor(max_workers=5)

amplitude_client = Amplitude("789ce7dc13f64ec5569c8e810875c094")

def send_amplitude_event(event_type: str, user_telegram_id: int, event_properties: dict = None):
    try:
        event = BaseEvent(
            event_type=event_type,
            user_id=str(user_telegram_id),
            event_properties=event_properties or {}
        )
        amplitude_client.track(event)
    except Exception as e:
        print(f"Ошибка при отправке события в Amplitude: {str(e)}")

def log_event_to_amplitude(event_type: str, user_id: int, event_properties: dict = None):
    executor.submit(send_amplitude_event, event_type, user_id, event_properties)
