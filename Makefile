

setup:
	cd orchestrator && pipenv install --dev
	cd orchestrator && pipenv run pre-commit install

quality_checks:
	cd orchestrator && pipenv run isort . \
    	&& pipenv run black . \
    	&& pipenv run pylint --recursive=y .

test:
	cd orchestrator && pipenv run pytest mlops/tests

build_and_run:
	docker-compose up -d

all: setup quality_checks test build_and_run
