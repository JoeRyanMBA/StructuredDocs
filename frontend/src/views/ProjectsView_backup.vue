<template>
  <div class="projects-view">
    <Breadcrumbs />
    <h1>🎯 Projects</h1>
    <p>Manage projects, stakeholders, and review workflows.</p>
    
    <div class="actions-bar">
      <button class="create-btn">
        + New Project
      </button>
    </div>
    
    <div class="empty-projects">
      <div class="empty-content">
        <div class="empty-icon">🎯</div>
        <h2>No Projects Yet</h2>
        <p>Get started by creating your first project to organize topics, stakeholders, and review workflows.</p>
        <button class="create-first-btn">
          + Create Your First Project
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import Breadcrumbs from '../components/Breadcrumbs.vue'

export default {
  name: 'ProjectsView',
  components: {
    Breadcrumbs
  },
  data() {
    return {
      projects: [],
      showCreateModal: false,
      showEditModal: false,
      newProject: {
        name: '',
        description: ''
      },
      editingProject: {
        id: null,
        name: '',
        description: '',
        status: 'planning'
      }
    }
  },
  methods: {
    // Add basic methods to prevent errors
    editProject(project) {
      console.log('Edit project:', project)
    }
  }
}
</script>

<style scoped>
.projects-view {
  padding: 70px 20px 20px 20px;
}

.actions-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 30px;
}

.create-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}

.empty-projects {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 300px;
  margin: 20px 0;
  padding-top: 40px;
}

.empty-content {
  text-align: center;
  max-width: 500px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.create-first-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  cursor: pointer;
  margin: 0 auto;
}
</style>
