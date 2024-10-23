# Plataforma App Starplastic

Plataforma para sensorización y planificación industrial para Starplastic.

## Stack tecnología

- `Aiohttp`: Asynchronous HTTP Client/Server para asyncio y Python
- `Hopeit.engine`: Python engine para Microservices orchestration con Data Streams
- `OpenAPI`: Documentación y test de `endpoints`
- `Pip & venv`: Python dependency management and packaging
- `Docker & docker-compose` : Virtualización de la aplicación en imágenes
- `MongoDB`: Base de Datos
- `VueJS 3 + Vite`: Interfaz de Usuario
- `asyncio_mqtt`: Envío y recepción de mensajes MQTT
- `or tools`: Open Source software suite para optimización

## Development

Tools required:
* venv
* [VS Code](https://code.visualstudio.com/Download)
* [Nodejs LTS](https://nodejs.org/en/)
* [Docker](https://docs.docker.com/engine/install/)
* [Linux: Running docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/)

### Docker issues on Linux

- Check ip of docker interface
```bash
ifconfig
```

```
docker0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
        inet6 fe80::42:82ff:feed:51b3  prefixlen 64  scopeid 0x20<link>
        ether 02:42:82:ed:51:b3  txqueuelen 0  (Ethernet)
        RX packets 298357  bytes 18562702 (18.5 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 494317  bytes 745277108 (745.2 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```
- Edit /etc/hosts
```bash
sudo nano /etc/hosts
```
Add to final
```
172.17.0.1   host.docker.internal
```

### MongoDb

- VS code plugin: [MongoDB for VS Code](vscode:extension/mongodb.mongodb-vscode) 
  - Connection config: mongodb://rootuser:rootpass@localhost:27017/?authSource=admin&readPreference=primary&appname=mongodb-vscode%200.5.0&ssl=false
- Use Database starplasticDB (created by docker script)

### MinIO Docker Config

- Access console (see url in docker logs and user and password in docker yaml)
- Create buckets: `platform-images`, `platform-docs`

### Base dockers on dev environment
After the creation of the containers you can test them by running:
```
cd docker
docker-compose up
```
To stop base dockers
```
cd docker
docker-compose down
```
### All apps as dockers on local dev environment
```
cd ~/dev/lab/pue-platform/docker
cp .env.local .env
docker-compose -f docker-compose-apps-local.yml up
```
Go to: http://app0.me/admin/

To stop dockers
```
cd docker
docker-compose -f docker-compose-apps-local.yml down
```
### All apps as dockers on staging environment
```
cd docker
cp .env.qa .env
docker-compose -f docker-compose-apps-qa.yml up -d
```
To stop base dockers
```
cd docker
docker-compose -f docker-compose-apps-qa.yml down
```
### Sample users

DEF_ADM_SP = "admin.sp@app0.me"
DEF_OP_SP = "operario.sp@app0.me"
DEF_PASSWORD2S = "starpla2023DASH."

### Gitlab registry configurations

Go to Settings -> Repository -> Deploy tokens

docker login -u gitlab+deploy-token-xxxxxx -p LKLyfKuaaRutLT72Td77 registry.gitlab.com
