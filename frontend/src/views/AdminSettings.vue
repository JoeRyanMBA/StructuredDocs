<template>
  <section class="admin-settings-page">
    <h1>Export Branding Settings</h1>
    <p class="subtitle">Configure logo and styling defaults used by PDF and HTML publication exports.</p>

    <div v-if="loading" class="status loading">Loading settings...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <div v-else class="settings-card">
      <div class="settings-grid">
        <label class="setting-row" v-for="key in orderedKeys" :key="key">
          <div class="setting-label">
            <div class="label-title">{{ labelFor(key) }}</div>
            <div class="label-help">{{ descriptionFor(key) }}</div>
          </div>
          <input
            v-model="edits[key]"
            class="setting-input"
            type="text"
            :placeholder="placeholderFor(key)"
          />
        </label>
      </div>

      <div class="preview-card" :style="previewCssVars">
        <div class="preview-header">
          <div class="preview-logo-wrap">
            <img
              v-if="logoPreviewUrl && !logoPreviewErrored"
              :src="logoPreviewUrl"
              class="preview-logo"
              alt="Brand logo preview"
              @error="logoPreviewErrored = true"
            />
            <div v-else class="preview-logo-fallback">Logo</div>
          </div>
          <div>
            <div class="preview-title">{{ previewBrandName }}</div>
            <div class="preview-subtitle">Export branding preview</div>
          </div>
        </div>
        <div class="preview-body">
          <div class="preview-chip">Primary color</div>
          <div class="preview-chip accent">Accent color</div>
        </div>
        <div class="preview-note" v-if="logoPreviewUrl && logoPreviewErrored">
          HTML logo could not be previewed in-browser from this value. Export generation will still apply it server-side.
        </div>
      </div>

      <div class="export-test-card">
        <div class="export-test-title">Quick Export Test</div>
        <p class="export-test-subtitle">Use an existing publication ID to verify PDF and HTML output with current branding settings.</p>
        <div class="export-test-controls">
          <input
            v-model="publicationSearch"
            class="setting-input"
            type="text"
            placeholder="Filter publications by title..."
          />
          <select v-model="selectedPublicationId" class="setting-input" :disabled="loadingPublications">
            <option value="">Select publication...</option>
            <option v-for="pub in filteredPublications" :key="pub.id" :value="String(pub.id)">
              {{ pub.title || `Publication ${pub.id}` }} (ID {{ pub.id }})
            </option>
          </select>
          <button class="btn btn-outline-primary" :disabled="!canRunExportTest || exporting.pdf" @click="testPdfExport">
            <span v-if="exporting.pdf">Generating PDF...</span>
            <span v-else>Test PDF Export</span>
          </button>
          <button class="btn btn-outline-primary" :disabled="!canRunExportTest || exporting.preview" @click="testHtmlPreview">
            <span v-if="exporting.preview">Opening Preview...</span>
            <span v-else>Test HTML Preview</span>
          </button>
          <button class="btn btn-outline-primary" :disabled="!canRunExportTest || exporting.downloadHtml" @click="testHtmlDownload">
            <span v-if="exporting.downloadHtml">Downloading...</span>
            <span v-else>Download HTML Export</span>
          </button>
        </div>
        <div class="export-test-meta-row">
          <button class="btn btn-sm btn-outline-secondary" :disabled="loadingPublications" @click="loadPublications">
            <span v-if="loadingPublications">Refreshing...</span>
            <span v-else>Refresh Publications</span>
          </button>
          <span v-if="publicationsError" class="export-test-meta error-text">{{ publicationsError }}</span>
          <span v-else class="export-test-meta">{{ filteredPublications.length }} shown / {{ publications.length }} total</span>
        </div>
        <div v-if="exportMessage" class="status success">{{ exportMessage }}</div>
        <div v-if="exportError" class="status error">{{ exportError }}</div>
      </div>

      <div class="actions-row">
        <button class="btn btn-outline-danger" :disabled="saving" @click="resetBrandingDefaults">Reset Branding Defaults</button>
        <button class="btn btn-secondary" :disabled="saving" @click="reload">Discard Changes</button>
        <button class="btn btn-primary" :disabled="saving" @click="save">
          <span v-if="saving">Saving...</span>
          <span v-else>Save Settings</span>
        </button>
      </div>

      <div v-if="saveSuccess" class="status success">Settings saved successfully.</div>
      <div v-if="saveError" class="status error">{{ saveError }}</div>
    </div>
  </section>
