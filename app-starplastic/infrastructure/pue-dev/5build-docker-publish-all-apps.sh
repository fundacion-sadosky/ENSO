#!/bin/bash
clear

echo "===> PUE Platform create publish dockers..."
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


# run admin api
folder='app0-admin'
echo "===> creating publishing docker $folder..."
cd $folder
make build-docker publish-docker
echo "===> creating publishing docker $folder OK"
sleep 3
cd ..

folder='app0-app1'
echo "===> creating publishing $folder..."
cd $folder
make build-docker publish-docker
echo "===> creating publishing $folder OK"
sleep 3
cd ..

folder='app0-app2'
echo "===> creating publishing $folder..."
cd $folder
make build-docker publish-docker
echo "===> creating publishing $folder OK"
sleep 3
cd ..

folder='app0-app3'
echo "===> creating publishing $folder..."
cd $folder
make build-docker publish-docker
echo "===> creating publishing $folder OK"
sleep 3
cd ..

folder='app0-app4'
echo "===> creating publishing $folder..."
cd $folder
make build-docker publish-docker
echo "===> creating publishing $folder OK"
sleep 3
cd ..

folder='app0-app5'
echo "===> creating publishing $folder..."
cd $folder
make build-docker publish-docker
echo "===> creating publishing $folder OK"
sleep 3
cd ..

folder='app0-app6'
echo "===> creating publishing $folder..."
cd $folder
make build-docker publish-docker
echo "===> creating publishing $folder OK"
sleep 3
cd ..
