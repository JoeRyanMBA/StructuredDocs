<template>
  <div class="compact-toolbar">
    <!-- Metrics Icon -->
    <button 
      v-if="showMetrics" 
      @click="openMetricsModal" 
      class="toolbar-icon" 
      title="View Key Metrics"
    >
      <i class="fas fa-chart-bar"></i>
    </button>
    
    <!-- Calendar Icon -->
    <button 
      v-if="showCalendar" 
      @click="openCalendarModal" 
      class="toolbar-icon"
      title="View Calendar"
    >
      <i class="fas fa-calendar"></i>
    </button>

    <!-- Metrics Modal -->
    <div v-if="metricsModalOpen" class="modal-overlay" @click.self="closeMetricsModal">
      <div class="modal metrics-modal">
        <div class="modal-header">
          <h2>Key Metrics</h2>
          <button @click="closeMetricsModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="metrics-grid">
            <slot name="metrics"></slot>
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar Modal -->
    <div v-if="calendarModalOpen" class="modal-overlay" @click.self="closeCalendarModal">
      <div class="modal calendar-modal">
        <div class="modal-header">
          <h2>Calendar</h2>
          <button @click="closeCalendarModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <slot name="calendar"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CompactToolbar',
  props: {
    showMetrics: {
      type: Boolean,
      default: false
    },
    showCalendar: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      metricsModalOpen: false,
      calendarModalOpen: false
    }
  },
  methods: {
    openMetricsModal() {
      this.metricsModalOpen = true
    },
    closeMetricsModal() {
      this.metricsModalOpen = false
    },
    openCalendarModal() {
      this.calendarModalOpen = true
    },
    closeCalendarModal() {
      this.calendarModalOpen = false
    }
  }
}
</script>

<style scoped>
.compact-toolbar {
  position: fixed;
  top: calc(var(--header-height) + var(--ticker-height) + 1rem);
  right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  z-index: 999;
}

.toolbar-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--primary-deep-teal);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  box-shadow: var(--shadow-md);
  transition: all 0.2s ease;
}

.toolbar-icon:hover {
  background: var(--primary-medium-teal);
  transform: scale(1.1);
  box-shadow: var(--shadow-lg);
}

.toolbar-icon:active {
  transform: scale(0.95);
}

.modal {
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

.metrics-modal {
  width: 800px;
  max-width: 90vw;
}

.calendar-modal {
  width: 700px;
  max-width: 90vw;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-light-gray);
}

.modal-header h2 {
  margin: 0;
  color: var(--primary-deep-teal);
}

.modal-body {
  padding: 1.5rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .compact-toolbar {
    top: calc(var(--header-height) + var(--ticker-height) + 0.5rem);
    right: 1rem;
  }
  
  .toolbar-icon {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>