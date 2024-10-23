FROM python:3.11

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ARG ENGINE_VERSION

RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install hopeit.engine[web,cli,fs-storage,redis-streams,redis-storage,apps-visualizer,config-manager,log-streamer]==$ENGINE_VERSION

#prepare dependencies
FROM python:3.11
COPY --from=0 /opt/venv /opt/venv

RUN apt-get update \
    && apt-get install -y --no-install-recommends make git \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
ENV PATH=/app:$PATH

COPY Makefile .
COPY requirements.txt requirements.txt
COPY requirements.lock requirements.lock
RUN make deps-app0-admin

RUN pip install -r requirements.lock
#prepare app files
COPY app0-app5 app0-app5
COPY plugins plugins

COPY app0-app5/build/run-app.sh run-app.sh

# install app
RUN make 
RUN make install
RUN make api

#make final image
FROM python:3.11-slim
COPY --from=1 /opt/venv /opt/venv
COPY --from=1 /app /app

RUN apt-get update \
    && apt-get install -y libpq-dev \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*
ENV TZ="America/Buenos_Aires"

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN mkdir -p /var/log/hopeit
RUN mkdir -p /app0-admin/.secrets

WORKDIR /app
ENV PATH="/app:$PATH"
COPY app0-app5/build/update-openapi.sh .

ENV REDIS_URL="redis://localhost:6379"
ENV LOGS_LEVEL='INFO'
ENV LOGS_PATH="/var/log/hopeit"
ENV MONGO_URL="mongodb://rootuser:rootpass@localhost:27017"
ENV MONGO_DB="puedb"
ENV OBJECT_STORAGE_ACCESS_KEY_ID="minio"
ENV OBJECT_STORAGE_SECRET_ACCESS_KEY="minio123"
ENV OBJECT_STORAGE_ENDPOINT_URL="http://minio:9000"
ENV OBJECT_STORAGE_SSL="false"
ENV MQTT_HOST="broker.hivemq.com"
ENV MQTT_PORT="1883"
ENV CORS_ORIGIN="*"
ENV DOMAIN="localhost"

ENV CONFIG_FILES="app0-app5/config/server-slave.json,plugins/platform-auth/config/1x0.json,app0-app5/config/app0-app5.json,app0-app5/config/config-manager.json"
# To disable OPEN API set empty value to ENV API_FILE
ENV API_FILE="app0-app5/config/openapi.json"
ENV ENABLED_GROUPS="m,w"
ENV PORT=8026

EXPOSE $PORT
ENTRYPOINT ["run-app.sh"]
