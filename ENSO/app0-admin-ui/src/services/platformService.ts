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
  async getApps(filters: any) {
    const ret = await apiClient.post('/app-list', filters ? filters : {}).catch(handleAPIError)
    return ret.data
  },
  async getApp(obj_id: any) {
    const ret = await apiClient.get(`/app-get?obj_id=${obj_id}`).catch(handleAPIError)
    return ret.data
  },
  async saveApp(object: any) {
    const ret = await apiClient.post('/app-save', object).catch(handleAPIError)
    return ret.data
  },
  async saveAppAction(object: any, action: string) {
    const ret = await apiClient.post(`/app-save?action=${action}`, object).catch(handleAPIError)
    return ret.data
  },
  async addAppFile(app_id: string, tag: string, formData: FormData) {
    const ret = await apiClient.post(`/app-file-upload?app_id=${app_id}&tag=${tag}`, formData).catch(handleAPIError)

    return ret.data
  },
  async getAppFileObjectURL(app_id: string, doc_id: string) {
    const ret = await apiClient
      .get(`/app-file-get?app_id=${app_id}&doc_id=${doc_id}`, { responseType: 'arraybuffer' })
      .catch(handleAPIError)
    return window.URL.createObjectURL(new Blob([ret.data], { type: 'application/octet-binary' }))
  },
  async getAppFileBlob(app_id: string, doc_id: string) {
    const ret = await apiClient
      .get(`/app-file-get?app_id=${app_id}&doc_id=${doc_id}`, { responseType: 'arraybuffer' })
      .catch(handleAPIError)
    return new Blob([ret.data], { type: 'application/octet-binary' })
  },
  async getUsers(filters: any, page: number, pageSize: number) {
    const ret = await apiClient
      .post(`/user-list?page=${page}&page_size=${pageSize}`, filters ? filters : {})
      .catch(handleAPIError)
    return ret.data
  },
  async getUser(obj_id: any) {
    const ret = await apiClient.get(`/user-get?user_id=${obj_id}`).catch(handleAPIError)
    return ret.data
  },
  async saveUser(object: any) {
    const ret = await apiClient.post('/user-save', object).catch(handleAPIError)
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
  async getRole(obj_id: any) {
    const ret = await apiClient.get(`/role-get?obj_id=${obj_id}`).catch(handleAPIError)
    return ret.data
  },
  async saveRole(object: any) {
    const ret = await apiClient.post('/role-save', object).catch(handleAPIError)
    return ret.data
  },
  async saveRoleAction(object: any, action: string) {
    const ret = await apiClient.post(`/role-save?action=${action}`, object).catch(handleAPIError)
    return ret.data
  },
  async getCompanies(filters: any, page: number, pageSize: number) {
    const ret = await apiClient
      .post(`/company-list?page=${page}&page_size=${pageSize}`, filters ? filters : {})
      .catch(handleAPIError)
    return ret.data
  },
  async getCompany(obj_id: any) {
    const ret = await apiClient.get(`/company-get?company_id=${obj_id}`).catch(handleAPIError)
    return ret.data
  },
  async saveCompany(object: any) {
    const ret = await apiClient.post('/company-save', object).catch(handleAPIError)
    return ret.data
  },
  async saveCompanyAction(object: any, action: string) {
    const ret = await apiClient.post(`/company-save?action=${action}`, object).catch(handleAPIError)
    return ret.data
  },
  async getCompanyData(obj_id: any, category: string, filters: any) {
    const ret = await apiClient
      .post(`/company-data?company_id=${obj_id}&category=${category}`, filters)
      .catch(handleAPIError)
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
  async getLogoBlob(filename: string) {
    const ret = await apiClient
      .get(`/logo-get?doc_id=${filename}`, { responseType: 'arraybuffer' })
      .catch(handleAPIError)
    return new Blob([ret.data], { type: 'application/octet-binary' })
  },
  getLogoURL(filename: string) {
    return `${BASE_URL}/logo-get?doc_id=${filename}`
  },
  async getTmails(filters: any) {
    const ret = await apiClient.post('/tmail-list', filters).catch(handleAPIError)
    return ret.data
  },
  async getTmail(obj_id: any) {
    const ret = await apiClient.get(`/tmail-get?obj_id=${obj_id}`).catch(handleAPIError)
    return ret.data
  },
  async saveTmail(object: any) {
    const ret = await apiClient.post('/tmail-save', object).catch(handleAPIError)
    return ret.data
  },
  async getUserRoles(filters: any) {
    const ret = await apiClient.post('/user-role-list', filters).catch(handleAPIError)
    return ret.data
  },
  async saveUserRole(object: any) {
    const ret = await apiClient.post('/user-role-save', object).catch(handleAPIError)
    return ret.data
  },
  async saveUserRoleAction(object: any, action: string) {
    const ret = await apiClient.post(`/user-role-save?action=${action}`, object).catch(handleAPIError)
    return ret.data
  },
  async validateEmail(email: string) {
    const ret = await apiClient.get(`/user-validate-mail-unique?email=${email}`).catch(handleAPIError)
    return ret.data
  },
}
