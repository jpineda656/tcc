<!-- src/views/ProcessView.vue -->
<template>
  <TheNavbar />

  <div class="process-container">
    <h2 class="title">Procesos de Normalización y Entrenamiento</h2>

    <div class="buttons-section">
      <!-- Botón para Normalización -->
      <button
        class="btn-process"
        :disabled="isProcessing"
        @click="handleNormalization"
      >
        {{
          isProcessing && currentProcess === "normalization"
            ? "Normalizando..."
            : "Iniciar Normalización"
        }}
      </button>

      <!-- Botón para Entrenamiento -->
      <button
        class="btn-process"
        :disabled="isProcessing"
        @click="handleTraining"
      >
        {{
          isProcessing && currentProcess === "training"
            ? "Entrenando..."
            : "Iniciar Entrenamiento"
        }}
      </button>
    </div>

    <!-- Barra de progreso (se muestra solo si isProcessing es true) -->
    <div class="progress-section" v-if="isProcessing">
      <p>
        <strong>Proceso en curso:</strong> {{ currentProcessLabelComputed }}
      </p>
      <div class="progress-bar">
        <div
          class="progress-bar-fill"
          :style="{ width: progressValue + '%' }"
        >
          <span>{{ progressValue }}%</span>
        </div>
      </div>

      <!-- Mensaje final si ya está al 100% -->
      <div v-if="progressValue === 100" class="success-message">
        {{ successMessage }}
      </div>
    </div>

    <!-- Mensaje de error, si ocurre -->
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import TheNavbar from "@/components/TheNavbar.vue";
// Importa la instancia de Axios con interceptores configurados:
import axios from "@/services/api";

// Estado principal
const isProcessing = ref(false);
const progressValue = ref(0); // Valor numérico del 0 al 100
const currentProcess = ref(""); // "normalization" | "training"
const successMessage = ref("");
const errorMessage = ref("");

// Computed amigable para mostrar en la UI
function currentProcessLabel() {
  if (currentProcess.value === "normalization") return "Normalización de Datos";
  if (currentProcess.value === "training") return "Entrenamiento del Modelo";
  return "";
}
const currentProcessLabelComputed = computed(currentProcessLabel);

/**
 * Llama al endpoint para Normalización de datos.
 */
async function handleNormalization() {
  try {
    resetState();
    currentProcess.value = "normalization";
    isProcessing.value = true;
    progressValue.value = 0;

    // Llamada a tu endpoint /procesamiento/
    const response = await axios.post("/procesamiento/");
    // Verificamos que el status sea 2xx
    if (response.status < 200 || response.status >= 300) {
      throw new Error(`Error en el servidor: ${response.status}`);
    }

    // Simulación de barra de progreso local
    simulateProgress(() => {
      successMessage.value = "Normalización completada con éxito.";
    });
  } catch (error) {
    console.error("Error en la normalización:", error);
    errorMessage.value = "Error al normalizar los datos.";
  }
}

/**
 * Llama al endpoint para Entrenamiento del modelo.
 */
async function handleTraining() {
  try {
    resetState();
    currentProcess.value = "training";
    isProcessing.value = true;
    progressValue.value = 0;

    // Llamada a tu endpoint /entrenamiento/
    const response = await axios.post("/entrenamiento/");
    if (response.status < 200 || response.status >= 300) {
      throw new Error(`Error en el servidor: ${response.status}`);
    }

    // Simulación de barra de progreso local
    simulateProgress(() => {
      successMessage.value = "Entrenamiento finalizado con éxito.";
    });
  } catch (error) {
    console.error("Error en el entrenamiento:", error);
    errorMessage.value = "Error al entrenar el modelo.";
  }
}

/**
 * Simulación de progreso (0 -> 100%) cada 500ms.
 * Reemplaza con polling real si tu backend lo soporta.
 */
function simulateProgress(onComplete) {
  const interval = setInterval(() => {
    if (progressValue.value < 100) {
      progressValue.value += 10;
    } else {
      clearInterval(interval);
      isProcessing.value = false;
      onComplete && onComplete();
    }
  }, 500);
}

/**
 * Reinicia el estado antes de cualquier proceso nuevo.
 */
function resetState() {
  isProcessing.value = false;
  progressValue.value = 0;
  successMessage.value = "";
  errorMessage.value = "";
  currentProcess.value = "";
}
</script>

<style scoped>
.process-container {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1rem;
  background-color: var(--dark-gray);
  color: var(--text-color);
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.title {
  text-align: center;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: var(--white);
}

.buttons-section {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

/* Botones */
.btn-process {
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
  border-radius: 4px;
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease;
}

.btn-process:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-process:hover:not(:disabled) {
  background-color: var(--accent-color);
}

/* Sección de progreso */
.progress-section {
  margin-top: 1rem;
  text-align: center;
}

.progress-bar {
  width: 100%;
  background-color: var(--light-gray);
  height: 24px;
  border-radius: 12px;
  margin: 0.5rem 0;
  overflow: hidden;
  position: relative;
}

.progress-bar-fill {
  background-color: var(--accent-color);
  height: 100%;
  width: 0%;
  transition: width 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--white);
}

.success-message {
  color: #27ae60;
  margin-top: 1rem;
  font-weight: 600;
}

.error {
  color: var(--danger-color);
  margin-top: 1rem;
  font-weight: 500;
}
</style>
