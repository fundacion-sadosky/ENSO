#!/bin/bash
clear

echo "===> PUE Platform creating apis DEV ENVS..."
cd /home/fede/dev/lab/pue-platform
echo "===> SET ENV VARIABLES..."
export REDIS_URL='redis://localhost:6379'
export LOGS_LEVEL='INFO'
export LOGS_PATH='../logs'
export MONGO_URL="mongodb://rootuser:rootpass@localhost:27017"
export MONGO_DB="puedb"
export APP0_ADMIN_API_URL="http://localhost:8021"
export APP0_ADMIN_URL="http://localhost/admin"
export MAIL_APP_FROM="sender@app0.me"
export OBJECT_STORAGE_ACCESS_KEY_ID="minio"
export OBJECT_STORAGE_SECRET_ACCESS_KEY="minio123"
export OBJECT_STORAGE_ENDPOINT_URL="http://localhost:9000"
export OBJECT_STORAGE_SSL="true"
export MQTT_HOST="broker.hivemq.com"
export MQTT_PORT="1883"
export CORS_ORIGIN="http://localhost"
export DOMAIN="localhost"


# run apps apis
folder='app0-app1'
echo "===> creating venv api $folder..."
cd $folder
rm -rf venv
rm requirements.lock
python3.11 -m venv venv
source venv/bin/activate
make deps lock-requirements install api
echo "===> creating venv $folder OK"
deactivate
sleep 3
cd ..

folder='app0-app2'
echo "===> creating venv api $folder..."
cd $folder
rm -rf venv
rm requirements.lock
python3.11 -m venv venv
source venv/bin/activate
make deps lock-requirements install api
echo "===> creating venv $folder OK"
deactivate
sleep 3
cd ..

folder='app0-app3'
echo "===> creating venv api $folder..."
cd $folder
rm -rf venv
rm requirements.lock
python3.11 -m venv venv
source venv/bin/activate
make deps lock-requirements install api
echo "===> creating venv $folder OK"
deactivate
sleep 3
cd ..

folder='app0-app4'
echo "===> creating venv api $folder..."
cd $folder
rm -rf venv
rm requirements.lock
python3.11 -m venv venv
source venv/bin/activate
make deps lock-requirements install api
echo "===> creating venv $folder OK"
deactivate
sleep 3
cd ..

folder='app0-app5'
echo "===> creating venv api $folder..."
cd $folder
rm -rf venv
rm requirements.lock
python3.11 -m venv venv
source venv/bin/activate
make deps lock-requirements install api
echo "===> creating venv $folder OK"
deactivate
sleep 3
cd ..

folder='app0-app6'
echo "===> creating venv api $folder..."
cd $folder
rm -rf venv
rm requirements.lock
python3.11 -m venv venv
source venv/bin/activate
make deps lock-requirements install api
echo "===> creating venv $folder OK"
deactivate
sleep 3
cd ..
