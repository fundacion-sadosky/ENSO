<script setup lang="ts">
import { utils } from '/@src/services/utils'
import { platformService } from '/@src/services/platformService'
import { useNotyf } from '/@src/composable/useNotyf'

const props = defineProps({
  appId: {
    type: String,
    default: undefined,
  },
  item: {
    type: Object,
    default: undefined,
  },
})

const notyf = useNotyf()

const downloadFile = async () => {
  try {
    let fileBlob: Blob = await platformService.getAppFileBlob(props.appId, props.item.filename)
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(fileBlob)
    link.download = props.item.src_filename ? props.item.src_filename : 'file.xxx'
    link.target = '_blank'
    link.click()
  } catch (error: any) {
    notyf.error(error.message)
  }
}
</script>

<template>
  <VCardActionc
    v-if="props.item"
    dataicon="icon-park-outline:file-code"
    :title="utils.strShort(props.item.src_filename, 30)"
    :subtitle="utils.humanFileSize(props.item.size) + ' | ' + utils.dateFmtStrH(props.item.creation_date)"
    @click="downloadFile()"
  >
    <template #action>
      <VDropdown icon="feather:more-vertical" class="end-action" spaced right>
        <template #content>
          <a role="menuitem" href="#" class="dropdown-item is-media" @click="downloadFile()">
            <div class="icon">
              <i aria-hidden="true" class="lnil lnil-cloud-download"></i>
            </div>
            <div class="meta">
              <span>Download</span>
            </div>
          </a>
        </template>
      </VDropdown>
    </template>
  </VCardActionc>
</template>
