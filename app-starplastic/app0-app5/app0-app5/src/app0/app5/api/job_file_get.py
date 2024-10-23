"""
Job: job-file-load
"""
from typing import Optional

from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.app.logger import app_extra_logger
from hopeit.dataobjects import BinaryDownload

from app0.admin.util.object_storage import ObjectStorage, ObjectStorageConf, ObjectStorageConnConfig
from app0.admin.util import app_util

object_store: Optional[ObjectStorage] = None
logger, extra = app_extra_logger()

__steps__ = ['get_object']
__api__ = event_api(
    query_args=[
        ('job_id', str, "Job Id"),
        ('doc_id', str, "Resource filename"),
    ],
    responses={
        200: (BinaryDownload, 'File contents'),
        404: (str, "File not found")
    }
)


async def __init_event__(context: EventContext):
    global object_store
    if object_store is None:
        config: ObjectStorageConnConfig = context.settings(key='data_store', datatype=ObjectStorageConnConfig)
        bucket: ObjectStorageConf = context.settings(key='res_docs', datatype=ObjectStorageConf)
        object_store = await ObjectStorage().connect(conn_config=config, bucket=bucket.bucket)


async def get_object(payload: None, context: EventContext, *,
                     job_id: str, doc_id: str) -> Optional[str]:
    """
    Retrieve file
    """
    return f"{app_util.APP_APP5_RESOURCE_FOLDER}/{job_id}/{doc_id}"


async def __postprocess__(file_name: Optional[str], context: EventContext, response: PostprocessHook) -> str:
    assert object_store
    if file_name:
        logger.info(context, f"Getting {file_name}...")
        await object_store.get_streamed_response(file_name=file_name,
                                                 context=context,
                                                 response=response)
        return "Done"
    response.status = 400
    return "Object not found"
