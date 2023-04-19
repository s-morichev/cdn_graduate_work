import json
import logging

import requests
from urllib3.exceptions import ConnectionError

from config.components.common import API_LOAD_SERVICE_URL
from .schemas import UploadTask

logger = logging.getLogger(__name__)

ERROR_MESSAGE = 'Error occurred during sending data to Load Service API - %s'


def upload_file(task: UploadTask):
    try:
        response = requests.post(f'{API_LOAD_SERVICE_URL}/v1/tasks/upload_file_to_storage', data=task.json())
    except ConnectionError as err:
        logger.error("Cannot connect to load service, error: %s", err)
        raise
    result = response.json()
    if response.status_code != 200:
        logger.error(ERROR_MESSAGE, result)
        raise Exception(result)
    return json.dumps(result)
