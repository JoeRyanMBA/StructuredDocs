<template>
  <div class="bulk-review-portal">
    <!-- Loading -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p>Loading your review portal…</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-container error-state">
      <div class="state-icon">⚠️</div>
      <h2>Unable to Load Review</h2>
      <p>{{ error }}</p>
    </div>

    <!-- All done -->
    <div v-else-if="allComplete" class="state-container success-state">
      <div class="state-icon">🎉</div>
      <h2>All Done — Thank You!</h2>
      <p>You have reviewed all {{ batch.total }} topic{{ batch.total !== 1 ? 's' : '' }}. Your feedback has been submitted.</p>
    </div>

    <!-- Main portal -->
    <div v-else-if="batch" class="portal-layout">
      <!-- Header bar -->
      <header class="portal-header">
        <div class="header-left">
          <span class="app-name">StructuredDocs</span>
          <span class="divider">|</span>
          <span class="batch-label">Bulk Review</span>
          <HelpIcon feature="reviews.bulk" />
        </div>
        <div class="header-center">
          <div class="progress-bar-wrap">
            <div class="progress-bar-fill" :style="{ width: progressPct + '%' }"></div>
          </div>
          <span class="progress-text">{{ completedCount }} of {{ batch.total }} reviewed</span>
        </div>
        <div class="header-right">
          <span :class="['priority-badge', 'priority-' + (batch.priority || 'medium')]">
            {{ (batch.priority || 'medium').toUpperCase() }}
          </span>
          <span v-if="batch.due_date" class="due-date">Due: {{ formatDate(batch.due_date) }}</span>
        </div>
      </header>

      <!-- Topic navigation strip -->
      <nav class="topic-nav">
        <button
          v-for="(topic, idx) in batch.topics"
          :key="topic.review_id"
          :class="['topic-nav-btn', { active: idx === currentIndex, completed: topic.completed }]"
          @click="goTo(idx)"
          :title="topic.topic_title"
        >
          <span class="nav-num">{{ idx + 1 }}</span>
          <span v-if="topic.completed" class="nav-check">✓</span>
        </button>
      </nav>

      <!-- Body -->
      <div class="portal-body">
        <!-- Left: topic content -->
        <section class="content-panel">
          <div class="topic-header">
            <h1 class="topic-title">{{ currentTopic.topic_title }}</h1>
            <span v-if="currentTopic.completed" class="reviewed-badge">✓ Reviewed</span>
          </div>
          <div v-if="batch.message" class="author-message">
            <strong>Message from requester:</strong> {{ batch.message }}
          </div>

          <!-- View toggle -->
          <div class="content-actions">
            <div class="view-toggle">
              <button
                type="button"
                :class="['toggle-btn', { active: activeView === 'read' }]"
                @click="activeView = 'read'"
              >📖 Read Only</button>
              <button
                type="button"
                :class="['toggle-btn', { active: activeView === 'edit' }]"
                @click="activeView = 'edit'"
              >✏️ Edit Content</button>
            </div>
            <template v-if="currentHasEdits">
              <span class="edits-indicator">✏️ Edited</span>
              <button type="button" class="reset-edits-btn" @click="resetEdits">↩ Reset</button>
            </template>
          </div>

          <!-- Read-only view -->
          <div v-if="activeView === 'read'" class="topic-content" v-html="currentTopic.topic_content"></div>

          <!-- WYSIWYG editor view -->
          <div v-else class="editor-section">
            <div class="editor-notice">
              💡 Your edits are tracked and shared with the author for review — they won't be applied automatically.
            </div>
            <div ref="quillEditor" class="quill-editor-area"></div>
          </div>
        </section>

        <!-- Right: feedback panel -->
        <aside class="feedback-panel">
          <!-- If already submitted show summary -->
          <div v-if="currentTopic.completed" class="already-reviewed">
            <h3>✓ Feedback Submitted</h3>
            <p v-if="currentTopic.recommendation" class="recommendation-summary">
              Recommendation: <strong>{{ formatRecommendation(currentTopic.recommendation) }}</strong>
            </p>
            <p v-if="currentTopic.feedback" class="feedback-summary">{{ currentTopic.feedback }}</p>
            <p class="next-hint" v-if="nextIncomplete !== null">
              You can continue to the next topic using the button below.
            </p>
          </div>

          <!-- Feedback form -->
          <form v-else @submit.prevent="submitCurrentFeedback" class="feedback-form">
            <h3>Your Feedback</h3>

            <!-- Overall recommendation -->
            <div class="form-group">
              <label>Overall Recommendation <span class="required">*</span></label>
              <select v-model="form.recommendation" class="form-select" required>
                <option value="">Select recommendation…</option>
                <option value="approve">Approve as submitted</option>
                <option value="approve_with_changes">Approve with minor changes</option>
                <option value="needs_more_info">Request more information</option>
                <option value="reject">Reject — significant issues</option>
              </select>
            </div>

            <!-- Overall comments -->
            <div class="form-group">
              <label>Overall Comments</label>
              <textarea
                v-model="form.feedback"
                class="form-textarea"
                placeholder="Your general thoughts on this topic…"
                rows="4"
              ></textarea>
            </div>

            <!-- Specific feedback items -->
            <div class="specific-feedback">
              <h4>Specific Feedback Items</h4>
              <p class="help-text">Add specific comments, corrections, or suggestions (optional).</p>

              <div v-for="(item, idx) in form.feedback_items" :key="idx" class="feedback-item-card">
                <div class="item-header">
                  <span>Item {{ idx + 1 }}</span>
                  <button type="button" class="remove-btn" @click="removeItem(idx)">×</button>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>Type</label>
                    <select v-model="item.feedback_type" class="form-select">
                      <option value="general_comment">General Comment</option>
                      <option value="text_edit">Text Edit</option>
                      <option value="text_addition">Text Addition</option>
                      <option value="text_deletion">Text Deletion</option>
                      <option value="technical_correction">Technical Correction</option>
                      <option value="style_suggestion">Style Suggestion</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Priority</label>
                    <select v-model="item.priority" class="form-select">
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label>Section / Location</label>
                  <input v-model="item.section_title" type="text" class="form-input"
                    placeholder="e.g., Introduction, paragraph 2" />
                </div>

                <div v-if="item.feedback_type !== 'general_comment'" class="form-group">
                  <label>Original Text</label>
                  <textarea v-model="item.original_text" class="form-textarea"
                    placeholder="Copy the text you're referring to…" rows="2"></textarea>
                </div>

                <div v-if="item.feedback_type.includes('edit') || item.feedback_type.includes('addition')" class="form-group">
                  <label>Suggested Text</label>
                  <textarea v-model="item.suggested_text" class="form-textarea"
                    placeholder="Your suggested replacement or addition…" rows="2"></textarea>
                </div>

                <div class="form-group">
                  <label>Comment <span class="required">*</span></label>
                  <textarea v-model="item.comment" class="form-textarea"
                    placeholder="Explain your feedback…" rows="3" required></textarea>
                </div>

                <div class="form-group">
                  <label>Rationale (Optional)</label>
                  <textarea v-model="item.rationale" class="form-textarea"
                    placeholder="Why is this change needed?" rows="2"></textarea>
                </div>
              </div>

              <button type="button" class="btn btn-outline add-item-btn" @click="addItem">
                + Add Feedback Item
              </button>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-success" :disabled="submitting || !form.recommendation">
                {{ submitting ? 'Submitting…' : 'Submit & Continue' }}
              </button>
            </div>
          </form>

          <!-- Navigation -->
          <div class="nav-actions">
            <button class="btn btn-secondary" :disabled="currentIndex === 0" @click="goTo(currentIndex - 1)">
              ← Previous
            </button>
            <span class="nav-position">Topic {{ currentIndex + 1 }} of {{ batch.total }}</span>
            <button
              class="btn btn-secondary"
              :disabled="currentIndex === batch.total - 1"
              @click="goTo(currentIndex + 1)"
            >
              Next →
            </button>
          </div>
          <div v-if="nextIncomplete !== null && currentTopic.completed" class="next-prompt">
            <button class="btn btn-primary" @click="goTo(nextIncomplete)">
              Go to Next Unreviewed Topic →
            </button>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script>
