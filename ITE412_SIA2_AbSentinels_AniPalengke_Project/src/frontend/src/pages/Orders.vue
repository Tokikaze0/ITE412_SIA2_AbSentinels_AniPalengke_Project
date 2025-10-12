<template>
  <div class="space-y-6">
    <div>
      <h3 class="font-semibold">Create Order</h3>
      <form @submit.prevent="create" class="space-y-2">
        <input v-model.number="productId" placeholder="productId" type="number" class="border p-2 rounded w-full" />
        <input v-model.number="qty" placeholder="qty" type="number" class="border p-2 rounded w-full" />
        <button class="bg-green-600 text-white px-3 py-2 rounded">Create</button>
      </form>
    </div>

    <div>
      <h3 class="font-semibold">My Orders</h3>
      <div class="space-y-2">
        <div v-for="o in items" :key="o.id" class="border rounded p-3">
          <div>Order #{{ o.id }} - {{ o.status }}</div>
          <button @click="pay(o)" class="mt-2 border px-3 py-1 rounded">Pay</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const items = ref([])
const productId = ref(1)
const qty = ref(1)

async function load() {
  const res = await api.get('/orders')
  items.value = res.data.items
}
async function create() {
  await api.post('/orders', { items: [{ productId: productId.value, qty: qty.value }] })
  await load()
}
async function pay(o) {
  await api.post('/payments', { orderId: o.id, amount: 100 })
  await load()
}

onMounted(load)
</script>
