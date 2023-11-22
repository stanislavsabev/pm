SHELL := /bin/bash
PROJ_NAME=pm
VENV_NAME=.venv

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
	@mv src/$(PROJ_NAME) $(RUN_ARGS)
	@for f in $$(find . -name "*.py") Makefile README.md pyproject.toml; \
		do \
		[ -f "$$f" ] && sed -i 's/$(PROJ_NAME)/$(RUN_ARGS)/g' $$f; \
	done

.PHONY: init
init: ## Install package and its dependencies
	python -m venv $(VENV_NAME)
	source $(VENV_NAME)/bin/activate \
	&& python -m pip install --upgrade pip \
	&& pip install pip-tools \
	&& pip-compile requirements/requirements.in \
	&& pip-compile requirements/requirements-dev.in \
	&& pip-sync requirements/requirements.txt requirements/requirements-dev.txt \
	&& pip install -e .

.PHONY: update
update: ## Update dependencies
	source $(VENV_NAME)/bin/activate \
	&& pip-compile requirements/requirements.in \
	&& pip-compile requirements/requirements-dev.in \
	&& pip-sync requirements/requirements.txt requirements/requirements-dev.txt

.PHONY: run
run: ## Run example
	@source $(VENV_NAME)/bin/activate \
	&& python -m testing.run

.PHONY: clean
clean: ## Clean cache
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +

.PHONY: delete-venv
delete-venv: ## Delete virtual environment
	rm -rf $(PROJ_NAME).egg-info
	rm -rf $(VENV_NAME)

.PHONY: format
format:
	black $(PROJ_NAME)
	isort $(PROJ_NAME)

.PHONY: check
check:
	black --check $(PROJ_NAME) \
	& isort --check $(PROJ_NAME) \
	& flake8 $(PROJ_NAME) \
	& mypy $(PROJ_NAME)

.PHONY: package
package: ## Package the project into .zip file
	rm -rf .$(PROJ_NAME)
	mkdir .$(PROJ_NAME)
	cp Makefile .$(PROJ_NAME)/
	cp LICENSE .$(PROJ_NAME)/
	cp pyproject.toml .$(PROJ_NAME)/
	cp requirements-dev.txt .$(PROJ_NAME)/
	cp requirements.txt .$(PROJ_NAME)/
	cp setup.cfg .$(PROJ_NAME)/
	cp tox.ini .$(PROJ_NAME)/
	find ./src/$(PACKAGE_NAME) -name '*.py' -exec cp --parents "{}" .$(PROJ_NAME)/ \;
	find ./tests/$(PACKAGE_NAME) -name '*.py' -exec cp --parents "{}" .$(PROJ_NAME)/ \;
	cd .$(PROJ_NAME) && zip -r ../$(PROJ_NAME).zip .
	rm -rf .$(PROJ_NAME)
