<script setup lang="ts">
import { ref, onBeforeMount } from 'vue'
// import { useSession } from '/@src/stores/session'
import { modelService } from '/@src/services/modelService'
import { useNotyf } from '/@src/composable/useNotyf'
import type { AppData } from '/@src/models/model'
import ApexChart from 'vue3-apexcharts'
import { chartUtils } from '/@src/services/chartUtils'

const notyf = useNotyf()
// const session = useSession()
const appData = ref<AppData>()
const isLoading = ref(false)
const giGraph = chartUtils.getRealtimeGaugeOptions()
const g1Series = [54]

const loadAppData = async () => {
  isLoading.value = true
  try {
    let ret = await modelService.getAppData()
    appData.value = ret
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

onBeforeMount(async () => {
  await loadAppData()
})
</script>

<template>
  <div v-if="!isLoading">
    <!--Real timeDashboard-->
    <div class="columns is-multiline">
      <div class="column is-4">
        <VCardAdvanced>
          <template #header-left>
            <VBlock title="MACHINE01" subtitle="05/05/2023 15:30" center>
              <template #icon>
                <VAvatar initials="01" color="success" />
              </template>
            </VBlock>
          </template>
          <template #header-right>
            <VTag label="Activa" color="success" rounded />
          </template>
          <template #content>
            <VTag label="OT 2343" color="info" outlined />
            <ApexChart
              id="apex-chart-22"
              :height="giGraph.chart.height"
              :type="giGraph.chart.type"
              :series="g1Series"
              :options="giGraph"
            >
            </ApexChart>
          </template>
          <template #footer-left>
            <div class="tags">
              <VTag label="05/05/2023 15:30" color="solid" rounded />
            </div>
          </template>
          <template #footer-right>
            <VButton color="primary" raised>Más detalles</VButton>
          </template>
        </VCardAdvanced>
      </div>
    </div>
  </div>
</template>
