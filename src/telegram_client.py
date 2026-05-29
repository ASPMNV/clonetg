from telethon import TelegramClient, events
from telethon.tl.types import InputMessagesFilterEmpty
from typing import Optional, List
import logging
import os
import json
from pathlib import Path
from src.post_processor import ProcessedPost

logger = logging.getLogger(__name__)


class TelegramChannelBot:
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        phone: str,
        session_name: str = "translator_bot",
        device_model: str = "Desktop",
        system_version: str = "Windows 10",
        app_version: str = "4.8.1 x64",
        lang_code: str = "en",
        system_lang_code: str = "en-US"
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_name = session_name
        self.device_model = device_model
        self.system_version = system_version
        self.app_version = app_version
        self.lang_code = lang_code
        self.system_lang_code = system_lang_code
        self.client: Optional[TelegramClient] = None

    async def start(self):
        """
        Запустить клиент Telegram
        
        Telethon автоматически:
        - Создает файл сессии при первой авторизации
        - Использует существующий файл сессии для последующих запусков
        - Сохраняет сессию в файл {session_name}.session
        """
        session_file = f"{self.session_name}.session"
        session_exists = os.path.exists(session_file)
        
        if session_exists:
            logger.info(f"Найден файл сессии: {session_file}")
            logger.info("Попытка авторизации через сохраненную сессию...")
        else:
            logger.info(f"Файл сессии не найден: {session_file}")
            logger.info("Будет выполнена новая авторизация...")
        
        # Создать клиент с указанием файла сессии и параметров устройства
        self.client = TelegramClient(
            self.session_name,
            self.api_id,
            self.api_hash,
            device_model=self.device_model,
            system_version=self.system_version,
            app_version=self.app_version,
            lang_code=self.lang_code,
            system_lang_code=self.system_lang_code
        )
        
        # Запустить клиент (автоматически использует сессию если она есть)
        await self.client.start(phone=self.phone)
        
        # Проверка авторизации
        me = await self.client.get_me()
        logger.info(f"✅ Авторизован как: {me.first_name} (@{me.username})")
        logger.info(f"   Устройство: {self.device_model}")
        logger.info(f"   Версия: {self.app_version}")
        
        if not session_exists:
            logger.info(f"✅ Сессия сохранена в файл: {session_file}")
            logger.info("При следующем запуске авторизация не потребуется")
        else:
            logger.info("✅ Использована существующая сессия")

    async def stop(self):
        """Остановить клиент"""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram клиент остановлен")

    async def get_new_messages(
        self,
        channel: str,
        limit: int = 10,
        min_id: int = 0
    ) -> List:
        """
        Получить новые сообщения из канала
        
        Args:
            channel: ID или username канала
            limit: Максимальное количество сообщений
            min_id: ID последнего обработанного сообщения
            
        Returns:
            Список сообщений
        """
        try:
            messages = await self.client.get_messages(
                channel,
                limit=limit,
                min_id=min_id,
                reverse=True  # От старых к новым
            )
            
            logger.info(f"Получено {len(messages)} новых сообщений из {channel}")
            return messages
            
        except Exception as e:
            logger.error(f"Ошибка получения сообщений из {channel}: {e}")
            return []

    async def send_post(
        self,
        channel: str,
        post: ProcessedPost
    ) -> Optional[int]:
        """
        Отправить обработанный пост в канал
        
        Args:
            channel: ID или username целевого канала
            post: Обработанный пост
            
        Returns:
            ID отправленного сообщения или None
        """
        try:
            # Определить parse_mode и formatting_entities
            parse_mode = post.formatting if post.formatting else None
            formatting_entities = post.entities if post.entities else None
            
            # Отправка с медиа
            if post.media:
                if post.media_type == "photo":
                    sent_message = await self.client.send_file(
                        channel,
                        post.media,
                        caption=post.text,
                        spoiler=post.has_spoiler,
                        parse_mode=parse_mode,
                        formatting_entities=formatting_entities
                    )
                elif post.media_type in ["video", "document"]:
                    sent_message = await self.client.send_file(
                        channel,
                        post.media,
                        caption=post.text,
                        spoiler=post.has_spoiler,
                        parse_mode=parse_mode,
                        formatting_entities=formatting_entities
                    )
                else:
                    # Неизвестный тип медиа, отправляем только текст
                    sent_message = await self.client.send_message(
                        channel,
                        post.text,
                        parse_mode=parse_mode,
                        formatting_entities=formatting_entities
                    )
            else:
                # Отправка только текста
                sent_message = await self.client.send_message(
                    channel,
                    post.text,
                    parse_mode=parse_mode,
                    formatting_entities=formatting_entities
                )
            
            logger.info(f"Пост отправлен в {channel}, ID: {sent_message.id}")
            return sent_message.id
            
        except Exception as e:
            logger.error(f"Ошибка отправки поста в {channel}: {e}", exc_info=True)
            return None

    async def get_channel_info(self, channel: str):
        """Получить информацию о канале"""
        try:
            entity = await self.client.get_entity(channel)
            logger.info(f"Канал: {entity.title}, ID: {entity.id}")
            return entity
        except Exception as e:
            logger.error(f"Ошибка получения информации о канале {channel}: {e}")
            return None

    async def download_media(self, message, file_path: str = None):
        """
        Скачать медиа из сообщения
        
        Args:
            message: Сообщение с медиа
            file_path: Путь для сохранения (опционально)
            
        Returns:
            Путь к скачанному файлу
        """
        try:
            path = await self.client.download_media(message, file=file_path)
            logger.info(f"Медиа скачано: {path}")
            return path
        except Exception as e:
            logger.error(f"Ошибка скачивания медиа: {e}")
            return None

    def add_event_handler(self, handler, event_type=events.NewMessage):
        """
        Добавить обработчик событий
        
        Args:
            handler: Функция-обработчик
            event_type: Тип события
        """
        if self.client:
            self.client.add_event_handler(handler, event_type)
            logger.info(f"Добавлен обработчик событий: {handler.__name__}")
