"""
Machine: machine-data
"""
from typing import Union, Optional
from datetime import datetime

from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.dataobjects.payload import Payload

from app0.admin.db import db
from app0.admin.http import HttpRespInfo

from app0.app5.machine import MachineData, MachineDataStatus
from app0.app5.util import (ACT_MACHINE_METRIC_STATUS, IDX_MACHINE_METRIC, METRIC_STATUS,
                            ACT_MACHINE_METRIC_STATUS_PER_DAY, ACT_MACHINE_METRIC_STATUS_PER_HOUR,
                            ACT_MACHINE_METRIC_STATUS_TIME, MACH_STATUS_SIN_CONEXION,
                            ACT_MACHINE_METRIC_STATUS_PER_DAY_SENSE, date_util)
from app0.app5.util.machine_util import (gen_date_hour_array, group_states_sum_time, group_states_day_sum_time,
                                         group_states_day_hour_sum_time)
from app0.app5.sensor import MachineMetric

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('action', Optional[str], "action"),
        ('machine', Optional[str], "Machine"),
        ('date_from', Optional[str], "Date from (YYYYMMDD)"),
        ('date_to', Optional[str], "Date to (YYYYMMDD)")
    ],
    responses={
        200: (MachineData, "MachineData data object"),
        400: (str, "Bad request"),
        403: (str, "Operation forbidden"),
        404: (str, "Object not found")
    }
)


async def run(payload: None, context: EventContext, action: Optional[str] = None,
              machine: Optional[str] = None, date_from: Optional[str] = None,
              date_to: Optional[str] = None) -> Union[MachineData, HttpRespInfo]:
    mo = db(context.env)
    if action == ACT_MACHINE_METRIC_STATUS:
        return await _get_machine_metric_status(mo, machine, date_from, date_to)
    elif action == ACT_MACHINE_METRIC_STATUS_TIME:
        return await _get_machine_metric_status_v2(mo, machine, date_from, date_to)
    elif action == ACT_MACHINE_METRIC_STATUS_PER_DAY:
        return await _get_machine_metric_status_per_day(mo, machine, date_from, date_to)
    elif action == ACT_MACHINE_METRIC_STATUS_PER_DAY_SENSE:
        return await _get_machine_metric_status_per_day_sense(mo, machine, date_from, date_to)
    elif action == ACT_MACHINE_METRIC_STATUS_PER_HOUR:
        return await _get_machine_metric_status_per_hour(mo, machine, date_from, date_to)

    return HttpRespInfo(400, 'Action not recognized')


