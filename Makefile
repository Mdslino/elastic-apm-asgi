# Variables
GIT_CURRENT_BRANCH := ${shell git symbolic-ref --short HEAD}
BASE_DIR := ./
PKG_NAME := elastic_apm_asgi
SRC_DIR := $(BASE_DIR)/$(PKG_NAME)/


# Create a new release
# Usage: make release v=1.0.0
release:
	@if [ "$(v)" == "" ]; then \
		echo "You need to specify the new release version. Ex: make release v=1.0.0"; \
		exit 1; \
	fi
	@echo "Creating a new release version: ${v}"
	@echo "__version__ = '${v}'" > `pwd`/$(PKG_NAME)/version.py
	@git add $(PKG_NAME)/version.py
	@git commit -m '${v}'
	@git tag ${v}
	@git push origin ${v}
	@git push --set-upstream origin "${GIT_CURRENT_BRANCH}"
	@git push origin

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +