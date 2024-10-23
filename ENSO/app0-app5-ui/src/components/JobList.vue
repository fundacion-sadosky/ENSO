<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMediaQuery } from '@vueuse/core'

import type { VFlexTableWrapperDataResolver } from '/@src/components/base/table/VFlexTableWrapper.vue'
import { useQueryParam } from '/@src/composable/useTable'
import { modelService } from '/@src/services/modelService'
import { utils } from '/@src/services/utils'

const router = useRouter()
const isMobileScreen = useMediaQuery('(max-width: 767px)')
// the total data will be set by the fetchData function
const total = ref(0)
const queryParam = useQueryParam()

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

function onRowClick(row: any) {
  router.push({ name: 'job-edit', params: { objId: row.id } })
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
    label: 'Estado',
    sortable: true,
    align: 'end',
  },
} as const

const getJobDesc = (row: any) => {
  let desc = row.model_input ? `${row.model_input.ots.length} OTs` : 'No hay OTs'
  if (row.model_output?.completamiento_ordenes) {
    desc += `, ${row.model_output.completamiento_ordenes.toFixed(2)} horas`
  }
  if (row.description) {
    desc += `, ${row.description}`
  }
  return desc
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
      ]"
      with-icons
    />
    <VButtons align="right">
      <VButton :to="{ name: 'job-new' }" color="primary" icon="icon-park-outline:add" elevated>
        Nueva Planificación
      </VButton>
      <VButton :to="{ name: 'job-compare' }" color="primary" icon="icon-park-outline:align-horizontally" elevated>
        Comparar Planificaciones
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
            <template #before-navigation>
              <VFlex class="mr-4" column-gap="1rem">
                <VButton :loading="wrapperState.loading" size="medium" rounded @click="wrapperState.fetchData">
                  Actualizar
                </VButton>
              </VFlex>
            </template>
          </VFlexPagination>

          <VFlexTable
            rounded
            clickable
            :no-header="!wrapperState.loading && wrapperState.data.length === 0"
            @row-click="onRowClick"
          >
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
                <span class="light-text">{{ utils.strShort(getJobDesc(row), 50) }}</span>
              </template>
              <template v-if="column.key === 'status'">
                <JobStatus :model-job="row" />
                <JobScenarioStatus class="ml-2" :model-job="row" />
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
                        <option :value="25">25 ítems</option>
                        <option :value="50">50 ítems</option>
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
</template>
