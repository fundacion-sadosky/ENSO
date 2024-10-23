import { createRouter as createClientRouter, createWebHistory } from 'vue-router'

/**
 * routes are generated using vite-plugin-pages
 * each .vue files located in the ./src/pages are registered as a route
 * @see https://github.com/hannoeru/vite-plugin-pages
 */
import { RouteRecordRaw } from 'vue-router'
const routes: RouteRecordRaw[] = [
  {
    component: () => import('/src/pages/index.vue'),
    name: 'index',
    path: '/',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/home.vue'),
    name: 'home',
    path: '/home',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/dash1.vue'),
    name: 'dash1',
    path: '/dash1',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/dash1ot.vue'),
    name: 'dash1ot',
    path: '/dash1ot',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/machines.vue'),
    name: 'machines',
    path: '/machines',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/machine-edit.vue'),
    name: 'machine-edit',
    path: '/machine/:objId',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/machine-data.vue'),
    name: 'machine-data',
    path: '/machine/d/:objId',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/machine-charts.vue'),
    name: 'machine-charts',
    path: '/machine/s/:objId',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/jobs.vue'),
    name: 'jobs',
    path: '/jobs',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/job-new.vue'),
    name: 'job-new',
    path: '/job/jn/:originId?',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/job-edit.vue'),
    name: 'job-edit',
    path: '/job/e/:objId',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/job-compare.vue'),
    name: 'job-compare',
    path: '/job/c/',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/kpi1.vue'),
    name: 'kpi1',
    path: '/kpi1',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/kpi1-last.vue'),
    name: 'kpi1-last',
    path: '/kpi1-last',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/products.vue'),
    name: 'products',
    path: '/products',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/product-edit.vue'),
    name: 'product-edit',
    path: '/product/:objId',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/profile.vue'),
    name: 'profile',
    path: '/profile',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/profile-notifications.vue'),
    name: 'profile-notifications',
    path: '/profile-notifications',
    props: true,
    meta: { requiresAuth: true },
  },
  {
    component: () => import('/src/pages/error/error-page-4.vue'),
    name: 'error-page-4',
    path: '/error-page-4',
    props: true,
  },
  {
    component: () => import('/src/pages/error/error-page-5.vue'),
    name: 'error-page-5',
    path: '/error-page-5',
    props: true,
  },
  {
    component: () => import('/src/pages/error/error-page-forbidden.vue'),
    name: 'error-page-forbidden',
    path: '/error-page-forbidden',
    props: true,
  },
  {
    component: () => import('/src/pages/auth/logout.vue'),
    name: 'logout',
    path: '/logout',
    props: true,
  },
  {
    component: () => import('/src/pages/[...all].vue'),
    name: 'all',
    path: '/:all(.*)',
    props: true,
  },
]

export function createRouter() {
  const router = createClientRouter({
    history: createWebHistory('app5'),
    routes,
  })

  return router
}
