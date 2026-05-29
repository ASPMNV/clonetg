import re
from typing import Dict, Tuple, List
from telethon.extensions.html import unparse

def entities_to_html(text: str, entities: List) -> str:
    """
    Конвертирует текст с Telegram entities в HTML-строку.
    Использует встроенную утилиту Telethon.
    """
    if not text:
        return ""
    if not entities:
        return text
    
    return unparse(text, entities)

def protect_untranslatable(html: str) -> Tuple[str, Dict[str, str]]:
    """
    Заменяет непереводимые блоки (код, цитаты) на плейсхолдеры.
    
    Args:
        html: HTML-строка
        
    Returns:
        Tuple[HTML с плейсхолдерами, словарь плейсхолдеров]
    """
    placeholders = {}
    counter = 0
    
    # Регулярные выражения для поиска блоков
    # Используем нежадный поиск (.*?)
    patterns = [
        (r'(<pre.*?>.*?</pre>)', '___PRE_{i}___'),
        (r'(<code.*?>.*?</code>)', '___CODE_{i}___'),
        (r'(<blockquote.*?>.*?</blockquote>)', '___QUOTE_{i}___')
    ]
    
    protected_html = html
    
    for pattern, placeholder_format in patterns:
        matches = re.finditer(pattern, protected_html, flags=re.DOTALL | re.IGNORECASE)
        # Обрабатываем с конца, чтобы не сбить индексы при замене
        for match in reversed(list(matches)):
            original_text = match.group(1)
            placeholder = placeholder_format.format(i=counter)
            placeholders[placeholder] = original_text
            
            # Заменяем фрагмент
            start, end = match.span(1)
            protected_html = protected_html[:start] + placeholder + protected_html[end:]
            counter += 1
            
    return protected_html, placeholders

def restore_untranslatable(html: str, placeholders: Dict[str, str]) -> str:
    """
    Восстанавливает непереводимые блоки из плейсхолдеров.
    
    Args:
        html: HTML-строка с плейсхолдерами
        placeholders: Словарь плейсхолдеров
        
    Returns:
        HTML-строка с оригинальными блоками
    """
    restored_html = html
    for placeholder, original_text in placeholders.items():
        restored_html = restored_html.replace(placeholder, original_text)
    return restored_html
