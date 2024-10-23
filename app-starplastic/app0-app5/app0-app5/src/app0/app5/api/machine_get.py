"""
Machine: machine-get
"""
from typing import Union

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.dataobjects.payload import Payload

from app0.admin.db import db
from app0.admin.http import HttpRespInfo
from app0.app5.machine import Machine
from app0.app5.util import IDX_MACHINE

__steps__ = ['run']

__api__ = event_api(
    query_args=[
        ('obj_id', str, "Object ID"),
    ],
    responses={
        200: (Machine, "Machine"),
        404: (str, "Not found")
    }
)


async def run(payload: None, context: EventContext,
              obj_id: str) -> Union[Machine, HttpRespInfo]:
    mo = db(context.env)
    return await _get_app(mo, obj_id)


async def __postprocess__(payload: Union[Machine, HttpRespInfo], context: EventContext,
                          response: PostprocessHook) -> Union[Machine, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _get_app(es, oid: str) -> Union[Machine, HttpRespInfo]:
    doc = await es[IDX_MACHINE].find_one(ObjectId(oid))
    if not doc:
        return HttpRespInfo(404, 'Object not found')
    return Payload.from_obj(doc, Machine)
