"""
Admin: app-file-upload
"""
import os
import uuid
from typing import Optional, Union
from bson.objectid import ObjectId  # type: ignore

from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PreprocessHook
from hopeit.app.logger import app_extra_logger
from hopeit.dataobjects import BinaryAttachment
from hopeit.dataobjects.payload import Payload

from app0.admin.util.object_storage import ObjectStorage, ObjectStorageConf, ObjectStorageConnConfig
from app0.admin.db import db
from app0.admin.http import HttpRespInfo
from app0.admin.file import PlatformFile
from app0.admin.util import app_util, IDX_APP

logger, extra = app_extra_logger()
object_store: Optional[ObjectStorage] = None

__steps__ = ['put_object']
__api__ = event_api(
    query_args=[
        ('app_id', str, "App Id"),
        ('tag', Optional[str], "Tag"),
    ],
    fields=[('attachment', BinaryAttachment)],
    responses={
        200: (PlatformFile, "File info"),
        403: (HttpRespInfo, "Operation forbidden"),
        404: (HttpRespInfo, "Object not found")
    }
)


async def __init_event__(context: EventContext):
    global object_store
    if object_store is None:
        config: ObjectStorageConnConfig = context.settings(key='s3_store', datatype=ObjectStorageConnConfig)
        bucket: ObjectStorageConf = context.settings(key='bucket_docs', datatype=ObjectStorageConf)
        object_store = await ObjectStorage().connect(conn_config=config, bucket=bucket.bucket)


# pylint: disable=invalid-name
async def __preprocess__(payload: None, context: EventContext, request: PreprocessHook, *,
                         app_id: str, tag: Optional[str] = None) -> Union[str, PlatformFile]:
    assert object_store
    uploaded_file: PlatformFile = None  # type: ignore

    async for file_hook in request.files():
        _, fextension = os.path.splitext(file_hook.file_name)
        # filename format: company_id/filename.ext
        file_name = f"{str(uuid.uuid4())}{fextension}"
        object_id = f"{app_util.APP_APP_CONF_RESOURCE_FOLDER}/{app_id}/{file_name}"
        logger.info(context, f"Saving {file_name}...")
        file_info = await object_store.store_streamed_file(file_name=object_id, file_hook=file_hook)
        if file_info:
            uploaded_file = PlatformFile(
                bucket=file_info.bucket,
                filename=file_name,
                size=file_hook.size,
                src_filename=file_hook.file_name,
                object_id=object_id)
    args = await request.parsed_args()
    if not all(x in args for x in ['attachment']):
        request.status = 400
        return "Missing required fields"
    return uploaded_file


async def put_object(payload: PlatformFile, context: EventContext, *,
                     app_id: str, tag: Optional[str] = None) -> Union[PlatformFile, HttpRespInfo]:
    """
    Upload file and create notification
    """
    logger.info(context, "File uploaded...", extra=extra(file_id=payload.filename, size=payload.size))
    # agregar el log
    assert payload.creation_date
    es = db(context.env)
    await _update_app(es, payload, app_id, tag)

    return payload


async def _update_app(es, platform_file: PlatformFile, app_id: str, tag: Optional[str] = None):
    col = es[IDX_APP]
    if app_util.FILETYPE_GAMS_SOURCE == tag:
        await col.update_one({'_id': ObjectId(app_id)},
                             {'$set': {'file_resource_gams_source': Payload.to_obj(platform_file)}})
    elif app_util.FILETYPE_INPUT_SAMPLE == tag:
        await col.update_one({'_id': ObjectId(app_id)},
                             {'$set': {'file_resource_input_sample': Payload.to_obj(platform_file)}})
    elif app_util.FILETYPE_OUTPUT_SAMPLE == tag:
        await col.update_one({'_id': ObjectId(app_id)},
                             {'$set': {'file_resource_output_sample': Payload.to_obj(platform_file)}})


# async def _save_notification(es, model_job: ModelJob):
#     """Save notification of queue job"""
#     assert model_job.id
#     notification = Notification(
#         creation_date=datetime.now(tz=timezone.utc),
#         user_id=app_util.SYSTEM_USER,
#         user_name=app_util.SYSTEM_USER_DESC,
#         app_name=app_util.APP_APP1,
#         type=app_util.TYPE_JOB,
#         object_type=app_util.OBJECT_JOB,
#         object_id=model_job.id,
#         content=f"Job file uploaded for {app_util.APP_APP1} by {model_job.creation_user}")
#     await es[IDX_NOTIFICATION].replace_one({'_id': ObjectId(notification.id)},
#                                            Payload.to_obj(notification),
#                                            upsert=True)
