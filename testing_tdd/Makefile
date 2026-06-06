PYTHON := .venv/bin/python
PIP := .venv/bin/pip
PYTEST := .venv/bin/pytest
MYPY := .venv/bin/mypy
RUFF := .venv/bin/ruff
VENV := .venv

.PHONY: all venv install check-requirements typecheck format lint test check clean

all: check

$(VENV):
	python3 -m venv $(VENV)

install: $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .  # Устанавливаем пакет ndfl, чтобы pytest мог его импортировать

check-requirements: install
	$(PYTHON) scripts/check_deps.py

typecheck: install
	$(MYPY) src/ tests/

format: install
	$(RUFF) format src/ tests/

lint: install
	$(RUFF) check src/ tests/

test: install
	$(PYTEST) tests/ -v

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete