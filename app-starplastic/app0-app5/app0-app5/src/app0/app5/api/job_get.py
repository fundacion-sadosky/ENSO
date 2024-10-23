"""
Job: job-get
"""
from typing import Optional, Union

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.dataobjects.payload import Payload

from app0.admin.db import db
from app0.admin.http import HttpRespInfo

from app0.app5.model import ModelJob
from app0.app5.util import IDX_JOB

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('obj_id', str, "Job ID"),
    ],
    responses={
        200: (ModelJob, "Object updated"),
        403: (str, "Operation forbidden"),
        404: (str, "Object not found")
    }
)


async def run(payload: None, context: EventContext,
              obj_id: str) -> Union[ModelJob, HttpRespInfo]:
    es = db(context.env)
    model_job = await _get_job(es, obj_id)
    if model_job:
        return model_job
    return HttpRespInfo(404, "Not found")


async def __postprocess__(payload: Union[ModelJob, HttpRespInfo],
                          context: EventContext,
                          response: PostprocessHook) -> Union[ModelJob, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _get_job(es, oid: str) -> Optional[ModelJob]:
    doc = await es[IDX_JOB].find_one(ObjectId(oid))
    return Payload.from_obj(doc, ModelJob)
