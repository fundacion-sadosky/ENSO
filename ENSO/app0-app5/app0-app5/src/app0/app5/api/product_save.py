"""
Product: product-save
"""
from typing import Union, Optional

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.app.logger import app_extra_logger
from hopeit.dataobjects.payload import Payload

from app0.admin.http import HttpRespInfo
from app0.admin.db import db
from app0.app5.product import Product
from app0.app5.util import IDX_PRODUCT


logger, extra = app_extra_logger()

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('action', Optional[str], "Apply some action")
    ],
    payload=(Product, "Product Info"),
    responses={
        200: (Product, "Product updated"),
        400: (str, "Request error"),
        403: (str, "Forbidden"),
        404: (str, "Object not found")
    }
)


async def run(payload: Product, context: EventContext,
              action: Optional[str] = None) -> Union[Product, HttpRespInfo]:
    """App save and actions"""
    mo = db(context.env)
    # check user admin
    # role = context.auth_info['payload'].get('roles', 'noauth')
    # if ROLE_ADMIN not in roles:
    #     return HttpRespInfo(403, 'User is not admin')

    if not action:
        payload = await _save_product(mo, payload)
    else:
        return HttpRespInfo(400, 'Action not recognized')
    return payload


async def __postprocess__(payload: Union[Product, HttpRespInfo], context: EventContext,
                          response: PostprocessHook) -> Union[Product, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _save_product(mo, product: Product) -> Product:
    col = mo[IDX_PRODUCT]

    await col.replace_one({'_id': ObjectId(product.id)}, Payload.to_obj(product), upsert=True)

    return product
