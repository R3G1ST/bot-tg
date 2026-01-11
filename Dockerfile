FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir aiogram sqlalchemy asyncpg requests python-dotenv
CMD ["python", "bot/main.py"]
