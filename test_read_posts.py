#!/usr/bin/env python3
"""
Тест: Показать последние N постов из канала-источника
"""

import asyncio
import sys
from src.config import Config
from src.telegram_client import TelegramChannelBot


async def main():
    # Загрузить конфигурацию
    config = Config.load("config.json")
    
    # Создать клиент
    bot = TelegramChannelBot(
        api_id=config.telegram.api_id,
        api_hash=config.telegram.api_hash,
        phone=config.telegram.phone,
        session_name=config.telegram.session_name,
        device_model=config.telegram.device_model,
        system_version=config.telegram.system_version,
        app_version=config.telegram.app_version,
        lang_code=config.telegram.lang_code,
        system_lang_code=config.telegram.system_lang_code
    )
    
    try:
        # Запустить клиент
        await bot.start()
        
        # Спросить сколько постов показать
        try:
            n = int(input("\nСколько последних постов показать? (по умолчанию 5): ") or "5")
        except ValueError:
            n = 5
        
        print(f"\n{'='*60}")
        print(f"Последние {n} постов из {config.telegram.source_channel}")
        print(f"{'='*60}\n")
        
        # Получить последние N постов
        messages = await bot.client.get_messages(
            config.telegram.source_channel,
            limit=n
        )
        
        if not messages:
            print("❌ Постов не найдено")
            return
        
        # Показать посты
        for i, msg in enumerate(messages, 1):
            print(f"{'─'*60}")
            print(f"Пост #{i} | ID: {msg.id} | Дата: {msg.date}")
            print(f"{'─'*60}")
            
            # Текст
            if msg.text:
                text = msg.text[:200] + "..." if len(msg.text) > 200 else msg.text
                print(f"Текст: {text}")
            else:
                print("Текст: (нет)")
            
            # Медиа
            if msg.media:
                media_type = type(msg.media).__name__
                print(f"Медиа: {media_type}")
            else:
                print("Медиа: (нет)")
            
            # Репост
            if msg.fwd_from:
                print("Репост: Да")
            
            print()
        
        print(f"{'='*60}")
        print(f"Всего показано: {len(messages)} постов")
        print(f"{'='*60}")
        
    finally:
        await bot.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
