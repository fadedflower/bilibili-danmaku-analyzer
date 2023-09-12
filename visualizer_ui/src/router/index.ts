import {createRouter, createWebHistory} from 'vue-router'
import routes from './routes'

const router = createRouter({
  //routes,
  history: createWebHistory('/ui'),
  routes
})

export default router