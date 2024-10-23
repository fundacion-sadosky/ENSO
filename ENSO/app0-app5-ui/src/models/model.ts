export interface AppData {
  machines_working?: number
  production?: number
  alerts?: number
}

export interface Machine {
  id?: string
  nbr: string
  code: string
  name: string
  description?: string
  manufacturer?: string
  model?: string
  enabled?: boolean
  realtime_status?: boolean
  last_status_date?: string
  last_status?: any
}

export interface ItemOt {
  id?: number
  ot_nro?: string
  maquina_nro?: string
  producto_id?: string
  producto_desc?: string
  maquina_desc?: string
  color?: string
  peso?: number
  cantidad?: number
  horas?: number
  fecha_vencimiento?: string
  cadencia?: number
  operarios_requeridos?: number
  prioridad?: number
  setup_maquina?: number
}

export interface ItemFueraServicio {
  id?: number
  maquina?: string
  hora_inicio?: string
  hora_fin?: string
  motivo?: string
}

export interface ModelInput {
  tiempo_setup?: number
  cantidad_operarios?: number
  fecha_inicio?: string
  ots?: ItemOt[]
  fuera_servicios?: ItemFueraServicio[]
}

export interface AgendaMaquinaOt {
  id?: number
  ot_nro?: string
  maquina_nro?: string
  hora_inicio?: string
  hora_fin?: string
  cant_personal?: number
  producto?: string
  descripcion?: string
  is_setup_maquina?: boolean
}

export interface AgendaPersonal {
  id?: number
  cant_personal?: number
  hora_inicio?: string
  hora_fin?: string
}

export interface ModelOutput {
  completamiento_ordenes?: number
  tardanza_total?: number
  anticipacion_total?: number
  maxima_tardanza?: number
  maxima_anticipacion?: number
  total_setup?: number
  total_produccion?: number
  ordenes_tardias?: number
  ordenes_anticipadas?: number
  uso_operarios_total?: number
  productividad_operarios?: number
  plan_inicio?: string
  plan_fin?: string
  plan_inicio_preparacion?: string
  agenda_maquina_ot?: AgendaMaquinaOt[]
  agenda_personal?: AgendaPersonal[]
}

export interface JobRunLog {
  id?: string
  job_id?: string
  line_date?: string
  text?: string
}

export interface ModelJob {
  id?: string
  creation_date?: string
  creation_user?: string
  number?: string
  status?: string
  name?: string
  description?: string
  scenario_status?: string
  model_input?: ModelInput
  model_output?: ModelOutput
  start_date?: string
  end_date?: string
  error_text?: string
  result_files?: string[]
  origin_id?: string
  origin_desc?: string
}

export interface Product {
  id?: string
  barcode: string
  name: string
  description?: string
  envases_por_bulto?: number
  bultos_por_m3?: number
  envases_por_m3?: number
  cadencia_unidades_h?: number
  peso_envase?: number
  tipo_tapa?: string
  maquina?: string
  maquina_alternativa?: string
  operarios?: number
  palletizadores?: number
  cavidades_maquina?: number
}
