.PHONY: help marvin update clean-pyc clean-build clean-reports clean-deps clean

help:
	@echo "    marvin"
	@echo "        Prepare project to be used as a marvin package."
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

marvin:
	pip install -e . --process-dependency-links
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

clean-reports:
	rm -rf coverage_report/
	rm -f coverage.xml
	rm -f .coverage

clean-deps:
	pip freeze | grep -v "^-e" | xargs pip uninstall -y

clean: clean-build clean-pyc clean-reports clean-deps
