setup:
	cd orchestrator && pipenv install --dev
	cd orchestrator && pipenv run pre-commit install

quality_checks:
	cd orchestrator && pipenv run isort . \
    	&& pipenv run black . \
    	&& pipenv run pylint --recursive=y .

test:
	cd orchestrator && pipenv run pytest mlops/tests

generate_env:
	chmod +x deployment/generate_env.sh
	./deployment/generate_env.sh

build_and_run:
	docker-compose up -d --build

deploy:
	chmod +x ./deployment/deploy.sh
	chmod 600 $(KEY_PATH)
	./deployment/deploy.sh $(KEY_PATH)

all: setup quality_checks test generate_env build_and_run
