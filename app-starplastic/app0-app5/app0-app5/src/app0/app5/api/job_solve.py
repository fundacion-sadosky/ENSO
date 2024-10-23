"""
Job: job-solve
"""
from typing import Union

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.dataobjects.payload import Payload

from app0.admin.db import db
from app0.admin.http import HttpRespInfo
from app0.admin.util import app_util, IDX_NOTIFICATION
from app0.admin.notification import Notification

from app0.app5.model import ModelJob
from app0.app5.util import IDX_JOB, date_util

__steps__ = ['run']
__api__ = event_api(
    payload=(ModelJob, "Model Job"),
    responses={
        200: (ModelJob, "Model Job"),
        403: (HttpRespInfo, "Operation forbidden"),
        404: (HttpRespInfo, "Object not found")
    }
)


async def run(payload: ModelJob, context: EventContext) -> Union[ModelJob, HttpRespInfo]:
    es = db(context.env)
    # TODO do some validations if apply
    # save the job
    payload.status = app_util.STATUS_READY
    await _save_model_job(es, payload)
    await _save_notification(es, payload)
    return payload


async def __postprocess__(payload: Union[ModelJob, HttpRespInfo], context: EventContext,
                          response: PostprocessHook) -> Union[ModelJob, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _save_notification(es, model_job: ModelJob):
    """Save notification of queue job"""
    assert model_job.id
    notification = Notification(
        creation_date=date_util.now(),
        user_id=app_util.SYSTEM_USER,
        user_name=app_util.SYSTEM_USER_DESC,
        app_name=app_util.APP_APP5,
        type=app_util.TYPE_JOB,
        object_type=app_util.OBJECT_JOB,
        object_id=model_job.id,
        content=f"Job queued for {app_util.APP_APP5} by {model_job.creation_user}")
    await es[IDX_NOTIFICATION].replace_one({'_id': ObjectId(notification.id)},
                                           Payload.to_obj(notification),
                                           upsert=True)


async def _save_model_job(es, model_job: ModelJob) -> ModelJob:
    col = es[IDX_JOB]
    await col.replace_one({'_id': ObjectId(model_job.id)}, Payload.to_obj(model_job), upsert=True)
    return model_job
