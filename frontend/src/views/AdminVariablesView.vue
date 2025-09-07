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
      <div v-if="loadError" class="error-banner">
        <strong>Load failed:</strong>
        <span v-if="loadError.type">{{ loadError.type }} - </span>{{ loadError.detail || loadError.error || 'Unknown error' }}
      </div>
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
              <td>{{ (v.values && Array.isArray(v.values)) ? v.values.length : 0 }}</td>
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
      <div class="modal-content var-modal" @click.stop>
        <h3>{{ editingVar ? 'Edit Variable' : 'New Variable' }}</h3>
        <form @submit.prevent="saveVar" class="var-form">
          <label>Name*
            <input v-model="varForm.name" @input="handleNameInput" required maxlength="120" />
          </label>
          <label>Slug* <span v-if="!editingVar && slugAuto" class="badge auto-hint">auto</span>
            <input
              v-model="varForm.slug"
              :disabled="editingVar" 
              @input="handleSlugInput"
              required
              maxlength="120"
              :class="{ invalid: !slugValid }"
            />
          </label>
          <div class="form-help">
            <p>
              The slug is the stable token used inside content like <code>{{ slugTokenDisplay }}</code>.
              {{ editingVar ? 'It cannot be changed after creation.' : 'It will auto-generate from Name; you can edit before saving.' }}
            </p>
            <p class="rules">Allowed: lowercase letters, numbers, hyphens and underscores. Must start with a letter. Example: <code>organization_name</code></p>
            <p v-if="!slugValid" class="error-text">Slug invalid. Use a leading letter, then letters/numbers/_ or -.</p>
            <div v-if="!editingVar && slugValid && !slugAvailable" class="error-text" style="margin-top:.25rem;">
              Slug already exists.
              <button type="button" class="btn btn-sm" @click="applySuggestedSlug" v-if="slugSuggestion">Use suggestion: <code>{{ slugSuggestion }}</code></button>
            </div>
          </div>
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
            <button type="button" class="btn btn-secondary btn-sm" @click="closeVarModal">Cancel</button>
            <button type="submit" class="btn btn-primary btn-sm" :disabled="!formSubmitEnabled || isSaving">{{ isSaving ? (editingVar ? 'Saving…' : 'Creating…') : (editingVar ? 'Update' : 'Create') }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
<script>
import { toast } from '@/composables/useToast'
export default {
  name:'AdminVariablesView',
  // Inject global toast composable
  // (import added below after <script> tag adjustment)
  data(){
    return {
  variables:[],
  loading:false,
  loadError:null,
      selectedVar:null,
      showVarModal:false,
      editingVar:false,
      varForm:{ name:'', slug:'', description:'', scope:'global' },
      newValue:'',
      newValueDefault:false,
  slugTouched:false,
  slugAuto:true,
  slugAvailable:true,
  slugSuggestion:'',
  isSaving:false,
    }
  },
  created(){ this.refresh() },
  computed:{
    slugValid(){
      if(this.editingVar) return true; // existing slug assumed valid
      const s = this.varForm.slug;
      if(!s) return false;
      return /^[a-z][a-z0-9_-]*$/.test(s);
    },
    formSubmitEnabled(){
  return !!this.varForm.name.trim() && this.slugValid && this.slugAvailable;
    },
    previewSlugExample(){
      return this.varForm.slug || 'organization_name';
    },
    slugTokenDisplay(){
      return `{{${this.previewSlugExample}}}`;
    }
  },
  methods:{
    navigate(path){ this.$router.push(path) },
    async refresh(){
      this.loading = true
      try {
        const res = await fetch('/api/variables?include_values=1')
        const data = await res.json()
        if(Array.isArray(data)) {
          this.variables = data.map(v=>({ ...v, values: Array.isArray(v.values)? v.values : [] }))
          this.loadError = null
        } else {
          console.error('Variables endpoint error', data)
          this.variables = []
          this.loadError = data
        }
        if(this.selectedVar){
          this.selectedVar = this.variables.find(v=>v.id===this.selectedVar.id) || null
        }
      } catch(e){ console.error('Load failed', e); this.variables=[] }
      finally { this.loading = false }
    },
    selectVariable(v){ this.selectedVar = v },
    openCreateVar(){
      this.editingVar=false;
      this.varForm={ name:'', slug:'', description:'', scope:'global'};
      this.slugTouched=false; this.slugAuto=true; this.showVarModal=true;
    },
    editVar(v){
      this.editingVar=true;
      this.varForm={ name:v.name, slug:v.slug, description:v.description||'', scope:v.scope };
      this.slugTouched=true; this.slugAuto=false; this.showVarModal=true; this.selectedVar=v;
    },
    closeVarModal(){ this.showVarModal=false },
    handleNameInput(){
      if(this.editingVar) return;
      if(!this.slugTouched){
        const generated = this.generateSlug(this.varForm.name);
        this.varForm.slug = generated;
      }
    },
    handleSlugInput(){
      this.slugTouched = true; this.slugAuto = false;
      this.varForm.slug = this.sanitizeSlug(this.varForm.slug);
      this.queueValidateSlug();
    },
    queueValidateSlug(){
      clearTimeout(this._slugTimer);
      this._slugTimer = setTimeout(()=>{ this.validateSlugRemote(); }, 300);
    },
    async validateSlugRemote(){
      if(this.editingVar) return;
      const slug = this.varForm.slug;
      if(!slug) { this.slugAvailable=false; return; }
      try {
        const res = await fetch(`/api/variables/validate_slug?slug=${encodeURIComponent(slug)}`);
        if(!res.ok) return;
        const data = await res.json();
        this.slugAvailable = data.available;
        this.slugSuggestion = data.suggested;
      } catch(e){ /* silent */ }
    },
    applySuggestedSlug(){
      if(this.slugSuggestion && !this.slugAvailable){
        this.varForm.slug = this.slugSuggestion;
        this.slugTouched = true;
        this.slugAvailable = true;
  toast.success('Applied suggested slug')
      }
    },
    sanitizeSlug(raw){
      if(!raw) return '';
      let s = raw.toLowerCase();
      s = s.replace(/\s+/g,'_');
      s = s.replace(/[^a-z0-9_-]/g,'');
      s = s.replace(/^-+/, '');
      return s;
    },
    generateSlug(name){
      if(!name) return '';
      let base = name.trim().toLowerCase();
      base = base.replace(/[^a-z0-9]+/g,'_');
      base = base.replace(/_+/g,'_').replace(/^_+|_+$/g,'');
      base = base.replace(/^[^a-z]+/, '');
      return base;
    },
    async saveVar(){
      if(this.isSaving) return;
      // Validate slug format
      if(!this.slugValid){
        // attempt auto-generate if empty
        if(!this.varForm.slug && this.varForm.name){
          this.varForm.slug = this.generateSlug(this.varForm.name);
        }
        if(!this.slugValid) return; // still invalid
      }
      // Remote availability check if not already confirmed
      if(!this.slugAvailable){
        await this.validateSlugRemote();
        if(!this.slugAvailable) return; // wait for user to apply suggestion
      }
      this.isSaving = true;
      try {
        const payload = { name:this.varForm.name.trim(), slug:this.varForm.slug.trim(), description:this.varForm.description.trim(), scope:this.varForm.scope }
        const method = this.editingVar ? 'PUT' : 'POST'
        const url = this.editingVar ? `/api/variables/${this.selectedVar.id}` : '/api/variables'
        const res = await fetch(url,{ method, headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) })
        if(!res.ok) {
          // If server returns slug collision simultaneously, refresh availability
            await this.validateSlugRemote();
            toast.error('Failed to save variable');
            throw new Error('Save failed');
        }
        const data = await res.json();
        await this.refresh();
        toast.success(this.editingVar ? 'Variable updated' : `Variable created (${data.slug})`);
        this.showVarModal=false
      } catch(e){ console.error(e); }
      finally { this.isSaving = false }
    },
    async addValue(){
      if(!this.selectedVar || !this.newValue.trim()) return
      try {
        const res = await fetch(`/api/variables/${this.selectedVar.id}/values`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ value:this.newValue.trim(), is_default:this.newValueDefault }) })
        if(!res.ok) throw new Error('Add failed')
        this.newValue=''; this.newValueDefault=false; await this.refresh();
        toast.success('Value added');
      } catch(e){ console.error(e); toast.error('Failed to add value'); }
    },
    async deleteValue(val){
      if(!confirm('Delete this value?')) return
      try {
        const res = await fetch(`/api/variables/values/${val.id}`, { method:'DELETE' })
        if(!res.ok) throw new Error('Delete failed')
        await this.refresh();
        toast.success('Value deleted');
      } catch(e){ console.error(e); toast.error('Failed to delete value'); }
    },
    async makeDefault(val){
      if(!this.selectedVar) return
      try {
        const res = await fetch(`/api/variables/values/${val.id}`, { method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ is_default:true }) })
        if(!res.ok) throw new Error('Default update failed')
        await this.refresh();
        toast.success('Default updated');
      } catch(e){ console.error(e); toast.error('Failed to update default'); }
    }
  }
}
</script>
<style scoped>
.admin-variables { padding:1.25rem; }
.subtitle { color:#64748b; margin-bottom:1rem; }
.actions-bar { display:flex; gap:.5rem; margin-bottom:1rem; }
.actions-bar .btn { min-width:120px; }
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
.add-value-form .btn { min-width:70px; }
.add-value-form input[type=text]{ flex:1; }
.var-modal { max-width:480px; width:100%; padding:1.25rem 1.5rem; }
.var-form { display:flex; flex-direction:column; gap:.6rem; }
.var-form input, .var-form textarea, .var-form select { width:100%; }
.modal-actions { display:flex; justify-content:flex-end; gap:.5rem; margin-top:.5rem; }
.modal-actions .btn { min-width:90px; }
.form-help { font-size:.7rem; color:#64748b; line-height:1.2; margin-top:-.35rem; margin-bottom:.25rem; }
.form-help code { background:#f1f5f9; padding:0 .25rem; border-radius:4px; }
.form-help .rules { margin:.15rem 0 0 0; }
.error-text { color:#dc2626; font-weight:500; }
input.invalid { border:1px solid #dc2626; }
.badge.auto-hint { background:#e2e8f0; color:#475569; font-size:.55rem; padding:.15rem .35rem; border-radius:4px; margin-left:.25rem; text-transform:uppercase; letter-spacing:.5px; }
.error-banner { background:#fef2f2; color:#b91c1c; padding:.5rem .75rem; border:1px solid #fecaca; border-radius:6px; font-size:.7rem; margin-bottom:.75rem; }
</style>

<!-- (removed secondary script block; merged into primary export) -->
