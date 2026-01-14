# Используется образ Ubuntu 24.04
FROM ubuntu:24.04

# Скачивание и обновление пакетов
RUN apt-get update \
    && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    zstd \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/venv \
    && /opt/venv/bin/python -m pip install --upgrade pip \
    && curl -fsSL https://ollama.com/install.sh | sh

ENV PATH="/opt/venv/bin:$PATH"

# Создание рабочей директории и установка pip библиотек
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt


# Открытие портов
EXPOSE 8000 11434

# Скрипт при запуске контейнера
RUN echo '#!/bin/bash\n\
# Активация виртуального окружения\n\
source /opt/venv/bin/activate\n\
# Запуск Ollama\n\
ollama serve &\n\
# Ждем запуска Ollama\n\
sleep 5\n\
# Скачиваем модели\n\
ollama pull mxbai-embed-large:latest\n\
ollama pull gemma3:latest\n\
# Запускаем приложение\n\
uvicorn main:app --host 0.0.0.0 --port 8000\n' > /app/start.sh && \
chmod +x /app/start.sh

# Запуск приложения
CMD ["/app/start.sh"]