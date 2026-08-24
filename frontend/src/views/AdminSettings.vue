<template>
  <section class="admin-settings-page">
    <h1>Export Branding Settings</h1>
    <p class="subtitle">Configure logo and styling defaults used by PDF and HTML publication exports.</p>

    <div v-if="loading" class="status loading">Loading settings...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <div v-else class="settings-card">
      <div class="settings-grid">
        <div class="setting-row" v-for="key in orderedKeys" :key="key">
          <div class="setting-label">
            <div class="label-title">{{ labelFor(key) }}</div>
            <div class="label-help">{{ descriptionFor(key) }}</div>
          </div>
          <div class="setting-input-stack">
            <input
              v-model="edits[key]"
              class="setting-input"
              type="text"
              :placeholder="placeholderFor(key)"
              :disabled="isCoverBackgroundKey(key) && isNoCoverBackgroundEnabled()"
            />
            <label v-if="isCoverBackgroundKey(key)" class="cover-toggle">
              <input
                type="checkbox"
                :checked="isNoCoverBackgroundEnabled()"
                @change="toggleNoCoverBackground($event.target.checked)"
              />
              <span>No cover background (blank cover)</span>
            </label>
            <div v-if="isImageSetting(key)" class="image-controls">
              <select
                class="setting-input"
                :disabled="isCoverBackgroundKey(key) && isNoCoverBackgroundEnabled()"
                @change="applyAssetSelection(key, $event.target.value)"
              >
                <option value="">Select uploaded image...</option>
                <option v-for="asset in visibleBrandingAssetsForKey(key)" :key="asset.name" :value="asset.name">
                  {{ asset.name }}
                </option>
              </select>
              <label class="btn btn-secondary btn-sm upload-btn">
                <input
                  type="file"
                  class="upload-input"
                  accept="image/*"
                  :disabled="isUploadingAsset(key) || (isCoverBackgroundKey(key) && isNoCoverBackgroundEnabled())"
                  @change="uploadAssetForKey(key, $event)"
                />
                <span v-if="isUploadingAsset(key)">Uploading...</span>
                <span v-else>Upload Image</span>
              </label>
              <a
                v-if="assetUrlForSetting(key)"
                class="btn btn-secondary btn-sm"
                :href="assetUrlForSetting(key)"
                target="_blank"
                rel="noopener noreferrer"
              >
                Preview
              </a>
            </div>
            <div v-if="isImageSetting(key) && selectedAssetMissingForKey(key)" class="asset-empty-note error-text">
              Selected image file was not found in uploaded assets. Re-upload it or choose another image.
            </div>
            <div v-if="key.startsWith('export_pdf_') && key !== 'export_pdf_cover_background'" class="asset-empty-note">
              PDF title/footer logos should use JPG or PNG files for reliable rendering. SVG is best reserved for the HTML logo.
            </div>
            <div v-if="isImageSetting(key)" class="asset-filter-row">
              <label class="asset-filter-toggle">
                <input
                  type="checkbox"
                  :checked="isUnusedOnlyEnabled(key)"
                  :disabled="isCoverBackgroundKey(key) && isNoCoverBackgroundEnabled()"
                  @change="setUnusedOnly(key, $event.target.checked)"
                />
                <span>Show only unused images</span>
              </label>
              <span class="asset-filter-meta">{{ visibleBrandingAssetsForKey(key).length }} shown / {{ brandingAssets.length }} total</span>
            </div>
            <div v-if="isImageSetting(key) && (!isCoverBackgroundKey(key) || !isNoCoverBackgroundEnabled()) && visibleBrandingAssetsForKey(key).length" class="asset-thumb-grid">
              <div
                v-for="asset in visibleBrandingAssetsForKey(key)"
                :key="`${key}-${asset.name}`"
                class="asset-thumb-btn"
                :class="{ active: edits[key] === asset.name }"
              >
                <button
                  type="button"
                  class="asset-select-btn"
                  :title="asset.name"
                  @click="applyAssetSelection(key, asset.name)"
                >
                  <img
                    v-if="assetPreviewUrl(asset.name)"
                    :src="assetPreviewUrl(asset.name)"
                    :alt="asset.name"
                    class="asset-thumb-image"
                    @error="handleAssetPreviewError(asset.name)"
                  />
                  <span class="asset-thumb-name">{{ asset.name }}</span>
                  <div v-if="assetUsageSummary(asset)" class="asset-used-by">{{ assetUsageSummary(asset) }}</div>
                </button>
                <button
                  type="button"
                  class="btn btn-secondary btn-sm asset-delete-btn"
                  :disabled="isDeletingAsset(asset.name) || (asset.used_by && asset.used_by.length > 0)"
                  @click="deleteBrandingAsset(asset.name)"
                >
                  <span v-if="isDeletingAsset(asset.name)">Deleting...</span>
                  <span v-else-if="asset.used_by && asset.used_by.length">In Use</span>
                  <span v-else><i class="bi bi-trash" aria-hidden="true"></i>Delete</span>
                </button>
              </div>
            </div>
            <div v-else-if="isImageSetting(key)" class="asset-empty-note">No images match this filter.</div>
            <div v-if="isCoverBackgroundKey(key) && isNoCoverBackgroundEnabled()" class="asset-empty-note">Cover background is disabled for PDF exports.</div>
          </div>
        </div>
      </div>
      <div v-if="brandingAssetsError" class="status error">{{ brandingAssetsError }}</div>

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
        </div>
        <div class="button-group equal-width export-test-actions" role="group" aria-label="Quick export test actions">
          <button class="btn btn-primary btn-sm" :disabled="!canRunExportTest || exporting.pdf" @click="testPdfExport">
            <span v-if="exporting.pdf"><i class="bi bi-hourglass-split" aria-hidden="true"></i>Generating PDF...</span>
            <span v-else><i class="bi bi-file-earmark-pdf" aria-hidden="true"></i>Test PDF Export</span>
          </button>
          <button class="btn btn-secondary btn-sm" :disabled="!canRunExportTest || exporting.preview" @click="testHtmlPreview">
            <span v-if="exporting.preview"><i class="bi bi-hourglass-split" aria-hidden="true"></i>Opening Preview...</span>
            <span v-else><i class="bi bi-eye" aria-hidden="true"></i>Test HTML Preview</span>
          </button>
          <button class="btn btn-secondary btn-sm" :disabled="!canRunExportTest || exporting.downloadHtml" @click="testHtmlDownload">
            <span v-if="exporting.downloadHtml"><i class="bi bi-hourglass-split" aria-hidden="true"></i>Downloading...</span>
            <span v-else><i class="bi bi-download" aria-hidden="true"></i>Download HTML Export</span>
          </button>
        </div>
        <div class="export-test-meta-row">
          <button class="btn btn-secondary btn-sm" :disabled="loadingPublications" @click="loadPublications">
            <span v-if="loadingPublications"><i class="bi bi-hourglass-split" aria-hidden="true"></i>Refreshing...</span>
            <span v-else><i class="bi bi-arrow-repeat" aria-hidden="true"></i>Refresh Publications</span>
          </button>
          <span v-if="publicationsError" class="export-test-meta error-text">{{ publicationsError }}</span>
          <span v-else class="export-test-meta">{{ filteredPublications.length }} shown / {{ publications.length }} total</span>
        </div>
        <div v-if="exportMessage" class="status success">{{ exportMessage }}</div>
        <div v-if="exportError" class="status error">{{ exportError }}</div>
      </div>

      <div class="actions-row">
        <button class="btn btn-secondary reset-branding-btn" :disabled="saving" @click="resetBrandingDefaults">Reset Branding Defaults</button>
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
import {
  getAdminSettings,
  updateAdminSettings,
  listExportBrandingAssets,
  uploadExportBrandingAsset,
  deleteExportBrandingAsset,
  fetchExportBrandingAssetBlob,
} from '@/api/adminSettings'
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
const NO_COVER_BACKGROUND_SENTINEL = '__none__'

