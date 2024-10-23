"""
KPI: kpi-data
"""
from typing import Union, Optional, List
from datetime import datetime

from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.dataobjects.payload import Payload

from app0.admin.db import db
from app0.admin.http import HttpRespInfo
from app0.app5.machine import Machine, MachineDataStatus, KpiData, KpiDataMachine
from app0.app5.util import (date_util, ACT_KPI_MACHINES_LAST, ACT_KPI_MACHINES_MONTH, IDX_MACHINE, METRIC_STATUS,
                            IDX_MACHINE_METRIC, MACH_STATUS_SIN_CONEXION)
from app0.app5.util.machine_util import (gen_date_hour_array, group_states_sum_time)
from app0.app5.sensor import MachineMetric

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('action', Optional[str], "Some action"),
        ('m', Optional[str], "Month (1-12)"),
        ('y', Optional[str], "Year")
    ],
    responses={
        200: (KpiData, "KpiData object"),
        400: (str, "Bad request"),
        403: (str, "Operation forbidden"),
        404: (str, "Object not found")
    }
)


async def run(payload: None, context: EventContext, action: Optional[str] = None,
              m: Optional[str] = None, y: Optional[str] = None) -> Union[KpiData, HttpRespInfo]:
    mo = db(context.env)
    if not action:
        return HttpRespInfo(400, 'Action not recognized')
    elif action == ACT_KPI_MACHINES_LAST:
        return await _get_machine_kpi_last(mo)
    elif action == ACT_KPI_MACHINES_MONTH:
        return await _get_machine_kpi_month(mo, m, y)

    return HttpRespInfo(400, 'Action not recognized')


async def __postprocess__(payload: Union[KpiData, HttpRespInfo],
                          context: EventContext,
                          response: PostprocessHook) -> Union[KpiData, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _get_machine_kpi_last(mo) -> List[Machine]:
    """
    get machines with status
    """
    today = date_util.now()
    from1 = today.subtract(days=1)
    from7 = today.subtract(days=7)
    from15 = today.subtract(days=15)

    cursor = mo[IDX_MACHINE].find({'realtime_status': True}, sort=[('nbr', 1)])
    results = [Payload.from_obj(doc, Machine) for doc in await cursor.to_list(length=50)]
    kpi_machines = []
    for machine in results:
        kpi_machines.append(KpiDataMachine(
            nbr=machine.nbr,
            name=machine.name,
            code=machine.code,
            last_status_date=machine.last_status_date,
            last_status=machine.last_status,
            sense_last_1d=await _count_machine_metric_status(mo, machine.code, from1, from1),
            sense_last_7d=await _count_machine_metric_status(mo, machine.code, from7, from1),
            sense_last_15d=await _count_machine_metric_status(mo, machine.code, from15, from1),
        ))
    data = KpiData(
        machines = kpi_machines,
    )

    return data


async def _get_machine_kpi_month(mo, month: Optional[str] = None, year: Optional[str] = None) -> List[Machine]:
    """
    get machines with status
    """
    fmonth, tmonth = date_util.get_first_and_last_day_of_month(year, month)

    cursor = mo[IDX_MACHINE].find({'realtime_status': True}, sort=[('nbr', 1)])
    results = [Payload.from_obj(doc, Machine) for doc in await cursor.to_list(length=50)]
    kpi_machines = []
    for machine in results:
        status_list = await _get_machine_metric_status(mo, machine.code, fmonth, tmonth)
        kpi_machines.append(KpiDataMachine(
            nbr=machine.nbr,
            name=machine.name,
            code=machine.code,
            last_status_date=machine.last_status_date,
            last_status=machine.last_status,
            sense_month=await _count_machine_metric_status(mo, machine.code, fmonth, tmonth),
            status_list=status_list,
        ))
    data = KpiData(
        machines = kpi_machines,
    )

    return data


async def _count_machine_metric_status(mo, machine: str, dt_from: datetime, dt_to: datetime) -> int:
    """get data"""
    str_from = dt_from.strftime('%Y%m%d')
    str_to = dt_to.strftime('%Y%m%d')

    filter_query = { 'metric_date': {'$gte': str_from, '$lte': str_to},
                     'metric': METRIC_STATUS,
                     'machine': machine }

    cursor = mo[IDX_MACHINE_METRIC].aggregate([
        {'$match': filter_query},
        {'$group': { '_id': "$metric_value", 'total': { '$sum': "$metric_qty" } }}
    ])
    total_sense = 0
    for doc in await cursor.to_list(length=100):
        total_sense += doc['total']

    return total_sense


async def _get_machine_metric_status(mo, machine: str, dt_from: datetime, dt_to: datetime) -> List[MachineDataStatus]:
    """get data"""
    str_from = dt_from.strftime('%Y%m%d')
    str_to = dt_to.strftime('%Y%m%d')

    filter_query = { 'metric_date': {'$gte': str_from, '$lte': str_to},
                     'metric': METRIC_STATUS,
                     'machine': machine }

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

    return status_list
