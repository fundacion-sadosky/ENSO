<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ModelJob } from '/@src/models/model'
import { utils } from '/@src/services/utils'
import { chartUtils } from '/@src/services/chartUtils'
import { useNotyf } from '/@src/composable/useNotyf'

const notyf = useNotyf()
const FUERA_SERVICIO = 'FUERA SERVICIO'
export interface JobOutputProps {
  modelJob?: ModelJob
}
const props = withDefaults(defineProps<JobOutputProps>(), {
  modelJob: undefined,
})
const rangeGanttDates = ref([0, 100])
const planInicio: Date = computed(() => {
  if (props.modelJob.model_output?.plan_inicio_preparacion) {
    return utils.isoToDate(props.modelJob.model_output.plan_inicio_preparacion)
  } else {
    return utils.isoToDate(props.modelJob.model_output.plan_inicio)
  }
})
const planFin: Date = computed(() => {
  return utils.isoToDate(props.modelJob.model_output.plan_fin)
})
const timeDiff: number = computed(() => {
  return planFin.value.getTime() - planInicio.value.getTime()
})
const ganttPlanInicio: Date = computed(() => {
  return new Date(planInicio.value.getTime() + rangeGanttDates.value[0] * 0.01 * timeDiff.value)
})
const ganttPlanFin: Date = computed(() => {
  return new Date(planInicio.value.getTime() + rangeGanttDates.value[1] * 0.01 * timeDiff.value)
})

const ganttData: any = computed(() => {
  if (props.modelJob.model_output?.agenda_maquina_ot) {
    let baseList = []
    props.modelJob.model_output.agenda_maquina_ot.forEach((item: any) => {
      baseList.push(item)
    })
    // add fuera de servicio
    if (props.modelJob.model_input?.fuera_servicios) {
      props.modelJob.model_input?.fuera_servicios.forEach((item_fuera: any) => {
        baseList.push({
          id: 100 + item_fuera.id,
          ot_nro: `${FUERA_SERVICIO}: ${item_fuera.motivo}`,
          maquina_nro: item_fuera.maquina,
          hora_inicio: item_fuera.hora_inicio,
          hora_fin: item_fuera.hora_fin,
        })
      })
    }
    // get list of machines
    const uniqueMs = new Set()
    baseList.forEach((item) => uniqueMs.add(item.maquina_nro))
    let dataD = []
    uniqueMs.forEach((mnro) => {
      // filter ots by machine and build elements
      const elem = baseList
        .filter((item: any) => {
          return item.maquina_nro === mnro
        })
        .map((item: any) => {
          let label = `OT ${item.ot_nro}`
          if (item.ot_nro.startsWith(FUERA_SERVICIO)) {
            label = item.ot_nro
          } else if (item.is_setup_maquina) {
            label = `SETUP ${item.ot_nro}`
          }
          return {
            otBeginDate: utils.isoToGantt(item.hora_inicio),
            otEndDate: utils.isoToGantt(item.hora_fin),
            ganttBarConfig: {
              // each bar must have a nested ganttBarConfig object ...
              // ... and a unique "id" property
              id: item.id,
              label: label,
              style: {
                background: chartUtils.getRandomColor(),
                borderRadius: '5px',
                color: 'black',
              },
            },
          }
        })
      let gmrow = `${mnro}`
      let order_nro = 0
      if (gmrow.endsWith('pre')) {
        order_nro = parseInt(gmrow.replace(/pre$/, '')) * 100 + 1
      } else {
        order_nro = parseInt(gmrow) * 100
      }
      dataD.push({
        label: `M${mnro}`,
        fldsort: order_nro,
        list: elem,
      })
    })
    dataD = dataD.sort((a: any, b: any) => a.fldsort - b.fldsort)

    return dataD
  }
  return []
})

const agentaotslist = computed(() => {
  if (props.modelJob.model_output?.agenda_maquina_ot) {
    let baseList = []
    props.modelJob.model_output.agenda_maquina_ot.forEach((item: any) => {
      baseList.push(item)
    })
    let data = baseList
      //.sort((a: any, b: any) => a.hour - b.hour)
      .map((item: any, index: number) => {
        return [
          index + 1,
          `M${item.maquina_nro}`,
          item.ot_nro,
          item.descripcion?.length > 0 ? item.descripcion : `${item.cant_personal} operarios`,
          utils.isoToDmyhm(item.hora_inicio),
          utils.isoToDmyhm(item.hora_fin),
        ]
      })
    return data
  }

  return []
})

