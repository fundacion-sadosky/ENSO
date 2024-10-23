<script setup lang="ts">
import { computed, ref, onBeforeMount } from 'vue'
import { useRoute } from 'vue-router'
import { useNotyf } from '/@src/composable/useNotyf'
import { modelService } from '/@src/services/modelService'
import { utils } from '/@src/services/utils'
import {
  ACT_MACHINE_METRIC_STATUS_TIME,
  ACT_MACHINE_METRIC_STATUS_PER_DAY,
  ACT_MACHINE_METRIC_STATUS_PER_HOUR,
  MACH_STATUS_PRODUCCION,
  MACH_STATUS_PREPARACION,
  MACH_STATUS_CAMBIO_MOLDE,
  MACH_STATUS_CORRECTIVO,
  MACH_STATUS_LIMPIEZA,
  MACH_STATUS_PREVENTIVO,
  MACH_STATUS_SIN_CONEXION,
} from '/@src/data/constants'
import { GChart } from 'vue-google-charts'
import dayjs from 'dayjs'

const route = useRoute()
const isLoading = ref(false)
const notyf = useNotyf()
const data = ref({})
const dataPerDay = ref({})
const dataPerHour = ref({})
// const dataProdPerDay = ref({})
const qfrom = ref(dayjs().add(-7, 'day').toDate())
const qto = ref(dayjs().toDate())
const qday = ref(dayjs().toDate())

