<!-- src/views/LoginView.vue -->
<template>
  <div class="login-container">
    <h1>Login</h1>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="email">Email:</label>
        <input id="email" v-model="username" type="email" required :disabled="isLoading" />
      </div>
      <div class="form-group">
        <label for="password">Contraseña:</label>
        <input id="password" v-model="password" type="password" required :disabled="isLoading" />
      </div>
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? "Cargando..." : "Iniciar Sesión" }}
      </button>
    </form>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
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
    errorMessage.value = err.response?.data?.detail || "Error al iniciar sesión.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 2rem auto;
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.form-group {
  margin-bottom: 1rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
}
input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 0.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}
.error {
  color: red;
  margin-top: 1rem;
  font-size: 0.9rem;
  text-align: center;
}
</style>
