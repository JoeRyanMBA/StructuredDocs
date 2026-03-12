import { createRouter, createWebHistory } from 'vue-router'
import TopicsListView from '@/views/TopicsListView.vue'
import TopicView from '@/views/TopicView.vue'
import EditTopicView from '@/views/EditTopicView.vue'
import ImportView from '@/views/ImportView.vue'
import StartPage from '@/views/StartPage.vue'
import LoginView from '@/views/LoginView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import AdminUserManagement from '../views/AdminUserManagement.vue'
import SystemLogs from '../views/SystemLogs.vue'
import PerformanceMetrics from '../views/PerformanceMetrics.vue'
import AuditLogView from '../views/AuditLogView.vue'
import ProfileView from '../views/ProfileView.vue'
import EditNotification from '../views/EditNotification.vue'
import ProjectCreate from '../views/ProjectCreate.vue';
import CollectionCreate from '../views/CollectionCreate.vue';
import TopicCreate from '../views/TopicCreate.vue';
import AdminSettings from '../views/AdminSettings.vue';

// All routes
const routes = [
  {
    path: '/admin',
    name: 'Admin',
    component: AdminDashboard,
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') next(); else next('/dashboard');
    }
  },
  {
    path: '/admin/variables',
    name: 'AdminVariables',
    component: () => import('@/views/AdminVariablesView.vue'),
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') next(); else next('/dashboard');
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
    path: '/admin/audit',
    name: 'AuditLog',
    component: AuditLogView,
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') next(); else next('/dashboard');
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
    path: '/admin/feedback',
    name: 'AdminFeedback',
    component: () => import('@/views/admin/AdminFeedback.vue'),
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
    path: '/admin/bugs',
    name: 'AdminBugs',
    component: () => import('@/views/admin/AdminBugs.vue'),
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
    path: '/admin/help-links',
    name: 'AdminHelpLinks',
    component: () => import('@/views/admin/AdminHelpLinks.vue'),
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') next(); else next('/dashboard');
    }
  },
  // 📦 Archived Resources
  {
    path: '/admin/archived/projects',
    name: 'ArchivedProjects',
    component: () => import('@/views/ArchivedProjectsView.vue'),
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') next(); else next('/dashboard');
    }
  },
  {
    path: '/admin/archived/collections',
    name: 'ArchivedCollections',
    component: () => import('@/views/ArchivedCollectionsView.vue'),
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') next(); else next('/dashboard');
    }
  },
  {
    path: '/admin/archived/feedback',
    name: 'ArchivedFeedback',
    component: () => import('@/views/ArchivedFeedbackView.vue'),
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') next(); else next('/dashboard');
    }
  },
  {
    path: '/admin/archived/bugs',
    name: 'ArchivedBugs',
    component: () => import('@/views/ArchivedBugsView.vue'),
    meta: { requiresAuth: true, adminOnly: true },
    beforeEnter: (to, from, next) => {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'admin') next(); else next('/dashboard');
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
    path: '/notifications/manage',
    name: 'NotificationManagement',
    component: () => import('@/views/NotificationManagement.vue'),
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
  {
    path: '/auth/setup-password/:token',
    name: 'PasswordSetup',
    component: () => import('@/views/PasswordSetupView.vue'),
    props: true,
    meta: { requiresAuth: false }
  },
  {
    path: '/auth/reset-password/:token',
    name: 'PasswordReset',
    component: () => import('@/views/PasswordSetupView.vue'),
    props: true,
    meta: { requiresAuth: false }
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
    path: '/design/buttons',
    name: 'ButtonCatalog',
    component: () => import('@/views/ButtonCatalog.vue')
  },
  {
    path: '/topics',
    name: 'TopicsList',
    component: TopicsListView
  },
  {
    path: '/snippets',
    name: 'SnippetsLibrary',
    component: () => import('@/views/SnippetsLibrary.vue'),
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
    path: '/topics/:id',
    name: 'ViewTopic',
    component: TopicView,
    props: route => ({ topicId: parseInt(route.params.id, 10) })
  },
  {
    path: '/topics/:topicId/review-feedback/:reviewId',
    name: 'ReviewFeedback',
    component: () => import('@/views/ReviewFeedbackView.vue'),
    props: route => ({ 
      topicId: parseInt(route.params.topicId, 10),
      reviewId: parseInt(route.params.reviewId, 10)
    })
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
    path: '/projects/create',
    name: 'ProjectCreate',
    component: ProjectCreate,
    meta: { requiresAuth: true }
  },
  {
    path: '/collections/create',
    name: 'CollectionCreate',
    component: CollectionCreate,
    meta: { requiresAuth: true }
  },
  {
    path: '/topics/create',
    name: 'TopicCreate',
    component: TopicCreate,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/settings',
    name: 'AdminSettings',
    component: AdminSettings,
    meta: { requiresAuth: true, adminOnly: true }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/TasksView.vue')
  },
  {
    path: '/all-tasks',
    name: 'AllTasks',
    component: () => import('@/views/AllTasksView.vue')
  },
  {
    path: '/all-tags',
    name: 'AllTags',
    component: () => import('@/views/AllTagsView.vue')
  },
  {
    path: '/all-stakeholders',
    name: 'AllStakeholders',
    component: () => import('@/views/AllStakeholdersView.vue')
  },
  {
    path: '/all-milestones',
    name: 'AllMilestones',
    component: () => import('@/views/AllMilestonesView.vue')
  },
  {
    path: '/all-images',
    name: 'AllImages',
    component: () => import('@/views/AllImagesView.vue')
  },
  {
    path: '/all-links',
    name: 'AllLinks',
    component: () => import('@/views/AllLinksView.vue')
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
    component: () => import('@/views/ImportView.vue')
  },
  {
    path: '/import/dashboard',
    name: 'ImportDashboard',
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
    path: '/reviews/tasks',
    name: 'ReviewTasks',
    component: () => import('@/views/ReviewsListView.vue')
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
  
  // 🔗 External Review Portal (Token-based access)
  {
    path: '/review/:token',
    name: 'ReviewPortal',
    component: () => import('@/views/ReviewPortal.vue'),
    props: true,
    meta: { requiresAuth: false }
  },

  // 🔗 Bulk Review Portal (Token-based access, no auth required)
  {
    path: '/bulk-review/:token',
    name: 'BulkReviewPortal',
    component: () => import('@/views/BulkReviewPortal.vue'),
    props: true,
    meta: { requiresAuth: false }
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
  routes,
  // Always scroll to top on route change, but restore saved position for back/forward
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0 }
  }
})

// Authentication guard
function isAuthenticated() {
  try {
    const user = JSON.parse(localStorage.getItem('user'));
    return !!user;
  } catch (e) {
    return false;
  }
}

// Navigation guard to protect routes
router.beforeEach((to, from, next) => {
  // Routes that don't require authentication
  const publicRoutes = ['Login', 'ReviewPortal', 'BulkReviewPortal', 'PasswordSetup', 'PasswordReset', 'ButtonCatalog']
  
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