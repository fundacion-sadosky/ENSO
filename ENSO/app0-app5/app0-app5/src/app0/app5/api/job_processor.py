"""
Job: job-processor
"""
import traceback
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from dataclasses import dataclass, field

from bson.objectid import ObjectId  # type: ignore
from hopeit.app.context import EventContext
from hopeit.app.logger import app_extra_logger
from hopeit.dataobjects.payload import Payload
from hopeit.dataobjects import dataobject
from hopeit.server.steps import SHUFFLE

from app0.admin.db import db
from app0.admin.db.keystore import set_iddesc_key
from app0.admin.util import app_util, IDX_APP
from app0.admin.app import AppDef
from app0.admin.common import IdDescription
from app0.admin.file import PlatformFile

from app0.app5.model import ModelOutput, ModelJob, JobRunLog, AgendaMaquinaOt
from app0.app5.util import IDX_JOB, IDX_JOB_LOG, date_util
from app0.app5.util.funcion_modelo_v1 import run_model

logger, extra = app_extra_logger()

__steps__ = ['preprocess', SHUFFLE, 'process', SHUFFLE, 'postprocess']


@dataobject
@dataclass
class ProcJob:
    job: ModelJob
    app: Optional[AppDef] = None
    result_files: List[PlatformFile] = field(default_factory=list)
    model_output: Optional[ModelOutput] = None
    status: str = ''
    end_date: Optional[datetime] = None
    error_text: str = ''
    job_logs: Optional[List[JobRunLog]] = None


async def preprocess(payload: ModelJob, context: EventContext) -> ProcJob:
    """
    Pre Process Job
    """
    logger.info(context, "Starting job...")
    assert payload.id
    payload.start_date = date_util.now()
    payload.status = app_util.STATUS_RUNNING
    await _save_model_job(context, payload)
    app_def: Optional[AppDef] = await _get_app_def(context)
    # save in redis
    await set_iddesc_key(app_util.APP_APP5_JOB_KEY,
                         IdDescription(value=payload.id,
                                       label=f"Planificación {payload.number} EN EJECUCIÓN",
                                       details={'timestamp': date_util.now().strftime("%Y%m%d-%H%M%S"),
                                                'status': 'RUN'}))
    print('===> job.processor.preprocess redis status RUN')

    return ProcJob(job=payload, app=app_def)


async def process(payload: ProcJob, context: EventContext) -> ProcJob:
    """
    Process Job
    """
    try:
        model_output, run_logs = await _run_job(context, payload.job)
        logger.info(context, "Job Finished")
        print('===> Job Finished')
        # save logs
        payload.job_logs = run_logs
        if model_output.error_code:
            print('===> Job Finished ERROR')
            payload.model_output = model_output
            payload.status = app_util.STATUS_ENDED_ERROR
            payload.error_text = model_output.error_msg
            print(model_output.error_msg)
        else:
            print('===> Job Finished NO ERROR CODE')
            payload.model_output = model_output
            payload.status = app_util.STATUS_ENDED_OK
        payload.end_date = date_util.now()
    except Exception as e:
        payload.status = app_util.STATUS_ENDED_ERROR
        payload.error_text = str(e)
        logger.warning(context, f"Job process ERROR {e}")
        print(traceback.format_exc())
    print('===> job.processor.process return')
    print(payload)
    return payload


async def postprocess(payload: ProcJob, context: EventContext):
    """
    Post Process Job
    """
    print('===> job.processor.postprocess start')
    model_job = payload.job
    model_job.status = payload.status
    assert payload.status
    await _job_save_logs(context, payload.job_logs)
    if payload.status == app_util.STATUS_ENDED_OK:
        print('===> job.processor.postprocess end ok')
        model_job.result_files = payload.result_files
        # set desc to agenda ots
        payload = _set_desc_ots(payload)
        model_job.model_output = payload.model_output
        # add to model_output setup_maquina and extend plan inicio
        setups, inicio_preparacion = _add_setup_maquina(payload)
        model_job.model_output.agenda_maquina_ot.extend(setups)
        model_job.model_output.plan_inicio_preparacion = inicio_preparacion
        # set final status
        model_job.end_date = payload.end_date
        model_job.scenario_status = app_util.STATUS_SCENARIO_IN_EVALUATION
    else:
        model_job.error_text = payload.error_text
    await _save_model_job(context, model_job)
    # save in redis
    assert payload.job.id
    print('===> job.processor.postprocess finishing')
    await set_iddesc_key(app_util.APP_APP5_JOB_KEY,
                         IdDescription(value=payload.job.id,
                                       label=f"Planificación {payload.job.number} FINALIZADA",
                                       details={'timestamp': date_util.now().strftime("%Y%m%d-%H%M%S"),
                                                'status': 'END'}))
    print('===> job.processor.preprocess redis status END')


