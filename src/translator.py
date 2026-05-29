from google import genai
from google.genai import types
from typing import List, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class GeminiTranslator:
    def __init__(self, api_keys: List[str], model: str = "gemini-2.5-flash-lite", max_retries: int = 3):
        self.api_keys = api_keys
        self.model_name = model
        self.max_retries = max_retries
        self.current_key_index = 0
        
    def _get_next_key(self) -> tuple[str, int]:
        """Получить следующий API ключ для ротации"""
        key = self.api_keys[self.current_key_index]
        index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key, index

    async def translate(self, text: str, context: Optional[str] = None, preserve_formatting: bool = True, is_html: bool = False) -> tuple[str, int]:
        """
        Перевести текст на тайский язык
        
        Args:
            text: Текст для перевода
            context: Дополнительный контекст (например, описание репоста)
            preserve_formatting: Сохранять форматирование (цитаты, жирный, курсив)
            is_html: Является ли текст HTML-разметкой
            
        Returns:
            Tuple[переведенный текст, индекс использованного ключа]
        """
        if not text.strip():
            return "", -1

        prompt = self._build_prompt(text, context, preserve_formatting, is_html)
        
        for attempt in range(self.max_retries):
            api_key, key_index = self._get_next_key()
            
            try:
                client = genai.Client(api_key=api_key)
                
                # Используем asyncio для неблокирующего вызова
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=self.model_name,
                    contents=prompt
                )
                
                translated_text = response.text.strip()
                logger.info(f"Успешный перевод с ключом #{key_index}")
                return translated_text, key_index
                
            except Exception as e:
                logger.warning(f"Ошибка перевода с ключом #{key_index} (попытка {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt == self.max_retries - 1:
                    logger.error(f"Не удалось перевести текст после {self.max_retries} попыток")
                    raise
                
                # Небольшая задержка перед следующей попыткой
                await asyncio.sleep(1)
        
        return text, -1  # Возвращаем оригинальный текст в случае неудачи

    def _build_prompt(self, text: str, context: Optional[str] = None, preserve_formatting: bool = True, is_html: bool = False) -> str:
        """Построить промпт для перевода"""
        
        if is_html:
            base_prompt = f"""Переведи текст на тайский язык.

ВАЖНЫЕ ПРАВИЛА:
1. Текст содержит HTML-теги (например, <b>, <i>, <a href="...">, <u>, <s>, <tg-spoiler>, <tg-emoji>).
2. СОХРАНЯЙ все HTML-теги строго в тех же местах относительно переведенного текста.
3. НЕ ПЕРЕВОДИ названия тегов и их атрибуты (например, href, emoji-id). Переводи только текст между тегами.
4. В тексте есть специальные маркеры-плейсхолдеры: ___CODE_N___, ___PRE_N___, ___QUOTE_N___. НЕ ПЕРЕВОДИ их и НЕ УДАЛЯЙ, оставь как есть.
5. Сохраняй переносы строк, эмодзи и хештеги.
6. Не добавляй никаких собственных пояснений. В ответе должен быть только переведенный текст с оригинальными тегами.

Текст:
{text}"""
        else:
            base_prompt = f"""Переведи текст на тайский язык.

ВАЖНЫЕ ПРАВИЛА:
1. Сохрани все ссылки [текст](url), эмодзи, хештеги.
2. Сохрани структуру и переносы строк.
3. Не добавляй пояснений.

Текст:
{text}"""

        if context:
            base_prompt = f"Контекст: {context}\n\n" + base_prompt

        return base_prompt

    async def summarize_repost(self, repost_text: str) -> tuple[str, int]:
        """
        Кратко пересказать содержание репоста
        
        Returns:
            Tuple[краткое содержание на тайском, индекс использованного ключа]
        """
        prompt = f"""Кратко перескажи основную суть этого текста одним-двумя предложениями на тайском языке.
Начни с фразы типа "Переслано: " или "Из другого канала: ".

Текст:
{repost_text}"""

        for attempt in range(self.max_retries):
            api_key, key_index = self._get_next_key()
            
            try:
                client = genai.Client(api_key=api_key)
                
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=self.model_name,
                    contents=prompt
                )
                
                summary = response.text.strip()
                logger.info(f"Успешное резюме репоста с ключом #{key_index}")
                return summary, key_index
                
            except Exception as e:
                logger.warning(f"Ошибка резюме с ключом #{key_index}: {e}")
                
                if attempt == self.max_retries - 1:
                    return "", -1
                
                await asyncio.sleep(1)
        
        return "", -1
