import { ref, watch } from 'vue';
import axios from 'axios';
import { debounce } from 'lodash';

export function useTopicEditor(router) {
  const topicId = ref(null);

  const title = ref('');
  const content = ref('');
  const tags = ref([]);
  const reviewer = ref(null);
  const reviewComment = ref('');
  const reviewStatus = ref('draft');

  const version = ref('0.0.0');
  const isSaved = ref(false);
  const isSaving = ref(false);
  const lastSavedAt = ref(null);

  // Debounced autosave only runs if topicId exists
  const autosave = debounce(async () => {
    if (topicId.value === null) {
      console.log('[DEBUG] Autosave skipped — no topicId (create manually first)');
      return;
    }
    await saveTopic('autosave');
  }, 2500);

  watch([title, content, tags], autosave);

  async function saveTopic(mode = 'manual') {
    console.log(`[DEBUG] ${mode} save triggered — topicId =`, topicId.value);

    // Prevent autosave from creating
    if (mode === 'autosave' && topicId.value === null) {
      return;
    }

    isSaving.value = true;

    let response;
    if (topicId.value === null) {
      // Manual creation
      response = await axios.post('/api/topics', {
        title: title.value,
        rawContent: content.value,
        tags: tags.value,
        reviewer: reviewer.value,
        reviewComment: reviewComment.value,
        reviewStatus: reviewStatus.value
      });

      topicId.value = response.data.id;
      router.replace(`/authoring/live/${topicId.value}`);
      console.log('[DEBUG] Route replaced → /authoring/live/' + topicId.value);
    } else {
      // Update existing
      response = await axios.post('/api/topics', {
        id: topicId.value,
        title: title.value,
        rawContent: content.value,
        tags: tags.value,
        reviewer: reviewer.value,
        reviewComment: reviewComment.value,
        reviewStatus: reviewStatus.value
      });
    }

    console.log('[DEBUG] Save response:', response.data);
    version.value = response.data.version;
    isSaved.value = true;
    lastSavedAt.value = new Date();
    console.log(
      `[TOAST] ${mode === 'manual' ? 'Saved manually' : 'Autosaved'} (ID:${topicId.value}, v${version.value})`
    );
    isSaving.value = false;
  }

  // Hydrate existing topic by ID
  async function hydrateAndLoad(id) {
    const parsed = parseInt(id);
    if (isNaN(parsed)) return;

    topicId.value = parsed;
    console.log('[DEBUG] Hydrated topicId =', parsed);

    const res = await axios.get(`/api/topics/${parsed}`);
    const data = res.data;

    title.value = data.title || '';
    content.value = data.content || '';
    tags.value = data.tags || [];
    reviewer.value = data.reviewer || null;
    reviewComment.value = data.reviewComment || '';
    reviewStatus.value = data.reviewStatus || 'draft';
    version.value = data.version || '0.0.0';
    lastSavedAt.value = new Date(data.updatedAt);

    console.log('[DEBUG] Topic loaded:', data);
  }

  return {
    title,
    content,
    tags,
    reviewer,
    reviewComment,
    reviewStatus,
    version,
    lastSavedAt,
    isSaved,
    isSaving,
    saveTopic,
    hydrateAndLoad
  };
}