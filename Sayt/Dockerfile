# Используем образ Python
FROM python:3.12

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем зависимости и устанавливаем их
RUN pip install flask

# Копируем все файлы проекта в рабочую директорию контейнера
COPY app.py ./
COPY templates/ ./templates/

EXPOSE 5000
# Указываем команду для запуска приложения
CMD ["python", "app.py"]
