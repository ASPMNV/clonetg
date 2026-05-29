from typing import Optional, List
from dataclasses import dataclass
from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument
import logging
from src.format_utils import entities_to_html, protect_untranslatable, restore_untranslatable

logger = logging.getLogger(__name__)


@dataclass
class ProcessedPost:
    """Обработанный пост готовый к публикации"""
    text: str
    media: Optional[any] = None
    media_type: Optional[str] = None  # 'photo', 'document', 'video'
    has_spoiler: bool = False
    reply_to: Optional[int] = None
    formatting: Optional[str] = None  # 'html' или 'markdown' или None для entities
    entities: Optional[List] = None  # Telegram entities для форматирования


class PostProcessor:
    def __init__(self, translator, content_filter, handle_reposts: str = "summarize"):
        """
        Args:
            translator: Экземпляр GeminiTranslator
            content_filter: Экземпляр ContentFilter
            handle_reposts: "remove" или "summarize"
        """
        self.translator = translator
        self.content_filter = content_filter
        self.handle_reposts = handle_reposts

    async def process_message(self, message: Message) -> Optional[ProcessedPost]:
        """
        Обработать сообщение из Telegram
        
        Args:
            message: Сообщение Telethon
            
        Returns:
            ProcessedPost или None если сообщение нужно пропустить
        """
        try:
            # Получить оригинальный текст без markdown-форматирования (raw_text)
            text = getattr(message, 'raw_text', None) or message.message or message.text or ""
            
            if not text and not message.media:
                logger.info(f"Сообщение {message.id} пропущено (пустое)")
                return None
            
            # Обработка репоста
            if message.fwd_from:
                if self.handle_reposts == "remove":
                    logger.info(f"Сообщение {message.id} пропущено (репост)")
                    return None
                elif self.handle_reposts == "summarize":
                    if text:
                        summary, _ = await self.translator.summarize_repost(text)
                        if summary:
                            text = summary
                            # Сбросим entities, так как это теперь summary
                            message.entities = None
            
            # Сначала конвертируем в HTML, чтобы не сбить смещения (offsets) для entities
            import re
            translated_text = ""
            formatting = None
            
            if text:
                if getattr(message, "entities", None):
                    # Конвертируем в HTML используя оригинальный текст и entities
                    text = entities_to_html(text, message.entities)
                    formatting = "html"
                    is_html = True
                else:
                    is_html = False
                
                # Теперь удаляем рекламные ссылки (работает и для обычного текста, и для HTML)
                # В raw_text ссылки выглядят как "RU | BigLiquid | Pro Channel" без скобок
                text = re.sub(r'——\s*\n\s*(?:<a[^>]*>)?RU(?:</a>)?.*?Pro Channel(?:</a>)?.*', '', text, flags=re.DOTALL)
                
                if formatting == "html":
                    # Защищаем непереводимые блоки
                    protected_html, placeholders = protect_untranslatable(text)
                    
                    # Переводим HTML
                    translated_html, key_index = await self.translator.translate(protected_html, context=None, preserve_formatting=True, is_html=True)
                    logger.info(f"HTML текст переведен (ключ #{key_index})")
                    
                    # Восстанавливаем защищенные блоки
                    translated_text = restore_untranslatable(translated_html, placeholders)
                else:
                    # Обычный текст без форматирования
                    translated_text, key_index = await self.translator.translate(text, context=None, preserve_formatting=True, is_html=False)
                    logger.info(f"Обычный текст переведен (ключ #{key_index})")
            
            # Обработка медиа
            media = None
            media_type = None
            has_spoiler = False
            
            if message.media:
                if isinstance(message.media, MessageMediaPhoto):
                    media = message.media.photo
                    media_type = "photo"
                    has_spoiler = getattr(message.media, 'spoiler', False)
                    logger.info(f"Обнаружено фото в сообщении {message.id}")
                    
                elif isinstance(message.media, MessageMediaDocument):
                    doc = message.media.document
                    mime_type = doc.mime_type if doc else ""
                    
                    if mime_type.startswith('video/'):
                        media = doc
                        media_type = "video"
                        has_spoiler = getattr(message.media, 'spoiler', False)
                        logger.info(f"Обнаружено видео в сообщении {message.id}")
                    elif mime_type.startswith('image/'):
                        media = doc
                        media_type = "document"
                        logger.info(f"Обнаружен документ-изображение в сообщении {message.id}")
                    else:
                        media = doc
                        media_type = "document"
                        logger.info(f"Обнаружен документ в сообщении {message.id}")
            
            return ProcessedPost(
                text=translated_text,
                media=media,
                media_type=media_type,
                has_spoiler=has_spoiler,
                formatting=formatting,
                entities=None
            )
            
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения {message.id}: {e}", exc_info=True)
            return None
