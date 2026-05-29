import json
import logging
import traceback
import urllib.request
import urllib.error
from src.config import Config

logger = logging.getLogger(__name__)

def send_crash_alert(config: Config, error: Exception):
    """Отправляет уведомление об ошибке в Telegram"""
    if not hasattr(config, "alerts") or not config.alerts.enabled:
        return
        
    if not config.alerts.bot_token or not config.alerts.chat_id:
        logger.warning("Алерты включены, но bot_token или chat_id не настроены.")
        return
        
    tb_str = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    
    if len(tb_str) > 3800:
        tb_str = tb_str[-3800:]
        
    message = f"🚨 <b>КРИТИЧЕСКАЯ ОШИБКА БОТА</b> 🚨\n\nБот остановлен из-за ошибки:\n<pre>{tb_str}</pre>"
    
    url = f"https://api.telegram.org/bot{config.alerts.bot_token}/sendMessage"
    payload = {
        "chat_id": config.alerts.chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                logger.info("Алерт об ошибке успешно отправлен.")
            else:
                logger.error(f"Не удалось отправить алерт. Код ответа: {response.getcode()}")
    except Exception as e:
        logger.error(f"Ошибка при отправке алерта в Telegram: {e}")

def send_startup_alert(config: Config):
    """Отправляет уведомление о запуске бота"""
    if not hasattr(config, "alerts") or not config.alerts.enabled:
        return
        
    if not config.alerts.bot_token or not config.alerts.chat_id:
        return
        
    # Пытаемся получить IP адрес
    ip_addr = "Неизвестно"
    try:
        req = urllib.request.Request("https://api.ipify.org?format=json", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.getcode() == 200:
                ip_data = json.loads(response.read().decode('utf-8'))
                ip_addr = ip_data.get("ip", "Неизвестно")
    except Exception:
        pass
        
    mode = "Реальное время (Events)" if config.processing.realtime else f"Опрос каждые {config.processing.check_interval}с"
    
    message = (
        f"✅ <b>БОТ УСПЕШНО ЗАПУЩЕН</b> ✅\n\n"
        f"📡 <b>Источник:</b> {config.telegram.source_channel}\n"
        f"📤 <b>Цель:</b> {config.telegram.target_channel}\n"
        f"🤖 <b>Модель:</b> {config.gemini.model}\n"
        f"⚙️ <b>Режим:</b> {mode}\n"
        f"🌐 <b>IP сервера:</b> {ip_addr}\n"
    )
    
    url = f"https://api.telegram.org/bot{config.alerts.bot_token}/sendMessage"
    payload = {
        "chat_id": config.alerts.chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                logger.info("Уведомление о запуске успешно отправлено.")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления о запуске: {e}")
