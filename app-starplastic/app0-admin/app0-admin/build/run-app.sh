#!/bin/bash
if [ -z "$API_FILE" ] 
then
echo "$(date -u +'%Y-%m-%d %T,%3N') | INFO | Application running port=$PORT."
echo "$(date -u +'%Y-%m-%d %T,%3N') | INFO | OpenAPI Disabled."
exec python -m hopeit.server.web --port=$PORT --start-streams --config-files=$CONFIG_FILES
else
echo "$(date -u +'%Y-%m-%d %T,%3N') | INFO | Application running port=$PORT."
echo "$(date -u +'%Y-%m-%d %T,%3N') | WARNING | OpenAPI Enabled, it is recommended to disable it in production mode."
exec python -m hopeit.server.web --port=$PORT --start-streams --config-files=$CONFIG_FILES --api-file=$API_FILE
fi