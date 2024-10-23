<script setup lang="ts">
const emit = defineEmits(['close'])
</script>

<template>
  <div class="sidebar-panel is-generic">
    <div class="subpanel-header">
      <h3 class="no-mb">Configuraciones</h3>
      <div class="panel-close" tabindex="0" @keydown.space.prevent="emit('close')" @click="emit('close')">
        <i aria-hidden="true" class="iconify" data-icon="feather:x"></i>
      </div>
    </div>
    <div class="inner" data-simplebar>
      <ul>
        <li class="divider with-label">
          <span class="divider-label">App Starplastic</span>
        </li>
        <!-- <li>
          <RouterLink :to="{ name: 'home' }">Configuración</RouterLink>
        </li> -->
      </ul>
    </div>
  </div>
</template>

<style lang="scss">
@import '/@src/scss/layout/sidebar-panel';
</style>
