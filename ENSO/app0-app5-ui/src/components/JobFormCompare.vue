<script setup lang="ts">
import { ref } from 'vue'
import { useMediaQuery } from '@vueuse/core'
import type { VFlexTableWrapperDataResolver } from '/@src/components/base/table/VFlexTableWrapper.vue'
import { useQueryParam } from '/@src/composable/useTable'
import { modelService } from '/@src/services/modelService'
import { utils } from '/@src/services/utils'
import { IdDescription } from '../models/platform'
import { useNotyf } from '/@src/composable/useNotyf'

const notyf = useNotyf()
const isMobileScreen = useMediaQuery('(max-width: 767px)')
// the total data will be set by the fetchData function
const total = ref(0)
const queryParam = useQueryParam()
queryParam.limit = 5
const job1 = ref<IdDescription>()
const job2 = ref<IdDescription>()
const job3 = ref<IdDescription>()

// the fetchData function will be called each time one of the parameter changes
const fetchData: VFlexTableWrapperDataResolver = async ({ searchTerm, start, limit, sort, controller }) => {
  // searchTerm will contains the value of the wrapperState.searchInput
  // the update it's debounced 300 milis in VFlexTableWrapper to avoid to much requests
  console.log(controller)
  const searchQuery = searchTerm ? searchTerm : ''
  const qry: any = { flts: {} }
  if (searchQuery) {
    qry.flts['or_regex'] = {
      or_regex: {
        status: searchQuery,
        number: searchQuery,
        name: searchQuery,
      },
    }
  }
  // sort will be a string like "name:asc"
  if (sort && sort.includes(':')) {
    let [sortField, sortOrder] = sort.split(':')
    qry.sort = { field: sortField, order: sortOrder === 'asc' ? 1 : -1 }
  }
  const res = await modelService.getJobs(qry, start, limit)

  total.value = res.total

  // the return of the function must be an array
  return res.results
}

// column title & decorators
const columns = {
  number: {
    label: 'Planificación',
    sortable: true,
  },
  start_date: {
    label: 'Fecha',
    sortable: true,
  },
  model_input: {
    label: 'Descripción',
    sortable: false,
  },
  status: {
    label: 'Acciones',
    sortable: true,
    align: 'end',
  },
} as const

const getJobDesc = (row: any) => {
  const otDesc = row.model_input ? `${row.model_input.ots.length} OTs` : 'No hay OTs'
  const resDuracion = row.model_output ? `${row.model_output.completamiento_ordenes.toFixed(2)} horas` : ''
  return `${otDesc}, ${resDuracion}`
}

const addToCompare = (id: string, number: string, name: string) => {
  let jobName = number
  if (name) {
    jobName = `${number} - ${name}`
  }
  if (!job1.value) {
    job1.value = { value: id, label: jobName }
  } else if (!job2.value) {
    job2.value = { value: id, label: jobName }
  } else if (!job3.value) {
    job3.value = { value: id, label: jobName }
  } else {
    notyf.warning('No hay mas posiciones para comparar')
  }
}

