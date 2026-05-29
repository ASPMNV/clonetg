#!/usr/bin/env python3
"""
Telegram Channel Translator Bot
Автоматическое копирование и перевод постов из одного канала в другой
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

from src.config import Config
from src.bot_service import BotService


def setup_logging():
    """Настройка логирования"""
    # Создать директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настройка форматирования
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Настройка обработчиков
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / "bot.log", encoding="utf-8")
    ]
    
    # Базовая конфигурация
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    # Отключить избыточное логирование от библиотек
    logging.getLogger("telethon").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)


def check_config():
    """Проверить наличие конфигурационного файла"""
    if not os.path.exists("config.json"):
        print("❌ Файл config.json не найден!")
        print("📝 Скопируйте config.example.json в config.json и заполните необходимые данные")
        sys.exit(1)


def create_data_directory():
    """Создать директорию для данных"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)


async def main():
    """Главная функция"""
    # Настройка
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Telegram Channel Translator Bot")
    logger.info("=" * 60)
    
    # Проверки
    check_config()
    create_data_directory()
    
    # Загрузка конфигурации
    try:
        config = Config.load("config.json")
        logger.info("✅ Конфигурация загружена")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки конфигурации: {e}")
        sys.exit(1)
    
    # Проверка API ключей
    if not config.gemini.api_keys:
        logger.error("❌ Не указаны API ключи Gemini")
        sys.exit(1)
    
    logger.info(f"🔑 Загружено {len(config.gemini.api_keys)} API ключей Gemini")
    logger.info(f"📡 Канал-источник: {config.telegram.source_channel}")
    logger.info(f"📤 Целевой канал: {config.telegram.target_channel}")
    logger.info(f"🤖 Модель Gemini: {config.gemini.model}")
    logger.info(f"⏱️  Интервал проверки: {config.processing.check_interval} сек")
    
    # Запуск сервиса
    bot_service = BotService(config)
    
    # Отправляем уведомление о старте
    try:
        from src.alerting import send_startup_alert
        send_startup_alert(config)
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление о запуске: {e}")
        
    try:
        await bot_service.run()
    except KeyboardInterrupt:
        logger.info("\n👋 Остановка по запросу пользователя")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        try:
            from src.alerting import send_crash_alert
            send_crash_alert(config, e)
        except Exception as alert_error:
            logger.error(f"Не удалось отправить алерт: {alert_error}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
