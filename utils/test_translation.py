#!/usr/bin/env python3
"""
Утилита для тестирования перевода
"""

import asyncio
import sys
import os

# Добавить родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.translator import GeminiTranslator


async def test_translation():
    """Тестирование перевода"""
    print("=" * 60)
    print("Тест перевода через Gemini API")
    print("=" * 60)
    print()
    
    # Загрузить конфигурацию
    try:
        config = Config.load("config.json")
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        print("Убедитесь, что файл config.json существует")
        return
    
    # Создать переводчик (Gemini 3.5 Flash)
    translator = GeminiTranslator(
        api_keys=config.gemini.api_keys,
        model=config.gemini.model
    )
    
    # Тестовые тексты
    test_texts = [
        "Привет! Как дела?",
        "<b>Это тестовое сообщение</b> для проверки <i>перевода</i> на тайский язык.",
        "🎉 Отличные новости! Мы запустили <a href='https://example.com'>новый продукт</a>.",
        "Подписывайтесь на наш канал для получения актуальной информации.\n\n<blockquote>Это важная цитата, которую не нужно переводить!</blockquote>",
        "Код: <code>import os</code>"
    ]
    
    print(f"Тестирование с {len(config.gemini.api_keys)} API ключами")
    print(f"Модель: {config.gemini.model}")
    print()
    
    for i, text in enumerate(test_texts, 1):
        print(f"Тест {i}/{len(test_texts)}")
        print(f"Оригинал: {text}")
        
        try:
            from src.format_utils import protect_untranslatable, restore_untranslatable
            protected_html, placeholders = protect_untranslatable(text)
            
            translated, key_index = await translator.translate(protected_html, is_html=True)
            translated = restore_untranslatable(translated, placeholders)
            
            print(f"Перевод: {translated}")
            print(f"Использован ключ: #{key_index}")
            print("✅ Успешно")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        print("-" * 60)
        print()
        
        # Небольшая задержка между запросами
        await asyncio.sleep(1)
    
    print("Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(test_translation())
