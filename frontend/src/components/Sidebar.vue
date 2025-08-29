<template>
  <!-- DEPRECATED: This component is no longer used. Use components/SideBar.vue instead. -->
  <div class="deprecated-sidebar">
    Deprecated component. Do not use.
  </div>
  <!-- Intentionally minimal. If this renders, a wrong import is being used. -->
  <!-- Use SideBar.vue (capital B) -->
  <!-- File retained temporarily due to tooling delete limitations. -->
</template>

<script>
export default {
  name: 'DEPRECATED_Sidebar_DO_NOT_USE',
  mounted() {
    // Fail loudly if someone accidentally mounts this component
    // eslint-disable-next-line no-console
    console.error('Deprecated component mounted: components/Sidebar.vue. Use components/SideBar.vue instead.');
    if (process && process.env && process.env.NODE_ENV !== 'production') {
      throw new Error('Deprecated component used: components/Sidebar.vue. Import components/SideBar.vue instead.');
    }
  }
}
</script>

<style scoped>
.deprecated-sidebar {
  display: none; /* Never visible; exists only to catch accidental imports. */
}
</style>
  top: 40%;
  left: 0;
  width: 28px;
  height: 80px;
  background: #205493;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  z-index: 1001;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2);
  font-size: 1.2rem;
}

.sidebar {
  position: fixed;
  top: 60px;
  left: 0;
  width: 200px;
  min-height: calc(100vh - 60px);
  background: #f9f9f9;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
  padding: 0.5rem 0;
  transition: transform 0.3s ease;
  overflow-y: auto;
  z-index: 1000;
}

.sidebar.collapsed {
  transform: translateX(-100%);
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 0;
  border-bottom: 1px solid #e9ecef;
}

.nav-item:last-child {
  border-bottom: none;
}

.nav-link {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.75rem 1rem;
  text-decoration: none;
  color: #495057;
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
  text-align: left;
}

.nav-link:hover {
  background-color: #e9ecef;
  color: #205493;
}

.direct-link.router-link-active {
  background-color: #205493;
  color: white;
}

.direct-link.router-link-active .nav-icon {
  opacity: 1;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  margin-right: 0.75rem;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.nav-text {
  flex: 1;
  font-weight: 500;
}

.expand-icon {
  margin-left: auto;
  transition: transform 0.2s ease;
  display: flex;
  align-items: center;
  opacity: 0.6;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.expand-icon svg {
  transition: transform 0.2s ease;
}

.collapsible-link:hover .expand-icon {
  opacity: 1;
}

.sub-nav {
  list-style: none;
  padding: 0;
  margin: 0;
  background-color: #f1f3f4;
}

.sub-nav-item {
  margin: 0;
}

.sub-nav-link {
  display: block;
  padding: 0.5rem 1rem 0.5rem 3rem;
  text-decoration: none;
  color: #6c757d;
  font-size: 0.85rem;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.sub-nav-link:hover {
  background-color: #e9ecef;
  color: #495057;
  border-left-color: #205493;
}

.sub-nav-link.router-link-active {
  background-color: #d4edda;
  color: #155724;
  border-left-color: #28a745;
  font-weight: 500;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .sidebar {
    width: 250px;
  }
  
  .nav-link {
    padding: 1rem;
  }
  
  .nav-icon {
    width: 24px;
    margin-right: 1rem;
  }
}
</style>