import axios from 'axios'
import { useAuth } from '/@src/auth1'
import { handleAPIError } from '/@src/services/handleAPIError'

const currHostname = window.location.hostname
let BASE_URL: string
if (currHostname === (import.meta.env.VITE_APP1_HOST as string)) {
  BASE_URL = import.meta.env.VITE_APP1_API_ADMIN_URL as string
} else if (currHostname === (import.meta.env.VITE_APP2_HOST as string)) {
  BASE_URL = import.meta.env.VITE_APP2_API_ADMIN_URL as string
} else {
  BASE_URL = import.meta.env.VITE_APP_API_ADMIN_URL as string
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

export const platformService = {
  async getCurrUserApps() {
    const ret = await apiClient.get('/auth-user-apps').catch(handleAPIError)
    return ret.data
  },
  async getCurrUserRoles() {
    const ret = await apiClient.get('/auth-user-roles').catch(handleAPIError)
    return ret.data
  },
  async getCurrUserNotifications() {
    const ret = await apiClient.get('/auth-user-notifications').catch(handleAPIError)
    return ret.data
  },
  async saveUserAction(object: any, action: string) {
    const ret = await apiClient.post(`/user-save?action=${action}`, object).catch(handleAPIError)
    return ret.data
  },
  async getRoles(filters: any) {
    const ret = await apiClient.post('/role-list', filters ? filters : {}).catch(handleAPIError)
    return ret.data
  },
  async getNotifications(filters: any) {
    const ret = await apiClient.post('/notification-list', filters).catch(handleAPIError)
    return ret.data
  },
  async getNotification(obj_id: any) {
    const ret = await apiClient.get(`/notification-get?obj_id=${obj_id}`).catch(handleAPIError)
    return ret.data
  },
  async saveNotification(object: any) {
    const ret = await apiClient.post('/notification-save', object).catch(handleAPIError)
    return ret.data
  },
  async addLogo(formData: FormData) {
    const ret = await apiClient.post(`/logo-upload`, formData).catch(handleAPIError)

    return ret.data
  },
  async getLogoObjectURL(filename: string) {
    const ret = await apiClient
      .get(`/logo-get?doc_id=${filename}`, {
        responseType: 'arraybuffer',
      })
      .catch(handleAPIError)
    return window.URL.createObjectURL(new Blob([ret.data], { type: 'application/octet-binary' }))
  },
  getLogoURL(filename: string) {
    return `${BASE_URL}/logo-get?doc_id=${filename}`
  },
  async getKey(keyval: string) {
    const ret = await apiClient.get(`/key-consume?key=${keyval}`).catch(handleAPIError)
    return ret.data
  },
}
