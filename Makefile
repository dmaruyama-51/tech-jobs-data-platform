POETRY = $(shell which poetry)
POETRY_OPTION = --no-interaction --no-ansi
POETRY_RUN = ${POETRY} run ${POETRY_OPTION}

# ==============================
# Python
# ==============================	

MYPY_OPTIONS = --install-types --non-interactive --ignore-missing-imports

lint: 
	${POETRY_RUN} mypy ${MYPY_OPTIONS} -p functions
	${POETRY_RUN} ruff check . --fix

format: 
	${POETRY_RUN} ruff format .


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