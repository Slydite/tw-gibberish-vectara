// src/components/StatsCard.vue
<template>
  <div class="stats-card">
    <div v-for="(value, key) in stats" :key="key" class="stat-item">
      <h4>{{ formatLabel(key) }}</h4>
      <p>{{ formatValue(value) }}</p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'StatsCard',
  props: {
    stats: {
      type: Object,
      required: true
    }
  },
  setup() {
    const formatLabel = (key: string) => {
      return key
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
    }

    const formatValue = (value: any) => {
      if (typeof value === 'number') {
        return value.toFixed(2)
      }
      return value
    }

    return {
      formatLabel,
      formatValue
    }
  }
})
</script>

<style scoped>
.stats-card {
  background: rgba(255, 255, 255, 0);
  border-radius: 8px;
  padding: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-item {
  text-align: center;
}

.stat-item h4 {
  color: var(--color-text);
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  opacity: 0.8;
}

.stat-item p {
  color: var(--color-text);
  margin: 0;
  font-size: 1.25rem;
  font-weight: 500;
}
</style>
