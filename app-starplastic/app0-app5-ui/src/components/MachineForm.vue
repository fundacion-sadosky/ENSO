<script setup lang="ts">
import { computed, ref, onBeforeMount } from 'vue'
import { useRoute } from 'vue-router'
import { useWindowScroll } from '@vueuse/core'
import { useNotyf } from '/@src/composable/useNotyf'
import { modelService } from '/@src/services/modelService'
import type { Machine } from '/@src/models/model'
import { utils } from '/@src/services/utils'
import {
  ACT_MACHINE_STATUS_CAMBIO_MOLDE,
  ACT_MACHINE_STATUS_PREPARACION,
  ACT_MACHINE_STATUS_PREVENTIVO,
  ACT_MACHINE_STATUS_CORRECTIVO,
  ACT_MACHINE_STATUS_LIMPIEZA,
} from '/@src/data/constants'

const route = useRoute()
const isLoading = ref(false)
const notyf = useNotyf()
const { y } = useWindowScroll()
const theObj = ref<Machine>({
  id: undefined,
  name: '',
  nbr: '',
  code: '',
  enabled: true,
  realtime_status: true,
})

const isStuck = computed(() => {
  return y.value > 30
})

const vErrors = ref({
  name: false,
  nbr: false,
  code: false,
})
const validateForm = () => {
  vErrors.value.name = !theObj.value.name
  vErrors.value.nbr = !theObj.value.nbr
  vErrors.value.code = !theObj.value.code

  return !vErrors.value.name && !vErrors.value.nbr && !vErrors.value.code
}
const onSave = async () => {
  isLoading.value = true
  try {
    if (validateForm()) {
      const obj_r = await modelService.saveMachine(theObj.value)
      theObj.value = obj_r

      notyf.success('Cambios aplicados')
    }
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

const onChangeMachineState = async (action: string) => {
  isLoading.value = true
  try {
    const obj_r = await modelService.saveMachineAction(theObj.value, action)
    theObj.value = obj_r

    notyf.success('Estado seteado correctamente')
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

const loadMachine = async () => {
  isLoading.value = true
  try {
    const objId = route.params.objId as string
    let ret = await modelService.getMachine(objId)
    theObj.value = ret
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

onBeforeMount(async () => {
  await loadMachine()
})
</script>

<template>
  <VBreadcrumb
    v-if="theObj.id"
    :items="[
      {
        label: 'Home',
        hideLabel: true,
        icon: 'feather:home',
        to: { name: 'home' },
      },
      {
        label: 'Máquinas',
        icon: 'icon-park-outline:washing-machine',
        to: { name: 'machines' },
      },
      {
        label: theObj.name,
        to: { name: 'machine-edit', params: { objId: theObj.id } },
      },
    ]"
    with-icons
  />
  <div class="form-layout is-stacked">
    <div class="form-outer">
      <div :class="[isStuck && 'is-stuck']" class="form-header stuck-header">
        <div class="form-header-inner">
          <div class="left">
            <h3>Información de la máquina</h3>
          </div>
          <div class="right">
            <div class="buttons">
              <VButton :to="{ name: 'machines' }" icon="lnir lnir-arrow-left rem-100" light raised elevated>
                Volver
              </VButton>
              <VButton color="primary" :loading="isLoading" raised elevated @click="onSave"> Guardar </VButton>
            </div>
          </div>
        </div>
      </div>
      <div class="form-body">
        <div class="form-section">
          <div class="columns is-multiline">
            <div class="column is-12">
              <VMessage color="warning"
                ><b>ALERTA</b>: Cambiar el número o el código puede afectar el uso de los sensores. Si no está seguro
                acerca de los cambios, no lo haga. Ejemplo tópico MQTT: <b>'Máquina/M10/#'</b></VMessage
              >
            </div>

            <div class="column is-4">
              <VField label="* Número">
                <VControl :has-error="vErrors.nbr">
                  <VInput v-model="theObj.nbr" type="text" />
                  <p v-if="vErrors.nbr" class="help text-danger">Número es requerido</p>
                </VControl>
              </VField>
            </div>

            <div class="column is-8">
              <VField label="* Nombre">
                <VControl :has-error="vErrors.name">
                  <VInput v-model="theObj.name" type="text" />
                  <p v-if="vErrors.name" class="help text-danger">Nombre es requerido</p>
                </VControl>
              </VField>
            </div>

            <div class="column is-4">
              <VField label="* Código MQTT">
                <VControl :has-error="vErrors.code">
                  <VInput v-model="theObj.code" type="text" />
                  <p v-if="vErrors.code" class="help text-danger">Código MQTT es requerido</p>
                </VControl>
              </VField>
            </div>

            <div class="column is-8">
              <VField label="Descripción">
                <VControl>
                  <VTextarea
                    v-model="theObj.description"
                    rows="2"
                    placeholder=""
                    autocomplete="off"
                    autocapitalize="off"
                    spellcheck="false"
                  ></VTextarea>
                </VControl>
              </VField>
            </div>

            <div class="column is-6">
              <VField label="Fabricante">
                <VControl>
                  <VInput v-model="theObj.manufacturer" type="text" />
                </VControl>
              </VField>
            </div>

            <div class="column is-6">
              <VField label="Modelo">
                <VControl>
                  <VInput v-model="theObj.model" type="text" />
                </VControl>
              </VField>
            </div>

            <div class="column is-6">
              <VField>
                <VControl>
                  <VSwitchBlock v-model="theObj.enabled" color="primary" label="¿Máquina en uso?" />
                </VControl>
              </VField>
            </div>

            <div class="column is-6">
              <VField>
                <VControl>
                  <VSwitchBlock v-model="theObj.realtime_status" color="primary" label="¿Tiene sensor de uso MQTT?" />
                </VControl>
              </VField>
            </div>
            <div class="column is-12">
              <h4 class="title is-6 is-narrow has-text-primary">Última señal MQTT del equipo</h4>
            </div>
            <div class="column is-12">
              <VMessage v-if="theObj.last_status_date" color="info">
                <b>{{ utils.dateFmtDmyh(theObj.last_status_date) }} => {{ theObj.last_status.label }}</b>
              </VMessage>
              <VMessage v-if="!theObj.last_status_date" color="warning">
                No hay señales del sensor para la máquina
              </VMessage>
            </div>
            <div class="column is-12">
              <h4 class="title is-6 is-narrow has-text-primary">Setear estado en forma manual</h4>
            </div>
            <div class="column is-12">
              <VButton
                class="m-r-5 m-b-5"
                color="warning"
                raised
                :loading="isLoading"
                @click="onChangeMachineState(ACT_MACHINE_STATUS_CAMBIO_MOLDE)"
              >
                Cambio de Molde
              </VButton>
              <VButton
                class="m-r-5 m-b-5"
                color="warning"
                raised
                :loading="isLoading"
                @click="onChangeMachineState(ACT_MACHINE_STATUS_PREPARACION)"
              >
                En Preparación
              </VButton>
              <VButton
                class="m-r-5 m-b-5"
                color="warning"
                raised
                :loading="isLoading"
                @click="onChangeMachineState(ACT_MACHINE_STATUS_LIMPIEZA)"
              >
                En Limpieza y/o Lubricación
              </VButton>
              <VButton
                class="m-r-5 m-b-5"
                color="warning"
                raised
                :loading="isLoading"
                @click="onChangeMachineState(ACT_MACHINE_STATUS_PREVENTIVO)"
              >
                En Preventivo
              </VButton>
              <VButton
                class="m-r-5 m-b-5"
                color="warning"
                raised
                :loading="isLoading"
                @click="onChangeMachineState(ACT_MACHINE_STATUS_CORRECTIVO)"
              >
                En Correctivo
              </VButton>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
@import '/@src/scss/abstracts/all';
@import '/@src/scss/components/forms-outer';

.form-layout {
  max-width: 740px;
  margin: 0 auto;
}
</style>