const loadMachineData = async () => {
  isLoading.value = true
  try {
    const objId = route.params.objId as string
    const dfrom = dayjs(qfrom.value).format('YYYYMMDD')
    const dto = dayjs(qto.value).format('YYYYMMDD')
    let ret = await modelService.getMachineData(objId, ACT_MACHINE_METRIC_STATUS_TIME, dfrom, dto)
    data.value = ret
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

const loadMachineDataPerDay = async () => {
  isLoading.value = true
  try {
    const objId = route.params.objId as string
    const dfrom = dayjs(qfrom.value).format('YYYYMMDD')
    const dto = dayjs(qto.value).format('YYYYMMDD')
    let ret = await modelService.getMachineData(objId, ACT_MACHINE_METRIC_STATUS_PER_DAY, dfrom, dto)
    dataPerDay.value = ret
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

const loadMachineDataPerHour = async () => {
  isLoading.value = true
  try {
    const objId = route.params.objId as string
    const dto = dayjs(qday.value).format('YYYYMMDD')
    let ret = await modelService.getMachineData(objId, ACT_MACHINE_METRIC_STATUS_PER_HOUR, dto, dto)
    dataPerHour.value = ret
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

// const loadProductPerDay = async () => {
//   isLoading.value = true
//   try {
//     const objId = route.params.objId as string
//     const dfrom = dayjs(qfrom.value).format('YYYYMMDD')
//     const dto = dayjs(qto.value).format('YYYYMMDD')
//     let ret = await modelService.getProductData(objId, ACT_PRODUCT_METRIC_PRODUCED_PER_DAY, dfrom, dto)
//     dataProdPerDay.value = ret
//   } catch (error: any) {
//     notyf.error(error.message)
//   }
//   isLoading.value = false
// }

const doQueryPerDay = async () => {
  await loadMachineData()
  await loadMachineDataPerDay()
  // await loadProductPerDay()
}

const doQueryPerHour = async () => {
  await loadMachineDataPerHour()
}

const chartData: any = computed(() => {
  let dataH = [['Estado', 'Minutos']]
  if (data.value && data.value.status_list) {
    let baseList = data.value.status_list
    let dataD = baseList
      .sort((a: any, b: any) => b.seconds - a.seconds)
      .map((item: any) => {
        return [utils.getMachineStatusDesc(item.status), Math.floor(item.seconds / 60)]
      })
    return [...dataH, ...dataD]
  }
  return dataH
})

const chartOptions = {
  title: 'Utilización de la máquina (minutos)',
  // width: 520,
  height: 280,
}

const filterData2 = (list: any[], flt: string) => {
  let ret = 0.0
  const fltList = list.filter((it: any) => {
    return it.status === flt
  })
  if (fltList.length > 0) ret = fltList[0].seconds / 3600
  return ret
}
const chartData2: any = computed(() => {
  let dataH = [
    [
      'Día',
      MACH_STATUS_PRODUCCION,
      MACH_STATUS_PREPARACION,
      MACH_STATUS_CAMBIO_MOLDE,
      MACH_STATUS_CORRECTIVO,
      MACH_STATUS_LIMPIEZA,
      MACH_STATUS_PREVENTIVO,
      MACH_STATUS_SIN_CONEXION,
    ],
  ]
  if (dataPerDay.value && dataPerDay.value.status_list) {
    const grouped1 = dataPerDay.value.status_list.reduce((result, item) => {
      const day = item.day
      if (!result[day]) {
        result[day] = []
      }
      result[day].push(item)
      return result
    }, {})

    const grouped2 = Object.keys(grouped1).map((day) => ({
      day,
      items: grouped1[day],
    }))
    const dataD = grouped2.map((item: any) => {
      return [
        `${item.day.substring(6, 8)}/${item.day.substring(4, 6)}`,
        filterData2(item.items, MACH_STATUS_PRODUCCION),
        filterData2(item.items, MACH_STATUS_PREPARACION),
        filterData2(item.items, MACH_STATUS_CAMBIO_MOLDE),
        filterData2(item.items, MACH_STATUS_CORRECTIVO),
        filterData2(item.items, MACH_STATUS_LIMPIEZA),
        filterData2(item.items, MACH_STATUS_PREVENTIVO),
        filterData2(item.items, MACH_STATUS_SIN_CONEXION),
      ]
    })
    return [...dataH, ...dataD]
  }
  return dataH
})
const chartOptions2 = {
  title: 'Estados por día (horas)',
  legend: { position: 'bottom' },
  isStacked: true,
}

// const chartData3: any = computed(() => {
//   let dataH = [['Día', 'Producido']]
//   if (dataProdPerDay.value && dataProdPerDay.value.status_list) {
//     let baseList = dataProdPerDay.value.status_list
//     let dataD = baseList
//       .sort((a: any, b: any) => a.day - b.day)
//       .map((item: any) => {
//         return [`${item.day.substring(6, 8)}/${item.day.substring(4, 6)}`, item.seconds / 3600]
//       })
//     return [...dataH, ...dataD]
//   }
//   return dataH
// })

// const chartOptions3 = {
//   title: 'Productos fabricados por día',
//   legend: { position: 'bottom' },
// }

const filterData4 = (list: any[], flt: string) => {
  let ret = 0
  const fltList = list.filter((it: any) => {
    return it.status === flt
  })
  if (fltList.length > 0) ret = fltList[0].seconds / 60
  return ret
}
const chartData4: any = computed(() => {
  let dataH = [
    [
      'Hora',
      MACH_STATUS_PRODUCCION,
      MACH_STATUS_PREPARACION,
      MACH_STATUS_CAMBIO_MOLDE,
      MACH_STATUS_CORRECTIVO,
      MACH_STATUS_LIMPIEZA,
      MACH_STATUS_PREVENTIVO,
      MACH_STATUS_SIN_CONEXION,
    ],
  ]
  if (dataPerHour.value && dataPerHour.value.status_list) {
    const grouped1 = dataPerHour.value.status_list.reduce((result, item) => {
      const hour = item.hour
      if (!result[hour]) {
        result[hour] = []
      }
      result[hour].push(item)
      return result
    }, {})

    const grouped2 = Object.keys(grouped1).map((hour) => ({
      hour,
      items: grouped1[hour],
    }))
    let dataD = grouped2
      .map((item: any) => {
        return [
          item.hour,
          filterData4(item.items, MACH_STATUS_PRODUCCION),
          filterData4(item.items, MACH_STATUS_PREPARACION),
          filterData4(item.items, MACH_STATUS_CAMBIO_MOLDE),
          filterData4(item.items, MACH_STATUS_CORRECTIVO),
          filterData4(item.items, MACH_STATUS_LIMPIEZA),
          filterData4(item.items, MACH_STATUS_PREVENTIVO),
          filterData4(item.items, MACH_STATUS_SIN_CONEXION),
        ]
      })
      .sort((a: any, b: any) => a[0].localeCompare(b[0]))

    return [...dataH, ...dataD]
  }
  return dataH
})
const chartOptions4: any = computed(() => {
  return {
    title: 'Estados por hora ' + dayjs(qto.value).format('DD/MM/YYYY') + ' (minutos)',
    legend: { position: 'bottom' },
    isStacked: true,
  }
})

onBeforeMount(async () => {
  await loadMachineData()
  await loadMachineDataPerDay()
  await loadMachineDataPerHour()
  // await loadProductPerDay()
})
</script>

<template>
  <div class="list-view-toolbar">
    <VBreadcrumb
      v-if="data.machine"
      :items="[
        {
          label: 'Home',
          hideLabel: true,
          icon: 'feather:home',
          to: { name: 'home' },
        },
        {
          label: `Datos de Máquina ${data.machine}`,
          icon: 'icon-park-outline:chart-pie',
          to: { name: 'machine-edit', params: { objId: data.machine } },
        },
      ]"
      with-icons
    />
    <VButtons align="right">
      <VButton :to="{ name: 'dash1' }" icon="lnir lnir-arrow-left rem-100" light raised elevated> Volver </VButton>
      <VButton
        :to="{ name: 'machine-data', params: { objId: route.params.objId } }"
        color="primary"
        icon="icon-park-outline:table"
        raised
        elevated
      >
        Datos
      </VButton>
    </VButtons>
  </div>
  <VCard v-if="data.machine">
    <div class="columns is-multiline">
      <div class="column is-3">
        <VBlock :title="'Máquina ' + data.machine" subtitle="Estadísticas por Día" center>
          <template #icon>
            <VIconBox size="medium" color="info" rounded>
              <i aria-hidden="true" class="iconify" data-icon="icon-park-outline:factory-building"></i>
            </VIconBox>
          </template>
          <template #action><slot name="action"></slot></template>
        </VBlock>
      </div>
      <div class="column is-3">
        <VDatePicker v-model="qfrom" locale="es" color="green" trim-weeks :masks="{ L: 'DD/MM/YYYY' }">
          <template #default="{ inputValue, inputEvents }">
            <VField label="Desde">
              <VControl icon="icon-park-outline:calendar">
                <input class="input v-input" type="text" :value="inputValue" v-on="inputEvents" />
              </VControl>
            </VField>
          </template>
        </VDatePicker>
      </div>
      <div class="column is-3">
        <VDatePicker v-model="qto" locale="es" color="green" trim-weeks :masks="{ L: 'DD/MM/YYYY' }">
          <template #default="{ inputValue, inputEvents }">
            <VField label="Hasta">
              <VControl icon="icon-park-outline:calendar">
                <input class="input v-input" type="text" :value="inputValue" v-on="inputEvents" />
              </VControl>
            </VField>
          </template>
        </VDatePicker>
      </div>
      <div class="column is-3">
        <br />
        <VButton color="primary" raised outlined @click="doQueryPerDay">Aplicar</VButton>
      </div>
    </div>
  </VCard>
  <div v-if="data.machine" class="columns is-multiline mt-2">
    <div class="column is-6">
      <GChart type="PieChart" :data="chartData" :options="chartOptions" />
    </div>
    <div class="column is-6">
      <table class="table is-striped is-fullwidth">
        <thead>
          <tr>
            <th scope="col">Estado</th>
            <th scope="col" class="is-end">
              <div class="dark-inverted is-flex is-justify-content-flex-end">Tiempo</div>
            </th>
            <th scope="col" class="is-end">
              <div class="dark-inverted is-flex is-justify-content-flex-end">Porcentaje</div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(obj, index) in chartData.slice(1)" :key="index">
            <td>{{ obj[0] }}</td>
            <td class="is-end">
              <div class="is-flex is-justify-content-flex-end">
                {{ utils.minutesToHourMinutes(obj[1]) }}
              </div>
            </td>
            <td class="is-end">
              <div class="is-flex is-justify-content-flex-end">
                {{ ((obj[1] / (data.total_seconds / 60)) * 100).toFixed(2) }} %
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- <div v-if="chartData3.length > 1" class="column is-12">
      <GChart type="LineChart" :data="chartData3" :options="chartOptions3" />
    </div> -->
    <div v-if="chartData2.length > 1" class="column is-12">
      <GChart type="ColumnChart" :data="chartData2" :options="chartOptions2" />
    </div>
  </div>
  <VCard v-if="data.machine">
    <div class="columns is-multiline">
      <div class="column is-3">
        <VBlock :title="'Máquina ' + data.machine" subtitle="Estadísticas por Hora" center>
          <template #icon>
            <VIconBox size="medium" color="info" rounded>
              <i aria-hidden="true" class="iconify" data-icon="icon-park-outline:factory-building"></i>
            </VIconBox>
          </template>
          <template #action><slot name="action"></slot></template>
        </VBlock>
      </div>
      <div class="column is-3">
        <VDatePicker v-model="qday" locale="es" color="green" trim-weeks :masks="{ L: 'DD/MM/YYYY' }">
          <template #default="{ inputValue, inputEvents }">
            <VField label="Día">
              <VControl icon="icon-park-outline:calendar">
                <input class="input v-input" type="text" :value="inputValue" v-on="inputEvents" />
              </VControl>
            </VField>
          </template>
        </VDatePicker>
      </div>
      <div class="column is-3">
        <br />
        <VButton color="primary" raised outlined @click="doQueryPerHour">Aplicar</VButton>
      </div>
    </div>
  </VCard>
  <div v-if="data.machine" class="columns is-multiline mt-2">
    <div v-if="chartData4.length > 1" class="column is-12">
      <GChart type="ColumnChart" :data="chartData4" :options="chartOptions4" />
    </div>
  </div>
</template>
