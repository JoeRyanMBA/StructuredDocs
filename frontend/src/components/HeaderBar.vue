<template>
  <header class="header-bar">
    <img
      class="logo"
      src="https://www.census.gov/etc.clientlibs/census/clientlibs/census-pattern-library/resources/images/USCENSUS_IDENTITY_SOLO_BLACK_1.5in_R_no_padding.svg"
      alt="Census Bureau logo"
    />

    <h1 class="title">SCCMB Knowledge Base</h1>

    <nav class="nav-links">
      <router-link
        class="nav-btn"
        :to="{ name: 'TopicsList' }"
        active-class="is-active"
      >
        Topics
      </router-link>
      <router-link
        class="nav-btn"
        :to="{ name: 'ImportHome' }"
        active-class="is-active"
      >
        Import
      </router-link>
      <router-link
        class="nav-btn new-btn"
        :to="{ name: 'NewTopic' }"
      >
        + New Topic
      </router-link>
    </nav>
  </header>
  <hr class="header-divider" />
</template>

<script>
export default {
  name: 'HeaderBar'
  // lifecycle logging removed for clarity and performance
}
</script>

<style scoped>
.header-bar {
  position: fixed;
  top: 0;
  left: 0; right: 0;
  height: 60px;
  background: #fff;
  color: #112e51;
  display: flex;
  align-items: center;
  padding: 0 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 1000;
}

.logo {
  height: 40px;
}

.title {
  flex: 1;
  text-align: center;
  margin: 0;
  font-size: 1.5rem;
  font-family: 'Roboto', sans-serif;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
}

.nav-btn {
  padding: 0.5rem 1rem;
  text-decoration: none;
  color: #005a9c;
  border: 1px solid #005a9c;
  border-radius: 4px;
  transition: background 0.2s;
}

.nav-btn.is-active,
.nav-btn:hover {
  background: #005a9c;
  color: white;
}

.new-btn {
  background: #005a9c;
  color: white;
}

.header-divider {
  position: fixed;
  top: 60px;    /* same as header height */
  left: 0;
  right: 0;
  border: none;
  border-top: 1px solid #ddd;
  z-index: 999;
}
</style>