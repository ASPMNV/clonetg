#!/usr/bin/env python3
"""
Тест: Полный цикл - взять последний пост, перевести и опубликовать
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
from src.config import Config
from src.telegram_client import TelegramChannelBot
from src.translator import GeminiTranslator
from src.post_processor import PostProcessor, ProcessedPost
from src.filter import ContentFilter


async def main():
    # Загрузить конфигурацию
    config = Config.load("config.json")
    
    # Создать компоненты
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
    
    translator = GeminiTranslator(
        api_keys=config.gemini.api_keys,
        model=config.gemini.model
    )
    
    content_filter = ContentFilter(
        spam_keywords=config.filters.spam_keywords,
        allowed_domains=config.filters.allowed_domains,
        remove_referral_params=config.filters.remove_referral_params
    )
    
    processor = PostProcessor(
        translator=translator,
        content_filter=content_filter,
        handle_reposts=config.filters.handle_reposts
    )
    
    try:
        # Запустить клиент
        await bot.start()
        
        print(f"\n{'='*60}")
        print("ПОЛНЫЙ ЦИКЛ ОБРАБОТКИ ПОСТА")
        print(f"{'='*60}\n")
        
        # 1. Получить последний пост
        print(f"1️⃣ Получение поста из {config.telegram.source_channel}...")
        messages = await bot.client.get_messages(
            config.telegram.source_channel,
            limit=1
        )
        
        if not messages:
            print("❌ Постов не найдено")
            return
        
        msg = messages[0]
        print(f"   ✅ Получен пост ID: {msg.id}")
        
        if msg.text:
            print(f"   Текст: {msg.text[:100]}...")
        
        # 2. Обработать пост
        print(f"\n2️⃣ Обработка поста...")
        processed = await processor.process_message(msg)
        
        if not processed:
            print("   ❌ Пост отфильтрован (спам или пустой)")
            return
        
        print(f"   ✅ Пост обработан")
        print(f"   Переведенный текст: {processed.text[:100]}...")
        if processed.formatting:
            print(f"   Форматирование: {processed.formatting}")
        
        if processed.media:
            print(f"   Медиа: {processed.media_type}")
        
        # 3. Опубликовать
        print(f"\n3️⃣ Публикация в {config.telegram.target_channel}...")
        
        target_msg_id = await bot.send_post(
            config.telegram.target_channel,
            processed
        )
        
        if target_msg_id:
            print(f"   ✅ Опубликовано! ID: {target_msg_id}")
            print(f"   Ссылка: https://t.me/{config.telegram.target_channel.replace('@', '')}/{target_msg_id}")
        else:
            print("   ❌ Ошибка публикации")
        
        print(f"\n{'='*60}")
        print("ТЕСТ ЗАВЕРШЕН")
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
