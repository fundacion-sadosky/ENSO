<script setup lang="ts">
import type { PropType } from 'vue'
import { ref, onBeforeMount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useNotyf } from '/@src/composable/useNotyf'
import { modelService } from '/@src/services/modelService'
import type { ModelJob } from '/@src/models/model'
import { utils } from '/@src/services/utils'
import * as XLSX from 'xlsx'

import { AgGridVue } from 'ag-grid-vue3'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'

const router = useRouter()
const route = useRoute()
const notyf = useNotyf()
const isLoading = ref(false)
const modelJob = ref<ModelJob>()
const workbook = ref<XLSX.WorkBook>()

let xlsx_sheets_data = {}
const input_filename = ref<string>('')

const props = defineProps({
  activeTab: {
    type: String as PropType<'input'>,
    default: 'input',
  },
})
const tab = ref(props.activeTab)
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
  editable: true,
}
// aggrid end
function onSelectXLSXFile(event: Event) {
  try {
    let file = (event.target as HTMLInputElement).files![0]
    if (file) {
      input_filename.value = file.name
      let reader = new FileReader()

      reader.onload = (e: any) => {
        let data = e.target.result
        workbook.value = XLSX.read(data, { type: 'binary', cellDates: true, sheetStubs: true })
        var sheet_name_list = workbook.value.SheetNames
        for (const sheetName of sheet_name_list) {
          if (sheetName === 'config') {
            let x = XLSX.utils.sheet_to_json(workbook.value.Sheets[sheetName])
            ;(xlsx_sheets_data as any)[sheetName] = x
            console.log(`Sheet ${sheetName} present.`)
          }
          if (sheetName === 'fuera_servicio') {
            let x = XLSX.utils.sheet_to_json(workbook.value.Sheets[sheetName])
            ;(xlsx_sheets_data as any)[sheetName] = x
            console.log(`Sheet ${sheetName} present.`)
          }
          if (sheetName === 'ot') {
            let x = XLSX.utils.sheet_to_json(workbook.value.Sheets[sheetName])
            ;(xlsx_sheets_data as any)[sheetName] = x
            console.log(`Sheet ${sheetName} present.`)
          }
        }
        let config_sheet = XLSX.utils.sheet_to_json(workbook.value.Sheets['config'])
        console.log(config_sheet)
        let sheets_keys = Object.keys(xlsx_sheets_data)
        if (sheets_keys.includes('config')) {
          xlsx_sheets_data['config'].forEach((val: any) => {
            if (val['config'] == 'tiempo_preparacion') {
              modelJob.value.model_input.tiempo_setup = val['valor']
            }
            if (val['config'] == 'cantidad_operarios') {
              modelJob.value.model_input.cantidad_operarios = val['valor']
            }
            if (val['config'] == 'fecha_inicio') {
              modelJob.value.model_input.fecha_inicio = val['valor']
            }
          })
        }
        if (sheets_keys.includes('ot')) {
          rowDataOts.value = xlsx_sheets_data['ot'].map((e: any) => {
            return {
              id: e.__rowNum__,
              ot_nro: e.ot_nro,
              maquina_nro: e.maquina_nro,
              producto_id: e.producto_id,
              producto_desc: e.producto_desc,
              maquina_desc: e.maquina_desc,
              color: e.color,
              peso: e.peso,
              cantidad: e.cantidad,
              horas: e.horas.toFixed(2),
              fecha_vencimiento: utils.dateFmtDmy(e.fecha_vencimiento),
              cadencia: e.cadencia,
              operarios_requeridos: e.operarios_requeridos.toFixed(1),
              prioridad: e.prioridad,
              setup_maquina: e.setup_maquina.toFixed(2),
            }
          })
        }
        if (sheets_keys.includes('fuera_servicio')) {
          rowDataFuera.value = xlsx_sheets_data['fuera_servicio'].map((e: any) => {
            return {
              id: e.__rowNum__,
              maquina: e.maquina,
              hora_inicio: utils.dateFmtDmyh(e.hora_inicio),
              hora_fin: utils.dateFmtDmyh(e.hora_fin),
              motivo: e.motivo,
            }
          })
        }
      }
      reader.readAsBinaryString(file)
    }
  } catch (error: any) {
    notyf.error(error.message)
  }
}

