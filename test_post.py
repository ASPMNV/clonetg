#!/usr/bin/env python3
"""
Тест: Опубликовать тестовое сообщение в целевой канал
"""

import asyncio
import sys
import os

# Fix for Windows console UnicodeEncodeError
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Добавить родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime
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
        
        print(f"\n{'='*60}")
        print(f"Публикация в {config.telegram.target_channel}")
        print(f"{'='*60}\n")
        
        # Тестовое сообщение
        test_message = f"""<b>🤖 Тестовое сообщение от бота</b>

<i>Время:</i> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Это тест публикации в канал с <u>сохранением форматирования</u>.
<b>ทดสอบการโพสต์ในช่อง</b> (тест на тайском)

<a href="https://google.com">Тестовая ссылка</a>
<code>import telethon</code>

<blockquote>✅ Если вы видите это сообщение красиво отформатированным, бот работает правильно!</blockquote>"""
        
        print("Отправка сообщения...")
        print(f"\n{test_message}\n")
        
        # Отправить
        sent_msg = await bot.client.send_message(
            config.telegram.target_channel,
            test_message,
            parse_mode='html'
        )
        
        print(f"{'='*60}")
        print(f"✅ Сообщение опубликовано!")
        print(f"ID сообщения: {sent_msg.id}")
        print(f"Ссылка: https://t.me/{config.telegram.target_channel.replace('@', '')}/{sent_msg.id}")
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
        sys.exit(1)
