"""
Machine: sensor-data-csv
"""
import os
from typing import Union, Optional
from datetime import datetime
from pathlib import Path
import csv
import uuid
import aiofiles
from aiocsv import AsyncWriter

from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.app.logger import app_extra_logger
from hopeit.dataobjects.payload import Payload
from hopeit.dataobjects import BinaryDownload
from app0.admin.db import db
from app0.admin.http import HttpRespInfo
from app0.app5.sensor import SensorData, SensorMachine
from app0.app5.util import (ACT_SENSOR_RAW_STATUS, IDX_SENSOR_MACHINE, METRIC_STATUS, date_util)

logger, extra = app_extra_logger()
fs_csv: Optional[str] = None

__steps__ = ['get_file']
__api__ = event_api(
    query_args=[
        ('action', str, "action"),
        ('machine', str, "Machine"),
        ('date', str, "Date from (YYYYMMDD)"),
    ],
    responses={
        200: (BinaryDownload, 'File contents'),
        404: (str, "File not found")
    }
)


async def __init_event__(context: EventContext):
    global fs_csv
    if fs_csv is None:
        fs_csv = str(context.env['fs']['csv_store'])


async def get_file(payload: None, context: EventContext, action: str,
                   machine: str, date: str) -> Optional[str]:
    mo = db(context.env)
    if action == ACT_SENSOR_RAW_STATUS:
        sensor_data = await _get_sensor_raw_status(mo, machine, date)
        doc_id = await _generate_csv_file(sensor_data)

        return f"{fs_csv}/{doc_id}"

    return HttpRespInfo(400, 'Action not recognized')


async def __postprocess__(doc_id: Optional[str], context: EventContext, response: PostprocessHook) -> str:
    if doc_id and check_file_exists(doc_id):
        logger.info(context, f"Getting {doc_id}...")
        filename = os.path.basename(doc_id)
        file_size = os.path.getsize(doc_id)
        content_type = 'text/csv'
        stream_response = await response.prepare_stream_response(
            context,
            content_disposition=f'attachment; filename="{filename}"',
            content_type=content_type,
            content_length=file_size
        )
        chunk_size = 8192
        with open(doc_id, 'rb') as f:
            chunk = f.read(chunk_size)
            while chunk:
                await stream_response.write(chunk)
                chunk = f.read(chunk_size)

        return "Done"
    response.status = 404
    return "File not found"


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


def check_file_exists(file_path):
    path = Path(file_path)
    return path.is_file()


async def _generate_csv_file(sensor_data: SensorData) -> str:
    """_generate_csv_file"""
    filename = f"{sensor_data.machine}_{sensor_data.date_from}_{str(uuid.uuid4())}.csv"
    data = [['Máquina', 'Fecha', 'Valor']]
    for sense in sensor_data.sense_list:
        data.append([sense.machine, date_util.to_dmyhms(sense.sense_time), sense.valstr])
    # Define the CSV file name
    csv_file_name = f"{fs_csv}/{filename}"

    # Open the CSV file in write mode and write data
    # with open(csv_file_name, 'w', newline='') as csv_file:
    #     csv_writer = csv.writer(csv_file)
    #     csv_writer.writerows(data)

    # print(f'CSV file "{csv_file_name}" has been created successfully.')

    async with aiofiles.open(csv_file_name, mode="w", encoding="utf-8", newline="") as afp:
        writer = AsyncWriter(afp, dialect="unix")
        await writer.writerows(data)


    return filename
