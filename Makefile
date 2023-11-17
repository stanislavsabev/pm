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

.PHONY: package help

help: ## Show this message
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make \033[36m<target> [args...]\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)


rename: ## Rename this project. Args: <new-proj-name>
	@echo renaming project to: $(RUN_ARGS)
	@mv src/$(PROJ_NAME) $(RUN_ARGS)
	@for f in $$(find . -name "*.py") Makefile README.md pyproject.toml; \
		do \
		[ -f "$$f" ] && sed -i 's/$(PROJ_NAME)/$(RUN_ARGS)/g' $$f; \
	done

init: ## Install package and its dependencies into virtual environment
	python -m venv $(VENV_NAME)
	source $(VENV_NAME)/bin/activate \
	&& python -m pip install --upgrade pip \
	&& pip install -r requirements/requirements-dev.txt \
	&& pip install -e .

run: ## Run example
	source $(VENV_NAME)/bin/activate \
	&& python -m example

clean: ## Clean virtual environment
	rm -rf $(VENV_NAME)
	rm -rf $(PROJ_NAME).egg-info
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +

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