async def __postprocess__(payload: Union[MachineData, HttpRespInfo],
                          context: EventContext,
                          response: PostprocessHook) -> Union[MachineData, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _get_machine_metric_status(mo, machine: Optional[str] = None,
                                     date_from: Optional[str] = None, date_to: Optional[str] = None) -> MachineData:
    """get data"""
    if date_from and date_to:
        str_from = date_from
        str_to = date_to
    else:
        dt_from, dt_to = date_util.now_minus_days(7)
        str_from = dt_from.strftime('%Y%m%d')
        str_to = dt_to.strftime('%Y%m%d')

    filter_query = { 'metric_date': {'$gte': str_from, '$lte': str_to},
                     'metric': METRIC_STATUS }
    if machine:
        filter_query['machine']=machine

    cursor = mo[IDX_MACHINE_METRIC].aggregate([
        {'$match': filter_query},
        {'$group': { '_id': "$metric_value", 'total': { '$sum': "$metric_qty" } }}
    ])
    status_list = []
    total_sense = 0
    for doc in await cursor.to_list(length=100):
        status_list.append(MachineDataStatus(
            status=doc['_id'],
            qty=doc['total'],
        ))
        total_sense += doc['total']
    machine_data = MachineData(
        machine=machine,
        date_from=str_from,
        date_to=str_to,
        total_sense=total_sense,
        status_list = status_list,
    )
    return machine_data


async def _get_machine_metric_status_v2(mo, machine: Optional[str] = None,
                                        date_from: Optional[str] = None, date_to: Optional[str] = None) -> MachineData:
    """get data"""
    if date_from and date_to:
        str_from = date_from
        str_to = date_to
    else:
        dt_from, dt_to = date_util.now_minus_days(7)
        str_from = dt_from.strftime('%Y%m%d')
        str_to = dt_to.strftime('%Y%m%d')

    filter_query = { 'metric_date': {'$gte': str_from, '$lte': str_to},
                     'metric': METRIC_STATUS }
    if machine:
        filter_query['machine']=machine

    cursor = mo[IDX_MACHINE_METRIC].find(filter_query)
    objs = [Payload.from_obj(doc, MachineMetric) for doc in await cursor.to_list(length=5000)]

    # generate date hours array
    date_hours = gen_date_hour_array(datetime.strptime(str_from, '%Y%m%d'), datetime.strptime(str_to, '%Y%m%d'))
    # sumarizar por hora
    status_list = []
    total_sense = 0
    total_seconds = 0
    for date_hour in date_hours:
        SECONDS = 3600
        # filter objs by date and hour
        subobjs = [item for item in objs if item.metric_date == date_hour['date'] and item.metric_hour == date_hour['hour']]  # noqa
        # filter objs by date and hour with less than 20 MachineMetric
        subobjs = [obj for obj in subobjs if obj.metric_qty >= 20]
        # get sense in that timeframe
        hour_sense = sum(item.metric_qty for item in subobjs)
        # if total sense
        total_seconds += SECONDS
        total_sense += hour_sense
        if hour_sense == 0:
            # estado desconocido en esa hora
            status_list.append(MachineDataStatus(
                status=MACH_STATUS_SIN_CONEXION,
                day=date_hour['date'],
                hour=date_hour['hour'],
                qty=0,
                seconds=SECONDS
            ))
        else:
            # divido la cantidad de sense por hora
            seconds_per_sense = SECONDS / hour_sense
            # por cada estado, pondero por la cantidad de sensados
            for item in subobjs:
                status_list.append(MachineDataStatus(
                    status=item.metric_value,
                    day=date_hour['date'],
                    hour=date_hour['hour'],
                    qty=item.metric_qty,
                    seconds=int(item.metric_qty*seconds_per_sense),
                ))
    status_list = group_states_sum_time(status_list)
    machine_data = MachineData(
        machine=machine,
        date_from=str_from,
        date_to=str_to,
        total_sense=total_sense,
        total_seconds=total_seconds,
        status_list = status_list,
    )
    return machine_data


async def _get_machine_metric_status_per_day(mo, machine: Optional[str] = None,
                                             date_from: Optional[str] = None,
                                             date_to: Optional[str] = None) -> MachineData:
    """get data"""
    if date_from and date_to:
        str_from = date_from
        str_to = date_to
    else:
        dt_from, dt_to = date_util.now_minus_days(7)
        str_from = dt_from.strftime('%Y%m%d')
        str_to = dt_to.strftime('%Y%m%d')

    filter_query = {'metric_date': {'$gte': str_from, '$lte': str_to},
                    'metric': METRIC_STATUS }
    if machine:
        filter_query['machine']=machine

    cursor = mo[IDX_MACHINE_METRIC].find(filter_query)
    objs = [Payload.from_obj(doc, MachineMetric) for doc in await cursor.to_list(length=5000)]
    # generate date hours array
    date_hours = gen_date_hour_array(datetime.strptime(str_from, '%Y%m%d'), datetime.strptime(str_to, '%Y%m%d'))
    # sumarizar por hora
    status_list = []
    total_sense = 0
    total_seconds = 0
    for date_hour in date_hours:
        SECONDS = 3600
        # filter objs by date and hour
        subobjs = [item for item in objs if item.metric_date == date_hour['date'] and item.metric_hour == date_hour['hour']]  # noqa
        # filter objs by date and hour with less than 20 MachineMetric
        subobjs = [obj for obj in subobjs if obj.metric_qty >= 20]
        # get sense in that timeframe
        hour_sense = sum(item.metric_qty for item in subobjs)
        # if total sense
        total_seconds += SECONDS
        total_sense += hour_sense
        if hour_sense == 0:
            # estado desconocido en esa hora
            status_list.append(MachineDataStatus(
                status=MACH_STATUS_SIN_CONEXION,
                day=date_hour['date'],
                hour=date_hour['hour'],
                qty=0,
                seconds=SECONDS
            ))
        else:
            # divido la cantidad de sense por hora
            seconds_per_sense = SECONDS / hour_sense
            # por cada estado, pondero por la cantidad de sensados
            for item in subobjs:
                status_list.append(MachineDataStatus(
                    status=item.metric_value,
                    day=date_hour['date'],
                    hour=date_hour['hour'],
                    qty=item.metric_qty,
                    seconds=int(item.metric_qty*seconds_per_sense),
                ))

    status_list = group_states_day_sum_time(status_list)
    machine_data = MachineData(
        machine=machine,
        date_from=str_from,
        date_to=str_to,
        total_sense=total_sense,
        total_seconds=total_seconds,
        status_list = status_list,
    )
    return machine_data


async def _get_machine_metric_status_per_hour(mo, machine: Optional[str] = None,
                                              date_from: Optional[str] = None,
                                              date_to: Optional[str] = None) -> MachineData:
    """get data"""
    if date_from and date_to:
        str_from = date_from
        str_to = date_to
    else:
        dt_from, dt_to = date_util.now_minus_days(7)
        str_from = dt_from.strftime('%Y%m%d')
        str_to = dt_to.strftime('%Y%m%d')

    filter_query = {'metric_date': {'$gte': str_from, '$lte': str_to},
                    'metric': METRIC_STATUS }
    if machine:
        filter_query['machine']=machine

    cursor = mo[IDX_MACHINE_METRIC].find(filter_query)
    objs = [Payload.from_obj(doc, MachineMetric) for doc in await cursor.to_list(length=5000)]
    # generate date hours array
    date_hours = gen_date_hour_array(datetime.strptime(str_from, '%Y%m%d'), datetime.strptime(str_to, '%Y%m%d'))
    # sumarizar por hora
    status_list = []
    total_sense = 0
    total_seconds = 0
    for date_hour in date_hours:
        SECONDS = 3600
        # filter objs by date and hour
        subobjs = [item for item in objs if item.metric_date == date_hour['date'] and item.metric_hour == date_hour['hour']]  # noqa
        # filter objs by date and hour with less than 20 MachineMetric
        subobjs = [obj for obj in subobjs if obj.metric_qty >= 20]
        # get sense in that timeframe
        hour_sense = sum(item.metric_qty for item in subobjs)
        # if total sense
        total_seconds += SECONDS
        total_sense += hour_sense
        if hour_sense == 0:
            # estado desconocido en esa hora
            status_list.append(MachineDataStatus(
                status=MACH_STATUS_SIN_CONEXION,
                day=date_hour['date'],
                hour=date_hour['hour'],
                qty=0,
                seconds=SECONDS
            ))
        else:
            # divido la cantidad de sense por hora
            seconds_per_sense = SECONDS / hour_sense
            # por cada estado, pondero por la cantidad de sensados
            for item in subobjs:
                status_list.append(MachineDataStatus(
                    status=item.metric_value,
                    day=date_hour['date'],
                    hour=date_hour['hour'],
                    qty=item.metric_qty,
                    seconds=int(item.metric_qty*seconds_per_sense),
                ))

    status_list = group_states_day_hour_sum_time(status_list)
    machine_data = MachineData(
        machine=machine,
        date_from=str_from,
        date_to=str_to,
        total_sense=total_sense,
        status_list = status_list,
    )
    return machine_data


async def _get_machine_metric_status_per_day_sense(
        mo, machine: Optional[str] = None, date_from: Optional[str] = None,
        date_to: Optional[str] = None) -> MachineData:
    """get data"""
    if date_from and date_to:
        str_from = date_from
        str_to = date_to
    else:
        dt_from, dt_to = date_util.now_minus_days(7)
        str_from = dt_from.strftime('%Y%m%d')
        str_to = dt_to.strftime('%Y%m%d')

    filter_query = {'metric_date': {'$gte': str_from, '$lte': str_to},
                    'metric': METRIC_STATUS }
    if machine:
        filter_query['machine']=machine

    cursor = mo[IDX_MACHINE_METRIC].aggregate([
        {'$match': filter_query},
        {'$group': {'_id': {'day': '$metric_date', 'metric': '$metric_value'},
                    'total': {'$sum': '$metric_qty'}}}
    ])
    status_list = []
    total_sense = 0
    for doc in await cursor.to_list(length=100):
        status_list.append(MachineDataStatus(
            status=doc['_id']['metric'],
            day=doc['_id']['day'],
            qty=doc['total'],
        ))
        total_sense += doc['total']
    machine_data = MachineData(
        machine=machine,
        date_from=str_from,
        date_to=str_to,
        total_sense=total_sense,
        status_list = status_list,
    )
    return machine_data
