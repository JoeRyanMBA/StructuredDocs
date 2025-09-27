<template>
  <div class="compact-toolbar">
    <!-- Metrics Icon -->
    <button 
      v-if="showMetrics" 
      @click="openMetricsModal" 
      class="toolbar-icon" 
      title="View Key Metrics"
    >
      <i class="bi bi-bar-chart"></i>
    </button>
    
    <!-- Calendar Icon -->
    <button 
      v-if="showCalendar" 
      @click="openCalendarModal" 
      class="toolbar-icon"
      title="View Calendar"
    >
      <i class="bi bi-calendar-event"></i>
    </button>

    <!-- Metrics Slide-out Panel -->
    <div v-if="metricsModalOpen" class="slide-overlay" @click.self="closeMetricsModal">
      <div class="slide-panel metrics-panel" :class="{ 'slide-in': metricsModalOpen }">
        <div class="panel-header">
          <h2>Key Metrics</h2>
          <button @click="closeMetricsModal" class="close-btn">×</button>
        </div>
        <div class="panel-body">
          <div class="metrics-stack">
            <slot name="metrics"></slot>
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar Slide-out Panel -->
    <div v-if="calendarModalOpen" class="slide-overlay" @click.self="closeCalendarModal">
      <div class="slide-panel calendar-panel" :class="{ 'slide-in': calendarModalOpen }">
        <div class="panel-header">
          <h2>Calendar</h2>
          <button @click="closeCalendarModal" class="close-btn">×</button>
        </div>
        <div class="panel-body">
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

/* Slide-out overlay */
.slide-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  align-items: stretch;
}

/* Slide panel base */
.slide-panel {
  background: white;
  width: 400px;
  max-width: 90vw;
  height: 100%;
  box-shadow: var(--shadow-lg);
  transform: translateX(100%);
  transition: transform 0.3s ease-in-out;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.slide-panel.slide-in {
  transform: translateX(0);
}

/* Panel header */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-light-gray);
  background: var(--bg-white);
  flex-shrink: 0;
}

.panel-header h2 {
  margin: 0;
  color: var(--primary-deep-teal);
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary-cool-gray);
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--extended-lavender-gray);
  color: var(--primary-deep-teal);
}

/* Panel body */
.panel-body {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
}

/* Stacked metrics layout */
.metrics-stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Override metric card layout for stacked display */
.metrics-stack .metric-card {
  width: 100%;
  min-width: unset;
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
  
  .slide-panel {
    width: 100%;
    max-width: 100vw;
  }
  
  .panel-header {
    padding: 1rem;
  }
  
  .panel-body {
    padding: 1rem;
  }
  
  .metrics-stack {
    gap: 0.75rem;
  }
}
</style>