const newJob = async () => {
  isLoading.value = true
  try {
    const originId = route.params.originId as string
    let ret
    if (originId) {
      ret = await modelService.newJobOrigin(originId)
    } else {
      ret = await modelService.newJob()
    }
    modelJob.value = ret
    if (modelJob.value?.model_input?.ots) {
      rowDataOts.value = modelJob.value?.model_input?.ots.map((e: any) => {
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
    if (modelJob.value?.model_input?.fuera_servicios) {
      rowDataFuera.value = modelJob.value?.model_input?.fuera_servicios.map((e: any) => {
        return {
          id: e.id,
          maquina: e.maquina,
          hora_inicio: utils.isoToDmyhm(e.hora_inicio),
          hora_fin: utils.isoToDmyhm(e.hora_fin),
          motivo: e.motivo,
        }
      })
    }
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

const vErrors = ref({
  tiempo_setup: false,
  cantidad_operarios: false,
  fecha_inicio: false,
  ots: false,
})
const validateForm = () => {
  vErrors.value.tiempo_setup = !modelJob.value?.model_input?.tiempo_setup
  vErrors.value.cantidad_operarios = !modelJob.value?.model_input?.cantidad_operarios
  vErrors.value.fecha_inicio = !modelJob.value?.model_input?.fecha_inicio
  let curRowData = rowDataOts.value.slice()
  vErrors.value.ots = !curRowData || curRowData.length == 0

  return (
    !vErrors.value.tiempo_setup &&
    !vErrors.value.cantidad_operarios &&
    !vErrors.value.fecha_inicio &&
    !vErrors.value.ots
  )
}

const runModel = async () => {
  try {
    if (validateForm()) {
      modelJob.value.model_input.ots = rowDataOts.value.slice().map((e: any) => {
        return {
          id: e.id,
          ot_nro: `${e.ot_nro}`,
          maquina_nro: `${e.maquina_nro}`,
          producto_id: `${e.producto_id}`,
          producto_desc: e.producto_desc,
          maquina_desc: e.maquina_desc,
          color: e.color,
          peso: parseFloat(e.peso),
          cantidad: parseInt(e.cantidad),
          horas: parseFloat(e.horas),
          fecha_vencimiento: utils.dmyToIso(e.fecha_vencimiento),
          cadencia: parseInt(e.cadencia),
          operarios_requeridos: parseFloat(e.operarios_requeridos),
          prioridad: parseInt(e.prioridad),
          setup_maquina: parseFloat(e.setup_maquina),
        }
      })
      modelJob.value.model_input.fuera_servicios = rowDataFuera.value.slice().map((e: any) => {
        return {
          id: e.id,
          maquina: `${e.maquina}`,
          hora_inicio: utils.dmyhmToIso(e.hora_inicio),
          hora_fin: utils.dmyhmToIso(e.hora_fin),
          motivo: e.motivo,
        }
      })
      const obj_r = await modelService.solveJob(modelJob.value)
      notyf.success(`Planificación ${modelJob.value?.number} en cola de ejecución`)
      router.push({ name: 'job-edit', params: { objId: obj_r.id } })
    }
  } catch (error: any) {
    notyf.error(error.message)
  }
}
onBeforeMount(async () => {
  await newJob()
})
</script>

<template>
  <VBreadcrumb
    v-if="modelJob"
    :items="[
      {
        label: 'Home',
        hideLabel: true,
        icon: 'feather:home',
        to: { name: 'home' },
      },
      {
        label: 'Planificaciones',
        icon: 'icon-park-outline:timeline',
        to: { name: 'jobs' },
      },
      {
        label: modelJob.number ?? 'unknown',
      },
    ]"
    with-icons
  />

  <div v-if="!isLoading && modelJob" class="job-details">
    <div class="tabs-wrapper">
      <div class="tabs-inner">
        <div class="tabs is-toggle">
          <ul>
            <li :class="[tab === 'input' && 'is-active']">
              <a @click="tab = 'input'"><span>Datos de entrada</span></a>
            </li>
          </ul>
        </div>
      </div>

      <!-- T1 Model input -->
      <div v-if="tab === 'input'" class="tab-content is-active">
        <div v-if="modelJob" class="columns job-details-inner">
          <div class="column is-12">
            <div class="job-details-card">
              <div class="card-head">
                <div class="title-wrap">
                  <h3>Planificación # {{ modelJob.number }}</h3>
                  <p>{{ utils.dateFmtDmyh(modelJob.creation_date) }} - {{ modelJob.creation_user }}</p>
                  <JobStatus :model-job="modelJob" />
                </div>
                <VButtons align="right">
                  <VButton color="primary" icon="icon-park-outline:play-one" elevated @click="runModel()">
                    Ejecutar Planificación
                  </VButton>
                  <VButton
                    href="/app5/model_input_sample.xlsx"
                    color="primary"
                    icon="icon-park-outline:excel"
                    elevated
                    outlined
                  >
                    Ejemplo
                  </VButton>
                  <VButton
                    href="/app5/model_input_sample_empty.xlsx"
                    color="primary"
                    icon="icon-park-outline:file-withdrawal-one"
                    outlined
                    elevated
                  >
                    Plantilla
                  </VButton>
                </VButtons>
              </div>
              <div class="job-files">
                <h4>Parámetros</h4>
                <div class="columns is-multiline">
                  <div class="column is-3">
                    <VField v-tooltip="'Tiempo de preparación (horas)'" label="* Tiempo de preparación (h)">
                      <VControl :has-error="vErrors.tiempo_setup">
                        <VInput
                          v-model.number="modelJob.model_input.tiempo_setup"
                          type="number"
                          class="input"
                          placeholder=""
                        />
                        <p v-if="vErrors.tiempo_setup" class="help text-danger">Tiempo de preparación es requerido</p>
                      </VControl>
                    </VField>
                  </div>
                  <div class="column is-3">
                    <VField
                      v-tooltip="'Cantidad de operarios disponibles para el conjunto de máquinas'"
                      label="* Cant. operarios disponibles"
                    >
                      <VControl :has-error="vErrors.cantidad_operarios">
                        <VInput
                          v-model.number="modelJob.model_input.cantidad_operarios"
                          type="number"
                          class="input"
                          placeholder=""
                        />
                        <p v-if="vErrors.cantidad_operarios" class="help text-danger">
                          Cantidad Operarios es requerido
                        </p>
                      </VControl>
                    </VField>
                  </div>
                  <div class="column is-3">
                    <VDatePicker
                      v-model="modelJob.model_input.fecha_inicio"
                      locale="es"
                      color="green"
                      trim-weeks
                      :masks="{ L: 'DD/MM/YYYY' }"
                      mode="dateTime"
                      is24hr
                    >
                      <template #default="{ inputValue, inputEvents }">
                        <VField label="* Fecha y Hora de inicio del plan">
                          <VControl icon="icon-park-outline:alarm-clock" :has-error="vErrors.fecha_inicio">
                            <input class="input v-input" type="text" :value="inputValue" v-on="inputEvents" />
                          </VControl>
                          <p v-if="vErrors.fecha_inicio" class="help text-danger">Fecha de inicio es requerida</p>
                        </VField>
                      </template>
                    </VDatePicker>
                  </div>
                  <div class="column is-3">
                    <h4>Cargar desde XLSX</h4>
                    <VField grouped>
                      <VControl>
                        <div class="file has-name">
                          <label class="file-label">
                            <input
                              class="file-input"
                              type="file"
                              name="resume"
                              accept=".xls,.xlsx"
                              @change="onSelectXLSXFile"
                            />
                            <span class="file-cta">
                              <span class="file-icon">
                                <i class="fas fa-cloud-upload-alt"></i>
                              </span>
                              <span class="file-label"> Seleccionar archivo Excel… </span>
                            </span>
                            <span class="file-name light-text"> {{ input_filename }} </span>
                          </label>
                        </div>
                      </VControl>
                    </VField>
                  </div>
                </div>
              </div>
              <div class="job-files">
                <h4>Órdenes de trabajo</h4>
                <div class="columns is-multiline">
                  <div class="column is-12">
                    <VMessage v-if="vErrors.ots" color="danger"> Al menos una órden de trabajo es requerida. </VMessage>
                    <ag-grid-vue
                      class="ag-theme-alpine"
                      style="height: 400px"
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
              <div class="job-files">
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
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
@import '/@src/scss/abstracts/all';
@import '/@src/scss/components/forms-outer';

.form-layout {
  max-width: 740px;
  margin: 0 auto;
}

/* ==========================================================================
1. Project Details
========================================================================== */

.is-navbar {
  .job-details {
    padding-top: 30px;
  }
}

.job-details {
  .tabs-wrapper {
    .tabs-inner {
      .tabs {
        margin: 0 auto;

        li {
          background: var(--white);
        }
      }
    }
  }

  .job-details-inner {
    padding: 20px 0;

    .job-details-card {
      @include vuero-s-card();

      padding: 40px;

      .card-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        // margin-bottom: 20px;

        .title-wrap {
          h3 {
            font-family: var(--font-alt);
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--dark-text);
            line-height: 1.2;
            transition: all 0.3s;
          }
        }
      }

      .claim-overview {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 0;

        p {
          max-width: 420px;
        }
      }

      .job-features {
        display: flex;
        padding: 15px 0;
        border-top: 1px solid var(--fade-grey-dark-3);
        border-bottom: 1px solid var(--fade-grey-dark-3);

        .job-feature {
          margin-right: 20px;
          width: calc(25% - 20px);

          i {
            font-size: 1.6rem;
            color: var(--primary);
            margin-bottom: 8px;
          }

          h4 {
            font-family: var(--font-alt);
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--dark);
          }

          p {
            line-height: 1.2;
            font-size: 0.85rem;
            color: var(--light-text);
            margin-bottom: 0;
          }
        }
      }

      .job-files {
        padding: 10px 0;

        h4 {
          font-family: var(--font-alt);
          font-weight: 600;
          font-size: 0.9rem;
          text-transform: uppercase;
          color: var(--primary);
          margin-bottom: 12px;
        }

        .file-box {
          display: flex;
          align-items: center;
          padding: 8px;
          background: var(--white);
          border: 1px solid transparent;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s;

          &:hover {
            border-color: var(--fade-grey-dark-3);
            box-shadow: var(--light-box-shadow);
          }

          img {
            display: block;
            width: 48px;
            min-width: 48px;
            height: 48px;
          }

          .meta {
            margin-left: 12px;
            line-height: 1.3;

            span {
              display: block;

              &:first-child {
                font-family: var(--font-alt);
                font-size: 0.9rem;
                font-weight: 600;
                color: var(--dark-text);
              }

              &:nth-child(2) {
                font-size: 0.9rem;
                color: var(--light-text);

                i {
                  position: relative;
                  top: -3px;
                  font-size: 0.3rem;
                  color: var(--light-text);
                  margin: 0 4px;
                }
              }
            }
          }

          .dropdown {
            margin-left: auto;
          }
        }
      }
    }

    .side-card {
      @include vuero-s-card();

      padding: 40px;
      margin-bottom: 1.5rem;

      h4 {
        font-family: var(--font-alt);
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        color: var(--primary);
        margin-bottom: 16px;
      }
    }

    .job-team-card {
      @include vuero-s-card();

      padding: 40px;
      max-width: 940px;
      display: block;
      margin: 0 auto;

      .column {
        padding: 1.5rem;

        &:nth-child(odd) {
          border-right: 1px solid var(--fade-grey-dark-3);
        }

        &.has-border-bottom {
          border-bottom: 1px solid var(--fade-grey-dark-3);
        }
      }
    }

    .task-grid {
      .grid-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;

        h3 {
          font-family: var(--font-alt);
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--dark-text);
          line-height: 1.2;
        }

        .buttons {
          display: flex;
          align-items: center;
          background: var(--white);
          padding: 8px 24px;
          border-radius: 100px;

          > span {
            font-family: var(--font-alt);
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--dark-text);
            margin-right: 20px;
          }
        }
      }

      .task-card {
        @include vuero-s-card();

        min-height: 200px;
        display: flex !important;
        flex-direction: column;
        justify-content: space-between;
        padding: 30px;
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          transform: translateY(-5px);
          box-shadow: var(--light-box-shadow);
        }

        .title-wrap {
          h3 {
            font-size: 1.1rem;
            font-family: var(--font-alt);
            font-weight: 600;
            color: var(--dark-text);
            line-height: 1.2;
            margin-bottom: 4px;
          }

          span {
            font-family: var(--font);
            font-size: 0.9rem;
            color: var(--light-text);
          }
        }

        .content-wrap {
          display: flex;
          align-items: center;
          justify-content: space-between;

          .left {
            .attachments {
              display: flex;
              align-items: center;

              i {
                font-size: 15px;
                color: var(--light-text);
              }

              span {
                margin-left: 2px;
                font-size: 0.9rem;
                font-family: var(--font);
                color: var(--light-text);
              }
            }
          }
        }

        .content-wrap-full {
          align-items: center;
          justify-content: space-between;

          .left {
            .attachments {
              display: flex;
              align-items: center;

              i {
                font-size: 15px;
                color: var(--light-text);
              }

              span {
                margin-left: 2px;
                font-size: 0.9rem;
                font-family: var(--font);
                color: var(--light-text);
              }
            }
          }
        }
      }
    }
  }
}

