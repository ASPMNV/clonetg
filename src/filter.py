import re
from typing import List, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import logging

logger = logging.getLogger(__name__)


class ContentFilter:
    def __init__(
        self,
        spam_keywords: List[str],
        allowed_domains: List[str],
        remove_referral_params: bool = True
    ):
        self.spam_keywords = [kw.lower() for kw in spam_keywords]
        self.allowed_domains = allowed_domains
        self.remove_referral_params = remove_referral_params
        
        # Параметры, которые обычно используются для реферальных ссылок
        self.referral_params = {
            'ref', 'referral', 'utm_source', 'utm_medium', 'utm_campaign',
            'utm_term', 'utm_content', 'affiliate', 'aff', 'partner',
            'promo', 'promocode', 'discount', 'coupon'
        }

    def is_spam(self, text: str) -> bool:
        """
        Проверить, является ли пост рекламным спамом
        
        Args:
            text: Текст поста
            
        Returns:
            True если пост является спамом
        """
        if not text:
            return False
            
        text_lower = text.lower()
        
        # Проверка на ключевые слова спама
        spam_count = sum(1 for keyword in self.spam_keywords if keyword in text_lower)
        
        # Если найдено 2 или больше спам-слов, считаем спамом
        if spam_count >= 2:
            logger.info(f"Пост отфильтрован как спам (найдено {spam_count} ключевых слов)")
            return True
        
        # Проверка на чрезмерное количество ссылок (больше 5)
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if len(urls) > 5:
            logger.info(f"Пост отфильтрован как спам (слишком много ссылок: {len(urls)})")
            return True
        
        # Проверка на чрезмерное использование эмодзи (больше 30% текста)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # эмодзи эмоций
            "\U0001F300-\U0001F5FF"  # символы и пиктограммы
            "\U0001F680-\U0001F6FF"  # транспорт и символы карты
            "\U0001F1E0-\U0001F1FF"  # флаги
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        emoji_count = len(emoji_pattern.findall(text))
        text_length = len(text.strip())
        
        if text_length > 0 and emoji_count / text_length > 0.3:
            logger.info(f"Пост отфильтрован как спам (слишком много эмодзи)")
            return True
        
        return False

    def filter_links(self, text: str) -> str:
        """
        Фильтровать и очищать ссылки в тексте
        
        Args:
            text: Текст с возможными ссылками
            
        Returns:
            Текст с отфильтрованными ссылками
        """
        if not text:
            return text
        
        # Найти все URL в тексте
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        
        def replace_url(match):
            url = match.group(0)
            cleaned_url = self._clean_url(url)
            
            # Если URL не прошел фильтрацию, удаляем его
            if cleaned_url is None:
                logger.info(f"Удалена ссылка: {url}")
                return ""
            
            return cleaned_url
        
        filtered_text = re.sub(url_pattern, replace_url, text)
        
        # Убрать лишние пробелы
        filtered_text = re.sub(r'\s+', ' ', filtered_text).strip()
        
        return filtered_text

    def _clean_url(self, url: str) -> Optional[str]:
        """
        Очистить URL от реферальных параметров и проверить домен
        
        Args:
            url: URL для очистки
            
        Returns:
            Очищенный URL или None если URL нужно удалить
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Проверка разрешенных доменов - если список пустой, разрешаем все
            # Если список не пустой, проверяем что домен в списке
            if self.allowed_domains and len(self.allowed_domains) > 0:
                # Если в списке есть "*", разрешаем все домены
                if "*" not in self.allowed_domains:
                    domain_allowed = any(
                        allowed in domain for allowed in self.allowed_domains
                    )
                    if not domain_allowed:
                        logger.debug(f"Домен {domain} не в списке разрешенных")
                        # Не удаляем ссылку, просто логируем
                        # return None
            
            # Удаление реферальных параметров
            if self.remove_referral_params:
                query_params = parse_qs(parsed.query)
                
                # Фильтруем параметры
                cleaned_params = {
                    k: v for k, v in query_params.items()
                    if k.lower() not in self.referral_params
                }
                
                # Собираем URL обратно
                new_query = urlencode(cleaned_params, doseq=True)
                cleaned_url = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    new_query,
                    parsed.fragment
                ))
                
                return cleaned_url
            
            return url
            
        except Exception as e:
            logger.warning(f"Ошибка при обработке URL {url}: {e}")
            return None

    def clean_text(self, text: str) -> str:
        """
        Общая очистка текста
        
        Args:
            text: Исходный текст
            
        Returns:
            Очищенный текст
        """
        if not text:
            return text
        
        # Фильтрация ссылок
        text = self.filter_links(text)
        
        # Удаление множественных переносов строк
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Удаление лишних пробелов
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
