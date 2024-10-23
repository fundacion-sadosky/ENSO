"""
Apps: app-get
"""
from typing import Optional, Union

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.dataobjects.payload import Payload

from app0.admin.app import AppDef
from app0.admin.db import db
from app0.admin.util import IDX_APP

__steps__ = ['run']

__api__ = event_api(
    query_args=[
        ('obj_id', Optional[str], "App ID"),
        ('name', Optional[str], "App name"),
    ],
    responses={
        200: (AppDef, "App"),
        404: (str, "Not found")
    }
)


async def run(payload: None, context: EventContext,
              obj_id: Optional[str] = None, name: Optional[str] = None) -> Optional[AppDef]:
    es = db(context.env)
    if obj_id:
        return await get_app(es, obj_id)
    if name:
        return await get_app_by_name(es, name)
    return None


async def __postprocess__(payload: Optional[AppDef], context: EventContext,
                          response: PostprocessHook) -> Union[AppDef, str]:
    if payload is None:
        response.status = 404
        return "App not found"
    return payload


async def get_app_by_name(es, name) -> Optional[AppDef]:
    if name:
        doc = await es[IDX_APP].find_one({'name': {'$eq': name}})
        return Payload.from_obj(doc, AppDef) if doc else None
    return None


async def get_app(es, oid: str) -> Optional[AppDef]:
    doc = await es[IDX_APP].find_one(ObjectId(oid))
    return Payload.from_obj(doc, AppDef)
