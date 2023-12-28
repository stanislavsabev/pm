SHELL := /bin/bash
PROJ_DIR=pm
VENV_PATH=$$(cat .python-cfg)

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
	python -m venv $(VENV_PATH)
	source $(VENV_PATH)/bin/activate \
	&& python -m pip install --upgrade pip \
	&& pip install pip-tools \
	&& pip-compile requirements/requirements.in \
	&& pip-compile requirements/requirements-dev.in \
	&& pip-sync requirements/requirements.txt requirements/requirements-dev.txt \
	&& pip install -e .

.PHONY: update
req-update: ## Update requirements
	source $(VENV_PATH)/bin/activate \
	&& pip-compile requirements/requirements.in \
	&& pip-compile requirements/requirements-dev.in \
	&& pip-sync requirements/requirements.txt requirements/requirements-dev.txt

.PHONY: run
run: ## Run example
	@source $(VENV_PATH)/bin/activate \
	&& python -m testing.run

.PHONY: delete-venv
delete-venv: ## Delete virtual environment
	rm -rf $(VENV_PATH)
	rm -rf $(PROJ_DIR).egg-info

.PHONY: clean
clean: ## Clean cache
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +

.PHONY: cleanall
cleanall: clean delete-venv ## Clean cache and venv

.PHONY: open-cfg
open-cfg: ## Open config
	code ~/.pm

.PHONY: format
format: ## Format with black and isort
	black $(PROJ_DIR)
	isort $(PROJ_DIR)

.PHONY: check
check: ## Check with mypy and flake8
	flake8 $(PROJ_DIR)
	mypy $(PROJ_DIR)

.PHONY: checkall
checkall: format check ## Format and check with mypy and flake8

.PHONY: build
build: format check test ## Format and check with mypy and flake8

.PHONY: test
test: ## Run pytest with coverage
	pytest

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
