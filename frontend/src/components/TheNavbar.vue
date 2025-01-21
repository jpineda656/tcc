<!-- src/components/TheNavbar.vue -->
<template>
  <nav class="navbar">
    <div class="navbar-container">
      <ul class="navbar-links">
        <li><router-link to="/dashboard" aria-label="Ir al Dashboard">Dashboard</router-link></li>
        <li><router-link to="/users" aria-label="Gestionar usuarios">Usuarios</router-link></li>
        <li><router-link to="/roles" aria-label="Gestionar roles">Roles</router-link></li>
        <li><router-link to="/camera" aria-label="Abrir cámara">Capturar Señas</router-link></li>
      </ul>
      <button class="btn btn-secondary" @click="handleLogout" aria-label="Cerrar sesión">Logout</button>
    </div>
  </nav>
</template>


<script setup>
import { useAuthStore } from "@/store/auth";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

async function handleLogout() {
  try {
    await authStore.logout();
    router.push("/login");
  } catch (error) {
    console.error("Error al cerrar sesión:", error);
    // Podrías mostrar un mensaje de error al usuario aquí
  }
}
</script>

<style scoped>
.navbar {
  background-color: #2c3e50;
  padding: 0.75rem 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-links {
  list-style: none;
  display: flex;
  gap: 1rem;
  margin: 0;
}

.navbar a {
  color: #ffffff;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.3s ease;
}

.navbar a:hover {
  color: #1abc9c;
}

.navbar a.router-link-active {
  color: #1abc9c;
}

.btn-secondary {
  background-color: #e74c3c;
  color: #ffffff;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  font-size: 1rem;
}

.btn-secondary:hover {
  background-color: #c0392b;
}
</style>
