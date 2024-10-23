<script setup lang="ts">
import { ref, onBeforeMount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { modelService } from '/@src/services/modelService'
import { useNotyf } from '/@src/composable/useNotyf'
import { ACT_KPI_MACHINES_MONTH, optMeses } from '/@src/data/constants'
import { utils } from '/@src/services/utils'
import { GChart } from 'vue-google-charts'

const router = useRouter()
const notyf = useNotyf()
const machines = ref([])
const isLoading = ref(false)
const filters = ref('')
const fltMes = ref('')
const fltAnio = ref('')

const filteredData: any = computed(() => {
  if (!filters.value) {
    return machines.value
  } else {
    return machines.value.filter((item: any) => {
      return item.name.match(new RegExp(filters.value, 'i'))
    })
  }
})

const getChartData = (status_list) => {
  let dataH = [['Estado', 'Minutos']]
  if (status_list) {
    let baseList = status_list
    let dataD = baseList
      .sort((a: any, b: any) => b.seconds - a.seconds)
      .map((item: any) => {
        return [utils.getMachineStatusDesc(item.status), Math.floor(item.seconds / 60)]
      })
    return [...dataH, ...dataD]
  }
  return dataH
}

const chartOptions = {
  title: 'Utilización (minutos)',
  // width: 520,
  // height: 280,
  legend: { position: 'bottom' },
}
const goToMachineData = (machine: string) => {
  router.push({ name: 'machine-charts', params: { objId: machine } })
}
const refreshMachineStatus = async () => {
  isLoading.value = true
  try {
    let ret = await modelService.getKpiDataAction(ACT_KPI_MACHINES_MONTH, fltMes.value, fltAnio.value)
    machines.value = ret.machines
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}
const loadMachineStatus = async () => {
  isLoading.value = true
  try {
    let ret = await modelService.getKpiDataAction(ACT_KPI_MACHINES_MONTH)
    machines.value = ret.machines
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

onBeforeMount(async () => {
  const currentDate = new Date()
  fltAnio.value = currentDate.getFullYear().toString()
  fltMes.value = (currentDate.getMonth() + 1).toString().padStart(2, '0')
  await loadMachineStatus()
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
          label: 'KPIs mes',
          icon: 'icon-park-outline:chart-line',
          to: { name: 'dash1' },
        },
      ]"
      with-icons
    />
    <VButtons align="right">
      <VButton :to="{ name: 'kpi1-last' }" color="primary" icon="icon-park-outline:chart-scatter" raised elevated>
        Ver últimos días
      </VButton>
    </VButtons>
  </div>
  <div v-if="!isLoading">
    <!--Real timeDashboard-->
    <div class="tile-grid-toolbar">
      <VControl icon="feather:search">
        <input v-model="filters" class="input custom-text-filter" placeholder="Filtrar listado..." />
      </VControl>
      <VButtons align="right">
        <VField>
          <VControl>
            <Multiselect v-model="fltMes" mode="single" :options="optMeses" />
          </VControl>
        </VField>
        <VField>
          <VControl>
            <input v-model="fltAnio" class="input" />
          </VControl>
        </VField>
        <VButton color="primary" icon="icon-park-outline:change" raised elevated @click="refreshMachineStatus">
          Aplicar
        </VButton>
      </VButtons>
    </div>
    <div class="columns is-multiline">
      <div v-for="(machine, idx) in filteredData" :key="idx" class="column is-3">
        <VCardAdvanced>
          <template #header-left>
            <VTag :label="machine.name" color="info" rounded />
          </template>
          <template #header-right>
            <VIconButton
              v-tooltip="'Más detalles de la máquina'"
              color="primary"
              icon="icon-park-outline:arrow-right"
              raised
              outlined
              @click="goToMachineData(machine.code)"
            />
          </template>
          <template #content>
            <GChart type="PieChart" :data="getChartData(machine.status_list)" :options="chartOptions" />
          </template>
          <template #footer-left>
            <VButtons>
              <VButton color="primary" icon="icon-park-outline:ecg" outlined>
                Último estado: {{ utils.dateFmtDmyh(machine.last_status_date) }}</VButton
              >
              <VButton color="primary" icon="icon-park-outline:ecg" outlined>
                Mes: {{ machine.sense_month }} estados</VButton
              >
            </VButtons>
          </template>
        </VCardAdvanced>
      </div>
    </div>
  </div>
</template>
