HOPEIT_APPS_VISUALIZER_HOSTS=http://localhost:8021,http://localhost:8022,http://localhost:8098 \
REDIS_URL="redis://localhost:6379" \
LOGS_LEVEL="INFO" \
LOGS_PATH="/var/log/hopeit" \
CORS_ORIGIN="http://localhost" \
hopeit_server run --start-streams --port=8098 --start-streams \
--config-files=config/server.json,config/config-manager.json,config/apps-visualizer.json  \
--api-file=api/openapi.json
