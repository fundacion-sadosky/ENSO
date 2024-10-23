<script setup lang="ts">
import { computed, ref, onBeforeMount } from 'vue'
import { useRoute } from 'vue-router'
import { useNotyf } from '/@src/composable/useNotyf'
import { modelService } from '/@src/services/modelService'
import { utils } from '/@src/services/utils'
import {
  ACT_MACHINE_METRIC_STATUS_TIME,
  ACT_MACHINE_METRIC_STATUS_PER_DAY,
  ACT_MACHINE_METRIC_STATUS_PER_DAY_SENSE,
  ACT_MACHINE_METRIC_STATUS_PER_HOUR,
  ACT_SENSOR_RAW_STATUS,
} from '/@src/data/constants'
import dayjs from 'dayjs'

const route = useRoute()
const isLoading = ref(false)
const notyf = useNotyf()
const dataPerDay = ref({})
const dataPerDaySense = ref({})
const dataPerHour = ref({})
const dataSensorStatus = ref({})
const qfrom = ref(dayjs().add(-7, 'day').toDate())
const qto = ref(dayjs().toDate())
const qday = ref(dayjs().toDate())

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

const loadMachineDataPerDaySense = async () => {
  isLoading.value = true
  try {
    const objId = route.params.objId as string
    const dfrom = dayjs(qfrom.value).format('YYYYMMDD')
    const dto = dayjs(qto.value).format('YYYYMMDD')
    let ret = await modelService.getMachineData(objId, ACT_MACHINE_METRIC_STATUS_PER_DAY_SENSE, dfrom, dto)
    dataPerDaySense.value = ret
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

const loadMachineDataPerHour = async () => {
  isLoading.value = true
  try {
    const objId = route.params.objId as string
    const day = dayjs(qday.value).format('YYYYMMDD')
    console.log(day)
    let ret = await modelService.getMachineData(objId, ACT_MACHINE_METRIC_STATUS_PER_HOUR, day, day)
    console.log(ret)
    dataPerHour.value = ret
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

const loadSensorStatusData = async () => {
  isLoading.value = true
  try {
    const objId = route.params.objId as string
    const day = dayjs(qday.value).format('YYYYMMDD')
    let ret = await modelService.getSensorData(objId, ACT_SENSOR_RAW_STATUS, day)
    dataSensorStatus.value = ret
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

const datasensorstatuslist = computed(() => {
  if (dataSensorStatus.value && dataSensorStatus.value.sense_list) {
    let baseList = dataSensorStatus.value.sense_list
    let data = baseList
      .sort((a: any, b: any) => a.sense_time - b.sense_time)
      .map((item: any) => {
        return [item.id, item.sense_time.slice(11, -13), item.valstr, item.topic]
      })
    return data
  }

  return []
})

const dataperhourlist = computed(() => {
  if (dataPerHour.value && dataPerHour.value.status_list) {
    let baseList = dataPerHour.value.status_list
    let data = baseList
      .sort((a: any, b: any) => a.hour - b.hour)
      .map((item: any, index: number) => {
        return [index + 1, item.hour, item.status, utils.secondsToHourMinutes(item.seconds)]
      })
    return data
  }

  return []
})

const dataperdaylist = computed(() => {
  if (dataPerDay.value && dataPerDay.value.status_list) {
    let baseList = dataPerDay.value.status_list
    let data = baseList
      .sort((a: any, b: any) => a.day - b.day)
      .map((item: any, index: number) => {
        return [index + 1, item.day, item.status, utils.secondsToHourMinutes(item.seconds)]
      })
    return data
  }

  return []
})

const dataperdaysenselist = computed(() => {
  if (dataPerDaySense.value && dataPerDaySense.value.status_list) {
    let baseList = dataPerDaySense.value.status_list
    let data = baseList
      .sort((a: any, b: any) => a.day - b.day)
      .map((item: any, index: number) => {
        return [index + 1, item.day, item.status, item.qty]
      })
    return data
  }

  return []
})

const downloadFileSensorData = async () => {
  try {
    const objId = route.params.objId as string
    const day = dayjs(qday.value).format('YYYYMMDD')
    let fileBlob: Blob = await modelService.getSensorDataFileBlob(objId, ACT_SENSOR_RAW_STATUS, day)
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(fileBlob)
    link.download = `${objId}_${day}.csv`
    link.target = '_blank'
    link.click()
  } catch (error: any) {
    console.log(error)
    notyf.error(error.message)
  }
}

const doQueryPerDay = async () => {
  dataPerDay.value = {}
  dataPerDaySense.value = {}
  await loadMachineDataPerDay()
  await loadMachineDataPerDaySense()
}

const doQueryPerHour = async () => {
  dataPerHour.value = {}
  dataSensorStatus.value = {}
  await loadMachineDataPerHour()
  await loadSensorStatusData()
}

onBeforeMount(async () => {
  await loadMachineDataPerDay()
  await loadMachineDataPerDaySense()
  await loadMachineDataPerHour()
  await loadSensorStatusData()
})
</script>

<template>
  <div class="list-view-toolbar">
    <VBreadcrumb
      :items="[
        {
          label: 'Home',
          hideLabel: true,
          icon: 'feather:home',
          to: { name: 'home' },
        },
        {
          label: `Datos de Máquina ${route.params.objId}`,
          icon: 'icon-park-outline:chart-pie',
          to: { name: 'machine-edit', params: { objId: route.params.objId } },
        },
      ]"
      with-icons
    />
    <VButtons align="right">
      <VButton :to="{ name: 'dash1' }" icon="lnir lnir-arrow-left rem-100" light raised elevated> Volver </VButton>
      <VButton
        :to="{ name: 'machine-charts', params: { objId: route.params.objId } }"
        color="primary"
        icon="icon-park-outline:chart-pie"
        raised
        elevated
      >
        Datos
      </VButton>
    </VButtons>
  </div>
  <VCard>
    <div class="columns is-multiline">
      <div class="column is-3">
        <VBlock :title="'Máquina ' + route.params.objId" subtitle="Datos de sensores por Día" center>
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
  <div class="columns is-multiline mt-2">
    <div class="column is-6">
      <VTag color="info" label="Datos procesados" />
      <VSimpleDatatables
        v-if="dataperdaylist.length > 0"
        :options="{
          perPageSelect: [25, 100],
          perPage: 25,
          columns: [
            { select: 0, hidden: true },
            { select: 1, sortable: true },
            { select: 2, sortable: true },
            { select: 3, sortable: false },
          ],
          data: {
            headings: ['ID', 'Día', 'Estado', 'Tiempo (m)'],
            data: dataperdaylist,
          },
        }"
      />
    </div>
    <div class="column is-6">
      <VTag color="purple" label="Datos recibidos de los sensores" />
      <VSimpleDatatables
        v-if="dataperdaysenselist.length > 0"
        :options="{
          perPageSelect: [25, 100],
          perPage: 25,
          columns: [
            { select: 0, hidden: true },
            { select: 1, sortable: true },
            { select: 2, sortable: true },
            { select: 3, sortable: false },
          ],
          data: {
            headings: ['ID', 'Día', 'Estado', 'Cantidad de sensados'],
            data: dataperdaysenselist,
          },
        }"
      />
    </div>
  </div>
  <VCard>
    <div class="columns is-multiline">
      <div class="column is-3">
        <VBlock :title="'Máquina ' + route.params.objId" subtitle="Datos de sensores por Hora" center>
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
  <div class="columns is-multiline mt-2">
    <div class="column is-6">
      <VTag color="info" label="Datos procesados" />
      <VSimpleDatatables
        v-if="dataperhourlist.length > 0"
        :options="{
          perPageSelect: [25, 100],
          perPage: 25,
          columns: [
            { select: 0, hidden: true },
            { select: 1, sortable: true },
            { select: 2, sortable: true },
            { select: 3, sortable: false },
          ],
          data: {
            headings: ['ID', 'Hora', 'Estado', 'Tiempo (m)'],
            data: dataperhourlist,
          },
        }"
      />
    </div>
    <div class="column is-6">
      <VTag color="purple" label="Datos recibidos de los sensores" />
      <VButton
        class="ml-5"
        color="info"
        icon="icon-park-outline:download-two"
        size="medium"
        @click="downloadFileSensorData()"
      >
        Descargar CSV
      </VButton>
      <VSimpleDatatables
        v-if="datasensorstatuslist.length > 0"
        :options="{
          perPageSelect: [25, 100],
          perPage: 25,
          columns: [
            { select: 0, hidden: true },
            { select: 1, sortable: true },
            { select: 2, sortable: true },
            { select: 3, sortable: true },
          ],
          data: {
            headings: ['ID', 'Hora', 'Valor', 'Topic'],
            data: datasensorstatuslist,
          },
        }"
      />
    </div>
  </div>
</template>
