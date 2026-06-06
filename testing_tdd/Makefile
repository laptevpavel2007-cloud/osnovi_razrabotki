ifeq ($(OS),Windows_NT)
    PYTHON := .venv/Scripts/python.exe
    PIP := .venv/Scripts/pip.exe
    PYTEST := .venv/Scripts/pytest.exe
    MYPY := .venv/Scripts/mypy.exe
    RUFF := .venv/Scripts/ruff.exe
    SYS_PYTHON := py
else
    PYTHON := .venv/bin/python
    PIP := .venv/bin/pip
    PYTEST := .venv/bin/pytest
    MYPY := .venv/bin/mypy
    RUFF := .venv/bin/ruff
    SYS_PYTHON := python3
endif

VENV := .venv

.PHONY: all venv install check-requirements typecheck format lint test check clean

all: check

$(VENV):
	$(SYS_PYTHON) -m venv $(VENV)

install: $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .

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

check: install check-requirements typecheck lint test
	@echo "All checks passed!"

clean:
	$(SYS_PYTHON) scripts/clean.py