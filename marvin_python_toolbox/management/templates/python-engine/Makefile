.PHONY: help marvin update clean-pyc clean-build clean-reports clean

help:
	@echo "    marvin"
	@echo "        Prepare project to be used as a marvin package."
	@echo "    update"
	@echo "        Reinstall requirements and setup.py dependencies."
	@echo "    clean-all"
	@echo "        Remove all generated artifacts."
	@echo "    clean-pyc"
	@echo "        Remove python artifacts."
	@echo "    clean-build"
	@echo "        Remove build artifacts."
	@echo "    clean-reports"
	@echo "        Remove coverage reports."

marvin: SHELL:=/bin/bash
marvin: clean
	pip install -e . --process-dependency-links
	marvin --help

update:
	pip install -e . --process-dependency-links -U 

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +

clean-build:
	rm --force --recursive *.egg-info
	rm --force --recursive .cache
	rm --force --recursive .eggs
	rm --force --recursive dist

clean-reports:
	rm --force --recursive coverage_report/
	rm --force coverage_report.xml
	rm --force .coverage

clean: clean-build clean-pyc clean-reports
