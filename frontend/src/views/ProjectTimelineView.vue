<template>
  <div class="timeline-page">

    <!-- Loading / Error -->
    <div v-if="loading" class="loading-state">Loading timeline…</div>
    <div v-else-if="emptyMessage" class="empty-state">{{ emptyMessage }}</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>

    <template v-else>
      <!-- ── Header ──────────────────────────────────────────────────── -->
      <div class="tl-header">
        <div class="tl-header-left">
          <button class="back-btn" @click="$router.back()">← Back</button>
          <div>
            <h1>{{ project.name }}</h1>
            <p v-if="project.description" class="project-desc">{{ project.description }}</p>
          </div>
          <span :class="['status-badge', `status-${project.status}`]">{{ project.status }}</span>
        </div>

        <div class="tl-header-right">
          <!-- Progress ring -->
          <div class="progress-ring" :title="`${completedCount} of ${tasks.length} tasks complete`">
            <svg viewBox="0 0 36 36" class="ring-svg">
              <circle cx="18" cy="18" r="15.9" fill="none" stroke="#e9ecef" stroke-width="3"/>
              <circle cx="18" cy="18" r="15.9" fill="none" stroke="#008C9E" stroke-width="3"
                stroke-dasharray="100" :stroke-dashoffset="100 - progressPct"
                stroke-linecap="round" transform="rotate(-90 18 18)"/>
            </svg>
            <span class="ring-label">{{ progressPct }}%</span>
          </div>

          <!-- Stat chips -->
          <div class="stat-chips">
            <div class="stat-chip">
              <span class="chip-val">{{ tasks.length }}</span>
              <span class="chip-lbl">Tasks</span>
            </div>
            <div class="stat-chip chip-green">
              <span class="chip-val">{{ completedCount }}</span>
              <span class="chip-lbl">Done</span>
            </div>
            <div class="stat-chip chip-red">
              <span class="chip-val">{{ overdueCount }}</span>
              <span class="chip-lbl">Overdue</span>
            </div>
            <div class="stat-chip chip-teal">
              <span class="chip-val">{{ milestones.length }}</span>
              <span class="chip-lbl">Milestones</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Filters ─────────────────────────────────────────────────── -->
      <div class="filters-bar no-print">
        <label class="filter-label">Filter by assignee:</label>
        <select v-model="assigneeFilter" class="filter-select">
          <option value="">All assignees</option>
          <option v-for="a in assignees" :key="a" :value="a">{{ a }}</option>
        </select>
        <label class="filter-label">Status:</label>
        <select v-model="statusFilter" class="filter-select">
          <option value="">All statuses</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="review">Review</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <button class="print-btn no-print" @click="printTimeline">🖨️ Print</button>
      </div>

      <!-- ── Gantt Chart ─────────────────────────────────────────────── -->
      <div class="card gantt-card">
        <h2 class="section-title">📅 Gantt Chart</h2>

        <div v-if="ganttItems.length === 0" class="empty-gantt">
          No tasks or milestones with dates to display.
        </div>

        <div v-else class="gantt-wrapper">
          <!-- Label column -->
          <div class="gantt-labels">
            <div class="gantt-axis-spacer"></div>
            <div v-for="item in ganttItems" :key="item.key" class="gantt-label-row"
                 :class="{ 'label-milestone': item.type === 'milestone' }">
              <span class="label-icon">{{ item.type === 'milestone' ? '◆' : '▸' }}</span>
              <span class="label-text" :title="item.title">{{ item.title }}</span>
            </div>
          </div>

          <!-- Chart area (scrollable) -->
          <div class="gantt-chart-area" ref="ganttArea">
            <!-- Month headers -->
            <div class="gantt-months">
              <div v-for="m in ganttMonths" :key="m.label"
                   class="gantt-month" :style="{ left: m.left + 'px', width: m.width + 'px' }">
                {{ m.label }}
              </div>
            </div>

            <!-- Rows -->
            <div class="gantt-rows" :style="{ width: ganttTotalWidth + 'px' }">
              <div v-for="item in ganttItems" :key="item.key" class="gantt-row">
                <!-- Stripe background -->
                <div class="gantt-row-bg"></div>

                <!-- Task bar -->
                <div v-if="item.type === 'task'"
                     class="gantt-bar"
                     :class="['priority-' + item.priority, item.overdue ? 'overdue' : '', 'status-bar-' + item.status]"
                     :style="{ left: item.left + 'px', width: Math.max(item.width, 8) + 'px' }"
                     @mouseenter="showTooltip($event, item)"
                     @mouseleave="hideTooltip">
                  <span class="bar-label">{{ item.title }}</span>
                </div>

                <!-- Milestone diamond -->
                <div v-else
                     class="gantt-diamond"
                     :class="[item.overdue ? 'overdue' : '', 'ms-status-' + item.status]"
                     :style="{ left: (item.left - 8) + 'px' }"
                     @mouseenter="showTooltip($event, item)"
                     @mouseleave="hideTooltip">
                </div>
              </div>

              <!-- Today line -->
              <div v-if="todayLeft !== null" class="today-line"
                   :style="{ left: todayLeft + 'px' }">
                <span class="today-label">Today</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Unscheduled tasks -->
        <div v-if="unscheduledTasks.length" class="unscheduled-section">
          <h3 class="unscheduled-title">Unscheduled Tasks (no due date)</h3>
          <div class="unscheduled-list">
            <span v-for="t in unscheduledTasks" :key="t.id"
                  :class="['unsched-chip', 'priority-chip-' + t.priority]">
              {{ t.title }}
            </span>
          </div>
        </div>
      </div>

      <!-- Tooltip -->
      <div v-if="tooltip.visible" class="gantt-tooltip" :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }">
        <div class="tooltip-title">{{ tooltip.item.title }}</div>
        <div v-if="tooltip.item.type === 'milestone'" class="tooltip-row">
          <span class="tooltip-key">Date:</span> {{ tooltip.item.dateLabel }}
        </div>
        <template v-else>
          <div class="tooltip-row"><span class="tooltip-key">Status:</span> {{ tooltip.item.status }}</div>
          <div class="tooltip-row"><span class="tooltip-key">Priority:</span> {{ tooltip.item.priority }}</div>
          <div v-if="tooltip.item.assignee" class="tooltip-row">
            <span class="tooltip-key">Assignee:</span> {{ tooltip.item.assignee }}
          </div>
          <div class="tooltip-row"><span class="tooltip-key">Due:</span> {{ tooltip.item.dateLabel }}</div>
        </template>
        <div v-if="tooltip.item.overdue" class="tooltip-overdue">⚠️ Overdue</div>
      </div>

      <!-- ── Work Breakdown Table ────────────────────────────────────── -->
      <div class="card table-card">
        <h2 class="section-title">📋 Work Breakdown</h2>

        <div v-for="group in taskGroups" :key="group.milestoneId" class="task-group">
          <div class="group-header">
            <span class="group-icon">{{ group.milestoneId ? '◆' : '📁' }}</span>
            <span class="group-name">{{ group.milestoneName }}</span>
            <span v-if="group.milestoneId" :class="['ms-badge', 'ms-badge-' + group.milestoneStatus]">
              {{ group.milestoneStatus }}
            </span>
            <span v-if="group.milestoneDate" class="group-date">{{ fmtDate(group.milestoneDate) }}</span>
          </div>

          <table class="breakdown-table">
            <thead>
              <tr>
                <th @click="sortBy('title')" class="sortable">Task <span class="sort-icon">{{ sortIcon('title') }}</span></th>
                <th @click="sortBy('assigned_to')" class="sortable">Assignee <span class="sort-icon">{{ sortIcon('assigned_to') }}</span></th>
                <th @click="sortBy('priority')" class="sortable">Priority <span class="sort-icon">{{ sortIcon('priority') }}</span></th>
                <th @click="sortBy('status')" class="sortable">Status <span class="sort-icon">{{ sortIcon('status') }}</span></th>
                <th @click="sortBy('due_date')" class="sortable">Due Date <span class="sort-icon">{{ sortIcon('due_date') }}</span></th>
                <th>Collection</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in sortedGroupTasks(group.tasks)" :key="task.id"
                  :class="{ 'row-overdue': isTaskOverdue(task), 'row-done': task.status === 'completed' }">
                <td class="task-title-cell">{{ task.title }}</td>
                <td>{{ task.assigned_to || '—' }}</td>
                <td><span :class="['priority-badge', 'priority-' + task.priority]">{{ task.priority }}</span></td>
                <td><span :class="['status-chip', 'task-status-' + task.status]">{{ task.status.replace('_', ' ') }}</span></td>
                <td :class="{ 'cell-overdue': isTaskOverdue(task) }">{{ task.due_date ? fmtDate(task.due_date) : '—' }}</td>
                <td>{{ task.collection_name || '—' }}</td>
              </tr>
              <tr v-if="!group.tasks.length">
                <td colspan="6" class="empty-group">No tasks in this milestone.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="!filteredTasks.length" class="empty-table">No tasks match the current filters.</div>
      </div>
    </template>
  </div>
