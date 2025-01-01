POETRY = $(shell which poetry)
POETRY_OPTION = --no-interaction --no-ansi
POETRY_RUN = ${POETRY} run ${POETRY_OPTION}

MYPY_OPTIONS = --install-types --non-interactive --ignore-missing-imports

TF_DIR = ./terraform
TF = terraform

lint: 
	${POETRY_RUN} mypy ${MYPY_OPTIONS} -p functions
	${POETRY_RUN} ruff check . --fix
format: 
	${POETRY_RUN} ruff format .

all: lint format

tf-init:
	cd ${TF_DIR} && ${TF} init
tf-plan:
	cd ${TF_DIR} && ${TF} plan
tf-apply:
	cd ${TF_DIR} && ${TF} apply
tf-destroy:
	cd ${TF_DIR} && ${TF} destroy
tf-fmt:
	cd ${TF_DIR} && ${TF} fmt

.PHONY: lint format all tf-init tf-plan tf-apply tf-destroy tf-fmt