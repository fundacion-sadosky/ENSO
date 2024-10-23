build-docker:
	$(eval UI_VERSION := $(shell grep '"version"' package.json | cut -d '"' -f 4 | head -n 1))
	docker build --progress plain \
	--tag registry.gitlab.com/ingar-ue/pue-platform/app0-admin-ui:$(UI_VERSION) \
	--tag registry.gitlab.com/ingar-ue/pue-platform/app0-admin-ui .

publish-docker:
	$(eval UI_VERSION := $(shell grep '"version"' package.json | cut -d '"' -f 4 | head -n 1))
	docker push registry.gitlab.com/ingar-ue/pue-platform/app0-admin-ui:$(UI_VERSION) && \
	docker push registry.gitlab.com/ingar-ue/pue-platform/app0-admin-ui
