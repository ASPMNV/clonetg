#!/bin/bash
# Скрипт для установки systemd сервиса (Linux)

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Установка Telegram Channel Translator как systemd сервис ===${NC}"
echo

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Ошибка: Запустите скрипт с sudo${NC}"
    exit 1
fi

# Получить текущую директорию
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Директория проекта: ${PROJECT_DIR}${NC}"

# Получить пользователя
read -p "Введите имя пользователя для запуска сервиса (по умолчанию: $SUDO_USER): " SERVICE_USER
SERVICE_USER=${SERVICE_USER:-$SUDO_USER}

echo -e "${YELLOW}Пользователь: ${SERVICE_USER}${NC}"

# Найти Python
PYTHON_PATH=$(which python3)
echo -e "${YELLOW}Python: ${PYTHON_PATH}${NC}"

# Создать systemd unit файл
SERVICE_FILE="/etc/systemd/system/telegram-translator.service"

echo -e "${GREEN}Создание systemd unit файла...${NC}"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Telegram Channel Translator Bot
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PYTHON_PATH} ${PROJECT_DIR}/main.py
Restart=always
RestartSec=10
StandardOutput=append:${PROJECT_DIR}/logs/service.log
StandardError=append:${PROJECT_DIR}/logs/service.log

# Переменные окружения (опционально)
# Environment="TELEGRAM_API_ID=12345678"
# Environment="TELEGRAM_API_HASH=your_hash"

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Файл сервиса создан: ${SERVICE_FILE}${NC}"

# Создать директорию для логов если не существует
mkdir -p "${PROJECT_DIR}/logs"
chown ${SERVICE_USER}:${SERVICE_USER} "${PROJECT_DIR}/logs"

# Перезагрузить systemd
echo -e "${GREEN}Перезагрузка systemd...${NC}"
systemctl daemon-reload

# Включить автозапуск
echo -e "${GREEN}Включение автозапуска...${NC}"
systemctl enable telegram-translator

echo
echo -e "${GREEN}=== Установка завершена! ===${NC}"
echo
echo "Доступные команды:"
echo -e "  ${YELLOW}sudo systemctl start telegram-translator${NC}   - Запустить сервис"
echo -e "  ${YELLOW}sudo systemctl stop telegram-translator${NC}    - Остановить сервис"
echo -e "  ${YELLOW}sudo systemctl restart telegram-translator${NC} - Перезапустить сервис"
echo -e "  ${YELLOW}sudo systemctl status telegram-translator${NC}  - Статус сервиса"
echo -e "  ${YELLOW}journalctl -u telegram-translator -f${NC}       - Просмотр логов"
echo
echo -e "${YELLOW}Для запуска сервиса выполните:${NC}"
echo -e "  ${GREEN}sudo systemctl start telegram-translator${NC}"
