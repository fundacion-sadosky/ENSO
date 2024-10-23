"""
MQTT: mqtt-processor
"""
from typing import Optional

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.context import EventContext
from hopeit.app.logger import app_extra_logger
from hopeit.dataobjects.payload import Payload
from app0.admin.db import db
from app0.app5.sensor import SensorMachine
from app0.app5.util import (IDX_MACHINE, IDX_SENSOR_MACHINE,
                            MACH_STATUS_CAMBIO_MOLDE, MACH_STATUS_CORRECTIVO,
                            MACH_STATUS_LIMPIEZA, MACH_STATUS_PREPARACION,
                            MACH_STATUS_PREVENTIVO, MACH_STATUS_PRODUCCION)
from app0.app5.util.machine_util import get_estado

logger, extra = app_extra_logger()
estados_status = [MACH_STATUS_CAMBIO_MOLDE, MACH_STATUS_PREPARACION, MACH_STATUS_PRODUCCION, MACH_STATUS_LIMPIEZA,
                  MACH_STATUS_PREVENTIVO, MACH_STATUS_CORRECTIVO]
__steps__ = ['insert_sense', 'update_machine_last_status']


async def insert_sense(payload: SensorMachine, context: EventContext) -> Optional[SensorMachine]:
    """
    process SensorMachine incoming
    """
    mo = db(context.env)
    col = mo[IDX_SENSOR_MACHINE]
    await col.replace_one({'_id': ObjectId(payload.id)}, Payload.to_obj(payload), upsert=True)

    return payload


async def update_machine_last_status(payload: SensorMachine, context: EventContext) -> Optional[SensorMachine]:
    """
    update machine last status
    """
    mo = db(context.env)
    col = mo[IDX_MACHINE]
    if payload.valstr and payload.valstr in estados_status:
        new_status = get_estado(payload.valstr)
        print(f'===> Updating machine {payload.machine} - {payload.sense_time.isoformat()}')
        await col.update_one({'code': payload.machine}, {'$set': {'last_status_date': payload.sense_time.isoformat(),
                                                                  'last_status': Payload.to_obj(new_status)}})

    return payload
