<script setup lang="ts">
import { ref, onBeforeMount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { modelService } from '/@src/services/modelService'
import { useNotyf } from '/@src/composable/useNotyf'
import { ACT_KPI_MACHINES_LAST } from '/@src/data/constants'
import { utils } from '/@src/services/utils'

const router = useRouter()
const notyf = useNotyf()
const machines = ref([])
const isLoading = ref(false)
const filters = ref('')

const filteredData: any = computed(() => {
  if (!filters.value) {
    return machines.value
  } else {
    return machines.value.filter((item: any) => {
      return item.name.match(new RegExp(filters.value, 'i'))
    })
  }
})
const goToMachineData = (machine: string) => {
  router.push({ name: 'machine-charts', params: { objId: machine } })
}
const loadMachineStatus = async () => {
  isLoading.value = true
  try {
    let ret = await modelService.getKpiDataAction(ACT_KPI_MACHINES_LAST)
    machines.value = ret.machines
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}
onBeforeMount(async () => {
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
          label: 'KPIs últimos días',
          icon: 'icon-park-outline:chart-scatter',
          to: { name: 'dash1' },
        },
      ]"
      with-icons
    />
    <VButtons align="right">
      <VButton :to="{ name: 'kpi1' }" color="primary" icon="icon-park-outline:chart-line" raised elevated>
        Ver mes
      </VButton>
    </VButtons>
  </div>
  <div v-if="!isLoading">
    <!--Real timeDashboard-->
    <div class="tile-grid-toolbar">
      <VControl icon="feather:search">
        <input v-model="filters" class="input custom-text-filter" placeholder="Buscar..." />
      </VControl>
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
            <VBlock title="Último estado" :subtitle="utils.dateFmtDmyh(machine.last_status_date)">
              <template #icon>
                <VIconBox size="big" :color="utils.getMachineStatusColor(machine?.last_status?.value)" rounded>
                  <i class="iconify" :data-icon="utils.getMachineStatusIcon(machine?.last_status?.value)"></i>
                </VIconBox>
              </template>
            </VBlock>
          </template>
          <template #footer-left>
            <VButtons>
              <VButton color="primary" icon="icon-park-outline:ecg" outlined>
                Día anterior: {{ machine.sense_last_1d }} estados</VButton
              >
              <VButton color="primary" icon="icon-park-outline:ecg" outlined>
                Últimos 7 días: {{ machine.sense_last_7d }} estados</VButton
              >
              <VButton color="primary" icon="icon-park-outline:ecg" outlined>
                Últimos 15 días: {{ machine.sense_last_15d }} estados</VButton
              >
            </VButtons>
          </template>
        </VCardAdvanced>
      </div>
    </div>
  </div>
</template>
