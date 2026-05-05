FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poety install --only main --no-root

COPY src/app ./app

#poetry run uvicorn src.app.main:app --port=8002 --host=127.0.0.1
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]