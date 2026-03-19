<template>
  <div class="icon-catalog">
    <div class="dashboard-header">
      <h1>Icon Catalog</h1>
      <p class="subtitle">Reference for the active icon systems used across StructuredDocs and what each icon means in context.</p>
    </div>

    <div class="section-card">
      <div class="catalog-summary">
        <div class="summary-card">
          <div class="summary-number">{{ totalIconCount }}</div>
          <div class="summary-label">Active icons cataloged</div>
        </div>
        <div class="summary-card">
          <div class="summary-number">{{ bootstrapIcons.length }}</div>
          <div class="summary-label">Bootstrap Icons</div>
        </div>
        <div class="summary-card">
          <div class="summary-number">{{ navigationEmojiIcons.length + dashboardEmojiIcons.length }}</div>
          <div class="summary-label">Emoji icons</div>
        </div>
        <div class="summary-card">
          <div class="summary-number">{{ customIcons.length }}</div>
          <div class="summary-label">Custom icon components</div>
        </div>
      </div>

      <div class="catalog-controls">
        <input
          v-model="filter"
          class="filter-input"
          placeholder="Filter by icon name, meaning, token, or file..."
        />
      </div>
    </div>

    <div
      v-for="section in filteredSections"
      :key="section.key"
      class="section-card mt-8"
    >
      <div class="section-heading">
        <div>
          <h2>{{ section.title }}</h2>
          <p class="section-subtitle">{{ section.description }}</p>
        </div>
        <span class="section-count">{{ section.rows.length }}</span>
      </div>

      <div class="table-wrapper">
        <table class="catalog-table">
          <thead>
            <tr>
              <th style="width: 120px">Preview</th>
              <th style="width: 220px">Icon</th>
              <th>Meaning</th>
              <th style="width: 260px">Where used</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in section.rows" :key="row.key">
              <td>
                <div class="icon-preview" :class="`icon-preview--${section.previewType}`">
                  <IconPlus
                    v-if="section.previewType === 'custom' && row.token === 'IconPlus'"
                    size="22"
                  />
                  <i
                    v-else-if="section.previewType === 'bootstrap'"
                    :class="row.token"
                    aria-hidden="true"
                  />
                  <span
                    v-else
                    class="emoji-preview"
                    aria-hidden="true"
                  >
                    {{ row.token }}
                  </span>
                </div>
              </td>
              <td>
                <div class="icon-name">{{ row.label }}</div>
                <code>{{ row.token }}</code>
              </td>
              <td>{{ row.meaning }}</td>
              <td>
                <ul class="used-in-list">
                  <li v-for="file in row.usedIn" :key="file">{{ file }}</li>
                </ul>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="filteredSections.length === 0" class="section-card mt-8">
      <p class="empty-state">No icons match the current filter.</p>
    </div>

    <div class="section-card mt-8">
      <h2>Notes</h2>
      <ul class="notes-list">
        <li v-for="note in iconCatalogNotes" :key="note">{{ note }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import IconPlus from '@/components/icons/IconPlus.vue'
import {
  bootstrapIcons,
  navigationEmojiIcons,
  dashboardEmojiIcons,
  customIcons,
  iconCatalogNotes
} from '@/data/iconCatalog'

export default {
  name: 'IconCatalog',
  components: { IconPlus },
  data() {
    return {
      filter: '',
      bootstrapIcons,
      navigationEmojiIcons,
      dashboardEmojiIcons,
      customIcons,
      iconCatalogNotes
    }
  },
  computed: {
    totalIconCount() {
      return this.bootstrapIcons.length + this.navigationEmojiIcons.length + this.dashboardEmojiIcons.length + this.customIcons.length
    },
    filteredSections() {
      const q = (this.filter || '').trim().toLowerCase()
      const matches = row => {
        if (!q) return true
        return (
          row.label.toLowerCase().includes(q) ||
          row.token.toLowerCase().includes(q) ||
          row.meaning.toLowerCase().includes(q) ||
          row.usedIn.some(file => file.toLowerCase().includes(q))
        )
      }

      return [
        {
          key: 'bootstrap',
          title: 'Bootstrap Icons',
          description: 'Primary icon library for buttons, actions, status states, and detailed workflows.',
          previewType: 'bootstrap',
          rows: this.bootstrapIcons.filter(matches)
        },
        {
          key: 'navigation-emoji',
          title: 'Navigation Emoji Icons',
          description: 'High-level sidebar and navigation icons used to identify major areas of the app.',
          previewType: 'emoji',
          rows: this.navigationEmojiIcons.filter(matches)
        },
        {
          key: 'dashboard-emoji',
          title: 'Dashboard and Action Emoji Icons',
          description: 'Emoji used in metric cards and quick-action cards on dashboard-style pages.',
          previewType: 'emoji',
          rows: this.dashboardEmojiIcons.filter(matches)
        },
        {
          key: 'custom',
          title: 'Custom Icon Components',
          description: 'Project-specific icon components used where Bootstrap Icons are not enough.',
          previewType: 'custom',
          rows: this.customIcons.filter(matches)
        }
      ].filter(section => section.rows.length > 0)
    }
  }
}
</script>

<style scoped>
.catalog-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.summary-card {
  border: 1px solid var(--border-light-gray);
  border-radius: 12px;
  padding: 1rem;
  background: var(--bg-light-mist-gray);
}

.summary-number {
  font-size: 1.9rem;
  font-weight: 700;
  color: var(--primary-deep-teal);
  line-height: 1;
}

.summary-label {
  margin-top: 0.35rem;
  color: var(--text-secondary-cool-gray);
  font-size: 0.95rem;
}

.catalog-controls {
  display: flex;
  justify-content: flex-end;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-heading h2 {
  margin: 0;
}

.section-subtitle {
  margin: 0.35rem 0 0;
  color: var(--text-secondary-cool-gray);
}

.section-count {
  min-width: 3rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: var(--bg-light-mist-gray);
  color: var(--primary-deep-teal);
  font-weight: 600;
  text-align: center;
}

.table-wrapper {
  overflow-x: auto;
}

.catalog-table {
  width: 100%;
  border-collapse: collapse;
}

.catalog-table th,
.catalog-table td {
  border: 1px solid var(--border-light-gray);
  padding: 0.75rem;
  vertical-align: top;
}

.catalog-table thead th {
  background: var(--bg-light-mist-gray);
}

.icon-preview {
  width: 52px;
  height: 52px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--bg-light-mist-gray);
  color: var(--primary-deep-teal);
  font-size: 1.35rem;
}

.icon-preview--emoji {
  font-size: 1.5rem;
}

.icon-name {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.emoji-preview {
  line-height: 1;
}

.used-in-list,
.notes-list {
  margin: 0;
  padding-left: 1rem;
}

.empty-state {
  margin: 0;
  color: var(--text-secondary-cool-gray);
}

code {
  white-space: nowrap;
}

@media (max-width: 768px) {
  .section-heading {
    flex-direction: column;
  }

  .catalog-controls {
    justify-content: stretch;
  }

  .catalog-controls .filter-input {
    width: 100%;
  }
}
</style>
