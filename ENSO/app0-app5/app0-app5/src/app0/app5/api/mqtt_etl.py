"""
MQTT: mqtt-etl
"""
from typing import List, Optional
import asyncio

from bson.objectid import ObjectId  # type: ignore
from dataclasses import dataclass
from hopeit.dataobjects import dataobject
from hopeit.app.events import Spawn, service_running
from hopeit.app.logger import app_extra_logger
from hopeit.app.context import EventContext
from hopeit.dataobjects.payload import Payload

from app0.admin.db import db
from app0.app5.sensor import SensorMachine, MachineMetric, ProductMetric
from app0.app5.util import (IDX_MACHINE_METRIC, IDX_PRODUCT_METRIC, IDX_SENSOR_MACHINE, METRIC_STATUS,
                            METRIC_TIEMPO_CICLO)

logger, extra = app_extra_logger()

@dataobject
@dataclass
class SensorToProcess:
    list: List[SensorMachine]


__steps__ = ['summarize_mqtt', 'set_processed']


async def __service__(context: EventContext) -> Spawn[SensorToProcess]:
    mo = db(context.env)
    await _validate_collections(mo)
    interval = 120  # 2 minuto
    while service_running(context):
        print("=========================>")
        print("=====> procesando señales...")
        print("=========================>")
        filter_query = {'processed': {'$eq': False}}
        cursor = mo[IDX_SENSOR_MACHINE].find(filter_query)
        yield SensorToProcess(list=[Payload.from_obj(doc, SensorMachine) for doc in await cursor.to_list(length=5000)])

        await asyncio.sleep(interval)


async def summarize_mqtt(payload: SensorToProcess, context: EventContext) -> Optional[SensorToProcess]:
    mo = db(context.env)
    print("=========================>")
    print(f"=====> summarize_mqtt START: {len(payload.list)} registros...")
    print("=========================>")
    try:
        for sense in payload.list:
            assert sense.sense_time
            if sense.metric == METRIC_STATUS:
                await _summarize_mqtt_machine_status(mo, sense)
            elif sense.metric == METRIC_TIEMPO_CICLO:
                # TODO que hacemos con el tiempo de ciclo???
                await _summarize_mqtt_machine_tiempo_ciclo(mo, sense)
    except Exception as e:
        print(f"Error ETL sensor processing {e}")
        return None
    print("=========================>")
    print("=====> summarize_mqtt END")
    print("=========================>")

    return payload


async def set_processed(payload: SensorToProcess, context: EventContext) -> Optional[SensorToProcess]:
    print("=========================>")
    print("=====> set processed START")
    print("=========================>")
    mo = db(context.env)
    try:
        for sense in payload.list:
            sense.processed = True
            await mo[IDX_SENSOR_MACHINE].update_one({'_id': ObjectId(sense.id)},
                                                    {"$set": {'processed': True}})
    except Exception as e:
        print(f"Error ETL sensor processing {e}")
        return None
    print("=========================>")
    print("=====> set processed END")
    print("=========================>")

    return payload


async def _validate_collections(mo):
    query = {"name": {"$regex": r"^(?!system\.)"}}
    coll_names = await mo.list_collection_names(filter=query)
    if IDX_MACHINE_METRIC not in coll_names:
        await mo.create_collection(IDX_MACHINE_METRIC)
    if IDX_PRODUCT_METRIC not in coll_names:
        await mo.create_collection(IDX_PRODUCT_METRIC)


async def _summarize_mqtt_machine_tiempo_ciclo(mo, sense: SensorMachine):
    hour = sense.sense_time.hour
    status_hour = f"{hour}_{hour+1}"
    status_date = sense.sense_time.strftime('%Y%m%d')

    # query if exists metric for that hour, date, machine, product and metric
    cursor = mo[IDX_PRODUCT_METRIC].find({'$and': [{'metric_date': {'$eq': status_date}},
                                                   {'metric_hour': {'$eq': status_hour}},
                                                   {'machine': {'$eq': sense.machine}},
                                                   {'metric': {'$eq': METRIC_TIEMPO_CICLO}}]})
    objs = [Payload.from_obj(doc, ProductMetric) for doc in await cursor.to_list(length=100)]
    if len(objs)==0:
        # no metric in frame
        machine_metric = ProductMetric(
            metric_date=status_date,
            metric_hour=status_hour,
            machine=sense.machine,
            product='DESCONOCIDO',
            metric=METRIC_TIEMPO_CICLO,
            metric_qtyflt=sense.valflt,
        )
        await mo[IDX_PRODUCT_METRIC].replace_one({'_id': ObjectId(machine_metric.id)},
                                                 Payload.to_obj(machine_metric), upsert=True)
    elif len(objs)==1:
        # update metric
        obj = objs[0]
        await mo[IDX_PRODUCT_METRIC].update_one({'_id': ObjectId(obj.id)},
                                                {"$set": {'metric_qtyflt': obj.metric_qtyflt+sense.valflt}})
    else:
        raise ValueError(f"Product Metric: {len(objs)} registros para {status_date}-{status_hour}-{sense.machine}-{sense.product}-{sense.metric}")  # noqa


async def _summarize_mqtt_machine_status(mo, sense: SensorMachine):
    hour = sense.sense_time.hour
    status_hour = f"{hour}_{hour+1}"
    status_date = sense.sense_time.strftime('%Y%m%d')

    # query if exists metric for that hour, date, machine and metric
    cursor = mo[IDX_MACHINE_METRIC].find({'$and': [{'metric_date': {'$eq': status_date}},
                                                   {'metric_hour': {'$eq': status_hour}},
                                                   {'machine': {'$eq': sense.machine}},
                                                   {'metric': {'$eq': sense.metric}},
                                                   {'metric_value': {'$eq': sense.valstr}}]})
    objs = [Payload.from_obj(doc, MachineMetric) for doc in await cursor.to_list(length=100)]
    if len(objs)==0:
        # no metric in frame
        machine_metric = MachineMetric(
            metric_date=status_date,
            metric_hour=status_hour,
            machine=sense.machine,
            metric=sense.metric,
            metric_value=sense.valstr,
            metric_qty=1,
        )
        await mo[IDX_MACHINE_METRIC].replace_one({'_id': ObjectId(machine_metric.id)},
                                                 Payload.to_obj(machine_metric), upsert=True)
    elif len(objs)==1:
        # update metric
        obj = objs[0]
        await mo[IDX_MACHINE_METRIC].update_one({'_id': ObjectId(obj.id)},
                                                {"$set": {'metric_qty': obj.metric_qty+1}})
    else:
        raise ValueError(f"Machine Metric: {len(objs)} registros para {status_date}-{status_hour}-{sense.machine}-{sense.metric}-{sense.valstr}")  # noqa
