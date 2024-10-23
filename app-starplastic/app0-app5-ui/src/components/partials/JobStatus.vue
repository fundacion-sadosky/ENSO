<script setup lang="ts">
import { computed } from 'vue'
import type { ModelJob } from '/@src/models/model'
import {
  JOB_STATUS_READY,
  JOB_STATUS_RUNNING,
  JOB_STATUS_ENDED_OK,
  JOB_STATUS_ENDED_ERROR,
  JOB_STATUS_ENDED_OK_DESC,
  JOB_STATUS_READY_DESC,
  JOB_STATUS_RUNNING_DESC,
  JOB_STATUS_ENDED_ERROR_DESC,
} from '/@src/data/constants'

export interface JobStatusProps {
  modelJob?: ModelJob
}

const props = withDefaults(defineProps<JobStatusProps>(), {
  modelJob: undefined,
})

// Available modifiers are primary, info, success, warning, danger, orange, blue, green, purple, white, light and solid.
const stateColor = computed(() => {
  if (props.modelJob?.status === JOB_STATUS_READY) {
    return 'info'
  } else if (props.modelJob?.status === JOB_STATUS_RUNNING) {
    return 'purple'
  } else if (props.modelJob?.status === JOB_STATUS_ENDED_OK) {
    return 'success'
  } else if (props.modelJob?.status === JOB_STATUS_ENDED_ERROR) {
    return 'danger'
  }
  return 'info'
})

const stateDescription = computed(() => {
  if (props.modelJob?.status === JOB_STATUS_READY) {
    return JOB_STATUS_READY_DESC
  } else if (props.modelJob?.status === JOB_STATUS_RUNNING) {
    return JOB_STATUS_RUNNING_DESC
  } else if (props.modelJob?.status === JOB_STATUS_ENDED_OK) {
    return JOB_STATUS_ENDED_OK_DESC
  } else if (props.modelJob?.status === JOB_STATUS_ENDED_ERROR) {
    return JOB_STATUS_ENDED_ERROR_DESC
  }
  return props.modelJob.status ?? 'DESCONOCIDO'
})
</script>

<template>
  <VTag :color="stateColor" :label="stateDescription" />
</template>
