<template>
  <NotificationTicker
    :notifications="allNotifications"
    contextType="global"
    @mark-read="markNotificationRead"
  />
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Documentation Project Hub Dashboard</h1>
      <p class="welcome-text">Welcome, {{ $route?.meta?.user?.name || 'User' }}!</p>
    </div>
    <div v-if="loading" class="loading-overlay">
      <span class="loading-spinner">Loading dashboard...</span>
    </div>
    <div v-else>
      <div class="metrics-grid">
        <div class="metric-card" @click="navigateTo('/projects')" style="cursor:pointer;">
          <div class="metric-icon">📁</div>
          <div class="metric-content">
            <h3>Projects</h3>
            <div class="metric-number">{{ stats.projects.total }}</div>
            <div class="metric-detail">Active: {{ stats.projects.active }}</div>
          </div>
        </div>
        <div class="metric-card" @click="navigateTo('/collections')" style="cursor:pointer;">
          <div class="metric-icon">📚</div>
          <div class="metric-content">
            <h3>Collections</h3>
            <div class="metric-number">{{ stats.collections.total }}</div>
            <div class="metric-detail">New Today: {{ stats.collections.new_today }}</div>
          </div>
        </div>
        <div class="metric-card" @click="navigateTo('/topics')" style="cursor:pointer;">
          <div class="metric-icon">📝</div>
          <div class="metric-content">
            <h3>Topics</h3>
            <div class="metric-number">{{ stats.topics.total }}</div>
            <div class="metric-detail">Drafts: {{ stats.topics.drafts }}</div>
          </div>
        </div>
        <div class="metric-card" @click="navigateTo('/reviews')" style="cursor:pointer;">
          <div class="metric-icon">🔎</div>
          <div class="metric-content">
            <h3>Reviews</h3>
            <div class="metric-number">{{ stats.reviews.total }}</div>
            <div class="metric-detail">Pending: {{ stats.reviews.pending }}</div>
          </div>
        </div>
      </div>
      <div class="content-grid">
        <div class="dashboard-section">
          <h2>Projects Overview</h2>
          <div v-if="projects.length === 0" class="empty-state">
            <p>No projects found.</p>
          </div>
          <div v-else class="project-list">
            <div v-for="project in projects" :key="project.id" class="project-item">
              <div class="project-header">
                <h4>{{ project.name }}</h4>
                <span :class="['project-status', formatStatus(project.status)]">{{ formatStatus(project.status) }}</span>
              </div>
              <div class="project-description">{{ project.description }}</div>
              <div class="project-metrics">
                <span class="project-metric"><span class="metric-label">Created:</span> {{ formatRelativeTime(project.created_at) }}</span>
                <span v-if="project.milestones && project.milestones.length" class="project-metric"><span class="metric-label">Milestones:</span> {{ project.milestones.length }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="dashboard-section">
          <h2>Pending Actions</h2>
          <div v-if="pendingActions.length === 0" class="empty-state">
            <p>No pending actions.</p>
          </div>
          <div v-else class="action-list">
            <div v-for="action in pendingActions" :key="action.id" class="action-item" @click="handleActionClick(action)">
              <div class="action-icon">⚡</div>
              <div class="action-content">
                <div class="action-title">{{ action.title || action.name }}</div>
                <div class="action-description">{{ action.description }}</div>
                <div class="action-meta">{{ formatRelativeTime(action.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="dashboard-section full-width">
          <h2>Recent Activity</h2>
          <div v-if="recentActivity.length === 0" class="empty-state">
            <p>No recent activity.</p>
          </div>
          <div v-else class="activity-list">
            <div v-for="activity in recentActivity" :key="activity.id" class="activity-item">
              <div class="activity-icon">📄</div>
              <div class="activity-content">
                <div class="activity-title">{{ activity.filename }}</div>
                <div class="activity-description">
                  {{ activity.type === 'word' ? 'Word Document' : 'Markdown File' }} import - 
                  Status: {{ formatStatus(activity.status) }}
                  <span v-if="activity.topics_count"> - {{ activity.topics_count }} topics</span>
                </div>
                <div class="activity-time">{{ formatRelativeTime(activity.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="dashboard-section">
          <h2>Calendar</h2>
          <CalendarWidget :events="calendarEvents" />
        </div>
      </div>
    </div>
  </div>
</template>
