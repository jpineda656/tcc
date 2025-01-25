<!-- src/views/DashboardView.vue -->
<template>
  <div>
    <TheNavbar />
    <div class="dashboard-container">
      <h2>Bienvenido PoÑe'e APP</h2>
      <p>Usuario logueado: {{ username }}</p>
    </div>
  </div>
</template>

<script setup>
import TheNavbar from "@/components/TheNavbar.vue";
import { storeToRefs } from "pinia";
import { useAuthStore } from "@/store/auth";

const authStore = useAuthStore();
const { username } = storeToRefs(authStore);
</script>

<style scoped>
.dashboard-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1rem;
  background-color: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

</style>