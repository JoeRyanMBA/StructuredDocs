<template>
  <span v-if="link" class="help-icon-wrapper" :title="link.title">
    <button
      type="button"
      class="help-icon-btn"
      :aria-label="`Help: ${link.title}`"
      @click.stop="openModal"
    >
      <i class="bi bi-info-circle"></i>
    </button>

    <!-- Help modal -->
    <Teleport to="body">
      <div v-if="modalOpen" class="help-icon-modal-overlay" @click.self="closeModal">
        <div class="help-icon-modal" role="dialog" :aria-labelledby="`help-modal-title-${uid}`">
          <div class="help-icon-modal-header">
            <h5 :id="`help-modal-title-${uid}`">
              <i class="bi bi-info-circle-fill me-2"></i>{{ link.title }}
            </h5>
            <button
              type="button"
              class="plain-close btn-close"
              aria-label="Close"
              @click="closeModal"
            ></button>
          </div>
          <div class="help-icon-modal-body">
            <p class="help-description">{{ link.description }}</p>
          </div>
          <div v-if="link.kb_url" class="help-icon-modal-footer">
            <a :href="link.kb_url" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm">
              <i class="bi bi-book me-1"></i>Learn More
            </a>
          </div>
        </div>
      </div>
    </Teleport>
  </span>
</template>

<script>
import { useHelpLinks } from '@/composables/useHelpLinks'

let _uid = 0

export default {
  name: 'HelpIcon',

  props: {
    /** The feature key registered in the admin Help Links panel, e.g. 'import.upload' */
    feature: {
      type: String,
      required: true,
    },
  },

  setup() {
    const { ensureLoaded, getLink } = useHelpLinks()
    ensureLoaded()
    return { getLink }
  },

  data() {
    return {
      modalOpen: false,
      uid: ++_uid,
    }
  },

  computed: {
    link() {
      return this.getLink(this.feature)
    },
  },

  methods: {
    openModal() {
      this.modalOpen = true
    },
    closeModal() {
      this.modalOpen = false
    },
  },
}
</script>

<style scoped>
.help-icon-wrapper {
  display: inline-flex;
  align-items: center;
  margin-left: 4px;
  vertical-align: middle;
}

.help-icon-btn {
  background: none;
  border: none;
  padding: 0 2px;
  cursor: pointer;
  color: #6c757d;
  font-size: 0.95em;
  line-height: 1;
  transition: color 0.15s ease;
}

.help-icon-btn:hover {
  color: #0d6efd;
}

/* Modal overlay */
.help-icon-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1055;
}

.help-icon-modal {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  width: min(480px, 90vw);
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.help-icon-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 12px;
  border-bottom: 1px solid #dee2e6;
}

.help-icon-modal-header h5 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #212529;
}

.help-icon-modal-body {
  padding: 16px 20px;
  overflow-y: auto;
  flex: 1;
}

.help-description {
  margin: 0;
  white-space: pre-wrap;
  color: #495057;
  line-height: 1.6;
}

.help-icon-modal-footer {
  padding: 12px 20px 16px;
  border-top: 1px solid #dee2e6;
  text-align: right;
}
</style>
