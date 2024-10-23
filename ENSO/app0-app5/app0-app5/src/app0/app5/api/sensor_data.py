"""
Machine: sensor-data
"""
from typing import Union
from datetime import datetime

from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.dataobjects.payload import Payload
from app0.admin.db import db
from app0.admin.http import HttpRespInfo
from app0.app5.sensor import SensorData, SensorMachine
from app0.app5.util import (ACT_SENSOR_RAW_STATUS, ACT_SENSOR_RAW_TIEMPO_CICLO, IDX_SENSOR_MACHINE, METRIC_STATUS,
                            METRIC_TIEMPO_CICLO)

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('action', str, "action"),
        ('machine', str, "Machine"),
        ('date', str, "Date from (YYYYMMDD)"),
    ],
    responses={
        200: (SensorData, "MachineData data object"),
        400: (str, "Bad request"),
        403: (str, "Operation forbidden"),
        404: (str, "Object not found")
    }
)


async def run(payload: None, context: EventContext, action: str,
              machine: str, date: str) -> Union[SensorData, HttpRespInfo]:
    mo = db(context.env)
    if action == ACT_SENSOR_RAW_STATUS:
        return await _get_sensor_raw_status(mo, machine, date)
    elif action == ACT_SENSOR_RAW_TIEMPO_CICLO:
        return await _get_sensor_raw_tiempo_ciclo(mo, machine, date)

    return HttpRespInfo(400, 'Action not recognized')


async def __postprocess__(payload: Union[SensorData, HttpRespInfo],
                          context: EventContext,
                          response: PostprocessHook) -> Union[SensorData, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    return payload


async def _get_sensor_raw_status(mo, machine: str, date: str) -> SensorData:
    """get data"""
    input_date = datetime.strptime(date, '%Y%m%d')
    date_flt = f"^{input_date.strftime('%Y-%m-%d')}"

    # "sense_time": "2023-06-07T10:43:27.389081-03:00"
    filter_query = { 'sense_time': {'$regex': date_flt},
                     'machine': machine,
                     'metric': METRIC_STATUS }

    cursor = mo[IDX_SENSOR_MACHINE].find(filter_query)
    # max sense per day: 17280
    sense_list = [Payload.from_obj(doc, SensorMachine) for doc in await cursor.to_list(length=17280)]
    sensor_data = SensorData(
        machine=machine,
        date_from=date,
        date_to=date,
        sense_list = sense_list,
    )
    return sensor_data


async def _get_sensor_raw_tiempo_ciclo(mo, machine: str, date: str) -> SensorData:
    """get data"""
    input_date = datetime.strptime(date, '%Y%m%d')
    date_flt = f"^{input_date.strftime('%Y-%m-%d')}"

    # "sense_time": "2023-06-07T10:43:27.389081-03:00"
    filter_query = { 'sense_time': {'$regex': date_flt},
                     'machine': machine,
                     'metric': METRIC_TIEMPO_CICLO }

    cursor = mo[IDX_SENSOR_MACHINE].find(filter_query)
    # max sense per day: 17280
    sense_list = [Payload.from_obj(doc, SensorMachine) for doc in await cursor.to_list(length=17280)]
    sensor_data = SensorData(
        machine=machine,
        date_from=date,
        date_to=date,
        sense_list = sense_list,
    )
    return sensor_data
