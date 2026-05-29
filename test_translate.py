#!/usr/bin/env python3
"""
Тест: Перевести последний пост из канала-источника
"""

import asyncio
import sys
from src.config import Config
from src.telegram_client import TelegramChannelBot
from src.translator import GeminiTranslator


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
    
    # Создать переводчик
    translator = GeminiTranslator(
        api_keys=config.gemini.api_keys,
        model=config.gemini.model
    )
    
    try:
        # Запустить клиент
        await bot.start()
        
        print(f"\n{'='*60}")
        print(f"Получение последнего поста из {config.telegram.source_channel}")
        print(f"{'='*60}\n")
        
        # Получить последний пост
        messages = await bot.client.get_messages(
            config.telegram.source_channel,
            limit=1
        )
        
        if not messages or not messages[0].text:
            print("❌ Пост не найден или нет текста")
            return
        
        msg = messages[0]
        
        print(f"ID поста: {msg.id}")
        print(f"Дата: {msg.date}")
        print(f"\n{'─'*60}")
        print("ОРИГИНАЛ:")
        print(f"{'─'*60}")
        print(msg.text)
        
        print(f"\n{'─'*60}")
        print("ПЕРЕВОД НА ТАЙСКИЙ:")
        print(f"{'─'*60}")
        
        # Перевести
        if getattr(msg, "entities", None):
            from src.format_utils import entities_to_html, protect_untranslatable, restore_untranslatable
            raw_text = getattr(msg, 'raw_text', None) or msg.text or ""
            html_text = entities_to_html(raw_text, msg.entities)
            protected_html, placeholders = protect_untranslatable(html_text)
            print(f"\n[HTML Перед переводом]:\n{protected_html}")
            translated, key_index = await translator.translate(protected_html, is_html=True)
            translated = restore_untranslatable(translated, placeholders)
        else:
            translated, key_index = await translator.translate(msg.text)
        print(translated)
        
        print(f"\n{'─'*60}")
        print(f"Использован API ключ: #{key_index}")
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
