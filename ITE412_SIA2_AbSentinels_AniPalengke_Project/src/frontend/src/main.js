import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './assets/main.css'
import App from './pages/App.vue'
import routes from './router/index.js'

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
