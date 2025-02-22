setup:
	pip install uv
	uv pip sync requirements.txt requirements-dev.txt

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -f .coverage.*

clean: clean-pyc clean-test

test: clean
	uv pip run pytest tests --cov=src --cov-report=term-missing

mypy:
	uv pip run mypy src

lint:
	uv pip run ruff check src

format:
	uv pip run ruff format src

check: test mypy lint format


# Docker
########
IMAGE_NAME = container-registry.io/python-collab-template
IMAGE_TAG = latest

dev-env: refresh-containers
	@echo "Spinning up a dev environment ."
	@docker compose -f docker/docker-compose.yml down
	@docker compose -f docker/docker-compose.yml up -d dev
	@docker exec -ti composed_dev /bin/bash

refresh-containers:
	@echo "Rebuilding containers..."
	@docker compose -f docker/docker-compose.yml build

rebuild-images:
	@echo "Rebuilding images with the --no-cache flag..."
	@docker compose -f docker/docker-compose.yml build --no-cache

build-image:
	@echo Building dev image and tagging as ${IMAGE_NAME}:${IMAGE_TAG}
	@docker compose -f docker/docker-compose.yml down
	@docker compose -f docker/docker-compose.yml up -d dev
	@docker tag dev ${IMAGE_NAME}:${IMAGE_TAG}

push-image: build-image
	@echo Pushing image to container registry
	@docker push ${IMAGE_NAME}:${IMAGE_TAG}
