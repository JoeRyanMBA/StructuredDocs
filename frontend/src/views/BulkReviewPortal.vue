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
      <p>You have reviewed all {{ batch.total }} topic{{ batch.total !== 1 ? 's' : '' }}. Your feedback has been sent.</p>
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
                :class="['btn', activeView === 'read' ? 'btn-primary' : 'btn-secondary']"
                @click="activeView = 'read'"
              >📖 Read Only</button>
              <button
                type="button"
                :class="['btn', activeView === 'edit' ? 'btn-primary' : 'btn-secondary']"
                @click="activeView = 'edit'"
              >✏️ Edit Content</button>
            </div>
            <template v-if="currentHasEdits">
              <span class="edits-indicator">✏️ Edited</span>
              <button type="button" class="btn btn-outline btn-sm" @click="resetEdits">↩ Reset</button>
            </template>
          </div>

          <!-- Read-only view -->
          <div v-if="activeView === 'read'" class="topic-content" v-html="renderedTopicContent"></div>

          <!-- WYSIWYG editor view -->
          <div v-else class="editor-section review-editor-theme">
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
            <h3>✓ Feedback Sent</h3>
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
                <option value="approve">Approve as sent</option>
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
                {{ submitting ? 'Sending…' : 'Send & Continue' }}
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
import { markRaw } from 'vue'
import Quill from 'quill'
import 'quill/dist/quill.snow.css'
import '@/styles/review-editor.css'
import { getBulkReview, submitBulkTopicFeedback } from '@/api/reviews.js'
import HelpIcon from '@/components/HelpIcon.vue'
import { normalizeReviewHtml } from '@/utils/reviewHtml'
import { sanitizeHtml } from '@/utils/sanitize'
import { renderTopicMarkdown } from '@/utils/topicMarkdown'

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
    renderedTopicContent() {
      return sanitizeHtml(renderTopicMarkdown(this.currentTopic?.topic_content))
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
      return edited !== normalizeReviewHtml(this.renderedTopicContent)
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
      this.quillInstance = markRaw(new Quill(this.$refs.quillEditor, {
        modules: { toolbar: toolbarOptions },
        theme: 'snow',
        placeholder: 'Edit the content here…',
      }))
      // Restore any previously saved edits, otherwise use original content
      const reviewId = this.currentTopic?.review_id
      const originalContent = normalizeReviewHtml(this.renderedTopicContent)
      const saved = reviewId != null ? this.topicEdits[reviewId] : null
      this.quillInstance.clipboard.dangerouslyPasteHTML(
        saved == null ? originalContent : normalizeReviewHtml(saved)
      )
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
        this.quillInstance.clipboard.dangerouslyPasteHTML(
          normalizeReviewHtml(this.renderedTopicContent),
          'silent'
        )
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
        const savedEdit = this.topicEdits[topic.review_id]
        const edited = savedEdit == null ? null : normalizeReviewHtml(savedEdit)
        const hasEdits = edited !== null && edited !== normalizeReviewHtml(this.renderedTopicContent)
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
        alert('Failed to send feedback: ' + (err.message || 'Unknown error'))
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
        approve: 'Approve as sent',
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
  background: var(--bg-light-mist-gray);
  color: var(--text-primary-charcoal);
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 16px;
  color: var(--text-dark-gray);
}
.state-icon { font-size: 56px; }
.success-state h2 { color: var(--success-dark-green); }
.error-state h2 { color: var(--error-coral-red); }

.spinner {
  width: 44px; height: 44px;
  border: 4px solid var(--border-light-gray);
  border-top-color: var(--primary-deep-teal);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ---- Header ---- */
.portal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--primary-deep-teal);
  color: var(--bg-white);
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
.progress-bar-wrap { width: 100%; max-width: 300px; height: 8px; background: var(--primary-medium-teal); border-radius: 4px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: var(--bg-white); border-radius: 4px; transition: width 0.4s; }
.progress-text { font-size: 12px; opacity: 0.9; }

.header-right { display: flex; align-items: center; gap: 12px; font-size: 13px; }
.due-date { opacity: 0.85; }

/* ---- Priority badge ---- */
.priority-badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
.priority-urgent { background: var(--error-light-red); color: var(--error-dark-red); }
.priority-high { background: var(--warning-light-yellow); color: var(--warning-dark-yellow); }
.priority-medium { background: var(--info-light-blue); color: var(--info-dark-blue); }
.priority-low { background: var(--border-light-gray); color: var(--text-dark-gray); }