</template>

<script>
import { getAdminSettings, updateAdminSettings } from '@/api/adminSettings'
import { toFriendlyAuthError } from '@/api/base'
import { downloadPublicationPdf, downloadMobileKnowledgeBase, previewMobileKnowledgeBase, getPublications } from '@/api/publications'

const BRANDING_KEYS = [
  'export_brand_name',
  'export_pdf_title_logo',
  'export_pdf_footer_logo',
  'export_pdf_cover_background',
  'export_html_logo',
  'export_html_primary_color',
  'export_html_accent_color',
]

const LABELS = {
  export_brand_name: 'Brand Name',
  export_pdf_title_logo: 'PDF Title Logo',
  export_pdf_footer_logo: 'PDF Footer Logo',
  export_pdf_cover_background: 'PDF Cover Background',
  export_html_logo: 'HTML Header Logo',
  export_html_primary_color: 'HTML Primary Color',
  export_html_accent_color: 'HTML Accent Color',
}

const PLACEHOLDERS = {
  export_brand_name: 'StructuredDocs',
  export_pdf_title_logo: 'Title_Page_Logo.png',
  export_pdf_footer_logo: 'Footer_Logo.png',
  export_pdf_cover_background: 'SC Cover Background.png',
  export_html_logo: 'https://example.com/logo.png or company_logo.png',
  export_html_primary_color: '#005a9c',
  export_html_accent_color: '#112E51',
}

const DEFAULT_VALUES = {
  export_brand_name: 'StructuredDocs',
  export_pdf_title_logo: 'Title_Page_Logo.png',
  export_pdf_footer_logo: 'Footer_Logo.png',
  export_pdf_cover_background: 'SC Cover Background.png',
  export_html_logo: '',
  export_html_primary_color: '#005a9c',
  export_html_accent_color: '#112E51',
}

