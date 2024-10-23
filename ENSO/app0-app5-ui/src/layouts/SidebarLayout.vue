<script setup lang="ts">
import { ref, watchPostEffect, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { SidebarTheme } from '/@src/components/navigation/desktop/Sidebar.vue'
import { useViewWrapper } from '/@src/stores/viewWrapper'

const props = withDefaults(
  defineProps<{
    theme?: SidebarTheme
    defaultSidebar?: string
    closeOnChange?: boolean
    openOnMounted?: boolean
    nowrap?: boolean
  }>(),
  {
    defaultSidebar: 'settings',
    theme: 'color',
  }
)

const viewWrapper = useViewWrapper()
const route = useRoute()
const isMobileSidebarOpen = ref(false)
const isDesktopSidebarOpen = ref(props.openOnMounted)
const activeMobileSubsidebar = ref(props.defaultSidebar)

function switchSidebar(id: string) {
  if (id === activeMobileSubsidebar.value) {
    isDesktopSidebarOpen.value = !isDesktopSidebarOpen.value
  } else {
    isDesktopSidebarOpen.value = true
    activeMobileSubsidebar.value = id
  }
}

/**
 * watchPostEffect callback will be executed each time dependent reactive values has changed
 */
watchPostEffect(() => {
  viewWrapper.setPushed(isDesktopSidebarOpen.value ?? false)
})
watch(
  () => route.fullPath,
  () => {
    isMobileSidebarOpen.value = false

    if (props.closeOnChange && isDesktopSidebarOpen.value) {
      isDesktopSidebarOpen.value = false
    }
  }
)
</script>

<template>
  <div class="sidebar-layout">
    <div class="app-overlay"></div>

    <!-- Mobile navigation -->
    <MobileNavbar :is-open="isMobileSidebarOpen" @toggle="isMobileSidebarOpen = !isMobileSidebarOpen">
      <template #brand>
        <RouterLink :to="{ name: 'index' }" class="navbar-item is-brand">
          <AppLogo width="38px" height="38px" />
        </RouterLink>

        <div class="brand-end">
          <NotificationsMobileDropdown />
          <UserProfileDropdown />
        </div>
      </template>
    </MobileNavbar>

    <!-- Mobile sidebar links -->
    <MobileSidebar :is-open="isMobileSidebarOpen" @toggle="isMobileSidebarOpen = !isMobileSidebarOpen">
      <template #links>
        <li>
          <RouterLink :to="{ name: 'dash1' }">
            <i aria-hidden="true" class="iconify" data-icon="icon-park-outline:dashboard"></i>
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'jobs' }">
            <i aria-hidden="true" class="iconify" data-icon="icon-park-outline:timeline"></i>
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'kpi1' }">
            <i aria-hidden="true" class="iconify" data-icon="icon-park-outline:chart-line"></i>
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'machines' }">
            <i aria-hidden="true" class="iconify" data-icon="icon-park-outline:washing-machine"></i>
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'products' }">
            <i aria-hidden="true" class="iconify" data-icon="icon-park-outline:bottle-three"></i>
          </RouterLink>
        </li>
        <!-- <li>
          <RouterLink :to="{ name: 'dash1ot' }">
            <i aria-hidden="true" class="iconify" data-icon="icon-park-outline:dashboard"></i>
          </RouterLink>
        </li> -->
      </template>

      <template #bottom-links>
        <li>
          <a
            aria-label="Display Settings content"
            :class="[activeMobileSubsidebar === 'settings' && 'is-active']"
            tabindex="0"
            @keydown.space.prevent="activeMobileSubsidebar = 'settings'"
            @click="activeMobileSubsidebar = 'settings'"
          >
            <i aria-hidden="true" class="iconify" data-icon="icon-park-outline:setting-two"></i>
          </a>
        </li>
      </template>
    </MobileSidebar>

    <!-- Mobile subsidebar links -->
    <transition name="slide-x">
      <SettingsMobileSubsidebar v-if="isMobileSidebarOpen && activeMobileSubsidebar === 'settings'" />
    </transition>

    <!-- Desktop navigation -->
    <CircularMenu />

    <Sidebar :theme="props.theme" :is-open="isDesktopSidebarOpen">
      <template #links>
        <li>
          <RouterLink id="dash1" :to="{ name: 'dash1' }" data-content="Estado actual">
            <i aria-hidden="true" class="iconify sidebar-svg" data-icon="icon-park-outline:dashboard"></i>
          </RouterLink>
        </li>
        <li>
          <RouterLink id="planificacion" :to="{ name: 'jobs' }" data-content="Planificación">
            <i aria-hidden="true" class="iconify sidebar-svg" data-icon="icon-park-outline:timeline"></i>
          </RouterLink>
        </li>
        <li>
          <RouterLink id="kpis" :to="{ name: 'kpi1' }" data-content="KPIs">
            <i aria-hidden="true" class="iconify sidebar-svg" data-icon="icon-park-outline:chart-line"></i>
          </RouterLink>
        </li>
        <li>
          <RouterLink id="machines" :to="{ name: 'machines' }" data-content="Máquinas">
            <i aria-hidden="true" class="iconify sidebar-svg" data-icon="icon-park-outline:washing-machine"></i>
          </RouterLink>
        </li>
        <li>
          <RouterLink id="machines" :to="{ name: 'products' }" data-content="Productos">
            <i aria-hidden="true" class="iconify sidebar-svg" data-icon="icon-park-outline:bottle-three"></i>
          </RouterLink>
        </li>
        <!-- <li>
          <RouterLink id="dash1ot" :to="{ name: 'dash1ot' }" data-content="Estado OT">
            <i aria-hidden="true" class="iconify sidebar-svg" data-icon="icon-park-outline:dashboard"></i>
          </RouterLink>
        </li> -->
      </template>

      <template #bottom-links>
        <!-- Settings -->
        <!-- <li class="is-hidden-touch">
          <a
            :class="[activeMobileSubsidebar === 'settings' && 'is-active']"
            data-content="Configuración"
            aria-label="Ver Configuración"
            tabindex="0"
            @keydown.space.prevent="switchSidebar('settings')"
            @click="switchSidebar('settings')"
          >
            <i aria-hidden="true" class="iconify sidebar-svg" data-icon="icon-park-outline:setting-two"></i>
          </a>
        </li> -->

        <!-- Profile Dropdown -->
        <li>
          <UserProfileDropdown up />
        </li>
      </template>
    </Sidebar>

    <Transition name="slide-x">
      <KeepAlive>
        <SettingsSubsidebar
          v-if="isDesktopSidebarOpen && activeMobileSubsidebar === 'settings'"
          @close="isDesktopSidebarOpen = false"
        />
      </KeepAlive>
    </Transition>

    <VViewWrapper>
      <VPageContentWrapper>
        <template v-if="props.nowrap">
          <slot></slot>
        </template>
        <VPageContent v-else class="is-relative">
          <div class="page-title has-text-centered">
            <!-- Sidebar Trigger -->
            <div
              class="vuero-hamburger nav-trigger push-resize"
              tabindex="0"
              @keydown.space.prevent="isDesktopSidebarOpen = !isDesktopSidebarOpen"
              @click="isDesktopSidebarOpen = !isDesktopSidebarOpen"
            >
              <span class="menu-toggle has-chevron">
                <span :class="[isDesktopSidebarOpen && 'active']" class="icon-box-toggle">
                  <span class="rotate">
                    <i aria-hidden="true" class="icon-line-top"></i>
                    <i aria-hidden="true" class="icon-line-center"></i>
                    <i aria-hidden="true" class="icon-line-bottom"></i>
                  </span>
                </span>
              </span>
            </div>

            <div class="title-wrap">
              <h1 class="title is-4">{{ viewWrapper.pageTitle }}</h1>
            </div>

            <Toolbar class="desktop-toolbar">
              <ToolbarNotification />

              <a class="toolbar-link right-panel-trigger" href="/admin/home">
                <i aria-hidden="true" class="iconify" data-icon="feather:grid"></i>
              </a>
            </Toolbar>
          </div>

          <slot></slot>
        </VPageContent>
      </VPageContentWrapper>
    </VViewWrapper>
  </div>
</template>
