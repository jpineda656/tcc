<!-- src/views/ProcessView.vue -->
<template>
  <TheNavbar />

  <div class="process-container">
    <h2 class="title">Procesos de Normalización y Entrenamiento</h2>

    <!-- Botones para iniciar cada proceso -->
    <div class="buttons-section">
      <button
        class="btn-process"
        :disabled="isProcessing"
        @click="handleNormalization"
      >
        <span v-if="isProcessing && currentProcess === 'normalization'">
          Normalizando (background)...
        </span>
        <span v-else>Iniciar Normalización</span>
      </button>

      <button
        class="btn-process"
        :disabled="isProcessing"
        @click="handleTraining"
      >
        <span v-if="isProcessing && currentProcess === 'training'">
          Entrenando (background)...
        </span>
        <span v-else>Iniciar Entrenamiento</span>
      </button>
    </div>

    <!-- Mensaje de proceso en marcha -->
    <div class="status-section" v-if="isProcessing">
      <p>
        <strong>
          La tarea de {{ currentProcessLabelComputed }} se está ejecutando 
          en segundo plano...
        </strong>
      </p>
    </div>

    <!-- Mensaje de error (si ocurre) -->
    <p v-if="errorMessage" class="error">
      {{ errorMessage }}
    </p>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import TheNavbar from "@/components/TheNavbar.vue";
import axios from "@/services/api";

// Importar nuestras utils de alertas SweetAlert2
import { showSuccess, showError } from "@/utils/alertUtils";

/**
 * ESTADOS
 */
const isProcessing = ref(false);
const currentProcess = ref(""); // "normalization" | "training"
const errorMessage = ref("");

function currentProcessLabel() {
  if (currentProcess.value === "normalization") return "Normalización";
  if (currentProcess.value === "training") return "Entrenamiento";
  return "";
}
const currentProcessLabelComputed = computed(currentProcessLabel);

// Variable para el pollingInterval
let pollingInterval = null;

/**
 * handleNormalization
 * - Llama a /procesamiento/ (POST) para iniciar
 * - Al ok => inicia polling a /procesamiento/status
 */
async function handleNormalization() {
  try {
    resetState();
    currentProcess.value = "normalization";
    isProcessing.value = true;

    const resp = await axios.post("/procesamiento/");
    if (resp.status >= 200 && resp.status < 300) {
      // arranca polling
      startPolling("/procesamiento/status", "¡Normalización completada con éxito!");
    } else {
      throw new Error(`El servidor retornó status=${resp.status}`);
    }
  } catch (err) {
    console.error(err);
    errorMessage.value = "No se pudo iniciar la normalización.";
    isProcessing.value = false;
  }
}

/**
 * handleTraining
 * - Llama a /entrenamiento/ (POST) para iniciar
 * - Al ok => inicia polling a /entrenamiento/status
 */
async function handleTraining() {
  try {
    resetState();
    currentProcess.value = "training";
    isProcessing.value = true;

    const resp = await axios.post("/entrenamiento/");
    if (resp.status >= 200 && resp.status < 300) {
      startPolling("/entrenamiento/status", "¡Entrenamiento finalizado con éxito!");
    } else {
      throw new Error(`El servidor retornó status=${resp.status}`);
    }
  } catch (err) {
    console.error(err);
    errorMessage.value = "No se pudo iniciar el entrenamiento.";
    isProcessing.value = false;
  }
}

/**
 * startPolling
 * - Llama repetidamente al endpoint `statusUrl` cada 2s
 * - Si `status==="completed"`, detiene polling y showSuccess
 * - Si `status==="failed"`, detiene polling y showError
 */
function startPolling(statusUrl, successMsg) {
  pollingInterval = setInterval(async () => {
    try {
      const resp = await axios.get(statusUrl);
      const { status } = resp.data;
      if (status === "completed") {
        clearInterval(pollingInterval);
        pollingInterval = null;
        isProcessing.value = false;
        showSuccess(successMsg);
      } else if (status === "failed") {
        clearInterval(pollingInterval);
        pollingInterval = null;
        isProcessing.value = false;
        showError("La tarea falló en el backend.");
      }
    } catch (err) {
      console.error("Error en polling:", err);
      clearInterval(pollingInterval);
      pollingInterval = null;
      isProcessing.value = false;
      errorMessage.value = "Error consultando estado del proceso.";
    }
  }, 2000);
}

/**
 * resetState
 * Limpia variables al iniciar un nuevo proceso
 */
function resetState() {
  isProcessing.value = false;
  currentProcess.value = "";
  errorMessage.value = "";
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
}
</script>

<style scoped>
.process-container {
  max-width: 700px;
  margin: 2rem auto;
  padding: 1rem 2rem;
  background-color: var(--medium-gray);
  color: var(--text-color);
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.title {
  text-align: center;
  margin-bottom: 1rem;
  color: var(--white);
  font-size: 1.5rem;
}

.buttons-section {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1.5rem;
}

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
.btn-process:hover:not(:disabled) {
  background-color: var(--accent-color);
}
.btn-process:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.status-section {
  background-color: var(--dark-gray);
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}

.error {
  margin-top: 1rem;
  color: var(--danger-color);
  font-weight: 500;
}
</style>
