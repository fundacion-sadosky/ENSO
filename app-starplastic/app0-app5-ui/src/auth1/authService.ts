import axios, { AxiosInstance } from 'axios'
import AuthManager from '/@src/auth1/authManager'
import { useSession } from '/@src/stores/session'

const currHostname = window.location.hostname
let BASE_URL: string
if (currHostname === (import.meta.env.VITE_APP1_HOST as string)) {
  BASE_URL = import.meta.env.VITE_APP1_AUTH_URL as string
} else if (currHostname === (import.meta.env.VITE_APP2_HOST as string)) {
  BASE_URL = import.meta.env.VITE_APP2_AUTH_URL as string
} else {
  BASE_URL = import.meta.env.VITE_APP_AUTH_URL as string
}
console.log(`currHostname ${currHostname}`)
console.log(`BASE_URL ${BASE_URL}`)

const auth = axios.create({
  baseURL: BASE_URL as string,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'X-Track-Caller': 'app0-app5-ui',
    'X-Track-Session-Id': 'to-do',
  },
})

const authManager = new AuthManager(auth, useSession)
console.log('Create Auth Service instance')

export const useAuth = {
  async login(user: string, pass: string) {
    const ret = await authManager.login(user, pass)
    return ret
  },
  async loginWithRedirect(tgt: any) {
    return await authManager.loginWithRedirect(tgt)
  },
  async selfLogin() {
    return await authManager.selfLogin()
  },
  async logout() {
    return await authManager.logout()
  },
  async bindToken(apiClient: AxiosInstance) {
    return await authManager.bindToken(apiClient)
  },
  get isAuthenticated() {
    return authManager.isAuthenticated
  },
  async forgotPassword(username: string) {
    return await authManager.forgotPassword({ user: username })
  },
  async resetPassword(AuthNew: { auth_token: string; password: string }) {
    return await authManager.resetPassword(AuthNew)
  },
  async forbiddenAccess() {
    return await authManager.forbiddenAccess()
  },
  // @ts-ignore
  get roles() {
    return authManager.roles
  },
}
