<script setup lang="ts">
import type { PropType } from 'vue'
import { ref, onBeforeMount, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotyf } from '/@src/composable/useNotyf'
import { modelService } from '/@src/services/modelService'
import type { ModelJob } from '/@src/models/model'
import { utils } from '/@src/services/utils'
import {
  STATUS_SCENARIO_IN_EVALUATION,
  STATUS_SCENARIO_DISCARDED,
  STATUS_SCENARIO_APPLIED,
  STATUS_SCENARIO_IN_EVALUATION_DESC,
  STATUS_SCENARIO_DISCARDED_DESC,
  STATUS_SCENARIO_APPLIED_DESC,
  JOB_STATUS_ENDED_OK,
  JOB_STATUS_READY,
  JOB_STATUS_RUNNING,
  JOB_STATUS_ENDED_ERROR,
} from '/@src/data/constants'
import { useSession } from '/@src/stores/session'

const route = useRoute()
const router = useRouter()
const session = useSession()
const notyf = useNotyf()
const isLoading = ref(false)
const modelJob = ref<ModelJob>()
const confirmDeleteModelJob = ref(false)
const jobLogs = ref([])

const props = defineProps({
  activeTab: {
    type: String as PropType<'overview' | 'input' | 'interaction'>,
    default: 'overview',
  },
})
const tab = ref(props.activeTab)

const isJobFinishedOK = computed(() => {
  return modelJob.value?.status === JOB_STATUS_ENDED_OK
})

const copyJob = async () => {
  if (modelJob.value) {
    router.push({ name: 'job-new', params: { originId: modelJob.value.id } })
  }
}

