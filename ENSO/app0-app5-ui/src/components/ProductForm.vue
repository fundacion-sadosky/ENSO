<script setup lang="ts">
import { computed, ref, onBeforeMount } from 'vue'
import { useRoute } from 'vue-router'
import { useWindowScroll } from '@vueuse/core'
import { useNotyf } from '/@src/composable/useNotyf'
import { modelService } from '/@src/services/modelService'
import type { Product } from '/@src/models/model'

const route = useRoute()
const isLoading = ref(false)
const notyf = useNotyf()
const { y } = useWindowScroll()
const theObj = ref<Product>({
  id: undefined,
  barcode: '',
  name: '',
  description: '',
})

const isStuck = computed(() => {
  return y.value > 30
})

const vErrors = ref({
  name: false,
  barcode: false,
})
const validateForm = () => {
  vErrors.value.name = !theObj.value.name
  vErrors.value.barcode = !theObj.value.barcode

  return !vErrors.value.name && !vErrors.value.barcode
}
const onSave = async () => {
  isLoading.value = true
  try {
    if (validateForm()) {
      const obj_r = await modelService.saveProduct(theObj.value)
      theObj.value = obj_r

      notyf.success('Cambios aplicados')
    }
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

const loadProduct = async () => {
  isLoading.value = true
  try {
    const objId = route.params.objId as string
    let ret = await modelService.getProduct(objId)
    theObj.value = ret
  } catch (error: any) {
    notyf.error(error.message)
  }
  isLoading.value = false
}

onBeforeMount(async () => {
  await loadProduct()
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
        label: 'Productos',
        icon: 'icon-park-outline:bottle-three',
        to: { name: 'products' },
      },
      {
        label: theObj.name,
        to: { name: 'product-edit', params: { objId: theObj.id } },
      },
    ]"
    with-icons
  />
  <div class="form-layout is-stacked">
    <div class="form-outer">
      <div :class="[isStuck && 'is-stuck']" class="form-header stuck-header">
        <div class="form-header-inner">
          <div class="left">
            <h3>Información del producto</h3>
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
            <div class="column is-4">
              <VField label="* Código">
                <VControl :has-error="vErrors.barcode">
                  <VInput v-model="theObj.barcode" type="text" />
                  <p v-if="vErrors.barcode" class="help text-danger">Código es requerido</p>
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
            <div class="column is-12">
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
            <div class="column is-4">
              <VField label="Envases por bulto">
                <VControl>
                  <VInput v-model.number="theObj.envases_por_bulto" type="number" />
                </VControl>
              </VField>
            </div>
            <div class="column is-4">
              <VField label="Bultos por m3">
                <VControl>
                  <VInput v-model.number="theObj.bultos_por_m3" type="number" />
                </VControl>
              </VField>
            </div>
            <div class="column is-4">
              <VField label="Envases por m3">
                <VControl>
                  <VInput v-model.number="theObj.envases_por_m3" type="number" />
                </VControl>
              </VField>
            </div>
            <div class="column is-4">
              <VField label="Cadencia (h)">
                <VControl>
                  <VInput v-model.number="theObj.cadencia_unidades_h" type="number" />
                </VControl>
              </VField>
            </div>
            <div class="column is-4">
              <VField label="Peso envase">
                <VControl>
                  <VInput v-model.number="theObj.peso_envase" type="number" />
                </VControl>
              </VField>
            </div>
            <div class="column is-4">
              <VField label="Tipo tapa">
                <VControl>
                  <VInput v-model="theObj.tipo_tapa" type="text" />
                </VControl>
              </VField>
            </div>
            <div class="column is-6">
              <VField label="Máquina">
                <VControl>
                  <VInput v-model="theObj.maquina" type="text" />
                </VControl>
              </VField>
            </div>
            <div class="column is-6">
              <VField label="Máquina alternativa">
                <VControl>
                  <VInput v-model="theObj.maquina_alternativa" type="text" />
                </VControl>
              </VField>
            </div>
            <div class="column is-4">
              <VField label="Operarios">
                <VControl>
                  <VInput v-model.number="theObj.operarios" type="number" />
                </VControl>
              </VField>
            </div>
            <div class="column is-4">
              <VField label="Palletizadores">
                <VControl>
                  <VInput v-model.number="theObj.palletizadores" type="number" />
                </VControl>
              </VField>
            </div>
            <div class="column is-4">
              <VField label="Cavidades máquina">
                <VControl>
                  <VInput v-model.number="theObj.cavidades_maquina" type="number" />
                </VControl>
              </VField>
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
