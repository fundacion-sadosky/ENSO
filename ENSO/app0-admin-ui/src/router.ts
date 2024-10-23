import { createRouter as createClientRouter, createWebHistory } from 'vue-router'

import { RouteRecordRaw } from 'vue-router'
import { ROLE_ADMIN } from '/@src/data/constants'
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
    component: () => import('/src/pages/users.vue'),
    name: 'users',
    path: '/users',
    props: true,
    meta: { requiresAuth: true, requiredRole: ROLE_ADMIN },
  },
  {
    component: () => import('/src/pages/user-edit.vue'),
    name: 'user-edit',
    path: '/user/:objId',
    props: true,
    meta: { requiresAuth: true, requiredRole: ROLE_ADMIN },
  },
  {
    component: () => import('/src/pages/tmails.vue'),
    name: 'tmails',
    path: '/tmails',
    props: true,
    meta: { requiresAuth: true, requiredRole: ROLE_ADMIN },
  },
  {
    component: () => import('/src/pages/tmail-edit.vue'),
    name: 'tmail-edit',
    path: '/tmail/:objId',
    props: true,
    meta: { requiresAuth: true, requiredRole: ROLE_ADMIN },
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
    component: () => import('/src/pages/apps.vue'),
    name: 'apps',
    path: '/apps',
    props: true,
    meta: { requiresAuth: true, requiredRole: ROLE_ADMIN },
  },
  {
    component: () => import('/src/pages/app-edit.vue'),
    name: 'app-edit',
    path: '/app/:objId',
    props: true,
    meta: { requiresAuth: true, requiredRole: ROLE_ADMIN },
  },
  {
    component: () => import('/src/pages/roles.vue'),
    name: 'roles',
    path: '/roles',
    props: true,
    meta: { requiresAuth: true, requiredRole: ROLE_ADMIN },
  },
  {
    component: () => import('/src/pages/role-edit.vue'),
    name: 'role-edit',
    path: '/role/:objId',
    props: true,
    meta: { requiresAuth: true, requiredRole: ROLE_ADMIN },
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
    component: () => import('/src/pages/auth/login.vue'),
    name: 'login',
    path: '/login',
    props: true,
  },
  {
    component: () => import('/src/pages/auth/logout.vue'),
    name: 'logout',
    path: '/logout',
    props: true,
  },
  {
    component: () => import('/src/pages/auth/reset.vue'),
    name: 'reset',
    path: '/reset/:token',
    props: true,
  },
  {
    component: () => import('/src/pages/auth/first-set.vue'),
    name: 'first-set',
    path: '/fset/:token',
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
    history: createWebHistory('admin'),
    routes,
  })

  return router
}
