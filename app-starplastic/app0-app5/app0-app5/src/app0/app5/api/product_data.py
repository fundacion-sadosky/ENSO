"""
Product: product-data
"""
from typing import Union, Optional
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook

from app0.admin.db import db
from app0.admin.http import HttpRespInfo
from app0.app5.product import ProductData, ProductDataStatus
from app0.app5.util import IDX_PRODUCT_METRIC, ACT_PRODUCT_METRIC_PRODUCED_PER_DAY, METRIC_PRODUCT_PRODUCED, date_util

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('action', Optional[str], "action"),
        ('machine', Optional[str], "Machine"),
        ('date_from', Optional[str], "Date from (YYYYMMDD)"),
        ('date_to', Optional[str], "Date to (YYYYMMDD)")
    ],
    responses={
        200: (ProductData, "ProductData data object"),
        400: (str, "Bad request"),
        403: (str, "Operation forbidden"),
        404: (str, "Object not found")
    }
)


async def run(payload: None, context: EventContext, action: Optional[str] = None,
              machine: Optional[str] = None, date_from: Optional[str] = None,
              date_to: Optional[str] = None) -> Union[ProductData, HttpRespInfo]:
    mo = db(context.env)
    if action == ACT_PRODUCT_METRIC_PRODUCED_PER_DAY:
        return await _get_product_metric_produced_per_day(mo, machine, date_from, date_to)

    return HttpRespInfo(400, 'Action not recognized')


async def __postprocess__(payload: Union[ProductData, HttpRespInfo],
                          context: EventContext,
                          response: PostprocessHook) -> Union[ProductData, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _get_product_metric_produced_per_day(mo, machine: Optional[str] = None,
                                             date_from: Optional[str] = None,
                                             date_to: Optional[str] = None) -> ProductData:
    """get data"""
    if date_from and date_to:
        str_from = date_from
        str_to = date_to
    else:
        dt_from, dt_to = date_util.now_minus_days(7)
        str_from = dt_from.strftime('%Y%m%d')
        str_to = dt_to.strftime('%Y%m%d')

    filter_query = {'metric_date': {'$gte': str_from, '$lte': str_to},
                    'metric': METRIC_PRODUCT_PRODUCED }
    if machine:
        filter_query['machine']=machine

    cursor = mo[IDX_PRODUCT_METRIC].aggregate([
        {'$match': filter_query},
        {'$group': {'_id': '$metric_date',
                    'total': {'$sum': '$metric_qty'}}}
    ])
    status_list = []
    total_sense = 0
    for doc in await cursor.to_list(length=100):
        status_list.append(ProductDataStatus(
            day=doc['_id'],
            qty=doc['total'],
        ))
        total_sense += doc['total']
    product_data = ProductData(
        machine=machine,
        date_from=str_from,
        date_to=str_to,
        total_sense=total_sense,
        status_list = status_list,
    )
    return product_data
