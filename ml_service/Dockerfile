# Используйте официальный Python образ как основу
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт, на котором будет работать приложение
EXPOSE 8000

# Команда для запуска приложения с помощью uvicorn
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]
