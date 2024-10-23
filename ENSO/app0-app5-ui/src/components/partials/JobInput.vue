<script setup lang="ts">
import { onBeforeMount, ref } from 'vue'
import type { ModelJob } from '/@src/models/model'
import { AgGridVue } from 'ag-grid-vue3'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import { utils } from '/@src/services/utils'

export interface JobOutputProps {
  modelJob?: ModelJob
}
const props = withDefaults(defineProps<JobOutputProps>(), {
  modelJob: undefined,
})

// aggrid
const gridApi = ref(null) // Optional - for accessing Grid's API

// Obtain API from grid's onGridReady event
const onGridReady = (params: any) => {
  gridApi.value = params.api
}

const rowDataOts = ref([])
const rowDataFuera = ref([])

// Each Column Definition results in one Column.
// Es importante que el campo FIELD matchee con los parametros de los objetos que pertenecen a ROwData
const columnDefOts = ref([
  { headerName: 'OT', field: 'ot_nro' },
  { headerName: 'Producto', field: 'producto_id' },
  { headerName: 'Máquina', field: 'maquina_nro' },
  { headerName: 'Cantidad', field: 'cantidad' },
  { headerName: 'Horas', field: 'horas' },
  { headerName: 'Setup (h)', field: 'setup_maquina' },
  { headerName: 'Operarios Req.', field: 'operarios_requeridos' },
  { headerName: 'Prioridad', field: 'prioridad' },
  { headerName: 'Vencimiento', field: 'fecha_vencimiento' },
])
const columnDefFuera = ref([
  { headerName: 'Máquina', field: 'maquina' },
  { headerName: 'Hora inicio', field: 'hora_inicio' },
  { headerName: 'Hora fin', field: 'hora_fin' },
  { headerName: 'Motivo', field: 'motivo' },
])

// DefaultColDef sets props common to all Columns
const defaultColDef = {
  sortable: true,
  filter: false,
  flex: 1,
  editable: false,
}
// aggrid end

const loadData = () => {
  if (props.modelJob.model_input?.ots) {
    rowDataOts.value = props.modelJob.model_input?.ots.map((e: any) => {
      return {
        id: e.id,
        ot_nro: e.ot_nro,
        maquina_nro: e.maquina_nro,
        producto_id: e.producto_id,
        producto_desc: e.producto_desc,
        maquina_desc: e.maquina_desc,
        color: e.color,
        peso: e.peso,
        cantidad: e.cantidad,
        horas: e.horas.toFixed(2),
        fecha_vencimiento: utils.isoToDmy(e.fecha_vencimiento),
        cadencia: e.cadencia,
        operarios_requeridos: e.operarios_requeridos,
        prioridad: e.prioridad,
        setup_maquina: e.setup_maquina.toFixed(2),
      }
    })
  }
  if (props.modelJob.model_input?.fuera_servicios) {
    rowDataFuera.value = props.modelJob.model_input?.fuera_servicios.map((e: any) => {
      return {
        id: e.id,
        maquina: e.maquina,
        hora_inicio: utils.isoToDmyhm(e.hora_inicio),
        hora_fin: utils.isoToDmyhm(e.hora_fin),
        motivo: e.motivo,
      }
    })
  }
}

onBeforeMount(() => {
  loadData()
})
</script>

<template>
  <div v-if="props.modelJob.model_input" class="job-files">
    <h4>Parámetros</h4>
    <div class="columns is-multiline">
      <div class="column is-4">
        <VField label="Tiempo de preparación (h)">
          <VControl>
            <input :value="props.modelJob.model_input.tiempo_setup" type="number" class="input" disabled />
          </VControl>
        </VField>
      </div>
      <div class="column is-4">
        <VField label="Cant. operarios disponibles">
          <VControl>
            <input :value="props.modelJob.model_input.cantidad_operarios" type="number" class="input" disabled />
          </VControl>
        </VField>
      </div>
      <div class="column is-4">
        <VField label="Fecha de inicio del plan">
          <VControl>
            <input
              :value="utils.isoToDmyhm(props.modelJob.model_input.fecha_inicio)"
              type="text"
              class="input"
              disabled
            />
          </VControl>
        </VField>
      </div>
    </div>
  </div>
  <div v-if="props.modelJob.model_input" class="job-files">
    <h4>Órdenes de trabajo</h4>
    <div class="columns is-multiline">
      <div class="column is-12">
        <ag-grid-vue
          class="ag-theme-alpine"
          style="height: 300px"
          :column-defs="columnDefOts"
          :row-data="rowDataOts"
          :default-col-def="defaultColDef"
          row-selection="multiple"
          animate-rows="true"
          @grid-ready="onGridReady"
        >
        </ag-grid-vue>
      </div>
    </div>
  </div>
  <div v-if="props.modelJob.model_input" class="job-files">
    <h4>Máquina Fuera de Servicio</h4>
    <div class="columns is-multiline">
      <div class="column is-12">
        <ag-grid-vue
          class="ag-theme-alpine"
          style="height: 300px"
          :column-defs="columnDefFuera"
          :row-data="rowDataFuera"
          :default-col-def="defaultColDef"
          row-selection="multiple"
          animate-rows="true"
          @grid-ready="onGridReady"
        >
        </ag-grid-vue>
      </div>
    </div>
  </div>
</template>
