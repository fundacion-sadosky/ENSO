"""
Roles: role-get
"""
from typing import Optional, Union

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.dataobjects.payload import Payload

from app0.admin.app import AppRole
from app0.admin.db import db
from app0.admin.util import IDX_ROLE

__steps__ = ['run']

__api__ = event_api(
    query_args=[
        ('obj_id', Optional[str], "Role ID"),
        ('name', Optional[str], "Role name")
    ],
    responses={
        200: (AppRole, "App Role"),
        404: (str, "Not found")
    }
)


async def run(payload: None, context: EventContext,
              obj_id: Optional[str] = None, name: Optional[str] = None) -> Optional[AppRole]:
    es = db(context.env)
    if obj_id:
        return await get_role(es, obj_id)
    if name:
        return await get_role_by_name(es, name)
    return None


async def __postprocess__(payload: Optional[AppRole], context: EventContext,
                          response: PostprocessHook) -> Union[AppRole, str]:
    if payload is None:
        response.status = 404
        return "Role not found"
    return payload


async def get_role(es, oid: str) -> Optional[AppRole]:
    doc = await es[IDX_ROLE].find_one(ObjectId(oid))
    return Payload.from_obj(doc, AppRole)


async def get_role_by_name(es, name) -> Optional[AppRole]:
    if name:
        doc = await es[IDX_ROLE].find_one({'name': {'$eq': name}})
        if doc:
            return Payload.from_obj(doc, AppRole)
    return None
