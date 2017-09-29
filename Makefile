# Copyright [2017] [B2W Digital]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

.PHONY: help marvin update clean-pyc clean-build clean-reports clean

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

marvin: SHELL:=/bin/bash
marvin:
	# sudo apt-get install libsasl2-dev -y
	# pip install --upgrade pip
	# pip install virtualenvwrapper

	# @egrep "^export WORKON_HOME="  $(HOME)/.profile -q || echo "export WORKON_HOME=$(HOME)/.virtualenvs" >> $(HOME)/.profile
	# @egrep "^source $(VIRTUALENVWRAPPER_SCRIPT)"  $(HOME)/.profile -q || echo "source $(VIRTUALENVWRAPPER_SCRIPT)" >> $(HOME)/.profile
	# @egrep "^export MARVIN_HOME="  $(HOME)/.profile -q || echo "export MARVIN_HOME=$(HOME)/marvin" >> $(HOME)/.profile
	# @egrep "^export MARVIN_HOME="  $(HOME)/.profile -q || echo "export MARVIN_HOME=$(HOME)/marvin" >> $(HOME)/.profile

	# @( \
	#	source $(VIRTUALENVWRAPPER_SCRIPT); \
	#	source $(HOME)/.profile; \
	#	mkvirtualenv -a . marvin-toolbox-env; \
	#	pip install -e .; \
	#	marvin --help; \
	#)

	#mkdir -p $(HOME)/marvin

	#@egrep "^source $(HOME)/.profile" $(WORKON_HOME)/marvin-toolbox-env/bin/postactivate -q || echo "source $(HOME)/.profile" >> $(WORKON_HOME)/marvin-toolbox-env/bin/postactivate
	
	#@printf "\n\n"
	#@echo "Marvin created with success!!!"
	#@echo "To use type 'workon marvin-toolbox-env' and have fun!"
	pip install -e .
	marvin --help

update:
	pip install -e . -U 

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +

clean-build:
	rm --force --recursive *.egg-info
	rm --force --recursive .cache

clean-reports:
	rm --force --recursive coverage_report/
	rm --force coverage_report.xml
	rm --force .coverage

clean: clean-build clean-pyc clean-reports