const showOt = (bar: any) => {
  const bar_label = bar.ganttBarConfig.label
  let otLabel = `<b>${bar_label}</b>`
  if (bar_label.startsWith('OT ')) {
    if (props.modelJob.model_input?.ots) {
      const ots = props.modelJob.model_input?.ots.filter((ot: any) => {
        return bar_label.endsWith(ot.ot_nro)
      })
      if (ots.length > 0) {
        const i = ots[0]
        otLabel += ` <br>${i.producto_id} ${i.producto_desc}`
        otLabel += ` <br>${i.operarios_requeridos} operarios, ${i.horas} horas, ${i.cantidad} unidades`
      }
    }
  } else if (bar_label.startsWith('SETUP ')) {
    if (props.modelJob.model_input?.ots) {
      const ots = props.modelJob.model_input?.ots.filter((ot: any) => {
        return bar_label.endsWith(ot.ot_nro)
      })
      if (ots.length > 0) {
        const i = ots[0]
        otLabel += ` <br>Tiempo de Preparación`
        otLabel += ` <br>OT ${i.ot_nro}, ${i.setup_maquina} horas`
      }
    }
  }
  notyf.infoNoClose(otLabel)
}
</script>

<template>
  <div v-if="props.modelJob.model_output" class="job-files">
    <h4>Resultados de la planificación</h4>
    <div class="columns is-multiline">
      <div v-if="props.modelJob.model_output.completamiento_ordenes" class="column is-2">
        <VCard color="primary">
          <h3 class="title is-5 mb-2">Duración del Plan</h3>
          <h3 class="title is-5 mb-2">{{ props.modelJob.model_output.completamiento_ordenes.toFixed(2) }} horas</h3>
        </VCard>
      </div>
      <div v-if="props.modelJob.model_output.total_produccion" class="column is-2">
        <VCard color="info">
          <h3 class="title is-5 mb-2">Tiempo total de Producción</h3>
          <h3 class="title is-5 mb-2">{{ props.modelJob.model_output.total_produccion.toFixed(2) }} horas</h3>
        </VCard>
      </div>
      <div v-if="props.modelJob.model_output.total_setup" class="column is-2">
        <VCard color="info">
          <h3 class="title is-5 mb-2">Tiempo total de Setup</h3>
          <h3 class="title is-5 mb-2">{{ props.modelJob.model_output.total_setup.toFixed(2) }} horas</h3>
        </VCard>
      </div>
      <div v-if="props.modelJob.model_output.uso_operarios_total" class="column is-2">
        <VCard color="secondary">
          <h3 class="title is-5 mb-2">Tiempo de uso de Operarios</h3>
          <h3 class="title is-5 mb-2">{{ props.modelJob.model_output.uso_operarios_total.toFixed(2) }} horas</h3>
        </VCard>
      </div>
      <div v-if="props.modelJob.model_output.productividad_operarios" class="column is-2">
        <VCard color="secondary">
          <h3 class="title is-5 mb-2">Productividad Operarios</h3>
          <h3 class="title is-5 mb-2">{{ props.modelJob.model_output.productividad_operarios.toFixed(2) * 100 }} %</h3>
        </VCard>
      </div>
    </div>
  </div>
  <div v-if="props.modelJob.model_output" class="job-files">
    <div class="is-divider"></div>
    <h4>
      Gantt Agenda de OTs - {{ utils.isoToDmyhm(props.modelJob.model_output.plan_inicio) }} a
      {{ utils.isoToDmyhm(props.modelJob.model_output.plan_fin) }}
    </h4>
    <div class="columns is-multiline">
      <div class="column is-12">
        <VField v-slot="{ id }" class="has-rounded-tooltip">
          <VControl>
            <Slider :id="id" v-model="rangeGanttDates" :format="{ suffix: '%' }" />
          </VControl>
        </VField>
        <p>Mostrando desde {{ utils.dateFmtDmyh(ganttPlanInicio) }} hasta {{ utils.dateFmtDmyh(ganttPlanFin) }}</p>
      </div>
      <div class="column is-12">
        <g-gantt-chart
          :chart-start="utils.dateToGantt(ganttPlanInicio)"
          :chart-end="utils.dateToGantt(ganttPlanFin)"
          precision="day"
          bar-start="otBeginDate"
          bar-end="otEndDate"
          color-scheme="vue"
          @click-bar="showOt($event.bar)"
        >
          <template v-for="(item, key) in ganttData" :key="key">
            <g-gantt-row :label="item.label" :bars="item.list" :highlight-on-hover="true" />
          </template>
        </g-gantt-chart>
      </div>
    </div>
  </div>
  <div class="job-files">
    <h4>Resultados de la planificación</h4>
    <div class="columns is-multiline">
      <div class="column is-12">
        <VSimpleDatatables
          v-if="agentaotslist.length > 0"
          :options="{
            perPageSelect: [50],
            perPage: 50,
            columns: [
              { select: 0, hidden: true },
              { select: 1, sortable: true },
              { select: 2, sortable: true },
              { select: 3, sortable: true },
              { select: 4, sortable: true },
              { select: 5, sortable: true },
            ],
            data: {
              headings: ['ID', 'Máquina', 'OT', 'Descripción', 'Inicio', 'Fin'],
              data: agentaotslist,
            },
          }"
        />
      </div>
    </div>
  </div>
</template>
