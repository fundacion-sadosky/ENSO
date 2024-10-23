from typing import Optional, List
from datetime import datetime, timedelta
from app0.admin.common import IdDescription
from app0.app5.util import (MACH_STATUS_CAMBIO_MOLDE, MACH_STATUS_PREPARACION, MACH_STATUS_CICLO,
                            MACH_STATUS_PRODUCCION, MACH_STATUS_LIMPIEZA, MACH_STATUS_PREVENTIVO,
                            MACH_STATUS_CORRECTIVO, MACH_STATUS_TIEMPO_DE_CICLO)
from app0.app5.machine import MachineDataStatus
from app0.app5.util.date_util import is_today


# estados posibles
estados = [
    IdDescription(MACH_STATUS_CAMBIO_MOLDE, 'Cambio de Molde'),
    IdDescription(MACH_STATUS_PREPARACION, 'En Preparación'),
    IdDescription(MACH_STATUS_PRODUCCION, 'Producción'),
    IdDescription(MACH_STATUS_LIMPIEZA, 'Limpieza/Lubricación'),
    IdDescription(MACH_STATUS_PREVENTIVO, 'En Preventivo'),
    IdDescription(MACH_STATUS_CORRECTIVO, 'En Correctivo'),
    IdDescription(MACH_STATUS_CICLO, 'Ciclo'),
    IdDescription(MACH_STATUS_TIEMPO_DE_CICLO, 'TiempoDeCiclo'),
]


def get_estado(key: str) -> Optional[IdDescription]:
    return next((obj for obj in estados if obj.value == key), None)


def gen_date_hour_array(date_from, date_to):
    date_format = "%Y%m%d"

    current_date = date_from
    result = []

    while current_date <= date_to:
        range_hours = 24 if not is_today(current_date) else datetime.now().hour
        for hour in range(range_hours):
            date_hour_dict = {
                'date': current_date.strftime(date_format),
                'hour': f"{hour}_{hour+1}"
            }
            result.append(date_hour_dict)

        current_date += timedelta(days=1)

    return result


def group_states_sum_time(objs: List[MachineDataStatus]):
    sum_dict = {}

    for item in objs:
        name = item.status
        val = item.seconds
        
        if name in sum_dict:
            sum_dict[name] += val
        else:
            sum_dict[name] = val

    result = [MachineDataStatus(status=name, seconds=val) for name, val in sum_dict.items()]

    return result


def group_states_day_sum_time(objs: List[MachineDataStatus]):
    sum_dict = {}

    for item in objs:
        name = item.status
        day = item.day
        val = item.seconds
        key = f"{name}_{day}"
        
        if key in sum_dict:
            sum_dict[key] += val
        else:
            sum_dict[key] = val

    result = []
    for key, val in sum_dict.items():
        name, day = key.split('_')
        result.append(MachineDataStatus(status=name, day=day, seconds=val))

    return result


def group_states_day_hour_sum_time(objs: List[MachineDataStatus]):
    sum_dict = {}

    for item in objs:
        name = item.status
        day = item.day
        hour = item.hour
        val = item.seconds
        key = f"{name}_{day}_{hour}"
        
        if key in sum_dict:
            sum_dict[key] += val
        else:
            sum_dict[key] = val

    result = []
    for key, val in sum_dict.items():
        parts = key.split('_')
        name = parts[0]
        day = parts[1]
        hour = parts[2]
        result.append(MachineDataStatus(status=name, day=day, hour=hour, seconds=val))

    return result
