<!-- filepath: c:\Dev\StructuredDocs\frontend\src\components\TopicItem.vue -->
<template>
  <div class="topic-item">
    {{ topic.title || topic.label }}
  </div>
</template>

<script>
export default {
  name: 'TopicItem',
  props: {
    topic: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.topic-item {
  /* Add your topic item styles here */
  padding: 4px 8px;
  border-bottom: 1px solid #eee;
  color:#000
}
</style>