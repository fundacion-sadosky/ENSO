# App0 App5

App5 - Dashboard

## Development

### Create a venv environment

```bash
python3.11 -m venv venv
source ./venv/bin/activate
```

Install dependencies & modules
```bash
make deps
make lock-requirements
```

Install development dependencies & modules
```bash
make dev-deps
make install
```

To recreate env, only add previously:
```bash
rm -rf venv
rm requirements.lock
```

## Configure in platform

- Create app (Starplastic - Monitoreo y Planificación de la Producción - Imagen en `doc`)
- Create roles (Starplastic Admin, Starplastic Operario, Starplastic User)
- Setear en app default role como (Starplastic User)
- Crear usuario admin.sp@app0.me, y operario.sp@app0.me
- Setear permisos en usuarios

- Buscar en mail_store el mail enviado y setear la contraseña. La url debería ser similar a `http://localhost/admin/fset/f20c7cc3-433b-4a59-914a-9270f7b10728`
- Pass dev: cde456
- Pass staging: starpla2023DASH.

## Información técnica MQTT

### Máquinas

- M10, M13, M16, M17, M18, M21, M24, M27

### Mensaje
- mqttClient.publish("Máquina/M17/estado/CambioDeMolde", String(estado1).c_str());
- mqttClient.publish("Máquina/M17/estado/EnPreparación", String(estado2).c_str());
- mqttClient.publish("Máquina/M17/estado/Ciclo", String(estado3).c_str());
- mqttClient.publish("Máquina/M17/estado/EnProducción", String(estado4).c_str());
- mqttClient.publish("Máquina/M17/estado/EnLimpiezaLubricación", String(estado5).c_str());
- mqttClient.publish("Máquina/M17/estado/EnPreventivo", String(estado6).c_str());
- mqttClient.publish("Máquina/M17/estado/EnCorrectivo", String(estado7).c_str());

### Estados

CambioDeMolde, proceso de retiro y colocación de un nuevo molde. Trabajo realizado por PERSONAL TÉCNICO.
EnPreparación; todos los tiempos no comprendidos en los demás estados referidos a la preparación o puesta a punto de máquina por parte del OPERADOR.
Ciclo; no es un estado, si no que indica el momento en que se sopla o inyecta una pieza (o varios según cantidad de cavidades del molde).
EnProducción, a cargo del OPERADOR.
EnLimpiezaLubricación, PERSONAL TÉCNICO.
EnPreventivo, mantenimiento por parte del PERSONAL TÉCNICO.
EnCorrectivo, , mantenimiento por parte del PERSONAL TÉCNICO.

### Base de datos preliminar
https://lucid.app/lucidchart/951af122-edfa-4683-9d10-11d2d418f8a3/edit?page=0_0&invitationId=inv_c65e8e73-70f5-4812-be6f-edf0d2aed389#

### Planificación - Optimización

https://viktorsapozhok.github.io/docker-scip-pyscipopt/

### Mongo indexes

use('puedb')
db['app5.sensor_machine'].createIndex({ sense_time: "text" })


db['app5.sensor_machine'].createIndex({ sense_time: "text" })
