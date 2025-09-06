<template>
  <div class="admin-variables">
    <h1>Manage Variables</h1>
    <p class="subtitle">Create variables and define allowed values for publish-time substitution.</p>

    <div class="actions-bar">
      <button class="btn btn-primary" @click="openCreateVar">New Variable</button>
      <button class="btn btn-secondary" @click="refresh">Refresh</button>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else class="variables-layout">
      <div class="variables-list">
        <table class="vars-table">
          <thead>
            <tr><th>Slug</th><th>Name</th><th>Description</th><th>Scope</th><th>Values</th><th></th></tr>
          </thead>
          <tbody>
            <tr v-for="v in variables" :key="v.id" @click="selectVariable(v)" :class="{selected: selectedVar && selectedVar.id===v.id}">
              <td><code>{{ v.slug }}</code></td>
              <td>{{ v.name }}</td>
              <td class="muted">{{ v.description || '—' }}</td>
              <td>{{ v.scope }}</td>
              <td>{{ v.values.length }}</td>
              <td><button class="btn btn-sm" @click.stop="editVar(v)">Edit</button></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="variable-detail" v-if="selectedVar">
        <h2>{{ selectedVar.name }} <small><code>{{ selectedVar.slug }}</code></small></h2>
        <p>{{ selectedVar.description || 'No description.' }}</p>
        <h3>Values</h3>
        <table class="values-table">
          <thead><tr><th>Value</th><th>Default</th><th></th></tr></thead>
          <tbody>
            <tr v-for="val in selectedVar.values" :key="val.id">
              <td>{{ val.value }}</td>
              <td>{{ val.is_default ? '✔' : '' }}</td>
              <td>
                <button class="btn btn-sm" @click="makeDefault(val)" :disabled="val.is_default">Make Default</button>
                <button class="btn btn-sm btn-danger" @click="deleteValue(val)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="add-value-form">
          <input v-model="newValue" placeholder="New value" @keyup.enter="addValue" />
          <label><input type="checkbox" v-model="newValueDefault" /> Default</label>
          <button class="btn btn-primary btn-sm" @click="addValue" :disabled="!newValue.trim()">Add</button>
        </div>
      </div>
      <div v-else class="variable-detail empty">Select a variable to view and edit its values.</div>
    </div>

    <!-- Create / Edit Variable Modal -->
    <div v-if="showVarModal" class="modal-overlay" @click.self="closeVarModal">
      <div class="modal">
        <h3>{{ editingVar ? 'Edit Variable' : 'New Variable' }}</h3>
        <form @submit.prevent="saveVar" class="var-form">
          <label>Name*
            <input v-model="varForm.name" required maxlength="120" />
          </label>
          <label>Slug*
            <input v-model="varForm.slug" required maxlength="120" />
          </label>
          <label>Description
            <textarea v-model="varForm.description" rows="2" />
          </label>
          <label>Scope
            <select v-model="varForm.scope">
              <option value="global">Global</option>
              <option value="collection">Collection</option>
            </select>
          </label>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeVarModal">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="!varForm.name.trim()">{{ editingVar ? 'Update' : 'Create' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name:'AdminVariablesView',
  data(){
    return {
      variables:[],
      loading:false,
      selectedVar:null,
      showVarModal:false,
      editingVar:false,
      varForm:{ name:'', slug:'', description:'', scope:'global' },
      newValue:'',
      newValueDefault:false,
    }
  },
  created(){ this.refresh() },
  methods:{
    navigate(path){ this.$router.push(path) },
    async refresh(){
      this.loading = true
      try {
        const res = await fetch('/api/variables?include_values=1')
        this.variables = await res.json()
        if(this.selectedVar){
          // refresh selected reference
          this.selectedVar = this.variables.find(v=>v.id===this.selectedVar.id) || null
        }
      } catch(e){ console.error('Load failed', e) }
      finally { this.loading = false }
    },
    selectVariable(v){ this.selectedVar = v },
    openCreateVar(){ this.editingVar=false; this.varForm={ name:'', slug:'', description:'', scope:'global'}; this.showVarModal=true },
    editVar(v){ this.editingVar=true; this.varForm={ name:v.name, slug:v.slug, description:v.description||'', scope:v.scope }; this.showVarModal=true; this.selectedVar=v },
    closeVarModal(){ this.showVarModal=false },
    async saveVar(){
      try {
        const payload = { name:this.varForm.name.trim(), slug:this.varForm.slug.trim(), description:this.varForm.description.trim(), scope:this.varForm.scope }
        const method = this.editingVar ? 'PUT' : 'POST'
        const url = this.editingVar ? `/api/variables/${this.selectedVar.id}` : '/api/variables'
        const res = await fetch(url,{ method, headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) })
        if(!res.ok) throw new Error('Save failed')
        await this.refresh(); this.showVarModal=false
      } catch(e){ console.error(e) }
    },
    async addValue(){
      if(!this.selectedVar || !this.newValue.trim()) return
      try {
        const res = await fetch(`/api/variables/${this.selectedVar.id}/values`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ value:this.newValue.trim(), is_default:this.newValueDefault }) })
        if(!res.ok) throw new Error('Add failed')
        this.newValue=''; this.newValueDefault=false; await this.refresh()
      } catch(e){ console.error(e) }
    },
    async deleteValue(val){
      if(!confirm('Delete this value?')) return
      try {
        const res = await fetch(`/api/variables/values/${val.id}`, { method:'DELETE' })
        if(!res.ok) throw new Error('Delete failed')
        await this.refresh()
      } catch(e){ console.error(e) }
    },
    async makeDefault(val){
      if(!this.selectedVar) return
      try {
        const res = await fetch(`/api/variables/values/${val.id}`, { method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ is_default:true }) })
        if(!res.ok) throw new Error('Default update failed')
        await this.refresh()
      } catch(e){ console.error(e) }
    }
  }
}
</script>
<style scoped>
.admin-variables { padding:1.25rem; }
.subtitle { color:#64748b; margin-bottom:1rem; }
.actions-bar { display:flex; gap:.5rem; margin-bottom:1rem; }
.variables-layout { display:flex; gap:1rem; }
.variables-list { flex:1 1 50%; overflow:auto; }
.variable-detail { flex:1 1 50%; background:#fff; border:1px solid #e2e8f0; border-radius:8px; padding:1rem; }
.variable-detail.empty { display:flex; align-items:center; justify-content:center; color:#94a3b8; font-style:italic; }
.vars-table, .values-table { width:100%; border-collapse:collapse; font-size:.85rem; }
.vars-table th, .vars-table td, .values-table th, .values-table td { padding:.4rem .5rem; border-bottom:1px solid #e2e8f0; }
.vars-table tbody tr { cursor:pointer; }
.vars-table tbody tr.selected { background:#f1f5f9; }
.muted { color:#94a3b8; font-size:.75rem; }
.add-value-form { display:flex; gap:.5rem; align-items:center; margin-top:.75rem; }
.add-value-form input[type=text]{ flex:1; }
.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,.45); display:flex; align-items:flex-start; justify-content:center; padding-top:8vh; }
.modal { background:#fff; padding:1rem 1.25rem; width:420px; border-radius:8px; box-shadow:0 4px 24px rgba(0,0,0,.2); }
.var-form { display:flex; flex-direction:column; gap:.5rem; }
.var-form input, .var-form textarea, .var-form select { width:100%; }
.modal-actions { display:flex; justify-content:flex-end; gap:.5rem; margin-top:.5rem; }
</style>