const IMAGE_SETTING_KEYS = [
  'export_html_logo',
  'export_pdf_title_logo',
  'export_pdf_footer_logo',
  'export_pdf_cover_background',
]

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
      brandingAssets: [],
      brandingAssetsLoading: false,
      brandingAssetsLoaded: false,
      brandingAssetsError: '',
      uploadingAssetKeys: {},
      deletingAssetNames: {},
      assetPreviewUrls: {},
      showUnusedOnlyByKey: IMAGE_SETTING_KEYS.reduce((acc, settingKey) => {
        acc[settingKey] = false
        return acc
      }, {}),
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
      const basename = this.normalizeAssetBasename(raw)
      return basename ? (this.assetPreviewUrls[basename] || '') : ''
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
  async mounted() {
    await this.reload()
    await this.loadBrandingAssets()
    await this.loadPublications()
  },
  beforeUnmount() {
    this.revokeAssetPreviewUrls()
  },
  methods: {
    normalizeAssetBasename(value) {
      const cleaned = (value || '').trim()
      if (!cleaned) return ''
      const parts = cleaned.split('/')
      return (parts[parts.length - 1] || '').trim()
    },
    revokeAssetPreviewUrls(exceptNames = []) {
      const keep = new Set(exceptNames)
      const next = {}
      Object.entries(this.assetPreviewUrls).forEach(([name, url]) => {
        if (keep.has(name)) {
          next[name] = url
          return
        }
        if (url) {
          URL.revokeObjectURL(url)
        }
      })
      this.assetPreviewUrls = next
    },
    async ensureAssetPreviewUrl(filename) {
      const name = this.normalizeAssetBasename(filename)
      if (!name || this.assetPreviewUrls[name]) {
        return
      }
      try {
        const blob = await fetchExportBrandingAssetBlob(name)
        if (!blob) return
        const objectUrl = URL.createObjectURL(blob)
        this.assetPreviewUrls = {
          ...this.assetPreviewUrls,
          [name]: objectUrl,
        }
      } catch (_) {
        // Ignore per-file preview failures; list loading remains available.
      }
    },
    async syncAssetPreviewUrls() {
      const names = (this.brandingAssets || []).map(asset => this.normalizeAssetBasename(asset?.name)).filter(Boolean)
      this.revokeAssetPreviewUrls(names)
      await Promise.allSettled(names.map(name => this.ensureAssetPreviewUrl(name)))
    },
    isImageSetting(key) {
      return IMAGE_SETTING_KEYS.includes(key)
    },
    isCoverBackgroundKey(key) {
      return key === 'export_pdf_cover_background'
    },
    isUnusedOnlyEnabled(key) {
      return !!this.showUnusedOnlyByKey[key]
    },
    setUnusedOnly(key, enabled) {
      this.showUnusedOnlyByKey = {
        ...this.showUnusedOnlyByKey,
        [key]: !!enabled,
      }
    },
    visibleBrandingAssetsForKey(key) {
      const selected = this.normalizeAssetBasename(this.edits[key])
      return (this.brandingAssets || []).filter(asset => {
        const name = this.normalizeAssetBasename(asset?.name)
        if (!name) return false
        if (selected && name === selected) {
          return true
        }
        if (!this.isUnusedOnlyEnabled(key)) {
          return true
        }
        return !asset?.used_by || asset.used_by.length === 0
      })
    },
    selectedAssetMissingForKey(key) {
      const raw = (this.edits[key] || '').trim()
      if (!raw || raw === NO_COVER_BACKGROUND_SENTINEL) return false
      if (raw.startsWith('http://') || raw.startsWith('https://') || raw.startsWith('data:') || raw.startsWith('/')) {
        return false
      }
      if (!this.brandingAssetsLoaded || this.brandingAssetsLoading) {
        return false
      }
      const basename = this.normalizeAssetBasename(raw)
      if (!basename) return false
      return !this.brandingAssets.some(asset => this.normalizeAssetBasename(asset?.name) === basename)
    },
    isNoCoverBackgroundEnabled() {
      return (this.edits.export_pdf_cover_background || '').trim() === NO_COVER_BACKGROUND_SENTINEL
    },
    toggleNoCoverBackground(enabled) {
      this.edits.export_pdf_cover_background = enabled ? NO_COVER_BACKGROUND_SENTINEL : ''
    },
    isUploadingAsset(key) {
      return !!this.uploadingAssetKeys[key]
    },
    isDeletingAsset(filename) {
      return !!this.deletingAssetNames[filename]
    },
    applyAssetSelection(key, selectedName) {
      if (!selectedName) return
      this.edits[key] = selectedName
    },
    assetUrlForSetting(key) {
      const value = (this.edits[key] || '').trim()
      if (!value) return ''
      if (value === NO_COVER_BACKGROUND_SENTINEL) return ''
      if (value.startsWith('http://') || value.startsWith('https://') || value.startsWith('data:') || value.startsWith('/')) {
        return value
      }
      const basename = this.normalizeAssetBasename(value)
      return basename ? (this.assetPreviewUrls[basename] || '') : ''
    },
    assetPreviewUrl(filename) {
      const value = (filename || '').trim()
      if (!value) return ''
      if (value.startsWith('http://') || value.startsWith('https://') || value.startsWith('data:') || value.startsWith('/')) {
        return value
      }
      const basename = this.normalizeAssetBasename(value)
      if (!basename) return ''
      return this.assetPreviewUrls[basename] || `/api/admin/export-branding/assets/${encodeURIComponent(basename)}/preview`
    },
    handleAssetPreviewError(filename) {
      const basename = this.normalizeAssetBasename(filename)
      if (!basename) return
      delete this.assetPreviewUrls[basename]
      // A failed preview fetch should not remove a valid uploaded asset from the list.
      // Keep the asset until the full list refresh confirms the file is actually missing.
    },
    normalizeHexColor(value, fallback) {
      const trimmed = (value || '').trim()
      const valid = /^#?[0-9a-fA-F]{6}$/.test(trimmed)
      if (!valid) return fallback
      return trimmed.startsWith('#') ? trimmed : `#${trimmed}`
    },
    labelFor(key) {
      return LABELS[key] || key
    },
    usageLabelForKey(key) {
      return LABELS[key] || key
    },
    assetUsageSummary(asset) {
      const usedBy = Array.isArray(asset?.used_by) ? asset.used_by : []
      if (!usedBy.length) return ''
      if (usedBy.length === 1) {
        return `Used by: ${this.usageLabelForKey(usedBy[0])}`
      }
      return `Used by ${usedBy.length} settings`
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
        await Promise.allSettled(
          IMAGE_SETTING_KEYS
            .map(settingKey => this.normalizeAssetBasename(this.edits[settingKey]))
            .filter(Boolean)
            .map(name => this.ensureAssetPreviewUrl(name))
        )
        this.logoPreviewErrored = false
      } catch (err) {
        this.error = toFriendlyAuthError(err, 'Failed to load admin settings.')
      } finally {
        this.loading = false
      }
    },
    async loadBrandingAssets() {
      this.brandingAssetsLoading = true
      this.brandingAssetsLoaded = false
      this.brandingAssetsError = ''
      try {
        const assets = await listExportBrandingAssets()
        this.brandingAssets = Array.isArray(assets) ? assets : []
        await this.syncAssetPreviewUrls()
        this.brandingAssetsLoaded = true
      } catch (err) {
        this.brandingAssetsError = toFriendlyAuthError(err, 'Could not load uploaded branding images.')
      } finally {
        this.brandingAssetsLoading = false
      }
    },
    async uploadAssetForKey(key, event) {
      const input = event?.target
      const file = input?.files?.[0]
      if (!file) return

      this.uploadingAssetKeys = { ...this.uploadingAssetKeys, [key]: true }
      this.saveError = null
      this.saveSuccess = false
      try {
        const result = await uploadExportBrandingAsset(file, key)
        if (result?.filename) {
          this.edits[key] = result.filename
        }
        await this.loadBrandingAssets()
      } catch (err) {
        this.saveError = toFriendlyAuthError(err, 'Failed to upload branding image.')
      } finally {
        if (input) {
          input.value = ''
        }
        const next = { ...this.uploadingAssetKeys }
        delete next[key]
        this.uploadingAssetKeys = next
      }
    },
    async deleteBrandingAsset(filename) {
      if (!filename) return
      const ok = window.confirm(`Delete image "${filename}"?`)
      if (!ok) return

      this.deletingAssetNames = { ...this.deletingAssetNames, [filename]: true }
      this.brandingAssetsError = ''
      try {
        await deleteExportBrandingAsset(filename)
        Object.keys(this.edits).forEach(key => {
          if (this.isImageSetting(key) && this.edits[key] === filename) {
            this.edits[key] = ''
          }
        })
        this.brandingAssets = this.brandingAssets.filter(asset => this.normalizeAssetBasename(asset?.name) !== filename)
        delete this.assetPreviewUrls[this.normalizeAssetBasename(filename)]
        await this.loadBrandingAssets()
      } catch (err) {
        this.brandingAssetsError = toFriendlyAuthError(err, 'Failed to delete branding image.')
      } finally {
        const next = { ...this.deletingAssetNames }
        delete next[filename]
        this.deletingAssetNames = next
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
      await this.loadBrandingAssets()
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

.setting-input-stack {
  display: grid;
  gap: 8px;
}

.image-controls {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 8px;
  align-items: center;
}

.asset-thumb-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
}

.asset-filter-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.asset-filter-toggle {
  display: inline-flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 6px;
  font-size: 0.82rem;
  color: #374151;
}

.asset-filter-toggle span {
  white-space: nowrap;
}

.asset-filter-meta {
  font-size: 0.75rem;
  color: #6b7280;
}

.asset-empty-note {
  font-size: 0.78rem;
  color: #6b7280;
  padding: 4px 0;
}

.cover-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: nowrap;
  gap: 6px;
  font-size: 0.82rem;
  color: #374151;
  width: fit-content;
  max-width: 100%;
  margin: 0;
  padding: 0;
  text-align: left;
  align-self: start;
}

