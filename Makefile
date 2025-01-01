POETRY = $(shell which poetry)
POETRY_OPTION = --no-interaction --no-ansi
POETRY_RUN = ${POETRY} run ${POETRY_OPTION}

MYPY_OPTIONS = --install-types --non-interactive --ignore-missing-imports

lint: 
	${POETRY_RUN} mypy ${MYPY_OPTIONS} -p functions
	${POETRY_RUN} ruff check . --fix
format: 
	${POETRY_RUN} ruff format .

all: lint format

.PHONY: lint format all