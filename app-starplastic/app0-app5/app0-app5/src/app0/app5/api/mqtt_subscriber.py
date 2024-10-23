"""
MQTT: mqtt-subscriber
"""
from typing import Optional, List
import asyncio

import aiomqtt
from hopeit.app.events import Spawn, service_running
from hopeit.app.logger import app_extra_logger
from hopeit.app.context import EventContext
from app0.admin.db import db
from app0.app5.sensor import SensorMachine
from app0.app5.util import (MACH_STATUS_CICLO, MACH_STATUS_TIEMPO_DE_CICLO, MACH_STATUS_CAMBIO_MOLDE,
                            MACH_STATUS_PREPARACION, MACH_STATUS_PRODUCCION, MACH_STATUS_LIMPIEZA,
                            MACH_STATUS_PREVENTIVO, MACH_STATUS_CORRECTIVO, METRIC_TIEMPO_CICLO,
                            date_util, IDX_MACHINE)

logger, extra = app_extra_logger()

__steps__ = ['create_mqtt_sign']


async def __service__(context: EventContext) -> Spawn[SensorMachine]:
    interval = 10  # Seconds
    mqtt_host = context.env['mqtt']['host']
    mqtt_port = int(context.env['mqtt']['port'])
    assert mqtt_host
    assert mqtt_port
    while service_running(context):
        try:
            # Cancel the listener task after 24 hours - 86400 seconds
            async with asyncio.timeout(86400):
                active_topics = await _get_active_topics_to_subscribe(context)
                async with aiomqtt.Client(mqtt_host, port=mqtt_port, keepalive=60) as client:
                    async with client.messages() as messages:
                        for active_topic in active_topics:
                            print(f"=> subscribing to topic {active_topic}")
                            await client.subscribe(active_topic)
                        async for message in messages:
                            sensor_message: SensorMachine = _parse_sensor_msg(message.topic, message.payload)
                            if sensor_message:
                                yield sensor_message
        except aiomqtt.MqttError:
            logger.info(context, f'Connection lost; Reconnecting in {interval} seconds ...')
            await asyncio.sleep(interval)
        # Ignore the resulting TimeoutError
        except asyncio.TimeoutError:
            print("======> restarting mqtt subscribing...")
            pass


async def create_mqtt_sign(payload: SensorMachine, context: EventContext) -> SensorMachine:
    # logger.info(context, "Creating something...", extra=extra(
    #     payload_id=payload.id
    # ))
    result = payload
    result.client = "client001"
    result.sense_time = date_util.now()

    return result


def _parse_sensor_msg(topic, payload) -> Optional[SensorMachine]:
    value = payload.decode()
    # print(f"=====> {topic}: {value}")
    if value == "0":
        return None
    topics = topic.value.split("/")
    machine = topics[1]
    metric = topics[2]
    metric_value = topics[3]

    if metric_value == MACH_STATUS_CICLO:
        result = SensorMachine(
            topic=topic.value,
            machine=machine,
            metric=MACH_STATUS_CICLO,
            valint=int(value))
    elif metric_value == MACH_STATUS_TIEMPO_DE_CICLO:
        result = SensorMachine(
            topic=topic.value,
            machine=machine,
            metric=METRIC_TIEMPO_CICLO,
            valflt=float(value))
    elif metric_value in [MACH_STATUS_CAMBIO_MOLDE, MACH_STATUS_PREPARACION, MACH_STATUS_PRODUCCION,
                          MACH_STATUS_LIMPIEZA, MACH_STATUS_PREVENTIVO, MACH_STATUS_CORRECTIVO]:
        result = SensorMachine(
            topic=topic.value,
            machine=machine,
            metric=metric,
            valstr=metric_value)
    else:
        print("=====> no se que es")
        print(topic)
        return None

    # print(f"=====> {result}")
    return result


async def _get_active_topics_to_subscribe(context: EventContext) -> List[str]:
    mo = db(context.env)
    # await client.subscribe("Máquina/M10/#")
    results = []
    cursor = mo[IDX_MACHINE].find({'realtime_status': True})
    for doc in await cursor.to_list(length=100):
        results.append(f"Máquina/{doc['code']}/#")

    return results
