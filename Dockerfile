# Используем образ Python
FROM python:3.12

# Установка рабочей директории
WORKDIR /app

# Пробуем ENV для корректной работы с модулями
ENV PYTHONPATH=/app/src

# Копируем файл зависимостей
COPY ./requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY ./src ./src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]