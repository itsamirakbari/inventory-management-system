import logging

from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

LOGGER_NAME = "inventory_management_system"


def setup_logging():
    # 1. Logger holen
    logger = logging.getLogger(LOGGER_NAME)

    # 2. Logger konfigurieren
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # 3. Alte Handler entfernen
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    # 4. Formatter erstellen
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 5. FileHandler erstellen
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=50 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # 6. ConsoleHandler erstellen
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 7. Handler registrieren
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 8. Logger zurückgeben
    return logger



