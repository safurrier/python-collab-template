setup:
	python -m venv .venv && . .venv/bin/activate
	pip install --upgrade pip
	pip install -r requirements.dev
	pip install -r requirements.prod

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
	. .venv/bin/activate && py.test tests --cov=src --cov-report=term-missing --cov-fail-under 95

mypy:
	. .venv/bin/activate && mypy src

lint:
	. .venv/bin/activate && pylint src -j 4 --reports=y

docs: FORCE
	cd docs; . .venv/bin/activate && sphinx-apidoc -o ./source ./src
	cd docs; . .venv/bin/activate && sphinx-build -b html ./source ./build
FORCE:

check: test lint mypy

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