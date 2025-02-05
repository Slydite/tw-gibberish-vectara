// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import ModelView from '../components/ModelView.vue'
import HomeView from '../views/HomeView.vue'
import InputView from '../components/InputView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            component: HomeView,
            children: [
                {
                    path: '',
                    name: 'home',
                    component: { template: '<div>Welcome to the Dashboard</div>' }
                },
                {
                    path: 'vectara',
                    name: 'vectara',
                    component: ModelView,
                    props: { modelType: 'Vectara' }
                },
                {
                    path: 'gibberish',
                    name: 'gibberish',
                    component: ModelView,
                    props: { modelType: 'Gibberish' }
                },
                {
                    path: 'input',
                    name: 'input',
                    component: InputView
                }
            ]
        }
    ]
})

export default router