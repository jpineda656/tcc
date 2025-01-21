<!-- src/views/LoginView.vue -->
<template>
  <div class="login-wrapper">
    <div class="login-container">
      <h1>Iniciar Sesión</h1>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="username"
            type="email"
            required
            :disabled="isLoading"
            placeholder="tucorreo@ejemplo.com"
          />
        </div>
        <div class="form-group">
          <label for="password">Contraseña</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            :disabled="isLoading"
            placeholder="••••••"
          />
        </div>
        <button type="submit" :disabled="isLoading">
          {{ isLoading ? "Cargando..." : "Ingresar" }}
        </button>
      </form>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/store/auth";

const router = useRouter();
const authStore = useAuthStore();

const username = ref("");
const password = ref("");
const errorMessage = ref("");
const isLoading = ref(false);

async function handleLogin() {
  if (!username.value || !password.value) {
    errorMessage.value = "Por favor, completa todos los campos.";
    return;
  }

  try {
    isLoading.value = true;
    errorMessage.value = "";
    await authStore.login(username.value, password.value);
    const redirectPath = authStore.redirectPath || "/dashboard";
    router.push(redirectPath);
    authStore.clearRedirectPath();
  } catch (err) {
    // Capturamos mensaje de error devuelto por el backend
    errorMessage.value = err.response?.data?.detail || "Error al iniciar sesión.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
/* Suponiendo que tu tema define algo como:
   --background-color, --primary-color, --text-color, --accent-color, etc.
   en un archivo global. Ejemplo: */

.login-wrapper {
  /* Ocupar toda la pantalla con fondo */
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--background-color); /* Color de fondo general */
}

/* Contenedor principal del login */
.login-container {
  width: 360px;
  padding: 2rem;
  border-radius: 8px;
  background-color: var(--dark-gray); /* Por ejemplo, un tono oscuro */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  color: var(--text-color);
}

/* Título */
.login-container h1 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--white);
}

/* Agrupación de campos */
.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.4rem;
  font-weight: 500;
  color: var(--light-gray); /* Un tono un poco más claro */
}

input {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid var(--medium-gray);
  border-radius: 4px;
  font-size: 0.95rem;
  background-color: var(--dark-gray);
  color: var(--white);
  box-sizing: border-box;
}

/* estilo al focus del input */
input:focus {
  outline: none;
  border: 1px solid var(--accent-color);
}

button {
  width: 100%;
  padding: 0.6rem;
  margin-top: 0.5rem;
  background-color: var(--accent-color);
  color: var(--white);
  border: none;
  border-radius: 4px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover:not(:disabled) {
  background-color: var(--primary-color);
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Mensaje de error */
.error {
  margin-top: 1rem;
  color: var(--danger-color);
  text-align: center;
  font-size: 0.9rem;
}
</style>