import Quill from 'quill'
import 'quill/dist/quill.snow.css'
import { getBulkReview, submitBulkTopicFeedback } from '@/api/reviews.js'
import HelpIcon from '@/components/HelpIcon.vue'
import { normalizeReviewHtml } from '@/utils/reviewHtml'

export default {
  name: 'BulkReviewPortal',
  components: { HelpIcon },

  data() {
    return {
      loading: true,
      error: null,
      batch: null,
      currentIndex: 0,
      submitting: false,
      form: this.emptyForm(),
      // Editor state
      activeView: 'read',       // 'read' | 'edit'
      quillInstance: null,
      topicEdits: {},           // { [review_id]: editedHtml }
    }
  },

  computed: {
    token() {
      return this.$route.params.token
    },
    currentTopic() {
      return this.batch?.topics[this.currentIndex] || null
    },
    completedCount() {
      return this.batch?.topics.filter(t => t.completed).length || 0
    },
    progressPct() {
      if (!this.batch?.total) return 0
      return Math.round((this.completedCount / this.batch.total) * 100)
    },
    allComplete() {
      return this.batch && this.completedCount === this.batch.total
    },
    nextIncomplete() {
      if (!this.batch) return null
      for (let i = 0; i < this.batch.topics.length; i++) {
        if (!this.batch.topics[i].completed) return i
      }
      return null
    },
    currentEditedContent() {
      if (!this.currentTopic) return null
      return this.topicEdits[this.currentTopic.review_id] ?? null
    },
    currentHasEdits() {
      const edited = normalizeReviewHtml(this.currentEditedContent)
      if (!edited) return false
      return edited !== normalizeReviewHtml(this.currentTopic?.topic_content || '')
    },
  },

  watch: {
    activeView(newView) {
      if (newView === 'edit') {
        this.$nextTick(() => this.initQuill())
      } else {
        // v-if removes the DOM node; just clear the reference
        this.quillInstance = null
      }
    },
  },

  async created() {
    await this.loadBatch()
  },

  unmounted() {
    this.quillInstance = null
  },

  methods: {
    async loadBatch() {
      try {
        this.loading = true
        this.batch = await getBulkReview(this.token)
        // Start at first incomplete topic
        const first = this.batch.topics.findIndex(t => !t.completed)
        this.currentIndex = first >= 0 ? first : 0
      } catch (err) {
        this.error = err.message || 'Failed to load review portal.'
      } finally {
        this.loading = false
      }
    },

    goTo(index) {
      if (index < 0 || index >= this.batch.total) return
      // Tear down the editor before switching topics so the ref is fresh
      this.quillInstance = null
      this.activeView = 'read'
      this.currentIndex = index
      this.form = this.emptyForm()
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },

    initQuill() {
      if (!this.$refs.quillEditor || this.quillInstance) return
      const toolbarOptions = [
        [{ header: [1, 2, 3, false] }],
        ['bold', 'italic', 'underline'],
        [{ list: 'ordered' }, { list: 'bullet' }],
        [{ align: [] }],
        ['link'],
        ['clean'],
      ]
      this.quillInstance = new Quill(this.$refs.quillEditor, {
        modules: { toolbar: toolbarOptions },
        theme: 'snow',
        placeholder: 'Edit the content here…',
      })
      // Restore any previously saved edits, otherwise use original content
      const reviewId = this.currentTopic?.review_id
      const originalContent = normalizeReviewHtml(this.currentTopic?.topic_content || '')
      const saved = reviewId != null ? normalizeReviewHtml(this.topicEdits[reviewId]) : null
      this.quillInstance.root.innerHTML = saved ?? originalContent
      // Persist every keystroke to topicEdits
      this.quillInstance.on('text-change', () => {
        if (reviewId != null) {
          this.topicEdits[reviewId] = normalizeReviewHtml(this.quillInstance.root.innerHTML)
        }
      })
    },

    resetEdits() {
      if (!this.currentTopic) return
      const reviewId = this.currentTopic.review_id
      delete this.topicEdits[reviewId]
      if (this.quillInstance) {
        this.quillInstance.root.innerHTML = normalizeReviewHtml(this.currentTopic.topic_content || '')
      }
    },

    addItem() {
      this.form.feedback_items.push({
        feedback_type: 'general_comment',
        priority: 'medium',
        section_title: '',
        original_text: '',
        suggested_text: '',
        comment: '',
        rationale: '',
      })
    },

    removeItem(idx) {
      this.form.feedback_items.splice(idx, 1)
    },

    emptyForm() {
      return {
        recommendation: '',
        feedback: '',
        feedback_items: [],
      }
    },

    async submitCurrentFeedback() {
      if (!this.form.recommendation) return
      this.submitting = true
      try {
        const topic = this.currentTopic
        const edited = normalizeReviewHtml(this.topicEdits[topic.review_id])
        const hasEdits = edited != null && edited !== normalizeReviewHtml(topic.topic_content || '')
        const payload = {
          recommendation: this.form.recommendation,
          feedback: this.form.feedback,
          feedback_items: this.form.feedback_items.filter(i => i.comment.trim()),
          ...(hasEdits ? { edited_content: edited } : {}),
        }
        const result = await submitBulkTopicFeedback(this.token, topic.review_id, payload)

        // Update local state so UI reflects completion immediately
        topic.completed = true
        topic.recommendation = this.form.recommendation
        topic.feedback = this.form.feedback
        this.form = this.emptyForm()
        // Clear saved edits for this topic now that it's submitted
        delete this.topicEdits[topic.review_id]

        if (result.batch_complete) {
          this.batch.completed_count = this.batch.total
        } else {
          this.batch.completed_count = result.completed_count
          if (this.nextIncomplete !== null) {
            this.goTo(this.nextIncomplete)
          }
        }
      } catch (err) {
        alert('Failed to submit feedback: ' + (err.message || 'Unknown error'))
      } finally {
        this.submitting = false
      }
    },

    formatDate(iso) {
      if (!iso) return ''
      return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
    },

    formatRecommendation(val) {
      const map = {
        approve: 'Approve as submitted',
        approve_with_changes: 'Approve with changes',
        needs_more_info: 'Request more information',
        reject: 'Reject',
      }
      return map[val] || val
    },
  },
}
</script>

