<script setup lang="ts">
import { useHead } from '@vueuse/head'
import { useSession } from '/@src/stores/session'

const session = useSession()

let title = 'Platform Home'
if (session.userData?.fullname) {
  title += ' | ' + session.userData.fullname
}
useHead({ title: title })
</script>

<template>
  <SidebarLayout>
    <div class="page-content-inner">
      <HomeDashboard />
    </div>
  </SidebarLayout>
</template>
