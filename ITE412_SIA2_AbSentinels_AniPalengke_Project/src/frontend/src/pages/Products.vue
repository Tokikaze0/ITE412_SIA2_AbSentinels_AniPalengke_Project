<template>
  <div class="space-y-6">
    <div class="flex gap-2">
      <input v-model="q" placeholder="Search products" class="border p-2 rounded w-full" />
      <button @click="load" class="border px-3 py-2 rounded">Search</button>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="p in items" :key="p.id" class="border rounded p-3">
        <div class="font-semibold">{{ p.name }}</div>
        <div class="text-sm">₱{{ p.price }} | Stock: {{ p.stock }}</div>
      </div>
    </div>
    <div class="border-t pt-4">
      <h3 class="font-semibold">Create product (Farmer/Admin)</h3>
      <form @submit.prevent="create" class="space-y-2">
        <input v-model="form.name" placeholder="name" class="border p-2 rounded w-full" />
        <input v-model.number="form.price" placeholder="price" type="number" class="border p-2 rounded w-full" />
        <input v-model.number="form.stock" placeholder="stock" type="number" class="border p-2 rounded w-full" />
        <button class="bg-green-600 text-white px-3 py-2 rounded">Create</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const items = ref([])
const q = ref('')
const form = ref({ name: 'New Product', price: 100, stock: 5 })

async function load() {
  const res = await api.get('/products', { params: { q: q.value } })
  items.value = res.data.items
}
async function create() {
  await api.post('/products', form.value)
  await load()
}

onMounted(load)
</script>
