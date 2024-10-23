"""
Job: job-new
"""
from typing import Optional, Union
from datetime import timedelta
import random
import copy
from bson.objectid import ObjectId  # type: ignore

from hopeit.app.api import event_api
from hopeit.app.context import EventContext, PostprocessHook
from hopeit.dataobjects.payload import Payload

from app0.admin.db import db
from app0.admin.http import HttpRespInfo
from app0.admin.util import app_util, counter_util

from app0.app5.model import ModelJob, ModelInput, ItemOt
from app0.app5.util import IDX_JOB, date_util

__steps__ = ['run']
__api__ = event_api(
    query_args=[
        ('origin_job_id', Optional[str], "Origin Job Id")
    ],
    responses={
        200: (ModelJob, "Model Job with inputs with default values"),
        403: (HttpRespInfo, "Operation forbidden"),
        404: (HttpRespInfo, "Object not found")
    }
)


async def run(payload: None, context: EventContext,
              origin_job_id: Optional[str] = None) -> Union[ModelJob, HttpRespInfo]:
    mo = db(context.env)
    if origin_job_id:
        origin_job = await _get_job(mo, origin_job_id)
        if origin_job:
            return await _get_default_model_input(mo, context, origin=origin_job)
    return await _get_default_model_input(mo, context)


async def __postprocess__(payload: Union[ModelJob, HttpRespInfo], context: EventContext,
                          response: PostprocessHook) -> Union[ModelJob, str]:
    if isinstance(payload, HttpRespInfo):
        response.status = payload.code
        return payload.msg
    if payload is None:
        response.status = 404
        return "Object not found"
    return payload


async def _get_default_model_input(mo, context: EventContext, origin: Optional[ModelJob] = None) -> ModelJob:
    """Get default model input or copy from origin"""
    fecha_inicio=date_util.next_monday(7)
    ftop=fecha_inicio+timedelta(days=4)
    fecha_orden=date_util.to_dmy(ftop)
    model_input = ModelInput(
        fecha_inicio=fecha_inicio,
        ots=[
            ItemOt(id=1, ot_nro="24597", maquina_nro="24", producto_id="7020310", producto_desc="BID T64 20 ECO-BIDON",
                   maquina_desc="COEX-23 - SOPLADORA COEXTRUSORA KONG KEE", color="Blanco", peso=1050.0, cantidad=5760,
                   horas=34.9, fecha_vencimiento=date_util.from_dmy(fecha_orden), cadencia=165, operarios_requeridos=1,
                   prioridad=3, setup_maquina=0.15),
            ItemOt(id=2, ot_nro="24599", maquina_nro="23", producto_id="7020310", producto_desc="BID T64 20 ECO-BIDON",
                   maquina_desc="COEX-23 - SOPLADORA COEXTRUSORA KONG KEE", color="Blanco", peso=1050.0, cantidad=5760,
                   horas=12.0, fecha_vencimiento=date_util.from_dmy(fecha_orden), cadencia=165, operarios_requeridos=1,
                   prioridad=2, setup_maquina=0.15),
            ItemOt(id=3, ot_nro="24608", maquina_nro="23", producto_id="7020310", producto_desc="BID T64 20 ECO-BIDON",
                   maquina_desc="COEX-23 - SOPLADORA COEXTRUSORA KONG KEE", color="Blanco", peso=1050.0, cantidad=5760,
                   horas=14.0, fecha_vencimiento=date_util.from_dmy(fecha_orden), cadencia=165, operarios_requeridos=2,
                   prioridad=1, setup_maquina=0.15),
        ],
        fuera_servicios=[]
    )
    job = ModelJob(
        creation_date=date_util.now(),
        creation_user=context.auth_info['payload'].get('fullname', 'Noauth User'),
        number=await _generate_job_number(mo),
        status=app_util.STATUS_READY,
        model_input=copy.deepcopy(origin.model_input) if origin else model_input
    )
    if origin:
        job.origin_id = origin.id
        job.origin_desc = f"Planificación basada en Planificación #{origin.number}"

    return job


async def _generate_job_number(mo) -> str:
    """generate job number"""
    key = 'job5'
    fn = await counter_util.next_value(mo, key)
    file_number = str(fn).zfill(7)

    return file_number


