#!/bin/bash
export REDIS_URL="redis://localhost:6379"
export HOPEIT_SIMPLE_EXAMPLE_HOSTS="in-process"
export HOPEIT_APPS_VISUALIZER_HOSTS="in-process"
export CORS_ORIGIN="http://localhost"
hopeit_openapi create \
--title="Hopeit Apps Visualizer" \
--description="Hopeit Apps Visualizer" \
--api-version="$(python -m hopeit.server.version APPS_API_VERSION)" \
--config-files=config/server.json,config/config-manager.json,config/apps-visualizer.json \
--output-file=api/openapi.json