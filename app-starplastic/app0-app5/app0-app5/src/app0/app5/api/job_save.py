"""
Job: job-save
"""
from typing import Optional, Union

from bson.objectid import ObjectId  # type: ignore
from hopeit.dataobjects.payload import Payload
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.app.logger import app_extra_logger

from app0.admin.db import db
from app0.admin.http import HttpRespInfo

from app0.app5.model import ModelJob
from app0.app5.util import IDX_JOB, ACT_JOB_DELETE

logger, extra = app_extra_logger()

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('action', Optional[str], "Apply some action")
    ],
    payload=(ModelJob, "ModelJob"),
    responses={
        200: (ModelJob, "ModelJob"),
        400: (HttpRespInfo, "Request error"),
        403: (HttpRespInfo, "Operation forbidden"),
        404: (HttpRespInfo, "Object not found")
    }
)


async def run(payload: ModelJob, context: EventContext,
              action: Optional[str] = None) -> Optional[Union[ModelJob, HttpRespInfo]]:
    """save or make action"""
    es = db(context.env)
    if not action:
        await _save_model_job(es, payload)
    elif action == ACT_JOB_DELETE:
        await _model_job_delete(es, payload, context)
    else:
        return HttpRespInfo(400, 'Action not recognized')

    return payload


async def __postprocess__(payload: Optional[Union[ModelJob, HttpRespInfo]], context: EventContext,
                          response: PostprocessHook) -> Union[ModelJob, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    if payload is None:
        response.status = 404
        return "Object not found"
    return payload


async def _save_model_job(es, model_job: ModelJob) -> ModelJob:
    col = es[IDX_JOB]
    await col.replace_one({'_id': ObjectId(model_job.id)}, Payload.to_obj(model_job), upsert=True)
    return model_job


async def _model_job_delete(es, model_job: ModelJob, context: EventContext):
    logger.info(context, f"Deleting model_job {model_job}")
    await es[IDX_JOB].delete_one({'_id': ObjectId(model_job.id)})
