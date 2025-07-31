import { createRouter, createWebHistory } from 'vue-router'
import TopicsListView from '@/views/TopicsListView.vue'
import EditTopicView from '@/views/EditTopicView.vue'
import ImportView from '@/views/ImportView.vue'
import StartPage from '@/views/StartPage.vue'
import LoginView from '@/views/LoginView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import AdminUserManagement from '../views/AdminUserManagement.vue'
import SystemLogs from '../views/SystemLogs.vue'
import PerformanceMetrics from '../views/PerformanceMetrics.vue'
import ProfileView from '../views/ProfileView.vue'
import EditNotification from '../views/EditNotification.vue'

// All routes
const routes = [
  {
    path: '/admin',
    name: 'Admin',
    component: AdminDashboard,
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') {
        next();
      } else {
        next('/dashboard');
      }
    }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: AdminUserManagement,
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') {
        next();
      } else {
        next('/dashboard');
      }
    }
  },
  {
    path: '/admin/logs',
    name: 'SystemLogs',
    component: SystemLogs,
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') {
        next();
      } else {
        next('/dashboard');
      }
    }
  },
  {
    path: '/admin/metrics',
    name: 'PerformanceMetrics',
    component: PerformanceMetrics,
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') {
        next();
      } else {
        next('/dashboard');
      }
    }
  },
  {
    path: '/notifications/new',
    name: 'CreateNotification',
    component: () => import('@/views/CreateNotificationView.vue'),
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') {
        next();
      } else {
        next('/dashboard');
      }
    }
  },
  {
    path: '/notifications/edit/:id',
    name: 'EditNotification',
    component: EditNotification,
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') {
        next();
      } else {
        next('/dashboard');
      }
    }
  },
  
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  // 🔐 Authentication
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },

  // ▶️ Dashboard / Home
  {
    path: '/',
    name: 'Dashboard',
    component: StartPage
  },

  // ✏️ Authoring
  {
    path: '/author',
    name: 'AuthorHome',
    component: () => import('@/views/AuthorDashboard.vue')
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
    path: '/collections',
    name: 'Collections',
    component: () => import('@/views/CollectionsDashboard.vue')
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('@/views/ProjectsView.vue')
  },
  {
    path: '/organize/:id',
    name: 'Organize',
    component: () => import('@/views/Organize.vue'),
    props: true
  },

  // 📥 Import Section
  {
    path: '/import',
    name: 'ImportTopics',
    component: () => import('@/views/ImportDashboard.vue')
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
    path: '/publications',
    name: 'PublicationsHome',
    component: () => import('@/views/PublishDashboard.vue')
  },
  {
    path: '/publications/list',
    name: 'PublicationsList',
    component: () => import('@/views/PublicationsListView.vue')
  },
  {
    path: '/publications/:id',
    name: 'PublicationView',
    component: () => import('@/views/PublicationView.vue'),
    props: route => ({ id: parseInt(route.params.id, 10) })
  },
  {
    path: '/publish/mobile-kb',
    name: 'PublishMobileKB',
    component: () => import('@/views/PublishMobileKB.vue')
  },
  {
    path: '/publish/pdf',
    name: 'PublishPDF',
    component: () => import('@/views/PublishPDFView.vue')
  },

  // 📝 Review Section
  {
    path: '/reviews',
    name: 'ReviewsHome',
    component: () => import('@/views/ReviewsDashboard.vue')
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
  // Admin routes are defined above with proper authentication

  // 🛠️ Catch-all fallback
  {
    path: '/:catchAll(.*)',
    name: 'CatchAll',
    component: StartPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Authentication guard
function isAuthenticated() {
  return localStorage.getItem('isAuthenticated') === 'true'
}

// Navigation guard to protect routes
router.beforeEach((to, from, next) => {
  // Routes that don't require authentication
  const publicRoutes = ['Login']
  
  if (publicRoutes.includes(to.name)) {
    // If already logged in and trying to access login, redirect to dashboard
    if (to.name === 'Login' && isAuthenticated()) {
      next({ name: 'Dashboard' })
      return
    }
    next()
    return
  }
  
  // Check if user is authenticated
  if (!isAuthenticated()) {
    next({ name: 'Login' })
    return
  }
  
  next()
})

export default router