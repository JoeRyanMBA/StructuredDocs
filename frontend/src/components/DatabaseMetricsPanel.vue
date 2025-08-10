<template>
  <div class="dashboard-section full-width">
    <h2>Database Metrics</h2>
    <div class="db-metrics-grid">
      <div class="db-metric-card">
        <div class="db-metric-label">Tables</div>
        <div class="db-metric-value">{{ metrics.tables }}</div>
      </div>
      <div class="db-metric-card">
        <div class="db-metric-label">Rows</div>
        <div class="db-metric-value">{{ metrics.rows }}</div>
      </div>
      <div class="db-metric-card">
        <div class="db-metric-label">Size</div>
        <div class="db-metric-value">{{ metrics.size }}</div>
      </div>
      <div class="db-metric-card">
        <div class="db-metric-label">Last Backup</div>
        <div class="db-metric-value">{{ metrics.lastBackup }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DatabaseMetricsPanel',
  props: {
    metrics: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.db-metrics-grid {
  display: flex;
  gap: 2rem;
  margin-top: 1rem;
}
.db-metric-card {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem 2rem;
  min-width: 120px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.db-metric-label {
  font-size: 1rem;
  color: #666;
  margin-bottom: 0.5rem;
}
.db-metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #007acc;
}
</style>