async def _save_model_job(context: EventContext, model_job: ModelJob) -> ModelJob:
    es = db(context.env)
    await es[IDX_JOB].replace_one({'_id': ObjectId(model_job.id)}, Payload.to_obj(model_job))
    return model_job


async def _get_app_def(context: EventContext) -> Optional[AppDef]:
    es = db(context.env)
    doc = await es[IDX_APP].find_one({'url': {'$regex': f'{app_util.APP_APP5_URL_SUFFIX}$'}})
    return Payload.from_obj(doc, AppDef) if doc else None


async def _job_save_logs(context: EventContext, logs: List[JobRunLog]):
    es = db(context.env)
    for log in logs:
        await es[IDX_JOB_LOG].replace_one({'_id': ObjectId(log.id)},
                                           Payload.to_obj(log),
                                           upsert=True)


async def _run_job(context: EventContext, model_job: ModelJob) -> Tuple[ModelOutput, List[JobRunLog]]:
    """solve the model"""
    logger.debug(context, "_run_job Starting job")
    logs = []
    assert model_job.id
    logs.append(JobRunLog(job_id=model_job.id, line_date=date_util.now(),
                          text="Comenzando Planificación"))
    model_output = run_model(model_job.model_input)
    print(f"=> _run_job 1: {model_output}")

    logs.append(JobRunLog(job_id=model_job.id, line_date=date_util.now(),
                          text="Procesando resultados"))
    # setear plan inicio y plan fin
    for agenda_ot in model_output.agenda_maquina_ot:
        if not model_output.plan_inicio:
            model_output.plan_inicio = agenda_ot.hora_inicio
        elif model_output.plan_inicio > agenda_ot.hora_inicio:
            model_output.plan_inicio = agenda_ot.hora_inicio
        if not model_output.plan_fin:
            model_output.plan_fin = agenda_ot.hora_fin
        elif model_output.plan_fin < agenda_ot.hora_fin:
            model_output.plan_fin = agenda_ot.hora_fin

    logs.append(JobRunLog(job_id=model_job.id, line_date=date_util.now(),
                          text="Planificación Ejecutada"))

    print("=> _run_job 2")
    return model_output, logs


def _add_setup_maquina(payload: ProcJob) -> Tuple[List[AgendaMaquinaOt], datetime]:
    ret: List[AgendaMaquinaOt] = []
    inicio_preparacion = payload.job.model_output.plan_inicio
    # for every ot output
    id_setup = 900
    for agenda_ot in payload.model_output.agenda_maquina_ot:
        # get input related ot
        input_ots = [in_ot for in_ot in payload.job.model_input.ots if in_ot.ot_nro == agenda_ot.ot_nro]
        if len(input_ots) > 0:
            input_ot = input_ots[0]
            # query if model input for that ot has setup_maquina
            if input_ot.setup_maquina > 0.0:
                # generate AgendaMaquinaOt with time before
                start_setup = agenda_ot.hora_inicio - timedelta(hours=input_ot.setup_maquina)
                end_setup = agenda_ot.hora_inicio
                desc = "Tiempo de Setup Máquina"
                ret.append(AgendaMaquinaOt(id=id_setup,
                                           ot_nro=agenda_ot.ot_nro,
                                           hora_inicio=start_setup,
                                           hora_fin=end_setup,
                                           maquina_nro=f"{agenda_ot.maquina_nro}pre",
                                           cant_personal=agenda_ot.cant_personal,
                                           descripcion=desc,
                                           is_setup_maquina=True))
                # track plan inicio preparación
                if start_setup < inicio_preparacion:
                    inicio_preparacion = start_setup
                id_setup += 1

    return ret, inicio_preparacion


def _set_desc_ots(payload: ProcJob) -> ProcJob:
    assert payload.model_output.agenda_maquina_ot
    assert payload.job.model_input.ots
    agenda: List[AgendaMaquinaOt] = payload.model_output.agenda_maquina_ot
    for agenda_ot in agenda:
        # get input related ot
        input_ots = [in_ot for in_ot in payload.job.model_input.ots if in_ot.ot_nro == agenda_ot.ot_nro]
        if len(input_ots) > 0:
            input_ot = input_ots[0]
            desc = f"{input_ot.producto_id} {input_ot.producto_desc}, {input_ot.operarios_requeridos} operarios, {input_ot.horas} horas, {input_ot.cantidad} unidades"  # noqa
            agenda_ot.descripcion = desc

    payload.model_output.agenda_maquina_ot = agenda

    return payload