<style scoped>
/* ---- Layout ---- */
.bulk-review-portal {
  min-height: 100vh;
  background: #f4f6f9;
  font-family: Arial, sans-serif;
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 16px;
  color: #495057;
}
.state-icon { font-size: 56px; }
.success-state h2 { color: #198754; }
.error-state h2 { color: #dc3545; }

.spinner {
  width: 44px; height: 44px;
  border: 4px solid #dee2e6;
  border-top-color: #0d6efd;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ---- Header ---- */
.portal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #0d6efd;
  color: #fff;
  padding: 12px 24px;
  gap: 16px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-left { display: flex; align-items: center; gap: 8px; font-weight: bold; }
.app-name { font-size: 18px; }
.divider { opacity: 0.5; }
.batch-label { font-size: 14px; opacity: 0.85; }

.header-center { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; }
.progress-bar-wrap { width: 100%; max-width: 300px; height: 8px; background: rgba(255,255,255,0.3); border-radius: 4px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: #fff; border-radius: 4px; transition: width 0.4s; }
.progress-text { font-size: 12px; opacity: 0.9; }

.header-right { display: flex; align-items: center; gap: 12px; font-size: 13px; }
.due-date { opacity: 0.85; }

/* ---- Priority badge ---- */
.priority-badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
.priority-urgent { background: #dc3545; }
.priority-high { background: #fd7e14; }
.priority-medium { background: rgba(255,255,255,0.25); }
.priority-low { background: rgba(255,255,255,0.15); }

/* ---- Topic nav strip ---- */
.topic-nav {
  display: flex;
  gap: 6px;
  padding: 10px 24px;
  background: #fff;
  border-bottom: 1px solid #dee2e6;
  overflow-x: auto;
  flex-wrap: wrap;
}
.topic-nav-btn {
  display: flex; align-items: center; gap: 4px;
  min-width: 36px; height: 36px; padding: 0 10px;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  background: #f8f9fa;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s;
}
.topic-nav-btn:hover { border-color: #0d6efd; }
.topic-nav-btn.active { border-color: #0d6efd; background: #e7f1ff; font-weight: bold; }
.topic-nav-btn.completed { border-color: #198754; background: #d1e7dd; }
.nav-check { color: #198754; font-weight: bold; }

/* ---- Body ---- */
.portal-body {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 0;
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  align-items: start;
}
@media (max-width: 900px) {
  .portal-body { grid-template-columns: 1fr; }
}

/* ---- Content panel ---- */
.content-panel {
  background: #fff;
  border-radius: 8px;
  padding: 28px 32px;
  border: 1px solid #dee2e6;
  margin-right: 20px;
}
@media (max-width: 900px) { .content-panel { margin-right: 0; margin-bottom: 20px; } }

.topic-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.topic-title { font-size: 22px; margin: 0; color: #212529; }
.reviewed-badge { background: #d1e7dd; color: #0f5132; padding: 2px 10px; border-radius: 12px; font-size: 13px; font-weight: bold; }

.author-message {
  background: #fff3cd; border-left: 4px solid #ffc107;
  padding: 10px 14px; margin-bottom: 16px; border-radius: 4px; font-size: 14px; color: #856404;
}

.topic-content { line-height: 1.7; color: #343a40; }
.topic-content :deep(h1), .topic-content :deep(h2), .topic-content :deep(h3) { color: #212529; margin-top: 1.2em; }
.topic-content :deep(img) { max-width: 100%; border-radius: 4px; }
.topic-content :deep(table) { border-collapse: collapse; width: 100%; }
.topic-content :deep(td), .topic-content :deep(th) { border: 1px solid #dee2e6; padding: 8px 12px; }
.topic-content :deep(pre) { background: #f8f9fa; padding: 12px; border-radius: 6px; overflow-x: auto; }

/* ---- Feedback panel ---- */
.feedback-panel {
  position: sticky;
  top: 80px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  padding: 24px;
  max-height: calc(100vh - 110px);
  overflow-y: auto;
}

.already-reviewed { text-align: center; padding: 20px 0; color: #198754; }
.already-reviewed h3 { color: #198754; }
.recommendation-summary, .feedback-summary { color: #495057; font-size: 14px; }
.next-hint { font-size: 13px; color: #6c757d; margin-top: 12px; }

.feedback-form h3 { margin-top: 0; color: #212529; margin-bottom: 16px; }

.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-weight: 600; font-size: 13px; margin-bottom: 4px; color: #495057; }
.required { color: #dc3545; }
.form-select, .form-input { width: 100%; padding: 8px 10px; border: 1px solid #ced4da; border-radius: 6px; font-size: 14px; }
.form-select:focus, .form-input:focus { outline: none; border-color: #0d6efd; box-shadow: 0 0 0 2px rgba(13,110,253,0.15); }
.form-textarea { width: 100%; padding: 8px 10px; border: 1px solid #ced4da; border-radius: 6px; font-size: 14px; resize: vertical; }
.form-textarea:focus { outline: none; border-color: #0d6efd; box-shadow: 0 0 0 2px rgba(13,110,253,0.15); }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

.specific-feedback h4 { font-size: 14px; color: #495057; margin-bottom: 4px; }
.help-text { font-size: 12px; color: #6c757d; margin-bottom: 12px; }

.feedback-item-card {
  background: #f8f9fa; border: 1px solid #e9ecef;
  border-radius: 8px; padding: 14px; margin-bottom: 10px;
}
.item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-weight: 600; font-size: 13px; }
.remove-btn { background: none; border: none; color: #dc3545; font-size: 18px; cursor: pointer; padding: 0 4px; }
.remove-btn:hover { color: #a71d2a; }

.add-item-btn { width: 100%; margin-top: 4px; margin-bottom: 16px; }

.form-actions { margin-top: 16px; }

/* ---- Navigation ---- */
.nav-actions {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 20px; padding-top: 16px; border-top: 1px solid #dee2e6;
}
.nav-position { font-size: 13px; color: #6c757d; }

.next-prompt { margin-top: 12px; text-align: center; }

/* ---- Buttons ---- */
.btn { padding: 9px 18px; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; border: 1px solid transparent; transition: all 0.15s; }
.btn:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-success { background: #198754; color: #fff; border-color: #198754; width: 100%; }
.btn-success:hover:not(:disabled) { background: #157347; }
.btn-primary { background: #0d6efd; color: #fff; border-color: #0d6efd; }
.btn-primary:hover:not(:disabled) { background: #0b5ed7; }
.btn-secondary { background: #6c757d; color: #fff; border-color: #6c757d; }
.btn-secondary:hover:not(:disabled) { background: #5c636a; }
.btn-outline { background: #fff; color: #0d6efd; border-color: #0d6efd; }
.btn-outline:hover { background: #e7f1ff; }

/* ---- View toggle & editor ---- */
.content-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.view-toggle {
  display: flex;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  overflow: hidden;
}
.toggle-btn {
  padding: 6px 14px;
  font-size: 13px;
  background: #f8f9fa;
  border: none;
  cursor: pointer;
  color: #495057;
  transition: background 0.15s, color 0.15s;
}
.toggle-btn:first-child { border-right: 1px solid #dee2e6; }
.toggle-btn.active { background: #0d6efd; color: #fff; font-weight: 600; }
.toggle-btn:hover:not(.active) { background: #e9ecef; }

.edits-indicator {
  font-size: 12px;
  color: #0d6efd;
  font-weight: 600;
}
.reset-edits-btn {
  background: none;
  border: 1px solid #adb5bd;
  border-radius: 5px;
  padding: 4px 10px;
  font-size: 12px;
  cursor: pointer;
  color: #6c757d;
}
.reset-edits-btn:hover { background: #f8f9fa; color: #212529; }

.editor-section { display: flex; flex-direction: column; }
.editor-notice {
  background: #e7f1ff;
  border-left: 3px solid #0d6efd;
  padding: 8px 12px;
  font-size: 13px;
  color: #0c5460;
  margin-bottom: 10px;
  border-radius: 0 4px 4px 0;
}
.quill-editor-area { min-height: 400px; }
.quill-editor-area :deep(.ql-container) { font-size: 15px; min-height: 360px; }
.quill-editor-area :deep(.ql-editor) { min-height: 360px; line-height: 1.7; }
.quill-editor-area :deep(.ql-editor p) { margin-bottom: 1rem; }
.quill-editor-area :deep(.ql-editor h1),
.quill-editor-area :deep(.ql-editor h2),
.quill-editor-area :deep(.ql-editor h3) { margin-top: 1.5rem; margin-bottom: 0.75rem; font-weight: 600; }
.quill-editor-area :deep(.ql-editor ul),
.quill-editor-area :deep(.ql-editor ol) { margin-bottom: 1rem; }
.quill-editor-area :deep(.ql-editor li) { margin-bottom: 0.25rem; }
</style>
