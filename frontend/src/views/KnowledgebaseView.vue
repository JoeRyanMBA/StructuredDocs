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