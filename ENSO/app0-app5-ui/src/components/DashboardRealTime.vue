<script setup lang="ts">
import { ref, onBeforeMount, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { modelService } from '/@src/services/modelService'
import { useNotyf } from '/@src/composable/useNotyf'
import { ACT_MACHINE_STATUS } from '/@src/data/constants'
import { utils } from '/@src/services/utils'
import dayjs from 'dayjs'

const router = useRouter()
const notyf = useNotyf()
const machines = ref([])
const isLoading = ref(false)
const timerId = ref(0)

const loadMachineStatus = async () => {
  isLoading.value = true
  try {
    let ret = await modelService.getAppDataAction(ACT_MACHINE_STATUS)
    machines.value = ret.machines
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

const goToMachineData = (machine: string) => {
  router.push({ name: 'machine-charts', params: { objId: machine } })
}

const isValidStatusDate = (iso_date: string) => {
  if (iso_date) {
    const sdate = dayjs(iso_date)
    const now = dayjs()

    return now.diff(sdate, 'minute') < 2
  }

  return false
}

onMounted(async () => {
  timerId.value = setInterval(await loadMachineStatus, 15000) // Call fetchData every 15 seconds
})
onUnmounted(async () => {
  clearInterval(timerId.value)
})
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
          label: 'Estado actual de las máquinas habilitadas',
          icon: 'icon-park-outline:dashboard',
          to: { name: 'dash1' },
        },
      ]"
      with-icons
    />
  </div>
  <div v-if="!isLoading">
    <!--Real timeDashboard-->
    <div class="columns is-multiline">
      <div v-for="(machine, idx) in machines" :key="idx" class="column is-3">
        <VCardAdvanced v-if="isValidStatusDate(machine.last_status_date)">
          <template #header-left>
            <VTag :label="machine.nbr" :color="utils.getMachineStatusColor(machine?.last_status?.value)" rounded />
            <VTag
              :label="machine.last_status.label"
              :color="utils.getMachineStatusColor(machine?.last_status?.value)"
              rounded
            />
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
            <VBlock :title="machine.name" :subtitle="utils.dateFmtDmyh(machine.last_status_date)">
              <template #icon>
                <VIconBox size="big" :color="utils.getMachineStatusColor(machine?.last_status?.value)" rounded>
                  <i class="iconify" :data-icon="utils.getMachineStatusIcon(machine?.last_status?.value)"></i>
                </VIconBox>
              </template>
            </VBlock>
          </template>
        </VCardAdvanced>
        <VCardAdvanced v-if="!isValidStatusDate(machine.last_status_date)">
          <template #header-left>
            <VTag :label="machine.nbr" color="warning" rounded />
            <VTag label="Desconectada" color="warning" rounded />
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
            <VBlock :title="machine.name" subtitle="Sin datos en los últimos 2 minutos">
              <template #icon>
                <VIconBox size="big" color="warning" rounded>
                  <i class="iconify" data-icon="icon-park-outline:help"></i>
                </VIconBox>
              </template>
            </VBlock>
          </template>
        </VCardAdvanced>
      </div>
    </div>
  </div>
</template>
