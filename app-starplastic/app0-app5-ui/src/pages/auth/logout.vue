<script setup lang="ts">
import { useAuth } from '/@src/auth1'
import { onMounted } from 'vue'

onMounted(async () => {
  await useAuth.logout()
  window.open('/admin', '_self')
})
</script>

<template>
  <AuthLayout>
    <p>Logout...</p>
  </AuthLayout>
</template>