def rvalue(base_val: int, variation: float) -> int:
    """
    generate random value base_val +- variation (between 0.0 and 1.0)
    """
    if not variation or variation > 1.0:
        return base_val
    var_value: int = int(base_val * variation)
    return base_val + random.randrange(-var_value, var_value)


async def _get_job(mo, oid: str) -> Optional[ModelJob]:
    doc = await mo[IDX_JOB].find_one(ObjectId(oid))
    return Payload.from_obj(doc, ModelJob)


# async def _super_simple() -> Dict:
#     # yo voy a pasar algo así
#     model_input = {
#         'tiempo_setup': 0.5,
#         'cantidad_operarios': 1,
#         'ots': [
#             {'id': 1, 
#              'ot_nro': "24597",
#              'maquina_nro': "23",
#              'producto_id': "7020310",
#              'producto_desc': "BID T64 20 ECO-BIDON",
#              'maquina_desc': "COEX-23 - SOPLADORA COEXTRUSORA KONG KEE",
#              'color': "Blanco",
#              'peso': 1050.0,
#              'cantidad': 5760,
#              'horas': 34.9,
#              'fecha_vencimiento': datetime.strptime('19/07/2023', '%d/%m/%Y'),
#              'cadencia': 165,
#              'operarios_requeridos': 2,
#              'prioridad': 1},
#             {'id': 2, 
#              'ot_nro': "24599",
#              'maquina_nro': "23",
#              'producto_id': "7020310",
#              'producto_desc': "BID T64 20 ECO-BIDON",
#              'maquina_desc': "COEX-23 - SOPLADORA COEXTRUSORA KONG KEE",
#              'color': "Blanco",
#              'peso': 1050.0,
#              'cantidad': 5760,
#              'horas': 34.9,
#              'fecha_vencimiento': datetime.strptime('19/07/2023', '%d/%m/%Y'),
#              'cadencia': 165,
#              'operarios_requeridos': 2,
#              'prioridad': 1},
#         ],
#         'fuera_servicios': [
#             {'id': 1,
#              'maquina': "23",
#              'hora_inicio': datetime.strptime('19/07/2023 10:00', '%d/%m/%Y %H:%M'),
#              'hora_fin': datetime.strptime('19/07/2023 20:00', '%d/%m/%Y %H:%M'),
#             },
#         ]
#     }
#     print(model_input)
#     # ejecutar el proceso etc etc
#     # ejecutar el proceso etc etc
#     # ejecutar el proceso etc etc
#     # con los resultados del proceso, construir el model output
#     model_output = {
#         'completamiento_ordenes': 3.5,
#         'tardanza_total': 3.5,
#         'anticipacion_total': 3.5,
#         'maxima_tardanza': 3.5,
#         'maxima_anticipacion': 3.5,
#         'total_setup': 3.5,
#         'total_produccion': 3.5,
#         'ordenes_tardias': 3.5,
#         'ordenes_anticipadas': 3.5,
#         'uso_operarios_total': 3.5,
#         'productividad_operarios': 3.5,
#         'agenda_maquina_ot': [
#             {'id': 1,
#              'ot_nro': "5361",
#              'maquina_nro': "27",
#              'hora_inicio': datetime.strptime('19/07/2023 10:00', '%d/%m/%Y %H:%M'),
#              'hora_fin': datetime.strptime('19/07/2023 20:00', '%d/%m/%Y %H:%M'),
#             },
#             {'id': 2,
#              'ot_nro': "5823",
#              'maquina_nro': "27",
#              'hora_inicio': datetime.strptime('19/07/2023 21:00', '%d/%m/%Y %H:%M'),
#              'hora_fin': datetime.strptime('19/07/2023 23:30', '%d/%m/%Y %H:%M'),
#             },
#         ],
#         'agenda_personal': [
#             {'id': 1,
#              'cant_personal': 1.0,
#              'hora_inicio': datetime.strptime('19/07/2023 10:00', '%d/%m/%Y %H:%M'),
#              'hora_fin': datetime.strptime('19/07/2023 20:00', '%d/%m/%Y %H:%M'),
#             },
#             {'id': 2,
#              'cant_personal': 2.0,
#              'hora_inicio': datetime.strptime('19/07/2023 21:00', '%d/%m/%Y %H:%M'),
#              'hora_fin': datetime.strptime('19/07/2023 23:30', '%d/%m/%Y %H:%M'),
#             },
#         ],
#     }

#     return model_output
