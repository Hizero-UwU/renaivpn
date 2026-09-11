import logging
import sys
from pathlib import Path
from utils.config import settings


def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Настройка логгера с выводом в консоль и файл
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Файловый handler
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    file_handler = logging.FileHandler(
        log_dir / 'bot.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