/* ---- Topic nav strip ---- */
.topic-nav {
  display: flex;
  gap: 6px;
  padding: 10px 24px;
  background: var(--bg-white);
  border-bottom: 1px solid var(--border-light-gray);
  overflow-x: auto;
  flex-wrap: wrap;
}
.topic-nav-btn {
  display: flex; align-items: center; gap: 4px;
  min-width: 36px; height: 36px; padding: 0 10px;
  border: 2px solid var(--border-light-gray);
  border-radius: 6px;
  background: var(--bg-white);
  color: var(--text-primary-charcoal);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s;
}
.topic-nav-btn:hover { border-color: var(--primary-medium-teal); }
.topic-nav-btn.completed { border-color: var(--success-mint-green); background: var(--success-light-green); }
.topic-nav-btn.active { border-color: var(--primary-deep-teal); background: var(--info-light-blue); font-weight: bold; }
.topic-nav-btn:focus-visible { outline: 2px solid var(--primary-deep-teal); outline-offset: 2px; }
.nav-check { color: var(--success-dark-green); font-weight: bold; }

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
  background: var(--bg-white);
  border-radius: var(--border-radius-md);
  padding: 28px 32px;
  border: 1px solid var(--border-light-gray);
  margin-right: 20px;
}
@media (max-width: 900px) { .content-panel { margin-right: 0; margin-bottom: 20px; } }

.topic-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.topic-title { font-size: 22px; margin: 0; color: var(--primary-deep-teal); }
.reviewed-badge { background: var(--success-light-green); color: var(--success-dark-green); padding: 2px 10px; border-radius: 12px; font-size: 13px; font-weight: bold; }

.author-message {
  background: var(--warning-light-yellow); border-left: 4px solid var(--warning-amber);
  padding: 10px 14px; margin-bottom: 16px; border-radius: 4px; font-size: 14px; color: var(--warning-dark-yellow);
}

.topic-content { position: relative; isolation: isolate; line-height: 1.7; color: var(--text-primary-charcoal); }
.topic-content :deep(h1), .topic-content :deep(h2), .topic-content :deep(h3) { color: var(--primary-deep-teal); margin-top: 1.2em; }
.topic-content :deep(img) { max-width: 100%; border-radius: 4px; }
.topic-content :deep(table) { border-collapse: collapse; width: 100%; }
.topic-content :deep(td), .topic-content :deep(th) { border: 1px solid var(--border-light-gray); padding: 8px 12px; }
.topic-content :deep(pre) { background: var(--border-light-gray); padding: 12px; border-radius: 6px; overflow-x: auto; }
.topic-content :deep(ol) { list-style-type: decimal; }
.topic-content :deep(ol ol) { list-style-type: lower-alpha; }
.topic-content :deep(ol ol ol) { list-style-type: lower-roman; }
.topic-content :deep(ol ol ol ol) { list-style-type: upper-alpha; }

/* ---- Feedback panel ---- */
.feedback-panel {
  position: sticky;
  top: 80px;
  background: var(--bg-white);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-light-gray);
  padding: 24px;
  max-height: calc(100vh - 110px);
  overflow-y: auto;
}

.already-reviewed { text-align: center; padding: 20px 0; color: var(--success-dark-green); }
.already-reviewed h3 { color: var(--success-dark-green); }
.recommendation-summary, .feedback-summary { color: var(--text-dark-gray); font-size: 14px; }
.next-hint { font-size: 13px; color: var(--text-medium-gray); margin-top: 12px; }

.feedback-form h3 { margin-top: 0; color: var(--primary-deep-teal); margin-bottom: 16px; }

.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-weight: 600; font-size: 13px; margin-bottom: 4px; color: var(--text-dark-gray); }
.required { color: var(--error-coral-red); }
.form-select, .form-input, .form-textarea {
  width: 100%; padding: 8px 10px;
  border: 1px solid var(--border-color-gray); border-radius: 6px; font-size: 14px;
  background-color: var(--bg-white); color: var(--text-primary-charcoal);
}
.form-textarea { resize: vertical; }
.form-select:focus, .form-input:focus, .form-textarea:focus {
  outline: none; border-color: var(--primary-deep-teal);
  box-shadow: 0 0 0 2px var(--primary-light-teal-t);
}

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

.specific-feedback h4 { font-size: 14px; color: var(--text-dark-gray); margin-bottom: 4px; }
.help-text { font-size: 12px; color: var(--text-medium-gray); margin-bottom: 12px; }

.feedback-item-card {
  background: var(--bg-light-mist-gray); border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md); padding: 14px; margin-bottom: 10px;
}
.item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-weight: 600; font-size: 13px; }
.remove-btn { background: none; border: none; color: var(--error-coral-red); font-size: 18px; cursor: pointer; padding: 0 4px; }
.remove-btn:hover { color: var(--error-dark-red); }

.add-item-btn { width: 100%; margin-top: 4px; margin-bottom: 16px; }

.form-actions { margin-top: 16px; }
.form-actions .btn { width: 100%; }

/* ---- Navigation ---- */
.nav-actions {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border-light-gray);
}
.nav-position { font-size: 13px; color: var(--text-medium-gray); }

.next-prompt { margin-top: 12px; text-align: center; }

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
  gap: 4px;
  flex-wrap: wrap;
}

.edits-indicator {
  font-size: 12px;
  color: var(--primary-deep-teal);
  font-weight: 600;
}
.editor-section { display: flex; flex-direction: column; }
.editor-notice {
  background: var(--info-light-blue);
  border-left: 3px solid var(--primary-deep-teal);
  padding: 8px 12px;
  font-size: 13px;
  color: var(--info-dark-blue);
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
