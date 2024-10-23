<script setup lang="ts">
import { computed, ref, onBeforeMount } from 'vue'
import { modelService } from '/@src/services/modelService'
import { useNotyf } from '/@src/composable/useNotyf'

const notyf = useNotyf()
const datalist = ref([])
const filters = ref('')

const filteredData: any = computed(() => {
  if (!filters.value) {
    return datalist.value
  } else {
    return datalist.value.filter((item: any) => {
      return item.barcode.match(new RegExp(filters.value, 'i')) || item.name.match(new RegExp(filters.value, 'i'))
    })
  }
})

const loadProducts = async () => {
  try {
    const qry: any = { flts: {} }
    let ret = await modelService.getProducts(qry)
    datalist.value = ret.results
  } catch (error: any) {
    notyf.error(error.message)
  }
}

onBeforeMount(async () => {
  await loadProducts()
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
          label: 'Productos',
          icon: 'icon-park-outline:bottle-three',
          to: { name: 'products' },
        },
      ]"
      with-icons
    />
    <!-- <VButtons align="right">
      <VButton :to="{ name: 'product-edit', params: { objId: 'new' } }" color="primary" icon="fas fa-plus" raised elevated>
        Add App
      </VButton>
    </VButtons> -->
  </div>
  <div>
    <div class="tile-grid-toolbar">
      <VControl icon="feather:search">
        <input v-model="filters" class="input custom-text-filter" placeholder="Buscar..." />
      </VControl>
    </div>

    <div class="tile-grid tile-grid-v1">
      <!--List Empty Search Placeholder -->
      <VPlaceholderPage
        :class="[filteredData.length !== 0 && 'is-hidden']"
        title="No se encontraron resultados."
        subtitle="No pudimos encontrar ningún resultado para el filtro de búsqueda que ha introducido."
        larger
      >
        <template #image>
          <img class="light-image" src="../assets/illustrations/placeholders/search-6.svg" alt="" />
          <img class="dark-image" src="../assets/illustrations/placeholders/search-6-dark.svg" alt="" />
        </template>
      </VPlaceholderPage>

      <!--Tile Grid v1-->
      <transition-group name="list" tag="div" class="columns is-multiline">
        <!--Grid item-->
        <div v-for="obj in filteredData" :key="obj.id" class="column is-4">
          <div class="tile-grid-item">
            <div class="tile-grid-item-inner">
              <RouterLink :to="{ name: 'product-edit', params: { objId: obj.id } }">
                <VIconBox size="medium" color="primary" rounded>
                  <i class="iconify" data-icon="icon-park-outline:bottle-three"></i>
                </VIconBox>
              </RouterLink>
              <div class="meta">
                <RouterLink :to="{ name: 'product-edit', params: { objId: obj.id } }">
                  <span class="dark-inverted">{{ obj.barcode }}</span>
                  <span>{{ obj.name }}</span>
                </RouterLink>
              </div>
              <VDropdown icon="feather:more-vertical" spaced right>
                <template #content>
                  <RouterLink :to="{ name: 'product-edit', params: { objId: obj.id } }">
                    <a role="menuitem" class="dropdown-item is-media">
                      <div class="icon">
                        <i aria-hidden="true" class="lnil lnil-pencil-alt"></i>
                      </div>
                      <div class="meta">
                        <span>Detalles</span>
                        <span>Editar información</span>
                      </div>
                    </a>
                  </RouterLink>
                </template>
              </VDropdown>
            </div>
          </div>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<style lang="scss">
@import '/@src/scss/abstracts/all';

.tile-grid {
  .columns {
    margin-left: -0.5rem !important;
    margin-right: -0.5rem !important;
    margin-top: -0.5rem !important;
  }

  .column {
    padding: 0.5rem !important;
  }
}

.is-dark {
  .tile-grid {
    .tile-grid-item {
      @include vuero-card--dark;
    }
  }
}

.tile-grid-v1 {
  .tile-grid-item {
    @include vuero-s-card;

    border-radius: 14px;
    padding: 16px;

    .tile-grid-item-inner {
      display: flex;
      align-items: center;

      .meta {
        margin-left: 10px;
        line-height: 1.2;

        span {
          display: block;
          font-family: var(--font);

          &:first-child {
            color: var(--dark-text);
            font-family: var(--font-alt);
            font-weight: 600;
            font-size: 1rem;
          }

          &:nth-child(2) {
            color: var(--light-text);
            font-size: 0.9rem;
          }
        }
      }

      .dropdown {
        position: relative;
        margin-left: auto;
      }
    }
  }
}
</style>
