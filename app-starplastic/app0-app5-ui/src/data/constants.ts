export const ROLE_ADMIN = 'Starplastic Admin'
export const ROLE_USER = 'Starplastic User'
export const ROLE_OPERARIO = 'Starplastic User'

export const ACT_MACHINE_STATUS = 'ACT_MACHINE_STATUS'

export const MACH_STATUS_PRODUCCION = 'EnProducción'
export const MACH_STATUS_CAMBIO_MOLDE = 'CambioDeMolde'
export const MACH_STATUS_PREPARACION = 'EnPreparación'
export const MACH_STATUS_LIMPIEZA = 'EnLimpiezaLubricación'
export const MACH_STATUS_PREVENTIVO = 'EnPreventivo'
export const MACH_STATUS_CORRECTIVO = 'EnCorrectivo'
export const MACH_STATUS_SIN_CONEXION = 'SinConexión'

export const MACH_STATUS_PRODUCCION_DESC = 'En Producción'
export const MACH_STATUS_CAMBIO_MOLDE_DESC = 'Cambio de Molde'
export const MACH_STATUS_PREPARACION_DESC = 'En Preparación'
export const MACH_STATUS_LIMPIEZA_DESC = 'En Limpieza / Lubricación'
export const MACH_STATUS_PREVENTIVO_DESC = 'En Preventivo'
export const MACH_STATUS_CORRECTIVO_DESC = 'En Correctivo'
export const MACH_STATUS_SIN_CONEXION_DESC = 'Sin Conexión'

export const ACT_MACHINE_STATUS_CAMBIO_MOLDE = 'ACT_MACHINE_ARCHIVE'
export const ACT_MACHINE_STATUS_PREPARACION = 'ACT_MACHINE_STATUS_PREPARACION'
export const ACT_MACHINE_STATUS_LIMPIEZA = 'ACT_MACHINE_STATUS_LIMPIEZA'
export const ACT_MACHINE_STATUS_PREVENTIVO = 'ACT_MACHINE_STATUS_PREVENTIVO'
export const ACT_MACHINE_STATUS_CORRECTIVO = 'ACT_MACHINE_STATUS_CORRECTIVO'

export const ACT_MACHINE_METRIC_STATUS = 'ACT_MACHINE_METRIC_STATUS'
export const ACT_MACHINE_METRIC_STATUS_TIME = 'ACT_MACHINE_METRIC_STATUS_TIME'
export const ACT_MACHINE_METRIC_STATUS_PER_DAY = 'ACT_MACHINE_METRIC_STATUS_PER_DAY'
export const ACT_MACHINE_METRIC_STATUS_PER_HOUR = 'ACT_MACHINE_METRIC_STATUS_PER_HOUR'
export const ACT_MACHINE_METRIC_STATUS_PER_DAY_SENSE = 'ACT_MACHINE_METRIC_STATUS_PER_DAY_SENSE'

export const ACT_PRODUCT_METRIC_PRODUCED_PER_DAY = 'ACT_PRODUCT_METRIC_PRODUCED_PER_DAY'

export const ACT_SENSOR_RAW_STATUS = 'ACT_SENSOR_RAW_STATUS'
export const ACT_SENSOR_RAW_TIEMPO_CICLO = 'ACT_SENSOR_RAW_TIEMPO_CICLO'

export const ACT_KPI_MACHINES_LAST = 'ACT_KPI_MACHINES_LAST'
export const ACT_KPI_MACHINES_MONTH = 'ACT_KPI_MACHINES_MONTH'

export const ACT_JOB_DELETE = 'ACT_JOB_DELETE'

// job status
export const JOB_STATUS_READY = 'READY'
export const JOB_STATUS_RUNNING = 'RUNNING'
export const JOB_STATUS_ENDED_OK = 'ENDED OK'
export const JOB_STATUS_ENDED_ERROR = 'ENDED ERROR'

export const JOB_STATUS_READY_DESC = 'EN PREPARACIÓN'
export const JOB_STATUS_RUNNING_DESC = 'EJECUTANDO'
export const JOB_STATUS_ENDED_OK_DESC = 'FINALIZADO'
export const JOB_STATUS_ENDED_ERROR_DESC = 'ERROR'

// job file types
export const JOB_FILETYPE_INPUT = 'INPUT'
export const JOB_FILETYPE_OUTPUT = 'OUTPUT'
export const JOB_FILETYPE_OTHER = 'OTHER'

// scenario status
export const STATUS_SCENARIO_IN_EVALUATION = 'IN EVALUATION'
export const STATUS_SCENARIO_DISCARDED = 'DISCARDED'
export const STATUS_SCENARIO_APPLIED = 'APPLIED'

export const STATUS_SCENARIO_IN_EVALUATION_DESC = 'EN EVALUACIÓN'
export const STATUS_SCENARIO_DISCARDED_DESC = 'DESCARTADO'
export const STATUS_SCENARIO_APPLIED_DESC = 'PLANIFICADO'

export const optMeses = [
  { value: '01', label: 'Enero' },
  { value: '02', label: 'Febrero' },
  { value: '03', label: 'Marzo' },
  { value: '04', label: 'Abril' },
  { value: '05', label: 'Mayo' },
  { value: '06', label: 'Junio' },
  { value: '07', label: 'Julio' },
  { value: '08', label: 'Agosto' },
  { value: '09', label: 'Septiembre' },
  { value: '10', label: 'Octubre' },
  { value: '11', label: 'Noviembre' },
  { value: '12', label: 'Diciembre' },
]
