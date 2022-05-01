import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'

import TodoView from '../views/TodoView'
import DoneView from '../views/DoneView'
import ErrorView from '../views/ErrorView'
import EditTodoView from '../views/EditTodoView'

import {auth} from "@/firebaseConfig.js"
Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/todos',
    name: 'todos',
    meta: { // connects with the function later in this file.
      requiresAuth: true
    },
    component: TodoView
  },
  {
    path: '/done',
    name: 'done',
    meta: { // connects with the function later in this file.
      requiresAuth: true
    },
    component: DoneView
  },
  {
    path: '/todo/:id',
    name: 'todoID',
    meta: { // connects with the function later in this file.
      requiresAuth: true
    },
    component: EditTodoView
  },
  {
    path: '*',
    name: 'error',
    component: ErrorView
  },
  // {
  //   path: '/example',
  //   name: 'example',
  //   component: ExampleView
  // },
  // {
  //   path: '/example/:id',
  //   name: 'example',
  //   component: ExampleIdView,
  //   props:true
  // },
  // {
  //   path: '/idea/:ideaId',
  //   name: 'ideaView',
  //   component: IdeaView,
  //   props:true
  // },
  // {
  //   path: '/idea',
  //   name: 'getIdeaView',
  //   meta: { // connects with the function later in this file.
  //     requiresAuth: true
  //   },
  //   component: GetIdeaView
  // },

]


const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})


router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(x => x.meta.requiresAuth)

  if (requiresAuth && !auth.currentUser) {
    next('/')
    // could also just fire off a redirect login here, or redirect based on a meta property!
  } else {
    next()
  }
})

export default router
