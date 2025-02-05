// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Import router

import './assets/main.css'

const app = createApp(App)

app.use(router) // Use router
app.mount('#app')