FROM python:3.11

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ARG ENGINE_VERSION

RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install hopeit.engine[web,cli,redis-streams,redis-storage,apps-visualizer,config-manager]==$ENGINE_VERSION

#prepare dependencies
FROM python:3.11
COPY --from=0 /opt/venv /opt/venv

RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
ENV PATH=/app:$PATH


#prepare app files
COPY config config
COPY api api
COPY run-app.sh run-app.sh

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

ENV REDIS_URL="redis://localhost:6379"
ENV LOGS_LEVEL="INFO"
ENV LOGS_PATH="/var/log/hopeit"

# ENV CORS_ORIGIN="localhost"
ENV DOMAIN="localhost"

ENV HOPEIT_APPS_VISUALIZER_HOSTS=http://localhost:8021,http://localhost:8022,http://localhost:8098
ENV CONFIG_FILES=config/server.json,config/config-manager.json,config/apps-visualizer.json
# To disable OPEN API set empty value to ENV API_FILE
ENV API_FILE=api/openapi.json
ENV PORT=8098

EXPOSE $PORT
ENTRYPOINT ["run-app.sh"]