const cleanCompare = () => {
  job1.value = undefined
  job2.value = undefined
  job3.value = undefined
}
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
          label: 'Planificaciones',
          icon: 'icon-park-outline:timeline',
          to: { name: 'jobs' },
        },
        {
          label: 'Comparación',
        },
      ]"
      with-icons
    />
    <VButtons align="right">
      <VButton color="warning" icon="icon-park-outline:delete" outlined @click="cleanCompare">
        Limpiar Comparaciones
      </VButton>
    </VButtons>
  </div>
  <div class="columns">
    <div class="column is-12">
      <!-- 
          We use v-model to let VFlexTableWrapper update queryParam
        -->
      <VFlexTableWrapper
        v-model:page="queryParam.page"
        v-model:limit="queryParam.limit"
        v-model:searchTerm="queryParam.searchTerm"
        v-model:sort="queryParam.sort"
        :columns="columns"
        :data="fetchData"
        :total="total"
        class="mt-4"
      >
        <!-- 
            Here we retrieve the internal wrapperState. 
            Note that we can not destructure it 
          -->
        <template #default="wrapperState">
          <!--Table Pagination-->
          <VFlexPagination
            v-if="!isMobileScreen"
            v-model:current-page="wrapperState.page"
            :item-per-page="wrapperState.limit"
            :total-items="wrapperState.total"
            :max-links-displayed="0"
            no-router
          >
            <!-- The controls can be updated anywhere in the slot -->
            <template #before-pagination>
              <VFlex class="mr-4">
                <VField>
                  <VControl icon="feather:search">
                    <input v-model="wrapperState.searchInput" type="text" class="input" placeholder="Filtros..." />
                  </VControl>
                </VField>
              </VFlex>
            </template>
          </VFlexPagination>

          <VFlexTable rounded clickable :no-header="!wrapperState.loading && wrapperState.data.length === 0">
            <template #body>
              <!--
                  The wrapperState.loading will be update 
                  when the fetchData function is running 
                -->
              <div v-if="wrapperState.loading" class="flex-list-inner">
                <div v-for="key in wrapperState.limit" :key="key" class="flex-table-item">
                  <VFlexTableCell>
                    <VPlaceload class="mx-1" />
                  </VFlexTableCell>
                </div>
              </div>

              <!-- This is the empty state -->
              <div v-else-if="wrapperState.data.length === 0" class="flex-list-inner">
                <VPlaceholderSection
                  title="No hay planificaciones"
                  subtitle="No hay datos que coincidan con su consulta.."
                  class="my-6"
                >
                </VPlaceholderSection>
              </div>
            </template>

            <!-- This is the body cell slot -->
            <template #body-cell="{ row, column }">
              <template v-if="column.key === 'number'">
                <span class="light-text">{{ row.number }} {{ row.name }}</span>
              </template>
              <template v-if="column.key === 'start_date'">
                <span class="light-text">{{ utils.dateFmtDmyh(row.start_date ?? row.creation_date) }}</span>
              </template>
              <template v-if="column.key === 'model_input'">
                <span class="light-text">{{ utils.strShort(getJobDesc(row), 30) }}</span>
                <JobStatus class="ml-2" :model-job="row" />
                <JobScenarioStatus class="ml-2" :model-job="row" />
              </template>
              <template v-if="column.key === 'status'">
                <VButton
                  v-tooltip="'Comparar con otra planificación'"
                  icon="icon-park-outline:plus"
                  color="info"
                  raised
                  outlined
                  @click="addToCompare(row.id, row.number, row.name)"
                >
                  Comparar
                </VButton>
              </template>
            </template>
          </VFlexTable>

          <!--Table Pagination-->
          <VFlexPagination
            v-model:current-page="wrapperState.page"
            class="mt-5"
            :item-per-page="wrapperState.limit"
            :total-items="wrapperState.total"
            :max-links-displayed="2"
            no-router
          >
            <template #before-navigation>
              <VFlex class="mr-4" column-gap="1rem">
                <VField>
                  <VControl>
                    <div class="select is-rounded">
                      <select v-model="wrapperState.limit">
                        <option :value="10">10 ítems</option>
                      </select>
                    </div>
                  </VControl>
                </VField>
              </VFlex>
            </template>
          </VFlexPagination>
        </template>
      </VFlexTableWrapper>
    </div>
  </div>
  <div class="columns">
    <div class="column is-4">
      <VMessage v-if="!job1" color="info"> Agregue una planificación para comparar. </VMessage>
      <JobCompareCard v-if="job1" :job="job1" />
    </div>
    <div class="column is-4">
      <VMessage v-if="!job2" color="info"> Agregue una planificación para comparar. </VMessage>
      <JobCompareCard v-if="job2" :job="job2" />
    </div>
    <div class="column is-4">
      <VMessage v-if="!job3" color="info"> Agregue una planificación para comparar. </VMessage>
      <JobCompareCard v-if="job3" :job="job3" />
    </div>
  </div>
</template>