export default {
  name: 'AdminSettings',
  data() {
    return {
      allSettings: [],
      edits: {},
      loading: false,
      saving: false,
      error: null,
      saveError: null,
      saveSuccess: false,
      logoPreviewErrored: false,
      publicationSearch: '',
      selectedPublicationId: '',
      publications: [],
      loadingPublications: false,
      publicationsError: '',
      exporting: {
        pdf: false,
        preview: false,
        downloadHtml: false,
      },
      exportMessage: '',
      exportError: '',
    }
  },
  computed: {
    orderedKeys() {
      return BRANDING_KEYS
    },
    settingsByKey() {
      return Object.fromEntries(this.allSettings.map(s => [s.key, s]))
    },
    previewBrandName() {
      return (this.edits.export_brand_name || DEFAULT_VALUES.export_brand_name || '').trim() || DEFAULT_VALUES.export_brand_name
    },
    previewPrimaryColor() {
      return this.normalizeHexColor(this.edits.export_html_primary_color, DEFAULT_VALUES.export_html_primary_color)
    },
    previewAccentColor() {
      return this.normalizeHexColor(this.edits.export_html_accent_color, DEFAULT_VALUES.export_html_accent_color)
    },
    previewCssVars() {
      return {
        '--preview-primary': this.previewPrimaryColor,
        '--preview-accent': this.previewAccentColor,
      }
    },
    logoPreviewUrl() {
      const raw = (this.edits.export_html_logo || '').trim()
      if (!raw) return ''
      if (raw.startsWith('http://') || raw.startsWith('https://') || raw.startsWith('data:') || raw.startsWith('/')) {
        return raw
      }
      if (raw.startsWith('backend/static/')) {
        return `/${raw.replace(/^backend\//, '')}`
      }
      const basename = raw.split('/').pop()
      return basename ? `/static/backgrounds/${basename}` : ''
    },
    normalizedPublicationId() {
      const parsed = Number.parseInt(this.selectedPublicationId, 10)
      return Number.isFinite(parsed) && parsed > 0 ? parsed : null
    },
    canRunExportTest() {
      return this.normalizedPublicationId !== null
    },
    filteredPublications() {
      const term = (this.publicationSearch || '').trim().toLowerCase()
      if (!term) return this.publications
      return this.publications.filter(pub => {
        const title = (pub?.title || '').toLowerCase()
        const idText = String(pub?.id ?? '').toLowerCase()
        return title.includes(term) || idText.includes(term)
      })
    },
  },
  watch: {
    logoPreviewUrl() {
      this.logoPreviewErrored = false
    },
  },
  mounted() {
    this.reload()
    this.loadPublications()
  },
  methods: {
    normalizeHexColor(value, fallback) {
      const trimmed = (value || '').trim()
      const valid = /^#?[0-9a-fA-F]{6}$/.test(trimmed)
      if (!valid) return fallback
      return trimmed.startsWith('#') ? trimmed : `#${trimmed}`
    },
    labelFor(key) {
      return LABELS[key] || key
    },
    descriptionFor(key) {
      return this.settingsByKey[key]?.description || ''
    },
    placeholderFor(key) {
      return PLACEHOLDERS[key] || ''
    },
    async reload() {
      this.loading = true
      this.error = null
      this.saveError = null
      this.saveSuccess = false
      try {
        const settings = await getAdminSettings()
        this.allSettings = settings
        this.edits = Object.fromEntries(settings.map(s => [s.key, s.value]))
        this.logoPreviewErrored = false
      } catch (err) {
        this.error = toFriendlyAuthError(err, 'Failed to load admin settings.')
      } finally {
        this.loading = false
      }
    },
    async loadPublications() {
      this.loadingPublications = true
      this.publicationsError = ''
      try {
        const rows = await getPublications()
        this.publications = Array.isArray(rows) ? rows : []
        if (this.selectedPublicationId && !this.publications.some(p => String(p.id) === String(this.selectedPublicationId))) {
          this.selectedPublicationId = ''
        }
      } catch (err) {
        this.publicationsError = toFriendlyAuthError(err, 'Could not load publications for export testing.')
      } finally {
        this.loadingPublications = false
      }
    },
    buildPayload(valuesByKey) {
      return this.orderedKeys.map(key => ({
        key,
        value: valuesByKey[key] ?? '',
      }))
    },
    async persistPayload(payload, successMessage) {
      const result = await updateAdminSettings(payload)
      if (Array.isArray(result?.errors) && result.errors.length) {
        this.saveError = result.errors.join('; ')
        return false
      }
      this.saveSuccess = true
      if (successMessage) {
        this.saveError = null
      }
      await this.reload()
      return true
    },
    async save() {
      this.saving = true
      this.saveError = null
      this.saveSuccess = false
      try {
        const payload = this.buildPayload(this.edits)
        await this.persistPayload(payload)
      } catch (err) {
        this.saveError = toFriendlyAuthError(err, 'Failed to save admin settings.')
      } finally {
        this.saving = false
      }
    },
    async withExportAction(key, action) {
      this.exportError = ''
      this.exportMessage = ''
      this.exporting = { ...this.exporting, [key]: true }
      try {
        await action()
      } catch (err) {
        this.exportError = toFriendlyAuthError(err, 'Export test failed.')
      } finally {
        this.exporting = { ...this.exporting, [key]: false }
      }
    },
    async testPdfExport() {
      const pubId = this.normalizedPublicationId
      if (!pubId) {
        this.exportError = 'Enter a valid publication ID first.'
        return
      }
      await this.withExportAction('pdf', async () => {
        await downloadPublicationPdf(pubId, `publication_${pubId}_brand_test.pdf`)
        this.exportMessage = 'PDF export downloaded. Check logo, footer branding, and cover styling.'
      })
    },
    async testHtmlPreview() {
      const pubId = this.normalizedPublicationId
      if (!pubId) {
        this.exportError = 'Enter a valid publication ID first.'
        return
      }
      await this.withExportAction('preview', async () => {
        await previewMobileKnowledgeBase(pubId)
        this.exportMessage = 'HTML preview opened in a new tab/window.'
      })
    },
    async testHtmlDownload() {
      const pubId = this.normalizedPublicationId
      if (!pubId) {
        this.exportError = 'Enter a valid publication ID first.'
        return
      }
      await this.withExportAction('downloadHtml', async () => {
        await downloadMobileKnowledgeBase(pubId, `publication_${pubId}_mobile_brand_test.html`)
        this.exportMessage = 'HTML export downloaded for offline verification.'
      })
    },
    async resetBrandingDefaults() {
      const approved = window.confirm('Reset all export branding settings to system defaults? This will immediately update PDF and HTML export defaults.')
      if (!approved) return

      this.saving = true
      this.saveError = null
      this.saveSuccess = false
      try {
        const payload = this.buildPayload(DEFAULT_VALUES)
        const ok = await this.persistPayload(payload, 'Branding settings reset to defaults.')
        if (ok) {
          this.edits = { ...this.edits, ...DEFAULT_VALUES }
          this.logoPreviewErrored = false
        }
      } catch (err) {
        this.saveError = toFriendlyAuthError(err, 'Failed to reset branding defaults.')
      } finally {
        this.saving = false
      }
    },
  },
};
</script>

