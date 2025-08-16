<template>
  <div class="calendar-widget" :data-work-week="showWorkWeekOnly">
    <div class="calendar-header">
      <button @click="previousMonth" class="nav-btn">‹</button>
      <h3 class="month-year">{{ currentMonthYear }}</h3>
      <button @click="nextMonth" class="nav-btn">›</button>
    </div>
    
    <div class="calendar-controls">
      <label class="work-week-toggle">
        <input 
          type="checkbox" 
          v-model="showWorkWeekOnly" 
          @change="toggleWorkWeek"
        />
        <span class="toggle-slider"></span>
        <span class="toggle-label">Work Week Only</span>
      </label>
    </div>
    
    <div class="calendar-grid">
      <div 
        class="calendar-day-header" 
        v-for="day in displayDayHeaders" 
        :key="day"
      >{{ day }}</div>
      
      <div 
        v-for="date in displayCalendarDates" 
        :key="date.fullDate"
        :class="['calendar-date', {
          'other-month': !date.isCurrentMonth,
          'today': date.isToday,
          'has-events': date.events.length > 0
        }]"
      >
        <span class="date-number">{{ date.day }}</span>
        <div class="date-events">
          <div 
            v-for="event in date.events.slice(0, 2)" 
            :key="event.id"
            :class="['event-dot', `event-${event.type}`]"
            :title="event.title"
          ></div>
          <div v-if="date.events.length > 2" class="event-more">+{{ date.events.length - 2 }}</div>
        </div>
      </div>
    </div>
    
    <div class="calendar-legend">
      <div class="legend-item">
        <div class="event-dot event-milestone"></div>
        <span>Milestones</span>
      </div>
      <div class="legend-item">
        <div class="event-dot event-deadline"></div>
        <span>Deadlines</span>
      </div>
      <div class="legend-item">
        <div class="event-dot event-meeting"></div>
        <span>Meetings</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CalendarWidget',
  props: {
    events: {
      type: Array,
      default: () => []
    },
    showLegend: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      currentDate: new Date(),
      dayHeaders: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
      workWeekHeaders: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
      showWorkWeekOnly: true
    }
  },
  computed: {
    currentMonthYear() {
      return this.currentDate.toLocaleDateString('en-US', { 
        month: 'long', 
        year: 'numeric' 
      })
    },
    
    displayDayHeaders() {
      return this.showWorkWeekOnly ? this.workWeekHeaders : this.dayHeaders
    },
    
    displayCalendarDates() {
      return this.showWorkWeekOnly ? this.workWeekCalendarDates : this.calendarDates
    },
    
    calendarDates() {
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth()
      const today = new Date()
      
      // First day of the month
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      
      // Start from the first Sunday of the calendar view
      const startDate = new Date(firstDay)
      startDate.setDate(startDate.getDate() - firstDay.getDay())
      
      // Generate 42 days (6 weeks)
      const dates = []
      for (let i = 0; i < 42; i++) {
        const date = new Date(startDate)
        date.setDate(startDate.getDate() + i)
        
        const dateStr = date.toISOString().split('T')[0]
        const dayEvents = this.events.filter(event => 
          event.date === dateStr || 
          (event.startDate && event.startDate <= dateStr && event.endDate && event.endDate >= dateStr)
        )
        
        dates.push({
          day: date.getDate(),
          fullDate: dateStr,
          isCurrentMonth: date.getMonth() === month,
          isToday: date.toDateString() === today.toDateString(),
          events: dayEvents,
          dayOfWeek: date.getDay()
        })
      }
      
      return dates
    },
    
    workWeekCalendarDates() {
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth()
      const today = new Date()
      
      // First day of the month
      const firstDay = new Date(year, month, 1)
      
      // Find first Monday of the calendar view
      const startDate = new Date(firstDay)
      const dayOfWeek = firstDay.getDay()
      // If first day is Sunday (0), go back 6 days to Monday
      // If first day is Monday (1), stay
      // If first day is Tuesday (2), go back 1 day to Monday, etc.
      const daysToSubtract = dayOfWeek === 0 ? 6 : dayOfWeek - 1
      startDate.setDate(startDate.getDate() - daysToSubtract)
      
      // Generate work week dates (Monday-Friday only)
      const dates = []
      let currentWeekStart = new Date(startDate)
      
      // Generate 6 weeks worth of work days
      for (let week = 0; week < 6; week++) {
        for (let day = 0; day < 5; day++) { // Monday to Friday
          const date = new Date(currentWeekStart)
          date.setDate(currentWeekStart.getDate() + day)
          
          const dateStr = date.toISOString().split('T')[0]
          const dayEvents = this.events.filter(event => 
            event.date === dateStr || 
            (event.startDate && event.startDate <= dateStr && event.endDate && event.endDate >= dateStr)
          )
          
          dates.push({
            day: date.getDate(),
            fullDate: dateStr,
            isCurrentMonth: date.getMonth() === month,
            isToday: date.toDateString() === today.toDateString(),
            events: dayEvents,
            dayOfWeek: date.getDay()
          })
        }
        // Move to next week
        currentWeekStart.setDate(currentWeekStart.getDate() + 7)
      }
      
      return dates
    }
  },
  methods: {
    previousMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1, 1)
    },
    
    nextMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 1)
    },
    
    goToToday() {
      this.currentDate = new Date()
    },
    
    toggleWorkWeek() {
      // Method to handle work week toggle if needed for additional logic
      this.$emit('work-week-changed', this.showWorkWeekOnly)
    }
  }
}
</script>

