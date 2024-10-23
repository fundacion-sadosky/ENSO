<script setup lang="ts">
import { onBeforeUnmount } from 'vue'
import { initDarkmode } from '/@src/stores/darkmode'
import { useJobMonitor } from '/@src/stores/jobmonitor'
import { useSession } from '/@src/stores/session'
import { platformService } from '/@src/services/platformService'
import { useNotyf } from '/@src/composable/useNotyf'

// This is the global app setup function

// Initialize the darkmode watcher
initDarkmode()
// monitor spool with interval
const notyf = useNotyf()
const jobMonitor = useJobMonitor()
jobMonitor.disableMonitor()
const session = useSession()
const updateStatus = async () => {
  if (session.isAuthenticated) {
    // console.log('===> Querying status')
    if (jobMonitor.isEnabledMonitor()) {
      // console.log('===> Monitor enabled')
      // todo query key
      let kval = await platformService.getKey('app5-processing-job')
      // console.log('===> KVAL:')
      // console.log(kval)
      if (kval && kval['value'] !== 'none') {
        notyf.successNoClose(kval['label'])
        if (kval['details']['status'] === 'END') {
          jobMonitor.disableMonitor()
          // console.log('===> Disabling Monitor')
        }
      }
    } else {
      // console.log('===> Monitor disabled')
    }
  }
}
const queryMonitor = setInterval(updateStatus, 3000)
onBeforeUnmount(() => {
  clearInterval(queryMonitor)
})
</script>

<template>
  <div>
    <Suspense>
      <RouterView v-slot="{ Component }">
        <Transition name="fade-slow" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </Suspense>
    <VReloadPrompt app-name="TheApp" />
  </div>
</template>
