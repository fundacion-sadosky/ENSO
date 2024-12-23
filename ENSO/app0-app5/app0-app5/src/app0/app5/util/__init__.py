"""
util module
"""
import random
import string

# mongo db collections
IDX_SENSOR_MACHINE = 'app5.sensor_machine'
IDX_MACHINE = 'app5.machine'
IDX_PRODUCT = 'app5.product'
IDX_WORK_ORDER = 'app5.work_order'
IDX_MACHINE_METRIC = 'app5.machine_metric'
IDX_PRODUCT_METRIC = 'app5.product_metric'
IDX_JOB = 'app5.job'
IDX_JOB_LOG = 'app5.job_log'

# app actions
ACT_MACHINE_ARCHIVE = "ACT_MACHINE_ARCHIVE"
ACT_MACHINE_UNARCHIVE = "ACT_MACHINE_UNARCHIVE"
ACT_MACHINE_STATUS_CAMBIO_MOLDE = "ACT_MACHINE_ARCHIVE"
ACT_MACHINE_STATUS_PREPARACION = "ACT_MACHINE_STATUS_PREPARACION"
ACT_MACHINE_STATUS_LIMPIEZA = "ACT_MACHINE_STATUS_LIMPIEZA"
ACT_MACHINE_STATUS_PREVENTIVO = "ACT_MACHINE_STATUS_PREVENTIVO"
ACT_MACHINE_STATUS_CORRECTIVO = "ACT_MACHINE_STATUS_CORRECTIVO"

# Machine Status
MACH_STATUS_CAMBIO_MOLDE = "CambioDeMolde"
MACH_STATUS_PREPARACION = "EnPreparación"
MACH_STATUS_PRODUCCION = "EnProducción"
MACH_STATUS_LIMPIEZA = "EnLimpiezaLubricación"
MACH_STATUS_PREVENTIVO = "EnPreventivo"
MACH_STATUS_CORRECTIVO = "EnCorrectivo"
MACH_STATUS_CICLO = "Ciclo"
MACH_STATUS_TIEMPO_DE_CICLO = "TiempoDeCiclo"
MACH_STATUS_SIN_CONEXION = 'SinConexión'

# Metric
METRIC_STATUS = "estado"
METRIC_PRODUCT_PRODUCED = "fabricado"
METRIC_TIEMPO_CICLO = "tiempo_ciclo"

# app data actions
ACT_MACHINE_STATUS = "ACT_MACHINE_STATUS"
# job actions
ACT_JOB_DELETE = "ACT_JOB_DELETE"
# scenario actions
ACT_SCENARIO_DELETE = "ACT_SCENARIO_DELETE"
# machine metric actions
ACT_MACHINE_METRIC_STATUS = "ACT_MACHINE_METRIC_STATUS"
ACT_MACHINE_METRIC_STATUS_TIME = "ACT_MACHINE_METRIC_STATUS_TIME"
ACT_MACHINE_METRIC_STATUS_PER_DAY = "ACT_MACHINE_METRIC_STATUS_PER_DAY"
ACT_MACHINE_METRIC_STATUS_PER_HOUR = "ACT_MACHINE_METRIC_STATUS_PER_HOUR"
ACT_MACHINE_METRIC_STATUS_PER_DAY_SENSE = "ACT_MACHINE_METRIC_STATUS_PER_DAY_SENSE"
ACT_MACHINE_METRIC_STATUS_PER_HOUR_SENSE = "ACT_MACHINE_METRIC_STATUS_PER_HOUR_SENSE"
# product metric actions
ACT_PRODUCT_METRIC_PRODUCED_PER_DAY = "ACT_PRODUCT_METRIC_PRODUCED_PER_DAY"
# job actions
ACT_JOB_DELETE = "ACT_JOB_DELETE"
# sensor actions
ACT_SENSOR_RAW_STATUS = "ACT_SENSOR_RAW_STATUS"
ACT_SENSOR_RAW_TIEMPO_CICLO = "ACT_SENSOR_RAW_TIEMPO_CICLO"
# kpi data actions
ACT_KPI_MACHINES_MONTH = "ACT_KPI_MACHINES_MONTH"
ACT_KPI_MACHINES_LAST = "ACT_KPI_MACHINES_LAST"


def rstri(length) -> str:
    """
    get random digits string of length
    """
    return ''.join(random.choice(string.digits) for x in range(length))