<style scoped>
.calendar-widget {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.calendar-controls {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.work-week-toggle {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  user-select: none;
}

.work-week-toggle input[type="checkbox"] {
  display: none;
}

.toggle-slider {
  position: relative;
  width: 50px;
  height: 24px;
  background: #e2e8f0;
  border-radius: 12px;
  transition: background-color 0.3s ease;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform 0.3s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.work-week-toggle input[type="checkbox"]:checked + .toggle-slider {
  background: #205493;
}

.work-week-toggle input[type="checkbox"]:checked + .toggle-slider::before {
  transform: translateX(26px);
}

.toggle-label {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

.month-year {
  margin: 0;
  color: #205493;
  font-size: 1.2rem;
  font-weight: 600;
}

.nav-btn {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  font-size: 1.2rem;
  color: #64748b;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  background: #205493;
  color: white;
  border-color: #205493;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(var(--calendar-columns, 7), 1fr);
  gap: 1px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.calendar-widget[data-work-week="true"] .calendar-grid {
  --calendar-columns: 5;
}

.calendar-day-header {
  background: #f1f5f9;
  padding: 0.5rem;
  text-align: center;
  font-weight: 600;
  font-size: 0.8rem;
  color: #64748b;
  text-transform: uppercase;
}

.calendar-date {
  background: white;
  min-height: 80px;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.calendar-date:hover {
  background: #f8fafc;
}

.calendar-date.other-month {
  background: #f9fafb;
  color: #9ca3af;
}

.calendar-date.today {
  background: #dbeafe;
}

.calendar-date.today .date-number {
  background: #205493;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.date-number {
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.date-events {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  margin-top: auto;
}

.event-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.event-milestone {
  background: #009964;
}

.event-deadline {
  background: #dc2626;
}

.event-meeting {
  background: #7c3aed;
}

.event-more {
  font-size: 0.7rem;
  color: #6b7280;
  margin-left: 2px;
}

.calendar-legend {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #6b7280;
}

/* Responsive Design */
@media (max-width: 768px) {
  .calendar-date {
    min-height: 60px;
    padding: 0.25rem;
  }
  
  .calendar-legend {
    gap: 1rem;
    font-size: 0.75rem;
  }
  
  .month-year {
    font-size: 1rem;
  }
  
  .calendar-controls {
    margin-bottom: 0.75rem;
  }
  
  .toggle-label {
    font-size: 0.8rem;
  }
  
  .toggle-slider {
    width: 44px;
    height: 20px;
  }
  
  .toggle-slider::before {
    width: 16px;
    height: 16px;
  }
  
  .work-week-toggle input[type="checkbox"]:checked + .toggle-slider::before {
    transform: translateX(24px);
  }
}
</style>
