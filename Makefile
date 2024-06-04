SHELL := /bin/bash

PROJ_DIR = pm
TESTS_DIR = tests
PROJ_CFG := $(PWD)/.proj-cfg
PYTHON_CFG := $(PWD)/.python-cfg

check-var-defined = $(if $(strip $($1)),,$(error "$1" is not defined))

ifneq ("$(wildcard $(PROJ_CFG))","")
include  $(PROJ_CFG)
else ifneq ("$(wildcard $(PYTHON_CFG))","")
VENV_PATH:=$$(cat $(PYTHON_CFG))
else
VENV_PATH:=.venv
endif

# If the first argument is "rename"...
ifeq (rename,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "run"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

.PHONY: help
help: ## Show this message
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make \033[36m<target> [args...]\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: rename
rename: ## Rename this project. Args: <new-proj-name>
	@echo renaming project to: $(RUN_ARGS)
	@mv src/$(PROJ_DIR) $(RUN_ARGS)
	@for f in $$(find . -name "*.py") Makefile README.md pyproject.toml; \
		do \
		[ -f "$$f" ] && sed -i 's/$(PROJ_DIR)/$(RUN_ARGS)/g' $$f; \
	done

.PHONY: init
init: ## Install package and its dependencies
	$(call check-var-defined,VENV_PATH)
	python -m venv $(VENV_PATH)
	source $(VENV_PATH)/bin/activate \
	&& python -m pip install --upgrade pip \
	&& pip install pip-tools \
	&& pip-sync requirements/requirements.txt requirements/requirements-dev.txt \
	&& pip install -e .

.PHONY: update
req-update: ## Update requirements
	$(call check-var-defined,VENV_PATH)
	source $(VENV_PATH)/bin/activate \
	&& pip-compile requirements/requirements.in \
	&& pip-compile requirements/requirements-dev.in \
	&& pip-sync requirements/requirements.txt requirements/requirements-dev.txt \
	&& pip install -e .

.PHONY: run
run: ## Run example
	$(call check-var-defined,VENV_PATH)
	@source $(VENV_PATH)/bin/activate \
	&& python -m testing.run

.PHONY: delete-venv
delete-venv: ## Delete virtual environment
	$(call check-var-defined,VENV_PATH)
	rm -rf $(VENV_PATH)
	rm -rf $(PROJ_DIR).egg-info

.PHONY: clean
clean: ## Clean cache
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	find . -name ".mypy_cache" -type d -exec rm -rf {} +
	find . -name ".ruff_cache" -type d -exec rm -rf {} +

.PHONY: open-cfg
open-pm-cfg: ## Open pm config
	code ~/.pm

.PHONY: format
format: ## Format and style checks
	ruff format $(PROJ_DIR) $(TESTS_DIR)
	ruff check --fix $(PROJ_DIR) $(TESTS_DIR)

.PHONY: check
check: ## Check with mypy
	mypy $(PROJ_DIR)

.PHONY: checkall
checkall: format check ## Format, style checks and mypy

.PHONY: build
build: format check test ## Format and check with mypy and flake8

.PHONY: test
test: ## Run pytest with coverage
	pytest $(TESTS_DIR) -v --cov=$(PROJ_DIR) --cov-report=term --cov-report=html:build/htmlcov --cov-report=xml --cov-fail-under=80

.PHONY: cov
cov: ## Open test coverage report in browser
	firefox build/htmlcov/index.html

.PHONY: collect
collect: ## Run pytest collect only
	pytest --collect-only $(TESTS_DIR)

.PHONY: gh
gh: ## Open remote in browser
	firefox https://github.com/stanislavsabev/pm

.PHONY: package
package: ## Package the project into .zip file
	rm -rf .$(PROJ_DIR)
	mkdir .$(PROJ_DIR)
	cp Makefile .$(PROJ_DIR)/
	cp LICENSE .$(PROJ_DIR)/
	cp pyproject.toml .$(PROJ_DIR)/
	cp requirements-dev.txt .$(PROJ_DIR)/
	cp requirements.txt .$(PROJ_DIR)/
	cp setup.cfg .$(PROJ_DIR)/
	cp tox.ini .$(PROJ_DIR)/
	find ./src/$(PACKAGE_NAME) -name '*.py' -exec cp --parents "{}" .$(PROJ_DIR)/ \;
	find ./tests/$(PACKAGE_NAME) -name '*.py' -exec cp --parents "{}" .$(PROJ_DIR)/ \;
	cd .$(PROJ_DIR) && zip -r ../$(PROJ_DIR).zip .
	rm -rf .$(PROJ_DIR)
