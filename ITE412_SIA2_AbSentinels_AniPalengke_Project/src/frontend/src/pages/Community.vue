<template>
  <div class="space-y-6">
    <div>
      <h3 class="font-semibold">New Post</h3>
      <form @submit.prevent="create" class="space-y-2">
        <textarea v-model="content" placeholder="Share tips or questions" class="border p-2 rounded w-full"></textarea>
        <button class="bg-green-600 text-white px-3 py-2 rounded">Post</button>
      </form>
    </div>
    <div>
      <h3 class="font-semibold">Community Posts</h3>
      <div v-for="p in items" :key="p.id" class="border rounded p-3">
        <div class="text-sm text-gray-500">#{{ p.id }}</div>
        <div>{{ p.content }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const items = ref([])
const content = ref('Irrigation tip...')

async function load() {
  const res = await api.get('/community')
  items.value = res.data.items
}
async function create() {
  await api.post('/community', { content: content.value })
  content.value = ''
  await load()
}

onMounted(load)
</script>
