import axios from 'axios'
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

export const publicService = {
  async getEnabledPlans() {
    const ret = await apiClient.get('/plan-list-enabled').catch(handleAPIError)
    return ret.data
  },
  async saveNewRegistration(object: any) {
    const ret = await apiClient.post('/registration-pub-save', object).catch(handleAPIError)
    return ret.data
  },
  async addLogo(formData: FormData) {
    const ret = await apiClient.post(`/logo-upload`, formData).catch(handleAPIError)
    return ret.data
  },
  async getLogoBlob(filename: string) {
    const ret = await apiClient
      .get(`/logo-get?doc_id=${filename}`, { responseType: 'arraybuffer' })
      .catch(handleAPIError)
    return new Blob([ret.data], { type: 'application/octet-binary' })
  },
  getLogoURL(filename: string) {
    return `${BASE_URL}/logo-get?doc_id=${filename}`
  },
  async validateEmail(email: string) {
    const ret = await apiClient.get(`/user-validate-mail-unique?email=${email}`).catch(handleAPIError)
    return ret.data
  },
}
