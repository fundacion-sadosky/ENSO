"""
Product: product-get
"""
from typing import Union

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.dataobjects.payload import Payload

from app0.admin.db import db
from app0.admin.http import HttpRespInfo
from app0.app5.product import Product
from app0.app5.util import IDX_PRODUCT

__steps__ = ['run']

__api__ = event_api(
    query_args=[
        ('obj_id', str, "Object ID"),
    ],
    responses={
        200: (Product, "Product"),
        404: (str, "Not found")
    }
)


async def run(payload: None, context: EventContext,
              obj_id: str) -> Union[Product, HttpRespInfo]:
    mo = db(context.env)
    return await _get_app(mo, obj_id)


async def __postprocess__(payload: Union[Product, HttpRespInfo], context: EventContext,
                          response: PostprocessHook) -> Union[Product, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _get_app(es, oid: str) -> Union[Product, HttpRespInfo]:
    doc = await es[IDX_PRODUCT].find_one(ObjectId(oid))
    if not doc:
        return HttpRespInfo(404, 'Object not found')
    return Payload.from_obj(doc, Product)
