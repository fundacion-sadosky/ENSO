<script setup lang="ts">
import { computed } from 'vue'
import type { ModelJob } from '/@src/models/model'
import {
  STATUS_SCENARIO_IN_EVALUATION,
  STATUS_SCENARIO_DISCARDED,
  STATUS_SCENARIO_APPLIED,
  STATUS_SCENARIO_IN_EVALUATION_DESC,
  STATUS_SCENARIO_DISCARDED_DESC,
  STATUS_SCENARIO_APPLIED_DESC,
} from '/@src/data/constants'

export interface JobStatusProps {
  modelJob?: ModelJob
}

const props = withDefaults(defineProps<JobStatusProps>(), {
  modelJob: undefined,
})

// Available modifiers are primary, info, success, warning, danger, orange, blue, green, purple, white, light and solid.
const stateColor = computed(() => {
  if (props.modelJob?.scenario_status === STATUS_SCENARIO_DISCARDED) {
    return 'orange'
  } else if (props.modelJob?.scenario_status === STATUS_SCENARIO_IN_EVALUATION) {
    return 'info'
  } else if (props.modelJob?.scenario_status === STATUS_SCENARIO_APPLIED) {
    return 'success'
  }
  return 'info'
})

const stateDescription = computed(() => {
  if (props.modelJob?.scenario_status === STATUS_SCENARIO_DISCARDED) {
    return STATUS_SCENARIO_DISCARDED_DESC
  } else if (props.modelJob?.scenario_status === STATUS_SCENARIO_IN_EVALUATION) {
    return STATUS_SCENARIO_IN_EVALUATION_DESC
  } else if (props.modelJob?.scenario_status === STATUS_SCENARIO_APPLIED) {
    return STATUS_SCENARIO_APPLIED_DESC
  }
  return 'DESCONOCIDO'
})
</script>

<template>
  <VTag :color="stateColor" :label="stateDescription" />
</template>