</template>

<script>
import { getProjectTimeline } from '@/api/projects'

const PRIORITY_ORDER = { urgent: 0, high: 1, medium: 2, low: 3 }
const DAY_MS = 86400000
const PX_PER_DAY = 18

export default {
  name: 'ProjectTimelineView',
  data() {
    return {
      loading: true,
      error: '',
      emptyMessage: '',
      project: {},
      milestones: [],
      tasks: [],
      assigneeFilter: '',
      statusFilter: '',
      sortCol: 'due_date',
      sortDir: 1,
      tooltip: { visible: false, x: 0, y: 0, item: {} },
    }
  },
  async created() {
    try {
      const data = await getProjectTimeline(this.$route.params.id)
      this.project = data?.project || {}
      this.milestones = Array.isArray(data?.milestones) ? data.milestones : []
      this.tasks = Array.isArray(data?.tasks) ? data.tasks : []

      if (!this.project?.id && this.milestones.length === 0 && this.tasks.length === 0) {
        this.emptyMessage = 'No timeline data is available for this project yet.'
      }
    } catch (e) {
      const message = String(e?.response?.data?.error || e?.message || '').toLowerCase()
      const isNoDataCase =
        message.includes('404') ||
        message.includes('405') ||
        message.includes('not found') ||
        message.includes('method not allowed')

      if (isNoDataCase) {
        this.emptyMessage = 'No timeline data is available for this project yet.'
      } else {
        this.error = e?.response?.data?.error || 'Unable to load timeline right now.'
      }
    } finally {
      this.loading = false
    }
  },
  computed: {
    today() { return new Date(); },
    filteredTasks() {
      return this.tasks.filter(t => {
        if (this.assigneeFilter && t.assigned_to !== this.assigneeFilter) return false
        if (this.statusFilter && t.status !== this.statusFilter) return false
        return true
      })
    },
    assignees() {
      const s = new Set(this.tasks.map(t => t.assigned_to).filter(Boolean))
      return [...s].sort()
    },
    completedCount() { return this.tasks.filter(t => t.status === 'completed').length },
    overdueCount() { return this.tasks.filter(t => this.isTaskOverdue(t)).length },
    progressPct() {
      if (!this.tasks.length) return 0
      return Math.round((this.completedCount / this.tasks.length) * 100)
    },

    // Gantt helpers
    ganttDatedTasks() {
      return this.filteredTasks.filter(t => t.due_date)
    },
    unscheduledTasks() {
      return this.filteredTasks.filter(t => !t.due_date)
    },
    ganttMinDate() {
      const dates = []
      if (this.project.start_date) dates.push(new Date(this.project.start_date))
      this.milestones.forEach(m => { if (m.date) dates.push(new Date(m.date)) })
      this.ganttDatedTasks.forEach(t => { if (t.due_date) dates.push(new Date(t.due_date)) })
      dates.push(this.today)
      if (!dates.length) return this.today
      return new Date(Math.min(...dates.map(d => d.getTime())) - 14 * DAY_MS)
    },
    ganttMaxDate() {
      const dates = []
      if (this.project.target_completion) dates.push(new Date(this.project.target_completion))
      this.milestones.forEach(m => { if (m.date) dates.push(new Date(m.date)) })
      this.ganttDatedTasks.forEach(t => { if (t.due_date) dates.push(new Date(t.due_date)) })
      dates.push(this.today)
      if (!dates.length) return new Date(this.today.getTime() + 30 * DAY_MS)
      return new Date(Math.max(...dates.map(d => d.getTime())) + 14 * DAY_MS)
    },
    ganttTotalWidth() {
      const days = (this.ganttMaxDate - this.ganttMinDate) / DAY_MS
      return Math.max(days * PX_PER_DAY, 400)
    },
    ganttMonths() {
      const months = []
      const d = new Date(this.ganttMinDate)
      d.setDate(1)
      while (d <= this.ganttMaxDate) {
        const left = this.dateToX(d)
        const nextMonth = new Date(d.getFullYear(), d.getMonth() + 1, 1)
        const width = this.dateToX(nextMonth) - left
        months.push({
          label: d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
          left, width,
        })
        d.setMonth(d.getMonth() + 1)
      }
      return months
    },
    todayLeft() {
      if (this.today < this.ganttMinDate || this.today > this.ganttMaxDate) return null
      return this.dateToX(this.today)
    },
    ganttItems() {
      const items = []
      // Milestones sorted by date
      for (const m of this.milestones.filter(m => m.date)) {
        items.push({
          key: `ms-${m.id}`,
          type: 'milestone',
          title: m.name,
          left: this.dateToX(new Date(m.date)),
          width: 0,
          status: m.status,
          overdue: this.isMilestoneOverdue(m),
          dateLabel: this.fmtDate(m.date),
          priority: '',
          assignee: '',
        })
      }
      // Tasks with dates
      for (const t of this.ganttDatedTasks) {
        const due = new Date(t.due_date)
        // Use created_at as start if before due date
        let startDate = t.created_at ? new Date(t.created_at) : due
        if (startDate >= due) startDate = new Date(due.getTime() - DAY_MS)
        // Clamp start to ganttMinDate
        if (startDate < this.ganttMinDate) startDate = this.ganttMinDate
        const left = this.dateToX(startDate)
        const right = this.dateToX(due)
        items.push({
          key: `task-${t.id}`,
          type: 'task',
          title: t.title,
          left,
          width: Math.max(right - left, 8),
          status: t.status,
          priority: t.priority,
          overdue: this.isTaskOverdue(t),
          assignee: t.assigned_to,
          dateLabel: this.fmtDate(t.due_date),
        })
      }
      return items
    },

    // Work breakdown table
    taskGroups() {
      const groups = []
      // One group per milestone
      for (const m of [...this.milestones].sort((a, b) => (a.date || '') < (b.date || '') ? -1 : 1)) {
        groups.push({
          milestoneId: m.id,
          milestoneName: m.name,
          milestoneStatus: m.status,
          milestoneDate: m.date,
          tasks: [], // tasks don't reference milestones directly — general group used
        })
      }
      // All tasks go in "General" unless there are no milestones
      const general = { milestoneId: null, milestoneName: 'General Tasks', milestoneStatus: '', milestoneDate: null, tasks: this.filteredTasks }
      if (this.milestones.length === 0) {
        return [general]
      }
      // If milestones exist show them + general tasks below
      groups.push(general)
      return groups
    },
  },
  methods: {
    dateToX(date) {
      return ((date - this.ganttMinDate) / DAY_MS) * PX_PER_DAY
    },
    fmtDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    },
    isTaskOverdue(task) {
      if (!task.due_date) return false
      if (task.status === 'completed' || task.status === 'cancelled') return false
      return new Date(task.due_date) < this.today
    },
    isMilestoneOverdue(m) {
      if (!m.date) return false
      if (m.status === 'completed') return false
      return new Date(m.date) < this.today
    },
    showTooltip(event, item) {
      this.tooltip = { visible: true, x: event.clientX + 12, y: event.clientY + 12, item }
    },
    hideTooltip() { this.tooltip.visible = false },
    sortBy(col) {
      if (this.sortCol === col) { this.sortDir = -this.sortDir } else { this.sortCol = col; this.sortDir = 1 }
    },
    sortIcon(col) {
      if (this.sortCol !== col) return '↕'
      return this.sortDir === 1 ? '↑' : '↓'
    },
    sortedGroupTasks(tasks) {
      return [...tasks].sort((a, b) => {
        let va = a[this.sortCol] ?? ''
        let vb = b[this.sortCol] ?? ''
        if (this.sortCol === 'priority') { va = PRIORITY_ORDER[va] ?? 99; vb = PRIORITY_ORDER[vb] ?? 99 }
        if (va < vb) return -this.sortDir
        if (va > vb) return this.sortDir
        return 0
      })
    },
    printTimeline() { window.print() },
  },
}
</script>

