POETRY = $(shell which poetry)
POETRY_OPTION = --no-interaction --no-ansi
POETRY_RUN = ${POETRY} run ${POETRY_OPTION}

MYPY_OPTIONS = --install-types --non-interactive --ignore-missing-imports

TF_DIR = ./terraform
TF = terraform

# 引数（dev or prod）に応じてプロジェクトIDを取得
get_project_id = $(shell cat ${TF_DIR}/env/$(1).tfvars | grep project_id | cut -d'=' -f2 | tr -d '" ' )

tf-init-dev:
	gcloud config set project $(call get_project_id,dev)
	cd ${TF_DIR} && ${TF} init -reconfigure -backend-config=env/backend-dev.hcl

tf-init-prod:
	gcloud config set project $(call get_project_id,prod)
	cd ${TF_DIR} && ${TF} init -reconfigure -backend-config=env/backend-prod.hcl

tf-plan-dev:
	gcloud config set project $(call get_project_id,dev)
	cd ${TF_DIR} && ${TF} plan -var-file=env/dev.tfvars

tf-plan-prod:
	gcloud config set project $(call get_project_id,prod)
	cd ${TF_DIR} && ${TF} plan -var-file=env/prod.tfvars

tf-apply-dev:
	gcloud config set project $(call get_project_id,dev)
	cd ${TF_DIR} && ${TF} apply -var-file=env/dev.tfvars

tf-apply-prod:
	gcloud config set project $(call get_project_id,prod)
	cd ${TF_DIR} && ${TF} apply -var-file=env/prod.tfvars

tf-destroy-dev:
	gcloud config set project $(call get_project_id,dev)
	cd ${TF_DIR} && ${TF} destroy -var-file=env/dev.tfvars

tf-destroy-prod:
	gcloud config set project $(call get_project_id,prod)
	cd ${TF_DIR} && ${TF} destroy -var-file=env/prod.tfvars

.PHONY: lint format all tf-init-dev tf-init-prod tf-plan-dev tf-plan-prod tf-apply-dev tf-apply-prod tf-destroy-dev tf-destroy-prod