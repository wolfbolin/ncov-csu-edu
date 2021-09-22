import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/deal',
    name: 'Deal',
    component: () => import(/* webpackChunkName: "deal" */ '../views/Deal.vue')
  },
  {
    path: '/release',
    name: 'Release',
    component: () => import(/* webpackChunkName: "about" */ '../views/Release.vue')
  },
  {
    path: '/data',
    name: 'Data',
    component: () => import(/* webpackChunkName: "data" */ '../views/Data.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
