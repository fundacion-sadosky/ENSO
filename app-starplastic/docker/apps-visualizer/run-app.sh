#!/bin/bash

if [ -z "$API_FILE" ] 
then
echo "OPENAPI Disabled"
exec hopeit_server run --port=$PORT --start-streams --config-files=$CONFIG_FILES
else
echo "OPENAPI Enabled"
exec hopeit_server run --port=$PORT --start-streams --config-files=$CONFIG_FILES --api-file=$API_FILE
fi