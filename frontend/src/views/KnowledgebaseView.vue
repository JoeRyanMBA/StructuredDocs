<template>
  <div class="kb">
    <h1>{{ pub.title }}</h1>
    <ul>
      <li v-for="n in tree" :key="n.id">
        <router-link :to="`/kb/${n.id}`">{{ n.topic.title }}</router-link>
        <ul v-if="n.children.length">
          <li v-for="c in n.children" :key="c.id">
            <!-- recurse or use a recursive component -->
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>
<script>
export default { /* fetch same as builder */ }
</script>
<style scoped>
.kb {
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
}

.kb h1 {
  color: var(--primary-deep-teal);
  margin-bottom: 1.5rem;
  border-bottom: 2px solid var(--extended-lavender-gray);
  padding-bottom: 0.5rem;
}

ul {
  list-style-type: none;
  padding-left: 0;
}

li {
  margin-bottom: 0.5rem;
}

a {
  color: var(--primary-medium-teal);
  text-decoration: none;
  font-size: 1.1rem;
}

a:hover {
  text-decoration: underline;
  color: var(--primary-light-teal);
}

ul ul {
  padding-left: 1.5rem;
  margin-top: 0.5rem;
  border-left: 1px solid var(--extended-lavender-gray);
}
</style>