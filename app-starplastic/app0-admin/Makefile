SRC = $(wildcard **/src/*.py)

.PHONY: deps dev-deps install

deps:
	pip install --upgrade pip && \
	pip install -U -r requirements.txt

dev-deps: deps
	pip install -U -r requirements-dev.txt

lock-requirements:
	pip freeze > requirements.lock

install:
	pip install -U -e ./app0-admin && \
	pip install -U -e ./plugins/platform-auth

qa:
	/bin/bash app0-admin/build/ci-static.sh && \
	/bin/bash plugins/platform-auth/build/ci-static.sh

api:
	/bin/bash app0-admin/build/update-openapi.sh

dist-app0-admin:
	pip install wheel && \
	cd app0-admin && \
	rm -rf dist && \
	python setup.py sdist bdist_wheel

dist-plugin-auth:
	pip install wheel && \
	cd plugins/platform-auth/ && \
	rm -rf dist && \
	python setup.py sdist bdist_wheel

build-docker:
	$(eval ENGINE_VERSION := $(shell cat requirements.lock | grep hopeit.engine |  sed s/'hopeit.engine=='//))
	$(eval APP0_ADMIN_VERSION := $(shell python3 app0-admin/src/app0/admin/version.py APP0_ADMIN_VERSION))
	docker build --progress plain --build-arg ENGINE_VERSION=$(ENGINE_VERSION) \
	--tag registry.gitlab.com/ingar-ue/pue-platform/app0-admin:$(APP0_ADMIN_VERSION) \
	--tag registry.gitlab.com/ingar-ue/pue-platform/app0-admin .

build-docker-apps-visualizer:
	$(eval ENGINE_VERSION := $(shell cat requirements.lock | grep hopeit.engine |  sed s/'hopeit.engine=='//))
	$(eval APP0_ADMIN_VERSION := $(shell python3 app0-admin/src/app0/admin/version.py APP0_ADMIN_VERSION))
	cd ../docker/apps-visualizer && docker build --progress plain --build-arg ENGINE_VERSION=$(ENGINE_VERSION) \
	--tag registry.gitlab.com/ingar-ue/pue-platform/apps-visualizer:$(APP0_ADMIN_VERSION) \
	--tag registry.gitlab.com/ingar-ue/pue-platform/apps-visualizer .
	
publish-docker:
	$(eval APP0_ADMIN_VERSION := $(shell python3 app0-admin/src/app0/admin/version.py APP0_ADMIN_VERSION))
	docker push registry.gitlab.com/ingar-ue/pue-platform/app0-admin:$(APP0_ADMIN_VERSION) && \
	docker push registry.gitlab.com/ingar-ue/pue-platform/app0-admin

publish-docker-apps-visualizer:
	$(eval APP0_ADMIN_VERSION := $(shell python3 app0-admin/src/app0/admin/version.py APP0_ADMIN_VERSION))
	docker push registry.gitlab.com/ingar-ue/pue-platform/apps-visualizer:$(APP0_ADMIN_VERSION) && \
	docker push registry.gitlab.com/ingar-ue/pue-platform/apps-visualizer
