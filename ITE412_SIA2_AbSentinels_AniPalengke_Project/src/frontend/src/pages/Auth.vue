<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-lg font-semibold">Login</h2>
      <form @submit.prevent="login" class="space-y-2">
        <input v-model="email" placeholder="email" class="border p-2 rounded w-full" />
        <input v-model="password" placeholder="password" type="password" class="border p-2 rounded w-full" />
        <button class="bg-green-600 text-white px-3 py-2 rounded">Login</button>
      </form>
    </div>
    <div>
      <h2 class="text-lg font-semibold">Register</h2>
      <form @submit.prevent="register" class="space-y-2">
        <input v-model="reg.email" placeholder="email" class="border p-2 rounded w-full" />
        <input v-model="reg.password" placeholder="password" type="password" class="border p-2 rounded w-full" />
        <select v-model="reg.role" class="border p-2 rounded w-full">
          <option>Farmer</option>
          <option>Buyer</option>
          <option>Admin</option>
        </select>
        <button class="bg-blue-600 text-white px-3 py-2 rounded">Register</button>
      </form>
    </div>
    <div class="flex gap-2">
      <button @click="me" class="border px-3 py-2 rounded">Me</button>
      <button @click="logout" class="border px-3 py-2 rounded">Logout</button>
    </div>
    <pre>{{ user }}</pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api, { setToken } from '../services/api'

const email = ref('buyer@example.com')
const password = ref('buyer123')
const user = ref(null)
const reg = ref({ email: 'new@example.com', password: 'test123', role: 'Buyer' })

async function login() {
  const res = await api.post('/auth/login', { email: email.value, password: password.value })
  setToken(res.data.token)
  user.value = res.data.user
}
async function register() {
  const res = await api.post('/auth/register', reg.value)
  setToken(res.data.token)
  user.value = res.data.user
}
async function me() {
  const res = await api.get('/auth/me')
  user.value = res.data
}
async function logout() {
  await api.post('/auth/logout')
  setToken(null)
  user.value = null
}
</script>
