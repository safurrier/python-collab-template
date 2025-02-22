.PHONY: compile-deps setup clean-pyc clean-test clean test mypy lint format check clean-example dev-env refresh-containers rebuild-images build-image push-image

# Development Setup
#################
compile-deps:  # Compile dependencies from pyproject.toml
	uv pip compile pyproject.toml -o requirements.txt
	uv pip compile pyproject.toml --extra dev -o requirements-dev.txt

setup: compile-deps  # Install uv and project dependencies
	pip install uv
	uv pip sync requirements.txt requirements-dev.txt

# Cleaning
#########
clean-pyc:  # Remove Python compilation artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:  # Remove test and coverage artifacts
	rm -f .coverage
	rm -f .coverage.*

clean: clean-pyc clean-test

# Testing and Quality Checks
#########################
test: clean  # Run pytest with coverage
	uv pip run pytest tests --cov=src --cov-report=term-missing

mypy:  # Run type checking
	uv pip run mypy src

lint:  # Run ruff linter
	uv pip run ruff check src

format:  # Run ruff formatter
	uv pip run ruff format src

check: test mypy lint format  # Run all quality checks

# Project Management
##################
clean-example:  # Remove example code (use this to start your own project)
	rm -rf src/example.py tests/test_example.py
	touch src/__init__.py tests/__init__.py


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