<style scoped>
.admin-settings-page {
  max-width: 980px;
  margin: 0 auto;
  padding: 24px;
}

.subtitle {
  color: #6b7280;
  margin-bottom: 16px;
}

.settings-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #ffffff;
  padding: 18px;
}

.settings-grid {
  display: grid;
  gap: 14px;
}

.setting-row {
  display: grid;
  grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.label-title {
  font-weight: 600;
}

.label-help {
  color: #6b7280;
  font-size: 0.84rem;
  margin-top: 2px;
}

.setting-input {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.95rem;
  padding: 10px 12px;
}

.actions-row {
  margin-top: 18px;
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.export-test-card {
  margin-top: 18px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 14px;
  background: #fafafa;
}

.export-test-title {
  font-size: 0.96rem;
  font-weight: 700;
}

.export-test-subtitle {
  margin: 6px 0 0;
  color: #6b7280;
  font-size: 0.83rem;
}

.export-test-controls {
  margin-top: 12px;
  display: grid;
  grid-template-columns: minmax(0, 220px) minmax(0, 260px) repeat(3, minmax(0, 1fr));
  gap: 8px;
  align-items: center;
}

.export-test-meta-row {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.export-test-meta {
  font-size: 0.8rem;
  color: #6b7280;
}

.error-text {
  color: #b91c1c;
}

.preview-card {
  margin-top: 18px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: var(--preview-primary);
  color: #ffffff;
}

.preview-logo-wrap {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.18);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.preview-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-logo-fallback {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.preview-title {
  font-weight: 700;
  font-size: 1.06rem;
}

.preview-subtitle {
  font-size: 0.82rem;
  opacity: 0.9;
}

.preview-body {
  display: flex;
  gap: 10px;
  padding: 12px 14px;
  background: #f8fafc;
}

.preview-chip {
  border: 1px solid var(--preview-primary);
  color: var(--preview-primary);
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 0.78rem;
  font-weight: 600;
}

.preview-chip.accent {
  border-color: var(--preview-accent);
  color: var(--preview-accent);
}

.preview-note {
  padding: 10px 14px;
  border-top: 1px solid #e5e7eb;
  font-size: 0.8rem;
  color: #6b7280;
}

.status {
  margin-top: 14px;
  border-radius: 8px;
  padding: 10px 12px;
}

.loading {
  background: #eff6ff;
  color: #1d4ed8;
}

.success {
  background: #ecfdf5;
  color: #047857;
}

.error {
  background: #fef2f2;
  color: #b91c1c;
}

@media (max-width: 860px) {
  .setting-row {
    grid-template-columns: 1fr;
  }

  .export-test-controls {
    grid-template-columns: 1fr;
  }
}
</style>
