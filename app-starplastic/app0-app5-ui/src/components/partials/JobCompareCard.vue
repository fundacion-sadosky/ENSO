<script setup lang="ts">
import { onBeforeMount, ref } from 'vue'
import { modelService } from '/@src/services/modelService'
import type { ModelJob } from '/@src/models/model'
import { IdDescription } from '/@src/models/platform'
import { utils } from '/@src/services/utils'

export interface JobCompareCardProps {
  job?: IdDescription
}
const props = withDefaults(defineProps<JobCompareCardProps>(), {
  job: undefined,
})
const theObj = ref<ModelJob>()

const loadJob = async () => {
  const objId = props.job.value
  let ret = await modelService.getJob(objId)
  theObj.value = ret
}

onBeforeMount(async () => {
  await loadJob()
})
</script>

<template>
  <VCardActionc
    v-if="theObj"
    dataicon="icon-park-outline:application-one"
    :title="theObj.number ?? 'NO NUMBER'"
    :subtitle="utils.dateFmtDmyh(theObj.creation_date)"
  >
    <template #action>
      <VTag color="green" label="Plan" rounded />
    </template>
    <VCard color="primary">
      <h3 class="title is-5 mb-2">Duración del Plan</h3>
      <h3 class="title is-5 mb-2">{{ theObj.model_output.completamiento_ordenes.toFixed(2) }} horas</h3>
    </VCard>
    <VCard color="info">
      <h3 class="title is-5 mb-2">Tiempo total de Producción</h3>
      <h3 class="title is-5 mb-2">{{ theObj.model_output.total_produccion.toFixed(2) }} horas</h3>
    </VCard>
    <VCard color="secondary">
      <h3 class="title is-5 mb-2">Productividad Operarios</h3>
      <h3 class="title is-5 mb-2">{{ theObj.model_output.productividad_operarios.toFixed(2) * 100 }} %</h3>
    </VCard>
  </VCardActionc>
</template>
