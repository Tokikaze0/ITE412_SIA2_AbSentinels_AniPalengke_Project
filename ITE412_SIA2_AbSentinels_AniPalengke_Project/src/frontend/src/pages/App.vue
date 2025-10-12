<template>
  <div>
    <header class="bg-green-600 text-white">
      <div class="container py-4 flex gap-4 items-center">
        <h1 class="font-bold text-xl">AniPalengke</h1>
        <nav class="flex gap-3 text-sm">
          <RouterLink to="/products">Products</RouterLink>
          <RouterLink to="/orders">Orders</RouterLink>
          <RouterLink to="/delivery">Delivery</RouterLink>
          <RouterLink to="/notifications">Notifications</RouterLink>
          <RouterLink to="/community">Community</RouterLink>
          <RouterLink to="/advisory">Advisory</RouterLink>
          <RouterLink to="/auth" class="ml-auto">Auth</RouterLink>
        </nav>
      </div>
    </header>
    <main class="container py-6">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
</script>
