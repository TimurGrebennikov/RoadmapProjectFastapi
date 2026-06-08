# ===============================
# Настройки проекта
# ===============================
# Каталоги с кодом/тестами
PY_SRCS=src
# Порог для Radon:
# - запрещаем функции со сложностью CC уровней E/F
# - минимальный Maintainability Index (MI)
RADON_MIN_MI=65

# ===============================
# Служебные цели
# ===============================

.PHONY: help install lint fmt type security cc mi hal raw check

help:
	@echo "Available targets:"
	@echo " lint     - ruff check (with auto-fix)"
	@echo " fmt      - ruff format"
	@echo " type     - mypy (type checking)"
	@echo " security - bandit (security scan)"
	@echo " cc       - radon cc (cyclomatic complexity)"
	@echo " mi       - radon mi (maintainability index)"
	@echo " hal      - radon hal (Halstead metrics)"
	@echo " raw      - radon raw (SLOC, LLOC, comments)"
	@echo " check    - run all checks (ruff+mypy+bandit+radon)"

# ===============================
# Ruff: линт и форматирование
# ===============================
lint:
	poetry run ruff check $(PY_SRCS) --fix

fmt:
	poetry run ruff format $(PY_SRCS)

# ===============================
# Mypy: проверка типов
# ===============================
type:
	poetry run mypy $(PY_SRCS)

# ===============================
# Bandit: анализ безопасности
# ===============================
security:
	poetry run bandit -r src -lll -x .venv,venv,build,dist,migrations

# ===============================
# Radon: метрики
# ===============================
# Цикломатическая сложность: подробный вывод (-s), среднее (-a)
cc:
	poetry run radon cc -s -a $(PY_SRCS)
	@echo "✅ Radon CC: проверка сложности выполнена"

# Индекс поддерживаемости
mi:
	poetry run radon mi $(PY_SRCS)

# Метрика халстеда
hal:
	poetry run radon hal $(PY_SRCS)

# Метрика Raw
raw:
	poetry run radon raw $(PY_SRCS)

# ===============================
# Комплексные цели
# ===============================
check: lint fmt type security cc mi hal raw