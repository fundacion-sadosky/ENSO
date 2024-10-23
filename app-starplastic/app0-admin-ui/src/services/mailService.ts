import axios from 'axios'
import { useAuth } from '/@src/auth1'
import { handleAPIError } from '/@src/services/handleAPIError'

const currHostname = window.location.hostname
let BASE_URL: string
if (currHostname === (import.meta.env.VITE_APP1_HOST as string)) {
  BASE_URL = import.meta.env.VITE_APP1_API_URL as string
} else if (currHostname === (import.meta.env.VITE_APP2_HOST as string)) {
  BASE_URL = import.meta.env.VITE_APP2_API_URL as string
} else {
  BASE_URL = import.meta.env.VITE_APP_API_URL as string
}
console.log(`currHostname ${currHostname}`)
console.log(`BASE_URL ${BASE_URL}`)

const apiClient = axios.create({
  baseURL: BASE_URL as string,
  withCredentials: false,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})
useAuth.bindToken(apiClient)

export const mailService = {
  async testEmail() {
    const ret = await apiClient.get(`/setup-adhoc?code=TEST_HTML_MAIL`).catch(handleAPIError)
    return ret.data
  },
  async testAttachFile() {
    const ret = await apiClient.get(`/setup-adhoc?code=TEST_ATT_FILE`).catch(handleAPIError)
    return ret.data
  },
  async testAttachS3() {
    const ret = await apiClient.get(`/setup-adhoc?code=TEST_ATT_S3`).catch(handleAPIError)
    return ret.data
  },
  async testTmail(object: any) {
    const ret = await apiClient.post('/mail-test', object).catch(handleAPIError)
    return ret.data
  },
}
