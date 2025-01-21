// src/main.js
import { createApp } from "vue";
import App from "./App.vue";
import router from "@/router";
import pinia from "@/store";
import { useAuthStore } from "@/store/auth";
import './style.css'

const app = createApp(App);

// Configuración del store y router
app.use(pinia);
app.use(router);

// Inicializar la sesión del usuario
const authStore = useAuthStore();
authStore.initializeStore();

// Montar la aplicación
app.mount("#app");
