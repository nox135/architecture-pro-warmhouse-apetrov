# Используем базовый образ Python
FROM python:3.8-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы приложения в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8081

# Определяем команду для запуска приложения
CMD ["python", "temperature.py"]