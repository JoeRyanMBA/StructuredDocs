// frontend/src/router.js

import { createRouter, createWebHistory } from 'vue-router'
import TopicsListView from '@/views/TopicsListView.vue'
import EditTopicView from '@/views/EditTopicView.vue'

const routes = [
  // ▶️ Start / Home
  {
    path: '/',
    name: 'Start',
    component: () => import('@/views/StartPage.vue')
  },

  // ✏️ Authoring
  {
    path: '/author',
    name: 'AuthorHome',
    component: () => import('@/views/Author.vue')
  },
   {
    path: '/topics',
    name: 'TopicsList',
    component: TopicsListView
  },
  {
    path: '/topics/new',
    name: 'NewTopic',
    component: EditTopicView,
    props: route => ({ topicId: null })
  },
  {
    path: '/topics/:id/edit',
    name: 'EditTopic',
    component: EditTopicView,
    props: route => ({ topicId: parseInt(route.params.id, 10) })
  },
  {
    path: '/author-history',
    name: 'AuthorHistory',
    component: () => import('@/views/AuthorHistory.vue')
  },
  {
    path: '/organize',
    name: 'Organize',
    component: () => import('@/views/Organize.vue')
  },

  // 📥 Import Section
{
  path: '/import',
  name: 'ImportHome',
  component: () => import('@/views/ImportView.vue')
},
{
  path: '/import/:id/review',
  name: 'ImportReview',
  component: () => import('@/views/ImportReviewView.vue'),
  props: route => ({ id: route.params.id })
},
{
  path: '/import/history',
  name: 'ImportHistory',
  component: () => import('@/views/ImportHistoryView.vue')
},

  // 📤 Publish Section
    {
    path: '/Publications',
    name: 'PublicationsHome',
    component: () => import('@/views/PublicationsHome.vue')
  },
  {
    path: '/publications/:id',
    name: 'PublicationView',
    component: () => import('@/views/PublicationView.vue')
  },
  /* {
    path: '/publish/html',
    name: 'PublishHtml',
    component: () => import('@/views/PublishHtml.vue')
  },
  {
    path: '/publish/pdf',
    name: 'PublishPdf',
    component: () => import('@/views/PublishPdf.vue')
  },
  {
    path: '/publish/history',
    name: 'PublishHistory',
    component: () => import('@/views/PublishHistory.vue')
  }, */

  // 📝 Review Section
  {
    path: '/reviews',
    name: 'ReviewsHome',
    component: () => import('@/views/Reviews.vue')
  },
  {
    path: '/reviews/send',
    name: 'SMEReviews',
    component: () => import('@/views/SMEReviews.vue')
  },
  {
    path: '/reviews/incorporate',
    name: 'IncorporateFeedback',
    component: () => import('@/views/IncorporateFeedback.vue')
  },
  {
    path: '/reviews/history',
    name: 'ReviewHistory',
    component: () => import('@/views/ReviewHistory.vue')
  },

  // 🔒 Admin Section
  {
    path: '/admin',
    name: 'AdminHome',
    component: () => import('@/views/Admin.vue')
  },
  {
    path: '/admin/authors',
    name: 'ManageAuthors',
    component: () => import('@/views/ManageAuthors.vue')
  },
  {
    path: '/admin/users',
    name: 'ManageUsers',
    component: () => import('@/views/ManageUsers.vue')
  },
  {
    path: '/admin/logs',
    name: 'SystemLogs',
    component: () => import('@/views/SystemLogs.vue')
  },

  // 🛠️ Catch-all fallback
  {
    path: '/:catchAll(.*)',
    redirect: { name: 'TopicsList' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router