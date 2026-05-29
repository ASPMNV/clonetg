#!/usr/bin/env python3
"""
Утилита для проверки доступа к каналам
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.telegram_client import TelegramChannelBot


async def check_channels():
    """Проверка доступа к каналам"""
    print("=" * 60)
    print("Проверка доступа к Telegram каналам")
    print("=" * 60)
    print()
    
    # Загрузить конфигурацию
    try:
        config = Config.load("config.json")
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return
    
    # Создать клиент
    bot = TelegramChannelBot(
        api_id=config.telegram.api_id,
        api_hash=config.telegram.api_hash,
        phone=config.telegram.phone,
        device_model=config.telegram.device_model,
        system_version=config.telegram.system_version,
        app_version=config.telegram.app_version,
        lang_code=config.telegram.lang_code,
        system_lang_code=config.telegram.system_lang_code
    )
    
    try:
        # Запустить клиент
        await bot.start()
        print()
        
        # Проверить канал-источник
        print(f"Проверка канала-источника: {config.telegram.source_channel}")
        source_info = await bot.get_channel_info(config.telegram.source_channel)
        
        if source_info:
            print(f"✅ Название: {source_info.title}")
            print(f"   ID: {source_info.id}")
            
            # Получить последние сообщения
            messages = await bot.get_new_messages(
                config.telegram.source_channel,
                limit=5
            )
            print(f"   Последних сообщений: {len(messages)}")
        else:
            print("❌ Не удалось получить доступ к каналу-источнику")
        
        print()
        
        # Проверить целевой канал
        print(f"Проверка целевого канала: {config.telegram.target_channel}")
        target_info = await bot.get_channel_info(config.telegram.target_channel)
        
        if target_info:
            print(f"✅ Название: {target_info.title}")
            print(f"   ID: {target_info.id}")
        else:
            print("❌ Не удалось получить доступ к целевому каналу")
            print("   Убедитесь, что вы являетесь администратором канала")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await bot.stop()
    
    print()
    print("Проверка завершена!")


if __name__ == "__main__":
    asyncio.run(check_channels())
