.PHONY: help marvin marvin-prod update clean-pyc clean-build clean-reports clean-deps clean docker-build docker-push docker-run

DOCKER_VERSION?=0.00.01
DOCKER_REGISTRY_ADRESS?=docker.registry.io
MARVIN_DATA_PATH?=$(HOME)/marvin/data
MARVIN_ENGINE_NAME?={{project.name}}
MARVIN_TOOLBOX_VERSION?={{project.toolbox_version}}

help:
	@echo "    marvin"
	@echo "        Prepare project to be used as a marvin package."
	@echo "    marvin-prod"
	@echo "        Prepare project to be used in production environment."
	@echo "    update"
	@echo "        Reinstall requirements and setup.py dependencies."
	@echo "    clean"
	@echo "        Remove all generated artifacts."
	@echo "    clean-pyc"
	@echo "        Remove python artifacts."
	@echo "    clean-build"
	@echo "        Remove build artifacts."
	@echo "    clean-reports"
	@echo "        Remove coverage reports."
	@echo "    clean-deps"
	@echo "        Remove marvin setup.py dependencies."
	@echo "    docker-build"
	@echo "        Runs the docker build command with marvin env default parameters."
	@echo "    docker-push"
	@echo "        Runs the docker push command with marvin env default parameters."
	@echo "    docker-run"
	@echo "        Runs the docker run command with marvin env default parameters."

marvin:
	pip install -e ".[testing]" --process-dependency-links
	marvin --help

marvin-prod:
	pip install . --process-dependency-links
	marvin --help

update:
	pip install -e . -U --process-dependency-links

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +

clean-build:
	rm -rf *.egg-info
	rm -rf .cache
	rm -rf .eggs
	rm -rf dist
	rm -rf build

clean-reports:
	rm -rf coverage_report/
	rm -f coverage.xml
	rm -f .coverage

clean-deps:
	pip freeze | grep -v "^-e" | xargs pip uninstall -y

clean: clean-build clean-pyc clean-reports clean-deps

docker-build: clean-build
	mkdir -p build
	tar -cf build/engine.tar --exclude=*.log --exclude=*.pkl --exclude='build' --exclude='notebooks' --exclude=*.tar *
	cp -f $(MARVIN_DATA_PATH)/marvin-engine-executor-assembly-$(MARVIN_TOOLBOX_VERSION).jar build/marvin-engine-executor-assembly.jar
	sudo docker build -t $(DOCKER_REGISTRY_ADRESS)/$(MARVIN_ENGINE_NAME):$(DOCKER_VERSION) .

docker-run:
	sudo docker run --name=marvin-$(MARVIN_ENGINE_NAME)-$(DOCKER_VERSION) --mount type=bind,source=$(MARVIN_DATA_PATH),destination=/marvin-data -p 8000:8000 $(DOCKER_REGISTRY_ADRESS)/$(MARVIN_ENGINE_NAME):$(DOCKER_VERSION)

docker-push:
	sudo docker push $(DOCKER_REGISTRY_ADRESS)/$(MARVIN_ENGINE_NAME):$(DOCKER_VERSION)