const loadJob = async () => {
  isLoading.value = true
  try {
    const objId = route.params.objId
    let ret = await modelService.getJob(objId)
    modelJob.value = ret
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}
const onUpdateModelJob = async () => {
  try {
    const obj_r = await modelService.saveJob(modelJob.value)
    modelJob.value = obj_r
    notyf.success('Planificación actualizada')
  } catch (error: any) {
    notyf.error(error.message)
  }
}
const onDeleteModelJob = async () => {
  isLoading.value = true
  try {
    await modelService.saveJobAction(modelJob.value, 'ACT_JOB_DELETE')

    notyf.success(`Planificación ${modelJob.value?.number} eliminada`)
    confirmDeleteModelJob.value = false
    router.push({ name: 'jobs' })
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}
const loadJobLogs = async () => {
  try {
    const objId = route.params.objId
    const qry: any = {
      flts: {
        job_id: { eq: objId },
      },
    }
    let ret = await modelService.getJobLogs(qry, 0, 100)
    jobLogs.value = ret.results
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}
const reloadJob = async () => {
  await loadJob()
  await loadJobLogs()
}
onBeforeMount(async () => {
  await loadJob()
  await loadJobLogs()
})
</script>

<template>
  <VBreadcrumb
    v-if="modelJob"
    :items="[
      {
        label: 'Home',
        hideLabel: true,
        icon: 'feather:home',
        to: { name: 'home' },
      },
      {
        label: 'Planificaciones',
        icon: 'icon-park-outline:timeline',
        to: { name: 'jobs' },
      },
      {
        label: modelJob.number ?? 'unknown',
      },
    ]"
    with-icons
  />

  <div v-if="!isLoading && modelJob" class="job-details">
    <div class="tabs-wrapper">
      <div class="tabs-inner">
        <div class="tabs is-toggle">
          <ul>
            <li :class="[tab === 'overview' && 'is-active']">
              <a @click="tab = 'overview'"><span>Resultados</span></a>
            </li>
            <li :class="[tab === 'input' && 'is-active']">
              <a @click="tab = 'input'"><span>Datos de entrada</span></a>
            </li>
            <li :class="[tab === 'interaction' && 'is-active']">
              <a @click="tab = 'interaction'"><span>Interacción</span></a>
            </li>
          </ul>
        </div>
      </div>

      <!-- T0 Overview -->
      <div v-if="tab === 'overview'" class="tab-content is-active">
        <div v-if="modelJob" class="columns job-details-inner">
          <div class="column is-12">
            <div class="job-details-card">
              <div class="card-head">
                <div class="title-wrap">
                  <h3>Planificación # {{ modelJob.number }} Resultados</h3>
                  <p>{{ utils.dateFmtDmyh(modelJob.creation_date) }} - {{ modelJob.creation_user }}</p>
                  <p v-if="modelJob.origin_id">{{ modelJob.origin_desc }}</p>
                  <JobStatus :model-job="modelJob" />
                </div>
                <VButtons align="right">
                  <VButton
                    v-if="modelJob.status !== JOB_STATUS_ENDED_OK && modelJob.status !== JOB_STATUS_ENDED_ERROR"
                    v-tooltip="'Actualizar Planificación desde el servidor'"
                    icon="icon-park-outline:refresh"
                    color="primary"
                    outlined
                    raised
                    @click="reloadJob"
                  >
                    Actualizar
                  </VButton>
                  <VField v-if="isJobFinishedOK" v-tooltip="'Ingrese una descripción relacionada al plan'">
                    <VControl>
                      <VTextarea
                        v-model="modelJob.description"
                        rows="1"
                        placeholder="Ingrese descripción del plan"
                        autocomplete="off"
                        autocapitalize="off"
                        spellcheck="false"
                        @keyup.enter="onUpdateModelJob"
                      ></VTextarea>
                    </VControl>
                  </VField>
                  <VField v-if="isJobFinishedOK" v-tooltip="'Seleccione un estado para el plan'">
                    <VSelect v-model="modelJob.scenario_status" @keyup.enter="onUpdateModelJob">
                      <VOption value="">Desconocido</VOption>
                      <VOption :value="STATUS_SCENARIO_IN_EVALUATION">{{ STATUS_SCENARIO_IN_EVALUATION_DESC }}</VOption>
                      <VOption :value="STATUS_SCENARIO_DISCARDED">{{ STATUS_SCENARIO_DISCARDED_DESC }}</VOption>
                      <VOption :value="STATUS_SCENARIO_APPLIED">{{ STATUS_SCENARIO_APPLIED_DESC }}</VOption>
                    </VSelect>
                  </VField>
                  <VButton
                    v-if="modelJob.status === JOB_STATUS_ENDED_OK"
                    icon="icon-park-outline:disk"
                    color="primary"
                    outlined
                    raised
                    @click="onUpdateModelJob"
                  >
                    Guardar
                  </VButton>
                  <VButton
                    v-if="
                      modelJob.status === JOB_STATUS_ENDED_OK ||
                      modelJob.status === JOB_STATUS_ENDED_ERROR ||
                      modelJob.status === JOB_STATUS_RUNNING
                    "
                    v-tooltip="'Delete Job'"
                    icon="icon-park-outline:delete"
                    color="danger"
                    outlined
                    raised
                    @click="confirmDeleteModelJob = true"
                  >
                    Eliminar
                  </VButton>
                </VButtons>
              </div>
              <JobOutput v-if="modelJob.model_output" :model-job="modelJob" />
              <JobOutputWaiting v-if="modelJob.status == JOB_STATUS_READY" />
              <JobOutputWaiting v-if="modelJob.status == JOB_STATUS_RUNNING" />
              <div v-if="modelJob.error_text" class="job-files">
                <div class="is-divider"></div>
                <h4>Error Message</h4>
                <div class="columns is-multiline">
                  <div class="column is-12">
                    <VMessage v-if="modelJob.error_text" color="danger">{{ modelJob.error_text }}</VMessage>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- T1 Model input -->
      <div v-if="tab === 'input'" class="tab-content is-active">
        <div v-if="modelJob" class="columns job-details-inner">
          <div class="column is-12">
            <div class="job-details-card">
              <div class="card-head">
                <div class="title-wrap">
                  <h3>Datos de entrada</h3>
                </div>
                <VButtons align="right">
                  <VButton
                    v-tooltip="'Crear nueva Planificación con los mismos datos de entrada'"
                    color="primary"
                    icon="icon-park-outline:play-one"
                    elevated
                    @click="copyJob()"
                  >
                    Copiar Planificación
                  </VButton>
                </VButtons>
              </div>
              <JobInput :model-job="modelJob" />
            </div>
          </div>
        </div>
      </div>

      <!-- T3 Interaction  -->
      <div v-if="tab === 'interaction'" class="tab-content is-active">
        <div v-if="modelJob" class="columns job-details-inner">
          <div class="column is-12">
            <div class="job-details-card">
              <div class="card-head">
                <div class="title-wrap">
                  <h3>Interacción</h3>
                </div>
              </div>
              <div class="job-files">
                <div class="is-divider"></div>
                <h4>Running log</h4>
                <div class="columns is-multiline">
                  <div class="column is-12">
                    <table class="table is-striped is-fullwidth">
                      <tbody>
                        <tr v-for="(r, idx) in jobLogs" :key="idx">
                          <td>{{ utils.dateFmtDmyhs(r.line_date) }}</td>
                          <td>{{ r.text }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <VModal :open="confirmDeleteModelJob" title="Confirmar acción" size="small" @close="confirmDeleteModelJob = false">
    <template #content>
      <VPlaceholderSection title="" subtitle="¿Está seguro de Eliminar la planificación?" />
    </template>
    <template #action>
      <VButton color="danger" raised @click="onDeleteModelJob">Confirmar</VButton>
    </template>
  </VModal>
</template>

<style lang="scss">
@import '/@src/scss/abstracts/all';
@import '/@src/scss/components/forms-outer';

.form-layout {
  max-width: 740px;
  margin: 0 auto;
}

/* ==========================================================================
  1. Project Details
  ========================================================================== */

.is-navbar {
  .job-details {
    padding-top: 30px;
  }
}

.job-details {
  .tabs-wrapper {
    .tabs-inner {
      .tabs {
        margin: 0 auto;

        li {
          background: var(--white);
        }
      }
    }
  }

  .job-details-inner {
    padding: 20px 0;

    .job-details-card {
      @include vuero-s-card();

      padding: 40px;

      .card-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        // margin-bottom: 20px;

        .title-wrap {
          h3 {
            font-family: var(--font-alt);
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--dark-text);
            line-height: 1.2;
            transition: all 0.3s;
          }
        }
      }

      .job-overview {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 0;

        p {
          max-width: 420px;
        }
      }

      .job-features {
        display: flex;
        padding: 15px 0;
        border-top: 1px solid var(--fade-grey-dark-3);
        border-bottom: 1px solid var(--fade-grey-dark-3);

        .job-feature {
          margin-right: 20px;
          width: calc(25% - 20px);

          i {
            font-size: 1.6rem;
            color: var(--primary);
            margin-bottom: 8px;
          }

          h4 {
            font-family: var(--font-alt);
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--dark);
          }

          p {
            line-height: 1.2;
            font-size: 0.85rem;
            color: var(--light-text);
            margin-bottom: 0;
          }
        }
      }

      .job-files {
        padding: 10px 0;

        h4 {
          font-family: var(--font-alt);
          font-weight: 600;
          font-size: 0.9rem;
          text-transform: uppercase;
          color: var(--primary);
          margin-bottom: 12px;
        }

        .file-box {
          display: flex;
          align-items: center;
          padding: 8px;
          background: var(--white);
          border: 1px solid transparent;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s;

          &:hover {
            border-color: var(--fade-grey-dark-3);
            box-shadow: var(--light-box-shadow);
          }

          img {
            display: block;
            width: 48px;
            min-width: 48px;
            height: 48px;
          }

          .meta {
            margin-left: 12px;
            line-height: 1.3;

            span {
              display: block;

              &:first-child {
                font-family: var(--font-alt);
                font-size: 0.9rem;
                font-weight: 600;
                color: var(--dark-text);
              }

              &:nth-child(2) {
                font-size: 0.9rem;
                color: var(--light-text);

                i {
                  position: relative;
                  top: -3px;
                  font-size: 0.3rem;
                  color: var(--light-text);
                  margin: 0 4px;
                }
              }
            }
          }

          .dropdown {
            margin-left: auto;
          }
        }
      }
    }

    .side-card {
      @include vuero-s-card();

      padding: 40px;
      margin-bottom: 1.5rem;

      h4 {
        font-family: var(--font-alt);
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        color: var(--primary);
        margin-bottom: 16px;
      }
    }

    .job-team-card {
      @include vuero-s-card();

      padding: 40px;
      max-width: 940px;
      display: block;
      margin: 0 auto;

      .column {
        padding: 1.5rem;

        &:nth-child(odd) {
          border-right: 1px solid var(--fade-grey-dark-3);
        }

        &.has-border-bottom {
          border-bottom: 1px solid var(--fade-grey-dark-3);
        }
      }
    }

    .task-grid {
      .grid-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;

        h3 {
          font-family: var(--font-alt);
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--dark-text);
          line-height: 1.2;
        }

        .buttons {
          display: flex;
          align-items: center;
          background: var(--white);
          padding: 8px 24px;
          border-radius: 100px;

          > span {
            font-family: var(--font-alt);
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--dark-text);
            margin-right: 20px;
          }
        }
      }

      .task-card {
        @include vuero-s-card();

        min-height: 200px;
        display: flex !important;
        flex-direction: column;
        justify-content: space-between;
        padding: 30px;
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          transform: translateY(-5px);
          box-shadow: var(--light-box-shadow);
        }

        .title-wrap {
          h3 {
            font-size: 1.1rem;
            font-family: var(--font-alt);
            font-weight: 600;
            color: var(--dark-text);
            line-height: 1.2;
            margin-bottom: 4px;
          }

          span {
            font-family: var(--font);
            font-size: 0.9rem;
            color: var(--light-text);
          }
        }

        .content-wrap {
          display: flex;
          align-items: center;
          justify-content: space-between;

          .left {
            .attachments {
              display: flex;
              align-items: center;

              i {
                font-size: 15px;
                color: var(--light-text);
              }

              span {
                margin-left: 2px;
                font-size: 0.9rem;
                font-family: var(--font);
                color: var(--light-text);
              }
            }
          }
        }

        .content-wrap-full {
          align-items: center;
          justify-content: space-between;

          .left {
            .attachments {
              display: flex;
              align-items: center;

              i {
                font-size: 15px;
                color: var(--light-text);
              }

              span {
                margin-left: 2px;
                font-size: 0.9rem;
                font-family: var(--font);
                color: var(--light-text);
              }
            }
          }
        }
      }
    }
  }
}

