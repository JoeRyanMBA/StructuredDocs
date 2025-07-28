<template>
  <header class="header-bar">
    <router-link to="/projects" class="logo-link">
      <img
        class="logo"
        src="https://www.census.gov/etc.clientlibs/census/clientlibs/census-pattern-library/resources/images/USCENSUS_IDENTITY_SOLO_BLACK_1.5in_R_no_padding.svg"
        alt="Census Bureau logo"
      />
    </router-link>

    <router-link to="/projects" class="title-link">
      <h1 class="title">SCCMB Documentation Project Hub</h1>
    </router-link>


  </header>
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
  justify-content: space-between;
  padding: 0 0.25rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 1100;
}

.logo {
  height: 40px;
}

.logo-link, .title-link {
  text-decoration: none;
  color: inherit;
}

.title-link {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.title-link:hover .title {
  color: #005a9c;
}

.title {
  margin: 0;
  font-size: 1.5rem;
  font-family: 'Roboto', sans-serif;
  transition: color 0.2s;
  text-align: center;
  white-space: nowrap;
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
</style>