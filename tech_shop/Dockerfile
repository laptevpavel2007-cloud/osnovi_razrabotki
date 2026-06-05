FROM python:3.14-slim

LABEL maintainer="Laptevpavel2007@gmail.com"
LABEL description="Tech Shop"

RUN apt-get update && apt-get install -y \
    python3-tk tk locales \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG=ru_RU.UTF-8
ENV LANGUAGE=ru_RU:ru
ENV LC_ALL=ru_RU.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY packages/ ./packages/
COPY app/ ./app/
COPY data/ ./data/
COPY tests/ ./tests/
COPY scripts/ ./scripts/

ENV APP_ENV=production
ENV DB_PATH=/app/data/store.db
ENV DATA_DIR=/app/data
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app/data

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sqlite3; sqlite3.connect('/app/data/store.db').execute('SELECT 1')" || exit 1

EXPOSE 8080

CMD ["python", "-m", "app.main"]