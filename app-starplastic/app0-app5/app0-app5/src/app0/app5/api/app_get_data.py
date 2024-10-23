"""
Admin: app-get-data
"""
from typing import Union, Optional, List
from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.dataobjects.payload import Payload

from app0.admin.db import db
from app0.admin.http import HttpRespInfo

from app0.app5.app import AppData
from app0.app5.machine import Machine
from app0.app5.util import ACT_MACHINE_STATUS, IDX_MACHINE, IDX_PRODUCT_METRIC, MACH_STATUS_PRODUCCION
from app0.app5.util import date_util

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('action', Optional[str], "Some action")
    ],
    responses={
        200: (AppData, "App data object"),
        400: (str, "Bad request"),
        403: (str, "Operation forbidden"),
        404: (str, "Object not found")
    }
)


async def run(payload: None, context: EventContext, action: Optional[str] = None) -> Union[AppData, HttpRespInfo]:
    mo = db(context.env)
    if not action:
        app_data = await _get_config(mo)
        return app_data
    elif action == ACT_MACHINE_STATUS:
        return await _get_machine_status(mo)

    return HttpRespInfo(400, 'Action not recognized')


async def __postprocess__(payload: Union[AppData, HttpRespInfo],
                          context: EventContext,
                          response: PostprocessHook) -> Union[AppData, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _get_config(mo) -> AppData:
    """
    contar machines monitoring, global production, alert
    db['app5.machine'].count_documents({'last_status.value': {'$eq': 'EnProducción'}})
    """
    machines_working = await _machines_working(mo)
    production = await _product_last(mo, 7)
    data = AppData(
        machines_working=machines_working,
        production=production,
        alerts=0,
    )
    return data


async def _get_machine_status(mo) -> List[Machine]:
    """
    get machines with status
    """
    cursor = mo[IDX_MACHINE].find({'realtime_status': True}, sort=[('nbr', 1)])
    results = [Payload.from_obj(doc, Machine) for doc in await cursor.to_list(length=50)]
    data = AppData(
        machines = results,
    )

    return data


async def _machines_working(mo) -> int:
    return await mo[IDX_MACHINE].count_documents({'last_status.value': {'$eq': MACH_STATUS_PRODUCCION}})


async def _product_last(mo, days: int) -> int:
    dt_from, dt_to = date_util.now_minus_days(days)
    str_from = dt_from.strftime('%Y%m%d')
    str_to = dt_to.strftime('%Y%m%d')

    cursor = mo[IDX_PRODUCT_METRIC].aggregate([
        {'$match': { 'metric_date': {'$gte': str_from, '$lte': str_to} }},
        {'$group': { '_id': "$product", 'total': { '$sum': "$metric_qty" } }}
    ])
    qty = 0
    for doc in await cursor.to_list(length=100):
        qty += doc['total']
    return qty