<style scoped>
.timeline-page { padding: 1.5rem; max-width: 1300px; color: #333; }

/* Header */
.tl-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 1.25rem; flex-wrap: wrap; gap: 1rem;
}
.tl-header-left { display: flex; align-items: flex-start; gap: 1rem; flex: 1; }
.back-btn { background: none; border: 1px solid #ced4da; border-radius: 6px; padding: 0.35rem 0.75rem; cursor: pointer; color: #495057; font-size: 0.875rem; white-space: nowrap; }
.back-btn:hover { background: #f8f9fa; }
.tl-header-left h1 { margin: 0; font-size: 2rem; font-weight: 300; color: #005B6E; }
.project-desc { margin: 0.25rem 0 0; color: #6c757d; font-size: 0.9rem; }
.status-badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; text-transform: capitalize; }
.status-planning { background: #e3f2fd; color: #1565c0; }
.status-active { background: #e8f5e9; color: #2e7d32; }
.status-review { background: #fff8e1; color: #f57f17; }
.status-completed { background: #f3e5f5; color: #6a1b9a; }
.status-on_hold { background: #fce4ec; color: #880e4f; }

.tl-header-right { display: flex; align-items: center; gap: 1.5rem; }
.progress-ring { position: relative; width: 72px; height: 72px; }
.ring-svg { width: 100%; height: 100%; }
circle { transition: stroke-dashoffset 0.6s ease; }
.ring-label { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: 700; color: #005B6E; }

.stat-chips { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.stat-chip { display: flex; flex-direction: column; align-items: center; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 0.4rem 0.8rem; min-width: 60px; }
.chip-val { font-size: 1.3rem; font-weight: 700; line-height: 1; }
.chip-lbl { font-size: 0.7rem; color: #6c757d; text-transform: uppercase; letter-spacing: .04em; }
.chip-green .chip-val { color: #2e7d32; }
.chip-red .chip-val { color: #c62828; }
.chip-teal .chip-val { color: #005B6E; }

/* Filters */
.filters-bar { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.filter-label { font-size: 0.85rem; color: #495057; }
.filter-select { border: 1px solid #ced4da; border-radius: 6px; padding: 0.35rem 0.6rem; font-size: 0.875rem; }
.print-btn { margin-left: auto; background: #f8f9fa; border: 1px solid #ced4da; border-radius: 6px; padding: 0.35rem 0.9rem; cursor: pointer; font-size: 0.875rem; }
.print-btn:hover { background: #e9ecef; }

/* Cards */
.card { background: #fff; border: 1px solid #dee2e6; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }
.section-title { margin: 0 0 1.25rem; font-size: 1.1rem; font-weight: 600; color: #005B6E; }

/* Gantt */
.gantt-wrapper { display: flex; overflow-x: auto; }
.gantt-labels { flex-shrink: 0; width: 200px; padding-right: 0.5rem; }
.gantt-axis-spacer { height: 28px; }
.gantt-label-row { height: 32px; display: flex; align-items: center; gap: 0.35rem; font-size: 0.8rem; overflow: hidden; }
.label-milestone { font-weight: 600; }
.label-icon { flex-shrink: 0; color: #008C9E; }
.label-text { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 175px; }

.gantt-chart-area { flex: 1; overflow-x: auto; position: relative; }
.gantt-months { position: relative; height: 28px; background: #f8f9fa; border-bottom: 1px solid #dee2e6; }
.gantt-month { position: absolute; font-size: 0.72rem; color: #6c757d; padding: 0 4px; line-height: 28px; white-space: nowrap; overflow: hidden; border-left: 1px solid #e9ecef; }

.gantt-rows { position: relative; }
.gantt-row { position: relative; height: 32px; }
.gantt-row-bg { position: absolute; inset: 0; border-bottom: 1px solid #f0f0f0; }
.gantt-row:nth-child(even) .gantt-row-bg { background: #fafafa; }

.gantt-bar {
  position: absolute; top: 7px; height: 18px; border-radius: 4px; cursor: pointer;
  overflow: hidden; white-space: nowrap;
  transition: opacity 0.15s;
}
.gantt-bar:hover { opacity: .85; }
.bar-label { font-size: 0.72rem; color: #fff; padding: 0 5px; line-height: 18px; display: block; overflow: hidden; text-overflow: ellipsis; }

/* Priority colors for bars */
.priority-urgent { background: #dc3545; }
.priority-high    { background: #fd7e14; }
.priority-medium  { background: #008C9E; }
.priority-low     { background: #adb5bd; }
.status-bar-completed { opacity: .55; }
.status-bar-cancelled { opacity: .35; text-decoration: line-through; }
.gantt-bar.overdue { outline: 2px solid #c62828; }

/* Milestone diamond */
.gantt-diamond {
  position: absolute; top: 8px; width: 16px; height: 16px;
  background: #005B6E; transform: rotate(45deg); cursor: pointer;
}
.gantt-diamond.overdue { background: #dc3545; }
.ms-status-completed { background: #2e7d32; }

/* Today line */
.today-line { position: absolute; top: 0; bottom: 0; width: 2px; background: #dc3545; z-index: 5; pointer-events: none; }
.today-label { position: absolute; top: 0; left: 3px; font-size: 0.68rem; color: #dc3545; white-space: nowrap; background: #fff; }

/* Unscheduled */
.unscheduled-section { margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid #dee2e6; }
.unscheduled-title { font-size: 0.875rem; font-weight: 600; color: #6c757d; margin: 0 0 0.5rem; }
.unscheduled-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.unsched-chip { padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; background: #f8f9fa; border: 1px solid #dee2e6; }
.priority-chip-urgent { border-color: #dc3545; color: #dc3545; }
.priority-chip-high   { border-color: #fd7e14; color: #fd7e14; }
.priority-chip-medium { border-color: #008C9E; color: #008C9E; }

/* Tooltip */
.gantt-tooltip {
  position: fixed; z-index: 1000; background: #212529; color: #fff;
  padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; pointer-events: none;
  max-width: 240px; box-shadow: 0 4px 12px rgba(0,0,0,.3);
}
.tooltip-title { font-weight: 600; margin-bottom: 4px; }
.tooltip-row { margin: 2px 0; }
.tooltip-key { color: #adb5bd; margin-right: 4px; }
.tooltip-overdue { color: #ff6b6b; margin-top: 4px; font-size: 0.78rem; }

/* Work breakdown table */
.task-group { margin-bottom: 1.5rem; }
.group-header { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.75rem; background: #f0f9f9; border-radius: 6px; margin-bottom: 0.5rem; border-left: 4px solid #008C9E; }
.group-icon { color: #008C9E; }
.group-name { font-weight: 600; font-size: 0.95rem; }
.group-date { margin-left: auto; font-size: 0.8rem; color: #6c757d; }

.ms-badge { padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 600; }
.ms-badge-planned     { background: #e3f2fd; color: #1565c0; }
.ms-badge-in-progress { background: #fff8e1; color: #f57f17; }
.ms-badge-completed   { background: #e8f5e9; color: #2e7d32; }
.ms-badge-overdue     { background: #fde8ea; color: #c62828; }

.breakdown-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.breakdown-table th { text-align: left; padding: 8px 10px; border-bottom: 2px solid #dee2e6; color: #495057; font-size: 0.8rem; background: #f8f9fa; }
.breakdown-table td { padding: 7px 10px; border-bottom: 1px solid #f0f0f0; }
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { background: #e9ecef; }
.sort-icon { color: #adb5bd; font-size: 0.75rem; }

.task-title-cell { max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.priority-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 600; text-transform: capitalize; }
.priority-urgent { background: #fde8ea; color: #c62828; }
.priority-high   { background: #fff3e0; color: #e65100; }
.priority-medium { background: #e0f7f9; color: #005B6E; }
.priority-low    { background: #f5f5f5; color: #757575; }

.status-chip { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 600; text-transform: capitalize; }
.task-status-todo        { background: #f8f9fa; color: #495057; }
.task-status-in_progress { background: #e3f2fd; color: #1565c0; }
.task-status-review      { background: #fff8e1; color: #f57f17; }
.task-status-completed   { background: #e8f5e9; color: #2e7d32; }
.task-status-cancelled   { background: #f5f5f5; color: #9e9e9e; }

.row-overdue td { background: #fff5f5; }
.row-done td { opacity: .65; }
.cell-overdue { color: #c62828; font-weight: 600; }

.empty-group { color: #adb5bd; font-style: italic; text-align: center; padding: 1rem; }
.empty-gantt, .empty-table { text-align: center; color: #6c757d; padding: 2rem; }

/* Loading/Error */
.loading-state, .empty-state, .error-state { text-align: center; padding: 3rem; color: #6c757d; }
.empty-state { color: #4c6f7d; }
.error-state { color: #dc3545; }

/* Print */
@media print {
  .no-print { display: none !important; }
  .card { border: 1px solid #ccc; box-shadow: none; }
  .gantt-tooltip { display: none !important; }
  .back-btn { display: none; }
  body { font-size: 11pt; }
  .timeline-page { padding: 0; max-width: 100%; }
}

@media (max-width: 768px) {
  .tl-header { flex-direction: column; }
  .gantt-labels { width: 130px; }
  .label-text { max-width: 110px; }
}
</style>
