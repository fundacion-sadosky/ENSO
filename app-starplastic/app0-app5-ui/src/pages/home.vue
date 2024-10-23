<script setup lang="ts">
import { useHead } from '@vueuse/head'
import { useSession } from '/@src/stores/session'
import { useViewWrapper } from '/@src/stores/viewWrapper'

const session = useSession()
let title = 'Starplastic App'
if (session.userData?.fullname) {
  title += ' | ' + session.userData.fullname
}
useHead({ title: title })
const viewWrapper = useViewWrapper()
viewWrapper.setPageTitle(title)
</script>

<template>
  <SidebarLayout>
    <div class="page-content-inner">
      <HomeDashboard />
    </div>
  </SidebarLayout>
</template>
