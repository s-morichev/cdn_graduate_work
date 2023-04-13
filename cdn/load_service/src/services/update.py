import backoff
import httpx

from core.config import settings
from models.update import Updates
from services.storage import storage
from core.api_key import get_api_key_header
"""
Функции для отправки данных на сервер синхронизации
do_update() - проверяет список в редис, если там есть данные - отправляет на сервер
если отправка проходит успешно - удаляет отправленные данные из списка
send_heartbeat() - отправляет ping на сервер
Запускать их планируется из Celery
"""


def no_changes():
    return not storage.count()


@backoff.on_predicate(backoff.expo, max_tries=5)
def send_updates(updates: Updates) -> bool:
    """
    Отправляет обновления на сервер синхронизации
    если все ОК - возвращает True
    """
    url_str = settings.SYNC_URI
    sync_url = url_str.format(storage_id=settings.HOME_STORAGE_ID)

    body = updates.dict()
    headers = get_api_key_header()
    try:
        response = httpx.post(url=sync_url, headers=headers, json=body, timeout=1)
        response.raise_for_status()

    except httpx.HTTPError as err:
        return False

    return True


def do_update() -> bool:
    """
    Отправляет данные для обновления серверу синхронизации.
    Возвращает True если нет данных или данные отправлены удачно
    """
    # если нет данных для обновления - выходим
    if no_changes():
        return True

    # получаем список обновлений
    updates = storage.get_updates()
    count = len(updates.items)

    # отправляем обновления
    result = send_updates(updates)

    # если все хорошо - стираем из списка
    if result:
        storage.delete(count)

    return result


@backoff.on_predicate(backoff.expo, max_tries=3)
def send_heartbeat() -> bool:
    """Отправляет ping сообщение на sync сервер"""
    if settings.HEARTBEAT_URI:
        url = settings.HEARTBEAT_URI.format(storage_id=settings.HOME_STORAGE_ID)
        headers = get_api_key_header()
        try:
            response = httpx.post(url=url, headers=headers, json={"ping": "pong"}, timeout=1)
            response.raise_for_status()

        except httpx.HTTPError as err:
            return False

    return True
