"""
Machine: machine-save
"""
from typing import Union, Optional

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.app.logger import app_extra_logger
from hopeit.dataobjects.payload import Payload

from app0.admin.common import IdDescription
from app0.admin.http import HttpRespInfo
from app0.admin.db import db
from app0.app5.machine import Machine
from app0.app5.util import (IDX_MACHINE, ACT_MACHINE_STATUS_CAMBIO_MOLDE, ACT_MACHINE_STATUS_PREPARACION,
                            ACT_MACHINE_STATUS_LIMPIEZA, ACT_MACHINE_STATUS_PREVENTIVO, ACT_MACHINE_STATUS_CORRECTIVO,
                            MACH_STATUS_CAMBIO_MOLDE, MACH_STATUS_PREPARACION, MACH_STATUS_LIMPIEZA,
                            MACH_STATUS_PREVENTIVO, MACH_STATUS_CORRECTIVO, date_util)
from app0.app5.util.machine_util import get_estado


logger, extra = app_extra_logger()

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('action', Optional[str], "Apply some action")
    ],
    payload=(Machine, "Machine Info"),
    responses={
        200: (Machine, "Machine updated"),
        400: (str, "Request error"),
        403: (str, "Forbidden"),
        404: (str, "Object not found")
    }
)


async def run(payload: Machine, context: EventContext,
              action: Optional[str] = None) -> Union[Machine, HttpRespInfo]:
    """App save and actions"""
    mo = db(context.env)
    # check user admin
    # role = context.auth_info['payload'].get('roles', 'noauth')
    # if ROLE_ADMIN not in roles:
    #     return HttpRespInfo(403, 'User is not admin')

    if not action:
        payload = await _save_machine(mo, payload)
    elif action == ACT_MACHINE_STATUS_CAMBIO_MOLDE:
        return await _set_status_machine(mo, payload, get_estado(MACH_STATUS_CAMBIO_MOLDE))
    elif action == ACT_MACHINE_STATUS_PREPARACION:
        return await _set_status_machine(mo, payload, get_estado(MACH_STATUS_PREPARACION))
    elif action == ACT_MACHINE_STATUS_LIMPIEZA:
        return await _set_status_machine(mo, payload, get_estado(MACH_STATUS_LIMPIEZA))
    elif action == ACT_MACHINE_STATUS_PREVENTIVO:
        return await _set_status_machine(mo, payload, get_estado(MACH_STATUS_PREVENTIVO))
    elif action == ACT_MACHINE_STATUS_CORRECTIVO:
        return await _set_status_machine(mo, payload, get_estado(MACH_STATUS_CORRECTIVO))
    else:
        return HttpRespInfo(400, 'Action not recognized')
    return payload


async def __postprocess__(payload: Union[Machine, HttpRespInfo], context: EventContext,
                          response: PostprocessHook) -> Union[Machine, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _save_machine(mo, machine: Machine) -> Machine:
    col = mo[IDX_MACHINE]

    await col.update_one({'_id': ObjectId(machine.id)},
                         {"$set": {"name": machine.name,
                                   "code": machine.code,
                                   "description": machine.description,
                                   "manufacturer": machine.manufacturer,
                                   "model": machine.model,
                                   "enabled": machine.enabled,
                                   "realtime_status": machine.realtime_status}})

    return machine


async def _set_status_machine(mo, machine: Machine, status: IdDescription) -> Machine:
    col = mo[IDX_MACHINE]
    machine.last_status_date = date_util.now()
    machine.last_status = status
    await col.update_one({'_id': ObjectId(machine.id)},
                         {"$set": {'last_status_date': machine.last_status_date.isoformat(),
                                   'last_status': Payload.to_obj(status)}})

    return machine
