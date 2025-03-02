POETRY = $(shell which poetry)
POETRY_OPTION = --no-interaction --no-ansi
POETRY_RUN = ${POETRY} run ${POETRY_OPTION}

# ==============================
# Python
# ==============================	

MYPY_OPTIONS = --install-types --non-interactive --ignore-missing-imports

lint: 
	${POETRY_RUN} mypy ${MYPY_OPTIONS} -p functions
	${POETRY_RUN} ruff check . --extend-select I --fix

format: 
	${POETRY_RUN} ruff format .

test:
	${POETRY_RUN} pytest tests/

# ==============================
# dbt
# ==============================

DBT = cd dbt && DBT_PROFILES_DIR=~/.dbt ${POETRY_RUN} dbt

dbt-run-dev:
	set -a && source .env.dev && set +a && $(DBT) run --target dev

dbt-run-prod:
	set -a && source .env.prod && set +a && $(DBT) run --target prod

dbt-test-dev:
	set -a && source .env.dev && set +a && $(DBT) test --target dev

dbt-test-prod:
	set -a && source .env.prod && set +a && $(DBT) test --target prod

dbt-freshness-dev:
	set -a && source .env.dev && set +a && $(DBT) source freshness --target dev

dbt-freshness-prod:
	set -a && source .env.prod && set +a && $(DBT) source freshness --target prod

sql-lint:
	${POETRY_RUN} sqlfluff lint dbt/models/ --config dbt/.sqlfluff

sql-fix:
	${POETRY_RUN} sqlfluff fix dbt/models/ --config dbt/.sqlfluff


dbt-elementary-dev:
	set -a && source .env.dev && set +a && $(DBT) build --select elementary --target dev && edr report

dbt-elementary-prod:
	set -a && source .env.prod && set +a && $(DBT) build --select elementary --target prod && edr report

# ==============================
# Terraform
# ==============================

TF_DIR = ./terraform
TF = terraform
GCLOUD_CONFIG = gcloud config set project
GCLOUD_AUTH = gcloud auth application-default set-quota-project

# 引数（dev or prod）に応じてプロジェクトIDを取得
get_project_id = $(shell cat ${TF_DIR}/env/$(1).tfvars | grep project_id | cut -d'=' -f2 | tr -d '" ' )

tf-init-dev:
	${GCLOUD_CONFIG} $(call get_project_id,dev)
	${GCLOUD_AUTH} $(call get_project_id,dev)
	cd ${TF_DIR} && ${TF} init -reconfigure -backend-config=env/backend-dev.hcl

tf-init-prod:
	${GCLOUD_CONFIG} $(call get_project_id,prod)
	${GCLOUD_AUTH} $(call get_project_id,prod)
	cd ${TF_DIR} && ${TF} init -reconfigure -backend-config=env/backend-prod.hcl

tf-plan-dev:
	${GCLOUD_CONFIG} $(call get_project_id,dev)
	${GCLOUD_AUTH} $(call get_project_id,dev)
	cd ${TF_DIR} && ${TF} plan -var-file=env/dev.tfvars

tf-plan-prod:
	${GCLOUD_CONFIG} $(call get_project_id,prod)
	${GCLOUD_AUTH} $(call get_project_id,prod)
	cd ${TF_DIR} && ${TF} plan -var-file=env/prod.tfvars

tf-apply-dev:
	${GCLOUD_CONFIG} $(call get_project_id,dev)
	${GCLOUD_AUTH} $(call get_project_id,dev)
	cd ${TF_DIR} && ${TF} apply -var-file=env/dev.tfvars

tf-apply-prod:
	${GCLOUD_CONFIG} $(call get_project_id,prod)
	${GCLOUD_AUTH} $(call get_project_id,prod)
	cd ${TF_DIR} && ${TF} apply -var-file=env/prod.tfvars

tf-destroy-dev:
	${GCLOUD_CONFIG} $(call get_project_id,dev)
	${GCLOUD_AUTH} $(call get_project_id,dev)
	cd ${TF_DIR} && ${TF} destroy -var-file=env/dev.tfvars

tf-destroy-prod:
	${GCLOUD_CONFIG} $(call get_project_id,prod)
	${GCLOUD_AUTH} $(call get_project_id,prod)
	cd ${TF_DIR} && ${TF} destroy -var-file=env/prod.tfvars

tf-check:
	cd ${TF_DIR} && \
	${TF} init -backend=false && \
	${TF} fmt -recursive && \
	${TF} validate

all-check: lint format tf-check

# ==============================
# functions_frameworkのローカル実行
# ==============================
run-scraper:
	PYTHONPATH=functions ${POETRY_RUN} functions_framework --target scraping --source functions/func_scraper/main.py --port 8080

run-loader:
	PYTHONPATH=functions ${POETRY_RUN} functions_framework --target load_to_bigquery --source functions/func_loader/main.py --port 8080


.PHONY: lint format tf-init-dev tf-init-prod tf-plan-dev tf-plan-prod tf-apply-dev tf-apply-prod tf-destroy-dev tf-destroy-prod tf-check all-check