FROM python:3.9

WORKDIR /app

# Копируем все файлы в контейнер
COPY . /app

# Устанавливаем зависимости из requirements.txt
# When installing packages with pip in a Dockerfile,
# use the --no-cache-dir option. This tells pip not to use a 
# cache when installing packages, which ensures that the 
# latest version of the package is always used
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт 5000
EXPOSE 5000

# Запускаем Flask-приложение
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
