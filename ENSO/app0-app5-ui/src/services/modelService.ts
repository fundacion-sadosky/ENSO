import axios from 'axios'
import { useAuth } from '/@src/auth1'
import { handleAPIError } from '/@src/services/handleAPIError'
import { handleAPIErrorArrayBuffer } from '/@src/services/handleAPIErrorArrayBuffer'
import { useJobMonitor } from '/@src/stores/jobmonitor'

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

const jobMonitor = useJobMonitor()

export const modelService = {
  async getAppData() {
    const ret = await apiClient.get(`/app-get-data`).catch(handleAPIError)
    return ret.data
  },
  async getAppDataAction(action: string) {
    const ret = await apiClient.get(`/app-get-data?action=${action}`).catch(handleAPIError)
    return ret.data
  },
  async getMachines(filters: any) {
    const ret = await apiClient.post('/machine-list', filters ? filters : {}).catch(handleAPIError)
    return ret.data
  },
  async getMachine(obj_id: any) {
    const ret = await apiClient.get(`/machine-get?obj_id=${obj_id}`).catch(handleAPIError)
    return ret.data
  },
  async saveMachine(object: any) {
    const ret = await apiClient.post('/machine-save', object).catch(handleAPIError)
    return ret.data
  },
  async saveMachineAction(object: any, action: string) {
    const ret = await apiClient.post(`/machine-save?action=${action}`, object).catch(handleAPIError)
    return ret.data
  },
  async getMachineData(machine: string, action: string, from: string, to: string) {
    const ret = await apiClient
      .get(`/machine-data?action=${action}&machine=${machine}&date_from=${from}&date_to=${to}`)
      .catch(handleAPIError)
    return ret.data
  },
  async getProductData(machine: string, action: string, from: string, to: string) {
    const ret = await apiClient
      .get(`/product-data?action=${action}&machine=${machine}&date_from=${from}&date_to=${to}`)
      .catch(handleAPIError)
    return ret.data
  },
  async getSensorData(machine: string, action: string, datestr: string) {
    const ret = await apiClient
      .get(`/sensor-data?action=${action}&machine=${machine}&date=${datestr}`)
      .catch(handleAPIError)
    return ret.data
  },
  async getSensorDataFileBlob(machine: string, action: string, datestr: string) {
    const ret = await apiClient
      .get(`/sensor-data-csv?action=${action}&machine=${machine}&date=${datestr}`, { responseType: 'arraybuffer' })
      .catch(handleAPIErrorArrayBuffer)
    return new Blob([ret.data], { type: 'application/octet-binary' })
  },
  async getJobs(filters: any, offset: number, pageSize: number) {
    const ret = await apiClient
      .post(`/job-list?offset=${offset}&page_size=${pageSize}`, filters ? filters : {})
      .catch(handleAPIError)
    return ret.data
  },
  async newJob() {
    const ret = await apiClient.get('/job-new').catch(handleAPIError)
    return ret.data
  },
  async newJobOrigin(originId: string) {
    const ret = await apiClient.get(`/job-new?origin_job_id=${originId}`).catch(handleAPIError)
    return ret.data
  },
  async getJob(obj_id: any) {
    const ret = await apiClient.get(`/job-get?obj_id=${obj_id}`).catch(handleAPIError)
    return ret.data
  },
  async solveJob(object: any) {
    const ret = await apiClient.post('/job-solve', object).catch(handleAPIError)
    // enable querying job queue states
    jobMonitor.enableMonitor()
    return ret.data
  },
  async saveJobAction(object: any, action: string) {
    const ret = await apiClient.post(`/job-save?action=${action}`, object).catch(handleAPIError)
    return ret.data
  },
  async saveJob(object: any) {
    const ret = await apiClient.post('/job-save', object).catch(handleAPIError)
    return ret.data
  },
  async getJobLogs(filters: any, offset: number, pageSize: number) {
    const ret = await apiClient
      .post(`/job-log-list?offset=${offset}&page_size=${pageSize}`, filters ? filters : {})
      .catch(handleAPIError)
    return ret.data
  },
  async getKpiDataAction(action: string, m?: string, y?: string) {
    let ret = undefined
    if (m && y) {
      ret = await apiClient.get(`/kpi-data?action=${action}&m=${m}&y=${y}`).catch(handleAPIError)
    } else {
      ret = await apiClient.get(`/kpi-data?action=${action}`).catch(handleAPIError)
    }
    return ret.data
  },
  async getProducts(filters: any) {
    const ret = await apiClient.post('/product-list', filters ? filters : {}).catch(handleAPIError)
    return ret.data
  },
  async getProduct(obj_id: any) {
    const ret = await apiClient.get(`/product-get?obj_id=${obj_id}`).catch(handleAPIError)
    return ret.data
  },
  async saveProduct(object: any) {
    const ret = await apiClient.post('/product-save', object).catch(handleAPIError)
    return ret.data
  },
  async saveProductAction(object: any, action: string) {
    const ret = await apiClient.post(`/product-save?action=${action}`, object).catch(handleAPIError)
    return ret.data
  },
}