/* ==========================================================================
  2. Project Details Dark Mode
  ========================================================================== */

.is-dark {
  .job-details {
    .job-details-inner {
      .job-details-card {
        @include vuero-card--dark();

        .card-head {
          .title-wrap {
            h3 {
              color: var(--dark-dark-text) !important;
            }
          }
        }

        .job-features {
          border-color: var(--dark-sidebar-light-12);

          .job-feature {
            i {
              color: var(--primary);
            }

            h4 {
              color: var(--dark-dark-text);
            }
          }
        }

        .job-files {
          h4 {
            color: var(--primary);
          }

          .file-box {
            background: var(--dark-sidebar-light-3);

            &:hover {
              border-color: var(--dark-sidebar-light-10);
            }

            .meta {
              span {
                &:first-child {
                  color: var(--dark-dark-text);
                }
              }
            }
          }
        }
      }

      .side-card {
        @include vuero-card--dark();

        h4 {
          color: var(--primary);
        }
      }

      .job-team-card {
        @include vuero-card--dark();

        .column {
          border-color: var(--dark-sidebar-light-12);
        }
      }

      .task-grid {
        .grid-header {
          h3 {
            color: var(--dark-dark-text);
          }

          .filter {
            background: var(--dark-sidebar-light-1) !important;
            border-color: var(--dark-sidebar-light-4) !important;

            > span {
              color: var(--dark-dark-text);
            }
          }
        }

        .task-card {
          @include vuero-card--dark();

          .title-wrap {
            h3 {
              color: var(--dark-dark-text);
            }
          }
        }
      }
    }
  }
}

/* ==========================================================================
  3. Media Queries
  ========================================================================== */

@media only screen and (max-width: 767px) {
  .job-details {
    .job-details-inner {
      .job-details-card {
        padding: 30px;

        .claim-overview {
          flex-direction: column;

          p {
            margin-bottom: 20px;
          }
        }

        .job-features {
          flex-wrap: wrap;

          .job-feature {
            width: calc(50% - 20px);
            text-align: center;
            margin: 0 10px;

            &:first-child,
            &:nth-child(2) {
              margin-bottom: 20px;
            }
          }
        }
      }

      .job-team-card {
        padding: 30px;

        .column {
          border-right: none !important;
        }
      }
    }
  }
}

@media only screen and (min-width: 768px) and (max-width: 1024px) and (orientation: portrait) {
  .job-details {
    .job-details-inner {
      .job-details-card {
        .job-files {
          .columns {
            display: flex;

            .column {
              min-width: 50%;
            }
          }
        }
      }

      .job-team-card {
        .columns {
          display: flex;

          .column {
            min-width: 50%;
          }
        }
      }

      .task-grid {
        .columns {
          display: flex;

          .column {
            min-width: 50%;
          }
        }
      }
    }
  }
}
</style>
