import { acceptHMRUpdate, defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'

export type MonitorMode = 'none' | 'running_jobs'

export const useJobMonitor = defineStore('jobMonitor', () => {
  const monitormode = useStorage<MonitorMode>('monitormode', 'none')

  function enableMonitor() {
    monitormode.value = 'running_jobs'
  }

  function disableMonitor() {
    monitormode.value = 'none'
  }

  function isEnabledMonitor() {
    return monitormode.value == 'running_jobs'
  }

  return {
    enableMonitor,
    disableMonitor,
    isEnabledMonitor,
  } as const
})

/**
 * Pinia supports Hot Module replacement so you can edit your stores and
 * interact with them directly in your app without reloading the page.
 *
 * @see https://pinia.esm.dev/cookbook/hot-module-replacement.html
 * @see https://vitejs.dev/guide/api-hmr.html
 */
if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useJobMonitor, import.meta.hot))
}
