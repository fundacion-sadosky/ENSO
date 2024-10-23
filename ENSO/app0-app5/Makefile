SRC = $(wildcard **/src/*.py)

.PHONY: deps dev-deps install

deps: deps-app0-admin
	pip install --upgrade pip && \
	pip install -U -r requirements.txt

dev-deps: deps dev-deps-app0-admin
	pip install -U -r requirements-dev.txt

lock-requirements:
	pip freeze > requirements.lock

install:
	pip install -e ./app0-app5

dev-deps-app0-admin:
	pip install -e ../app0-admin/app0-admin && \
	pip install -e ../app0-admin/plugins/platform-auth

deps-app0-admin:
	pip install -U app0.admin \
	--index https://pue_operations:LKLyfKuaaRutLT72Td77@gitlab.com/api/v4/projects/35999627/packages/pypi/simple \
	--extra-index-url https://pypi.org/simple && \
	pip install -U app0.platform.auth \
	--index https://pue_operations:LKLyfKuaaRutLT72Td77@gitlab.com/api/v4/projects/35999627/packages/pypi/simple \
	--extra-index-url https://pypi.org/simple

api: 
	/bin/bash app0-app5/build/update-openapi.sh

qa:
	/bin/bash app0-app5/build/ci-static.sh

build-docker: build-docker-app build-docker-jobproc

publish-docker: publish-docker-app publish-docker-jobproc

build-docker-app:
	$(eval ENGINE_VERSION := $(shell cat requirements.lock | grep hopeit.engine |  sed s/'hopeit.engine=='//))
	$(eval APP0_APP_VERSION := $(shell python3 app0-app5/src/app0/app5/version.py APP0_APP_VERSION))
	docker build --progress plain --build-arg ENGINE_VERSION=$(ENGINE_VERSION) \
	--tag registry.gitlab.com/ingar-ue/pue-platform/app0-app5:$(APP0_APP_VERSION) \
	--tag registry.gitlab.com/ingar-ue/pue-platform/app0-app5 .

publish-docker-app:
	$(eval APP0_APP_VERSION := $(shell python3 app0-app5/src/app0/app5/version.py APP0_APP_VERSION))
	docker push registry.gitlab.com/ingar-ue/pue-platform/app0-app5:$(APP0_APP_VERSION) && \
	docker push registry.gitlab.com/ingar-ue/pue-platform/app0-app5

build-docker-jobproc:
	$(eval ENGINE_VERSION := $(shell cat requirements.lock | grep hopeit.engine |  sed s/'hopeit.engine=='//))
	$(eval APP0_APP_VERSION := $(shell python3 app0-app5/src/app0/app5/version.py APP0_APP_VERSION))
	docker build --progress plain --build-arg ENGINE_VERSION=$(ENGINE_VERSION) -f Dockerfile.job \
	--tag registry.gitlab.com/ingar-ue/pue-platform/app0-app5-job:$(APP0_APP_VERSION) \
	--tag registry.gitlab.com/ingar-ue/pue-platform/app0-app5-job .

publish-docker-jobproc:
	$(eval APP0_APP_VERSION := $(shell python3 app0-app5/src/app0/app5/version.py APP0_APP_VERSION))
	docker push registry.gitlab.com/ingar-ue/pue-platform/app0-app5-job:$(APP0_APP_VERSION) && \
	docker push registry.gitlab.com/ingar-ue/pue-platform/app0-app5-job
