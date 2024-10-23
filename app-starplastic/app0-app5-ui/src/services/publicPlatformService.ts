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

export const publicPlatformService = {
  getLogoURL(filename: string) {
    return `${BASE_URL}/logo-get?doc_id=${filename}`
  },
}
