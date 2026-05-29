import asyncio
import logging
from typing import Optional
from telethon import events
from src.config import Config
from src.database import Database
from src.telegram_client import TelegramChannelBot
from src.translator import GeminiTranslator
from src.filter import ContentFilter
from src.post_processor import PostProcessor

logger = logging.getLogger(__name__)


class BotService:
    def __init__(self, config: Config):
        self.config = config
        self.db = Database()
        
        # Инициализация компонентов
        self.telegram_bot = TelegramChannelBot(
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
        
        self.translator = GeminiTranslator(
            api_keys=config.gemini.api_keys,
            model=config.gemini.model,
            max_retries=config.gemini.max_retries
        )
        
        self.content_filter = ContentFilter(
            spam_keywords=config.filters.spam_keywords,
            allowed_domains=config.filters.allowed_domains,
            remove_referral_params=config.filters.remove_referral_params
        )
        
        self.post_processor = PostProcessor(
            translator=self.translator,
            content_filter=self.content_filter,
            handle_reposts=config.filters.handle_reposts
        )
        
        self.last_message_id = 0
        self.is_running = False

    async def start(self):
        """Запустить сервис"""
        logger.info("Запуск сервиса...")
        
        # Инициализация базы данных
        await self.db.init()
        logger.info("База данных инициализирована")
        
        # Запуск Telegram клиента
        await self.telegram_bot.start()
        
        # Проверка доступа к каналам
        self.source_info = await self.telegram_bot.get_channel_info(
            self.config.telegram.source_channel
        )
        target_info = await self.telegram_bot.get_channel_info(
            self.config.telegram.target_channel
        )
        
        if not self.source_info or not target_info:
            logger.error("Не удалось получить доступ к каналам")
            return
        
        logger.info(f"Канал-источник: {self.source_info.title}")
        logger.info(f"Целевой канал: {target_info.title}")
        
        self.is_running = True
        logger.info("Сервис успешно запущен")

    async def stop(self):
        """Остановить сервис"""
        logger.info("Остановка сервиса...")
        self.is_running = False
        await self.telegram_bot.stop()
        logger.info("Сервис остановлен")

    async def process_new_posts(self):
        """Обработать новые посты из канала-источника"""
        try:
            # Получить новые сообщения
            messages = await self.telegram_bot.get_new_messages(
                channel=self.config.telegram.source_channel,
                limit=self.config.processing.batch_size,
                min_id=self.last_message_id
            )
            
            if not messages:
                logger.debug("Новых сообщений нет")
                return
            
            logger.info(f"Обработка {len(messages)} новых сообщений")
            
            for message in messages:
                # Обновить ID последнего сообщения
                if message.id > self.last_message_id:
                    self.last_message_id = message.id
                
                # Проверить, не обработано ли уже
                if await self.db.is_processed(
                    self.config.telegram.source_channel,
                    message.id
                ):
                    logger.debug(f"Сообщение {message.id} уже обработано")
                    continue
                
                # Обработать сообщение
                try:
                    processed_post = await self.post_processor.process_message(message)
                    
                    if processed_post is None:
                        # Сообщение отфильтровано
                        await self.db.mark_processed(
                            self.config.telegram.source_channel,
                            message.id,
                            status="filtered"
                        )
                        continue
                    
                    # Отправить в целевой канал
                    target_message_id = await self.telegram_bot.send_post(
                        self.config.telegram.target_channel,
                        processed_post
                    )
                    
                    if target_message_id:
                        await self.db.mark_processed(
                            self.config.telegram.source_channel,
                            message.id,
                            target_message_id=target_message_id,
                            status="success"
                        )
                        logger.info(f"Сообщение {message.id} успешно обработано и отправлено")
                    else:
                        await self.db.mark_processed(
                            self.config.telegram.source_channel,
                            message.id,
                            status="error",
                            error_message="Не удалось отправить в целевой канал"
                        )
                    
                    # Небольшая задержка между сообщениями
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки сообщения {message.id}: {e}", exc_info=True)
                    await self.db.mark_processed(
                        self.config.telegram.source_channel,
                        message.id,
                        status="error",
                        error_message=str(e)
                    )
                    
        except Exception as e:
            logger.error(f"Ошибка в process_new_posts: {e}", exc_info=True)

    async def run(self):
        """Основной цикл работы сервиса"""
        await self.start()
        
        try:
            if self.config.processing.realtime:
                # Режим реального времени - подписка на события
                logger.info("🔥 Режим реального времени активирован")
                
                @self.telegram_bot.client.on(events.NewMessage(chats=[self.source_info.id]))
                async def handler(event):
                    logger.info(f"📨 Новое сообщение: {event.message.id}")
                    await self.process_single_message(event.message)
                
                # Держать соединение
                await self.telegram_bot.client.run_until_disconnected()
            else:
                # Режим опроса
                logger.info(f"⏰ Режим опроса: каждые {self.config.processing.check_interval} сек")
                while self.is_running:
                    await self.process_new_posts()
                    await asyncio.sleep(self.config.processing.check_interval)
                    
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки")
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}", exc_info=True)
        finally:
            await self.stop()
    
    async def process_single_message(self, message):
        """Обработать одно сообщение (для режима реального времени)"""
        try:
            # Проверить, не обработано ли уже
            if await self.db.is_processed(
                self.config.telegram.source_channel,
                message.id
            ):
                logger.debug(f"Сообщение {message.id} уже обработано")
                return
            
            # Обработать сообщение
            processed_post = await self.post_processor.process_message(message)
            
            if processed_post is None:
                # Сообщение отфильтровано
                await self.db.mark_processed(
                    self.config.telegram.source_channel,
                    message.id,
                    status="filtered"
                )
                return
            
            # Отправить в целевой канал
            target_message_id = await self.telegram_bot.send_post(
                self.config.telegram.target_channel,
                processed_post
            )
            
            if target_message_id:
                await self.db.mark_processed(
                    self.config.telegram.source_channel,
                    message.id,
                    target_message_id=target_message_id,
                    status="success"
                )
                logger.info(f"✅ Сообщение {message.id} обработано и отправлено")
            else:
                await self.db.mark_processed(
                    self.config.telegram.source_channel,
                    message.id,
                    status="error",
                    error_message="Не удалось отправить в целевой канал"
                )
                
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения {message.id}: {e}", exc_info=True)
            await self.db.mark_processed(
                self.config.telegram.source_channel,
                message.id,
                status="error",
                error_message=str(e)
            )
