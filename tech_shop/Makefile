SHELL := /bin/sh

APP_CMD := python -m app.main
TEST_CMD := python -m pytest tests/ -v
COVERAGE_CMD := python -m pytest tests/ --cov=packages --cov=app --cov-report=html
COMPOSE_FILE := infra/docker-compose.yaml
COMPOSE_UP_CMD := docker compose -f $(COMPOSE_FILE) up --build
COMPOSE_DOWN_CMD := docker compose -f $(COMPOSE_FILE) down -v

.PHONY: help setup run test coverage compose-up compose-down check clean

help:
	@printf '%s\n' \
		'help               Показать справку' \
		'setup              Установить зависимости и инициализировать окружение' \
		'run                Запустить приложение Tech Shop' \
		'test               Запустить все тесты (pytest)' \
		'coverage           Сгенерировать отчет о покрытии кода тестами' \
		'compose-up         Собрать и запустить контейнеры (Docker)' \
		'compose-down       Остановить и удалить контейнеры и тома' \
		'check              Полная локальная проверка (тесты + сборка)' \
		'clean              Удалить сгенерированные артефакты (кэш, бд, отчеты)'

setup:
	pip install -r requirements.txt

run:
	$(APP_CMD)

test:
	$(TEST_CMD)

coverage:
	$(COVERAGE_CMD)

compose-up:
	$(COMPOSE_UP_CMD)

compose-down:
	$(COMPOSE_DOWN_CMD)

check: test
	@echo "Все тесты пройдены!"

clean:
	python -c "import os, shutil; [shutil.rmtree(d, ignore_errors=True) for d in ['__pycache__', 'htmlcov', '.pytest_cache', 'build', 'dist']]"
	python -c "import os; [os.remove(f) for f in os.listdir('.') if f.endswith('.pyc') or f.endswith('.db')]"
	python -c "import os; [os.remove(os.path.join(r, f)) for r, _, fs in os.walk('.') for f in fs if f.endswith('.pyc') or '__pycache__' in r]"