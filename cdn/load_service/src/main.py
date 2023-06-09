import logging

import uvicorn

from core.logger import LOGGING
from service import app  # noqa: F401

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_config=LOGGING, log_level=logging.DEBUG, reload=True)
