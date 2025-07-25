// src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'
import PublicationsHome from '@/views/PublicationsHome.vue'
import PublicationView   from '@/views/PublicationView.vue'

const routes = [
  // Redirect root to topics list
  {
    path: '/',
    redirect: '/topics'
  },

  // Topics
  {
    path: '/topics',
    name: 'TopicsList',
    component: () => import('@/views/TopicsListView.vue')
  },
  {
    path: '/topics/new',
    name: 'NewTopic',
    component: () => import('@/views/EditTopicView.vue')
  },
  {
    path: '/topics/:id',
    name: 'EditTopic',
    component: () => import('@/views/EditTopicView.vue'),
    props: true
  },

  // Import flow
  {
    path: '/import',
    name: 'ImportHome',
    component: () => import('@/views/ImportView.vue')
  },
  {
    path: '/import/review/:id',
    name: 'ImportReview',
    component: () => import('@/views/ImportReviewView.vue'),
    props: true
  },
  {
    path: '/import/history',
    name: 'ImportHistory',
    component: () => import('@/views/ImportHistoryView.vue')
  },

  // Publication
  {
    path: '/publications',
    name: 'PublicationsHome',
    component: PublicationsHome
  },
  {
    path: '/publications/:id',
    name: 'PublicationView',
    component: PublicationView,
    props: true
  },
   
  // 404 fallback
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // if user used browser back/forward, restore scroll
    if (savedPosition) return savedPosition
    // otherwise scroll to top
    return { top: 0 }
  }
})

export default router