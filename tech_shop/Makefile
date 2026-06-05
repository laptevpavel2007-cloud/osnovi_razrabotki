# Интерпретатор и оболочка выбираются по ОС:
#   Windows -> py (лаунчер Python), оболочка cmd.exe (по умолчанию)
#   WSL/Linux/macOS -> python3, оболочка /bin/sh
ifeq ($(OS),Windows_NT)
    PYTHON ?= py
else
    PYTHON ?= python3
    SHELL := /bin/sh
endif

APP_CMD := $(PYTHON) -m app.main
TEST_CMD := $(PYTHON) -m pytest tests/ -v
COVERAGE_CMD := $(PYTHON) -m pytest tests/ --cov=packages --cov=app --cov-report=html
COMPOSE_FILE := infra/docker-compose.yaml
COMPOSE_UP_CMD := docker compose -f $(COMPOSE_FILE) up --build
COMPOSE_DOWN_CMD := docker compose -f $(COMPOSE_FILE) down -v

.PHONY: help setup run test coverage compose-up compose-down check clean build-lib install-lib-local

help:
	@echo help          Показать справку
	@echo setup         Установить зависимости
	@echo run           Запустить приложение Tech Shop
	@echo test          Запустить все тесты pytest
	@echo coverage      Отчет о покрытии кода тестами
	@echo compose-up    Собрать и запустить контейнеры Docker
	@echo compose-down  Остановить и удалить контейнеры и тома
	@echo check         Полная локальная проверка тесты
	@echo clean         Удалить сгенерированные артефакты

setup:
	$(PYTHON) -m pip install -r requirements.txt

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
	@echo Все тесты пройдены!

clean:
	$(PYTHON) -c "import shutil; [shutil.rmtree(d, ignore_errors=True) for d in ['__pycache__','htmlcov','.pytest_cache','build','dist']]"
	$(PYTHON) -c "import os; [os.remove(os.path.join(r,f)) for r,_,fs in os.walk('.') for f in fs if f.endswith('.pyc') or f.endswith('.db')]"

build-lib:
	cd packages/core && $(PYTHON) -m build

install-lib-local:
	$(PYTHON) -m pip install -e packages/core