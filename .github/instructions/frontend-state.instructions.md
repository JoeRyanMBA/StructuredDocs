---
description: "Use when managing Vue application state, composables, or complex client-side logic in StructuredDocs frontend. Covers composable patterns, reactive state management, API integration, and component communication."
name: "StructuredDocs Frontend State Management"
applyTo: "frontend/src/composables/**,frontend/src/pages/**,frontend/src/views/**"
---
# Frontend State Management Patterns

StructuredDocs frontend uses Vue 3 Composition API with composables for reusable stateful logic.

## Composable Pattern

Composables live in `frontend/src/composables/` and encapsulate related state and functions.

```javascript
// frontend/src/composables/useCollections.js
import { ref, reactive, computed } from 'vue'
import { getCollections, createCollection } from '@/api/collections'

export function useCollections(projectId) {
  const collections = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const sortedCollections = computed(() => 
    collections.value.sort((a, b) => a.name.localeCompare(b.name))
  )
  
  async function fetchCollections() {
    loading.value = true
    try {
      collections.value = await getCollections(projectId)
      error.value = null
    } catch (err) {
      error.value = err.message
      collections.value = []
    } finally {
      loading.value = false
    }
  }
  
  async function addCollection(name, description) {
    try {
      const newCollection = await createCollection(projectId, { name, description })
      collections.value.push(newCollection)
      return newCollection
    } catch (err) {
      error.value = err.message
      throw err
    }
  }
  
  return {
    collections,
    sortedCollections,
    loading,
    error,
    fetchCollections,
    addCollection,
  }
}
```

## Using Composables in Components

```vue
<template>
  <div>
    <button @click="fetchCollections" :disabled="loading">Refresh</button>
    <div v-if="loading">Loading...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <ul>
      <li v-for="coll in sortedCollections" :key="coll.id">
        {{ coll.name }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { useCollections } from '@/composables/useCollections'

const props = defineProps({
  projectId: Number,
})

const { collections, sortedCollections, loading, error, fetchCollections } = 
  useCollections(props.projectId)

// Fetch on mount
fetchCollections()
</script>
```

## API Layer Boundary

Keep network calls in `frontend/src/api/` modules:

```javascript
// frontend/src/api/collections.js
import { client } from './base'

export async function getCollections(projectId) {
  const { data } = await client.get(`/api/collections?project_id=${projectId}`)
  return data
}

export async function createCollection(projectId, payload) {
  const { data } = await client.post(`/api/collections`, {
    project_id: projectId,
    ...payload,
  })
  return data
}
```

**Rules:**
- API modules only handle HTTP calls
- Return raw response data
- Let composables handle state and logic
- Use consistent naming: `getX`, `createX`, `updateX`, `deleteX`

## Reactive State Patterns

### Simple Value
```javascript
const count = ref(0)
count.value++  // Must use .value in script
```

### Object State
```javascript
const form = reactive({
  name: '',
  email: '',
  submitted: false,
})

form.name = 'John'  // Direct assignment, no .value needed
```

### Computed Properties
```javascript
const fullName = computed(() => 
  `${form.firstName} ${form.lastName}`
)
```

### Watchers for Side Effects
```javascript
import { watch } from 'vue'

watch(() => props.projectId, async (newId) => {
  // Fetch when projectId changes
  await fetchCollections()
})
```

## Error Handling Pattern

```javascript
const error = ref(null)

async function performAction() {
  try {
    error.value = null
    await apiCall()
  } catch (err) {
    error.value = err.message
    current_app.logger?.error(err)  // Log to backend if available
  }
}
```

## Loading States

```javascript
const loading = ref(false)

async function fetchData() {
  loading.value = true
  try {
    data.value = await getData()
  } finally {
    loading.value = false  // Always clear, even on error
  }
}
```

## Component Communication

**Parent → Child:** Props
```vue
<ChildComponent :items="collections" :loading="loading" />
```

**Child → Parent:** Emits
```vue
<script setup>
const emit = defineEmits(['item-selected'])

function selectItem(item) {
  emit('item-selected', item)
}
</script>

<!-- Parent listens -->
<ChildComponent @item-selected="handleSelection" />
```

**Sibling/Distant:** Composable (shared state)
```javascript
// useSharedState.js
const selectedItem = ref(null)

// Multiple components can import and use
```

## Form Handling Pattern

```javascript
import { reactive, ref } from 'vue'

const form = reactive({
  name: '',
  email: '',
  message: '',
})

const submitted = ref(false)
const error = ref(null)

async function handleSubmit() {
  try {
    error.value = null
    await submitForm(form)
    submitted.value = true
    // Reset or redirect
  } catch (err) {
    error.value = err.message
  }
}
```

## Common Patterns

### Fetch on Component Mount
```javascript
import { onMounted } from 'vue'

onMounted(() => {
  fetchData()
})
```

### Fetch on Route Change
```javascript
import { useRoute } from 'vue-router'
import { watch } from 'vue'

const route = useRoute()

watch(() => route.params.id, () => {
  fetchData()
})
```

### Debounce Search Input
```javascript
import { ref } from 'vue'
import { debounce } from 'lodash'  // or use custom debounce

const query = ref('')
const results = ref([])

const search = debounce(async () => {
  results.value = await searchAPI(query.value)
}, 300)

watch(query, search)
```

### Modal/Dialog Pattern
```javascript
const showModal = ref(false)

function openModal() {
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}
```

## File Organization

```
frontend/src/
├── api/
│   ├── base.js           # Axios setup
│   ├── collections.js
│   ├── topics.js
│   └── ...
├── composables/
│   ├── useCollections.js
│   ├── useTopics.js
│   ├── useAuth.js
│   └── ...
├── components/
│   ├── CollectionCard.vue
│   ├── TopicEditor.vue
│   └── ...
├── pages/ (or views/)
│   ├── Collections.vue
│   ├── Topics.vue
│   └── ...
└── App.vue
```

## Best Practices

1. **Keep composables focused** — one responsibility per composable
2. **Expose only what's needed** — return minimal interface
3. **Document expected props** — add JSDoc comments
4. **Handle errors gracefully** — always have error state
5. **Clean up watchers** — composables return cleanup functions automatically
6. **Use TypeScript** (if available) — add type hints to composables
7. **Test composables in isolation** — they're just functions

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Stale data after update | Not refetching after API change | Add `watch` to trigger fetch on prop change |
| Memory leak on unmount | Watcher not cleaned up | Vue 3 cleans up automatically; check for manual listeners |
| Infinite loop | Watcher triggers itself | Avoid mutating watched value in watcher |
| Component not updating | Reactivity not set up (using plain object) | Use `ref()` for primitives, `reactive()` for objects |

## Files to Check

- `frontend/src/composables/` — examples of composable patterns
- `frontend/src/api/` — API module patterns
- `frontend/src/pages/` — component usage examples
- `frontend/src/components/` — reusable UI components

**Read:** [.github/instructions/frontend.instructions.md](./frontend.instructions.md) for general frontend patterns
