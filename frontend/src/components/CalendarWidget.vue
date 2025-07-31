<template>
  <div class="calendar-widget">
    <div class="calendar-header">
      <button @click="previousMonth" class="nav-btn">‹</button>
      <h3 class="month-year">{{ currentMonthYear }}</h3>
      <button @click="nextMonth" class="nav-btn">›</button>
    </div>
    
    <div class="calendar-grid">
      <div class="calendar-day-header" v-for="day in dayHeaders" :key="day">{{ day }}</div>
      
      <div 
        v-for="date in calendarDates" 
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
      dayHeaders: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    }
  },
  computed: {
    currentMonthYear() {
      return this.currentDate.toLocaleDateString('en-US', { 
        month: 'long', 
        year: 'numeric' 
      })
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
          events: dayEvents
        })
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
  background: #005a9c;
  color: white;
  border-color: #005a9c;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1rem;
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
  background: #005a9c;
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
  background: #059669;
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
}
</style>
