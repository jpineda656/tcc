<!-- src/components/TheNavbar.vue -->
<template>
  <nav class="navbar">
    <div class="navbar-container">
      <ul class="navbar-links">
        <li>
          <router-link to="/dashboard" aria-label="Ir al Dashboard">Dashboard</router-link>
        </li>
        <li>
          <router-link to="/camera" aria-label="Abrir cámara">Capturar Señas</router-link>
        </li>
        <li>
          <router-link to="/users" aria-label="Gestionar usuarios">Usuarios</router-link>
        </li>
        <li>
          <router-link to="/roles" aria-label="Gestionar roles">Roles</router-link>
        </li>
      </ul>

      <button class="btn-logout" @click="handleLogout" aria-label="Cerrar sesión">
        Logout
      </button>
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
  background-color: var(--primary-color);
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
  padding: 0; /* elimina posibles paddings por defecto */
}

.navbar-links li {
  /* puedes añadir estilos individuales si lo deseas */
}

.navbar a {
  color: var(--white);
  font-weight: 500;
  text-decoration: none;
  transition: color 0.3s ease;
}

.navbar a:hover {
  color: var(--accent-color); 
}

.navbar a.router-link-active {
  color: var(--accent-color);
}

/* Botón Logout */
.btn-logout {
  background-color: var(--danger-color);
  color: var(--white);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-logout:hover {
  /* Un tono más oscuro del danger color, o el que desees */
  background-color: #c0392b; 
}

/* Ajustar responsividad */
@media (max-width: 768px) {
  .navbar-links {
    flex-direction: column;
  }
  .navbar-container {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