/* ==========================================================================
    2. Project Details Dark Mode
    ========================================================================== */

.is-dark {
  .job-details {
    .job-details-inner {
      .job-details-card {
        @include vuero-card--dark();

        .card-head {
          .title-wrap {
            h3 {
              color: var(--dark-dark-text) !important;
            }
          }
        }

        .job-features {
          border-color: var(--dark-sidebar-light-12);

          .job-feature {
            i {
              color: var(--primary);
            }

            h4 {
              color: var(--dark-dark-text);
            }
          }
        }

        .job-files {
          h4 {
            color: var(--primary);
          }

          .file-box {
            background: var(--dark-sidebar-light-3);

            &:hover {
              border-color: var(--dark-sidebar-light-10);
            }

            .meta {
              span {
                &:first-child {
                  color: var(--dark-dark-text);
                }
              }
            }
          }
        }
      }

      .side-card {
        @include vuero-card--dark();

        h4 {
          color: var(--primary);
        }
      }

      .job-team-card {
        @include vuero-card--dark();

        .column {
          border-color: var(--dark-sidebar-light-12);
        }
      }

      .task-grid {
        .grid-header {
          h3 {
            color: var(--dark-dark-text);
          }

          .filter {
            background: var(--dark-sidebar-light-1) !important;
            border-color: var(--dark-sidebar-light-4) !important;

            > span {
              color: var(--dark-dark-text);
            }
          }
        }

        .task-card {
          @include vuero-card--dark();

          .title-wrap {
            h3 {
              color: var(--dark-dark-text);
            }
          }
        }
      }
    }
  }
}

/* ==========================================================================
    3. Media Queries
    ========================================================================== */

@media only screen and (max-width: 767px) {
  .job-details {
    .job-details-inner {
      .job-details-card {
        padding: 30px;

        .job-overview {
          flex-direction: column;

          p {
            margin-bottom: 20px;
          }
        }

        .job-features {
          flex-wrap: wrap;

          .job-feature {
            width: calc(50% - 20px);
            text-align: center;
            margin: 0 10px;

            &:first-child,
            &:nth-child(2) {
              margin-bottom: 20px;
            }
          }
        }
      }

      .job-team-card {
        padding: 30px;

        .column {
          border-right: none !important;
        }
      }
    }
  }
}

@media only screen and (min-width: 768px) and (max-width: 1024px) and (orientation: portrait) {
  .job-details {
    .job-details-inner {
      .job-details-card {
        .job-files {
          .columns {
            display: flex;

            .column {
              min-width: 50%;
            }
          }
        }
      }

      .job-team-card {
        .columns {
          display: flex;

          .column {
            min-width: 50%;
          }
        }
      }

      .task-grid {
        .columns {
          display: flex;

          .column {
            min-width: 50%;
          }
        }
      }
    }
  }
}
</style>
