<template>
  <div class="space-y-6">
    <div>
      <h3 class="font-semibold">Consume Events</h3>
      <button @click="consume" class="border px-3 py-2 rounded">Consume</button>
    </div>
    <div>
      <h3 class="font-semibold">Notifications</h3>
      <div v-for="n in items" :key="n.message" class="border rounded p-3">
        <div class="text-sm text-gray-500">{{ n.type }}</div>
        <div>{{ n.message }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const items = ref([])

async function load() {
  const res = await api.get('/notifications')
  items.value = res.data.items
}
async function consume() {
  await api.post('/notifications/consume')
  await load()
}

onMounted(load)
</script>
