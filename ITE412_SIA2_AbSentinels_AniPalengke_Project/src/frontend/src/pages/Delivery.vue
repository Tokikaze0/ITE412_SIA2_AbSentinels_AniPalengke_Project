<template>
  <div class="space-y-6">
    <div>
      <h3 class="font-semibold">Trigger Auto Delivery (consume OrderCreated)</h3>
      <button @click="consume" class="border px-3 py-2 rounded">Consume Events</button>
    </div>
    <div>
      <h3 class="font-semibold">Deliveries</h3>
      <div v-for="d in items" :key="d.id" class="border rounded p-3">
        <div>Delivery #{{ d.id }} - Order {{ d.orderId }} - {{ d.status }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const items = ref([])

async function load() {
  const res = await api.get('/delivery')
  items.value = res.data.items
}
async function consume() {
  await api.get('/delivery/track')
  await load()
}

onMounted(load)
</script>
