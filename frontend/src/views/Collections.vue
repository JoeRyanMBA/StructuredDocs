<template>
  <div class="collections-view">
    <Breadcrumbs />
    <h2>📁 Collections</h2>
    
    <p class="guidance-text">
      Create a new collection (document) by typing the name in the Collection name box, and then selecting Add Collection. Existing collections appear below.
    </p>
    
    <form @submit.prevent="createCollection" class="create-collection-form">
      <div class="form-row">
        <select v-model="newCollection.projectId" required class="form-input" style="max-width: 220px;">
          <option value="">Select Project...</option>
          <option v-for="project in projects" :key="project.id" :value="project.id">{{ project.name }}</option>
        </select>
        <input 
          v-model="newCollection.name" 
          placeholder="Collection name" 
          required 
          class="form-input"
        />
        <input 
          v-model="newCollection.form_number" 
          placeholder="Collection ID (e.g., FORM-001)" 
          required 
          pattern="^[A-Za-z0-9\-_]+$"
          title="Only letters, numbers, hyphens, and underscores are allowed"
          class="form-input"
        />
        <button type="submit" class="form-button">Add Collection</button>
      </div>
      <small class="form-help">
        Select a project for this collection. Collection ID is a unique alphanumeric identifier for this document (e.g., FORM-001, DOC-ABC-123)
      </small>
    </form>
  
    <p style="margin-top: 20px; margin-bottom: 10px; font-weight: 500;">Select a collection to organize:</p>
  
    <ul>
      <li v-for="col in collections" :key="col.id">
        <div v-if="col.id !== undefined && col.id !== null">
          <router-link
            :to="{ name: 'Organize', params: { id: String(col.id) } }"
            style="text-decoration: none; color: #2563eb; cursor: pointer;"
          >
            {{ col.name }}
          </router-link>
        </div>
        <span v-else>
          {{ col.name || 'Unnamed Collection' }} (No ID available)
        </span>
      </li>
    </ul>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import CollectionTree from '@/components/CollectionTree.vue'
import { getCollections } from '@/api/collections.js'
import { getProjects } from '@/api/projects.js'

export default {
  name: 'CollectionsTree',
  components: { Breadcrumbs, CollectionTree },
  data() {
    return {
      collections: [],
      projects: [],
      newCollection: {
        name: '',
        form_number: '',
        projectId: ''
      }
    }
  },
  async created() {
    try {
      const [collections, projects] = await Promise.all([
        getCollections(),
        getProjects()
      ]);
      this.collections = collections;
      this.projects = projects;
    } catch (error) {
      console.error('Failed to load collections or projects:', error)
      this.collections = [];
      this.projects = [];
    }
  },
  methods: {
    async createCollection() {
      const res = await fetch('/api/collections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          name: this.newCollection.name,
          form_number: this.newCollection.form_number,
          projectId: this.newCollection.projectId ? Number(this.newCollection.projectId) : null
        })
      });
      if (res.ok) {
        this.collections = await getCollections();
        this.newCollection.name = '';
        this.newCollection.form_number = '';
        this.newCollection.projectId = '';
      } else {
        const error = await res.json();
        alert(`Error: ${error.error || 'Failed to create collection'}`);
      }
    }
  }
}
</script>

<style scoped>
.collections-view {
  margin: 0 auto;
}

.guidance-text {
  background: #f8f9fa;
  border-left: 4px solid #007acc;
  border-radius: .75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #495057;
  font-size: 0.95rem;
  line-height: 1.5;
}

.create-collection-form {
  margin-bottom: 2rem;
}

.form-row {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}

.form-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-input:focus {
  outline: none;
  border-color: #007acc;
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.1);
}

.form-button {
  padding: 0.75rem 1.5rem;
  background: #007acc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  white-space: nowrap;
}

.form-button:hover {
  background: #005a9c;
}

.form-help {
  display: block;
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
  line-height: 1.4;
}
</style>