.cover-toggle input {
  margin: 0;
  flex-shrink: 0;
}

.cover-toggle span {
  white-space: normal;
  line-height: 1.2;
  margin-left: 0;
}

.asset-thumb-btn {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #ffffff;
  padding: 6px;
  display: grid;
  gap: 6px;
  text-align: left;
  min-width: 0;
  overflow: hidden;
}

.asset-thumb-btn.active {
  border-color: #0d6efd;
  box-shadow: 0 0 0 2px rgba(13, 110, 253, 0.12);
}

.asset-thumb-image {
  width: 100%;
  height: 64px;
  object-fit: contain;
  border-radius: 6px;
  background: #f8fafc;
  display: block;
}

.asset-select-btn {
  border: none;
  background: transparent;
  padding: 0;
  margin: 0;
  text-align: left;
  display: grid;
  gap: 6px;
  cursor: pointer;
  width: 100%;
  min-width: 0;
  align-items: start;
}

.asset-delete-btn {
  align-self: center;
  width: auto;
  min-width: 96px;
  max-width: 100%;
  white-space: nowrap;
}

.asset-thumb-name {
  font-size: 0.72rem;
  line-height: 1.2;
  color: #4b5563;
  word-break: break-word;
}

.asset-used-by {
  font-size: 0.68rem;
  color: #1d4ed8;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  padding: 3px 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.upload-btn {
  position: relative;
  overflow: hidden;
}

.upload-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.actions-row {
  margin-top: 18px;
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.actions-row .btn {
  height: 38px;
  min-height: 38px;
  padding: 0.5rem 0.9rem;
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.reset-branding-btn:hover:not(:disabled),
.reset-branding-btn:focus-visible:not(:disabled) {
  background-color: #dc3545;
  border-color: #dc3545;
  color: #ffffff;
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
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  align-items: center;
}

.export-test-actions {
  width: 100%;
  margin-top: 8px;
}

.export-test-actions .btn {
  width: 100%;
}

.export-test-actions .btn i,
.export-test-meta-row .btn i {
  margin-right: 0.4rem;
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

  .image-controls {
    grid-template-columns: 1fr;
  }

  .export-test-controls {
    grid-template-columns: 1fr;
  }

  .asset-thumb-grid {
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  }
}
</style>
