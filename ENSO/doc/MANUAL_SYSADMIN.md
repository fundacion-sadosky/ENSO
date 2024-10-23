# APP Starplastic - Manual de sysadmin

Plataforma para sensorización y planificación industrial para Starplastic.

![img](app_starplastic.png)

## Stack tecnología

- `Aiohttp`: Asynchronous HTTP Client/Server para asyncio y Python
- `Hopeit.engine`: Python engine para Microservices orchestration con Data Streams
- `OpenAPI`: Documentación y test de `endpoints`
- `Pip & venv`: Python dependency management and packaging
- `Docker & docker-compose` : Virtualización de la aplicación en imágenes
- `MongoDB`: Base de Datos
- `VueJS 3 + Vite`: Interfaz de Usuario
- `aimqtt`: Envío y recepción de mensajes MQTT
- `or tools`: Open Source software suite para optimización

## Código fuente e imágenes Docker

El código fuente se encuentra en un repositorio de Gitlab: https://gitlab.com/fhernand23/app-starplastic

Las imágenes de docker se distribuyen en la misma infraestructura de **gitlab**.

## Arquitectura

- Repositorio de Datos principal: MongoDB
- Repositorio de Archivos/Recursos: Minio
- Microservicios basados en imágenes de docker (Backend en python, Frontend en Vue.js)
- IOT: MQTT

La aplicación se distribuye en imágenes de docker, un formato estándar que puede implementarse en diversas formas de forma relativamente fácil, pero se recomienda un entorno en el sistema operativo linux, que es conocido por su robustez y seguridad.

## Servidor Staging

Actualmente, tanto la Aplicación como la Base de datos se encuentra instalado bajo el esquema de imágenes de Docker, configuradas en un servidor propio del instituto ingar, bajo la dirección **https://ingarue.santafe-conicet.gov.ar/admin**

Dicho servidor es un servidor de tipo STAGING, que puede ser utilizado para producción, pero cuya disponibilidad podría sufrir interrupciones.

## Servidor Producción

### Uso de memoria y procesador estimado

* CONTAINER ID   NAME                      CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS

* 6eb8b46cef75   mongodb                   0.56%     1.382GiB / 31.28GiB   4.42%     34.6MB / 31.3MB   803kB / 73.7MB    36
* 599ada2fbca6   docker_redis_1            0.25%     392.3MiB / 31.28GiB   1.22%     26.6MB / 131MB    0B / 5.49GB       5
* fdf7eb59e0d9   docker_minio_1            0.00%     118MiB / 31.28GiB     0.37%     18.2kB / 149kB    5.18MB / 217MB    13
* 2b7ebb5ca72d   docker_api-gateway_1      0.00%     9.512MiB / 31.28GiB   0.03%     8.26MB / 8.75MB   319kB / 0B        12
* dbb398287268   docker_certbot_1          0.00%     1.684MiB / 31.28GiB   0.01%     7.21kB / 911B     0B / 4.1kB        2
* ff97e9045e7e   docker_app0-admin-api_1   0.04%     111.6MiB / 31.28GiB   0.35%     923kB / 1.43MB    6.46MB / 332kB    4
* 399f52b6cee7   docker_app0-admin-ui_1    0.00%     1.855MiB / 31.28GiB   0.01%     21kB / 5.31kB     12.3kB / 4.1kB    2
* 402c26b4afb4   docker_app0-app5-api_1    0.71%     114.5MiB / 31.28GiB   0.36%     39.5MB / 44.9MB   86kB / 23.4MB     14
* 9f741576d131   docker_app0-app5-job_1    0.13%     112.9MiB / 31.28GiB   0.35%     1.23MB / 3.22MB   8.41MB / 45.1kB   3
* fd9a8d485f2e   docker_app0-app5-ui_1     0.00%     2.031MiB / 31.28GiB   0.01%     151kB / 6.77MB    6.87MB / 4.1kB    2

### Posibilidad 1: Cloud server

La aplicación se puede instalar en el proveedor Linode utilizando un servidor virtual, con un costo aproximado de 25 dólares mensuales.

Previamente, hay que registrar el dominio requerido con el cual será identificado el servidor en internet.

### Posibilidad 2: Private local server

La aplicación puede instalarse en un servidor local de la empresa, cuyo requerimiento es que el sistema operativo sea Linux y que tenga una conexión a internet.

Previamente, hay que registrar el dominio requerido con el cual será identificado el servidor en internet.

## Backup (y Restore)

La aplicación es completamente stateless (o sea, sin estado) con lo cual no hay nada para realizar backup en cuanto a la aplicación en si.
En cuanto a la base de datos, es recomendable plantear un esquema de backup que dependerá del proveedor.

## Usuarios y permisos

Inicialmente, se crearon 2 usuarios con sus respectivos niveles de Administrador y Operario:
* Administrador - Usuario: **admin.sp@app0.me** - Contraseña: **starpla2023DASH.**
* Operario - Usuario: **operario.sp@app0.me** - Contraseña: **starpla2023DASH.**
(Contraseñas sin comillas, con punto final).

## Soporte post-instalación

Se proveerá de un soporte post instalación de correción de errores por 3 meses posteriores a la finalización del proyecto, durante los meses de octubre, noviembre y diciembre de 2023.
