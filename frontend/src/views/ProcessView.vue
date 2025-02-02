<!-- src/views/ProcessView.vue -->
<template>
  <TheNavbar />

  <div class="process-card">
    <h2 class="title">Procesos de Normalización y Entrenamiento</h2>

    <div class="buttons-section">
      <!-- Botón para Normalización -->
      <button
        class="btn-process"
        :disabled="isProcessing"
        @click="handleNormalization"
      >
        <span v-if="isProcessing && currentProcess === 'normalization'">
          <!-- Consejo #1: Spinner + texto -->
          <i class="spinner"></i> Normalizando...
        </span>
        <span v-else>Iniciar Normalización</span>
      </button>

      <!-- Botón para Entrenamiento -->
      <button
        class="btn-process"
        :disabled="isProcessing"
        @click="handleTraining"
      >
        <span v-if="isProcessing && currentProcess === 'training'">
          <i class="spinner"></i> Entrenando...
        </span>
        <span v-else>Iniciar Entrenamiento</span>
      </button>

      <!-- Consejo #3: Botón Cancelar proceso -->
      <button
        class="btn-cancel"
        v-if="isProcessing"
        @click="cancelProcess"
      >
        Cancelar
      </button>
    </div>

    <!-- Sección de progreso (se muestra solo si isProcessing es true) -->
    <div class="progress-section" v-if="isProcessing">
      <p>
        <strong>Proceso en curso:</strong> {{ currentProcessLabelComputed }}
      </p>

      <!-- Consejos #4 y #8: Animaciones y Tiempo Estimado -->
      <div class="time-estimate">
        <p>
          Estimado restante: 
          <strong v-if="timeLeft > 0">{{ timeLeft }} s</strong>
          <span v-else>-</span>
        </p>
      </div>

      <div class="progress-bar">
        <div
          class="progress-bar-fill"
          :class="{ complete: progressValue >= 100 }"
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

    <!-- Consejo #1 y #5: Notificaciones dulces se mostrarán con sweetalert2 -->

    <!-- Mensaje de error local (por si también quieres mostrarlo) -->
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

    <!-- Consejo #2: Log / consola de mensajes -->
    <div class="log-console" v-if="processLogs.length">
      <h3>Detalles del proceso</h3>
      <ul>
        <li v-for="(log, idx) in processLogs" :key="idx">{{ log }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import TheNavbar from "@/components/TheNavbar.vue";
import axios from "@/services/api";
import Swal from "sweetalert2";

//
// ESTADOS
//
const isProcessing = ref(false);
const progressValue = ref(0); // Valor numérico del 0 al 100
const currentProcess = ref(""); // "normalization" | "training"
const successMessage = ref("");
const errorMessage = ref("");

// Consejo #2: Log interno para mensajes
const processLogs = ref([]);

// Consejo #8: Tiempo estimado (ejemplo)
const timeLeft = ref(0); // en segundos

//
// COMPUTED
//
function currentProcessLabel() {
  if (currentProcess.value === "normalization") return "Normalización de Datos";
  if (currentProcess.value === "training") return "Entrenamiento del Modelo";
  return "";
}
const currentProcessLabelComputed = computed(currentProcessLabel);

//
// MÉTODOS
//
function addLog(message) {
  const now = new Date().toLocaleTimeString();
  processLogs.value.push(`[${now}] ${message}`);
}

/**
 * Cancela el proceso (Consejo #3).
 * Detiene la barra de progreso, resetea estado. Si quisieras
 * cancelar a nivel backend, necesitarías un endpoint /cancel o similar.
 */
function cancelProcess() {
  addLog("El usuario ha cancelado el proceso.");
  clearInterval(progressInterval.value);
  progressInterval.value = null;
  resetState();
}

/**
 * Llama al endpoint para Normalización de datos.
 */
async function handleNormalization() {
  try {
    resetState();
    currentProcess.value = "normalization";
    isProcessing.value = true;
    progressValue.value = 0;
    addLog("Iniciando normalización...");

    // Llamada a tu endpoint
    const response = await axios.post("/procesamiento/");
    if (response.status < 200 || response.status >= 300) {
      throw new Error(`Error en el servidor: ${response.status}`);
    }

    // Usamos barra de progreso simulada (o polling real)
    startSimulatedProgress("Normalización completada con éxito.");
  } catch (error) {
    console.error("Error en la normalización:", error);
    addLog("Error en la normalización.");
    showError("Error al normalizar los datos.");
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
    addLog("Iniciando entrenamiento...");

    const response = await axios.post("/entrenamiento/");
    if (response.status < 200 || response.status >= 300) {
      throw new Error(`Error en el servidor: ${response.status}`);
    }

    startSimulatedProgress("Entrenamiento finalizado con éxito.");
  } catch (error) {
    console.error("Error en el entrenamiento:", error);
    addLog("Error en el entrenamiento.");
    showError("Error al entrenar el modelo.");
  }
}

/**
 * Consejo #5: Mostrar error con sweetalert2
 */
function showError(msg) {
  errorMessage.value = msg;
  Swal.fire("Error", msg, "error");
  isProcessing.value = false;
}

/**
 * Consejo #5: Mostrar éxito con sweetalert2
 */
function showSuccess(msg) {
  successMessage.value = msg;
  Swal.fire("Éxito", msg, "success");
}

/**
 * startSimulatedProgress:
 * Arranca la simulación (o harías polling real).
 * Consejo #4: animaciones suaves en la barra (ver CSS).
 * Consejo #8: tiempo estimado (ejemplo).
 */
let progressInterval = ref(null);
function startSimulatedProgress(finalMsg) {
  let iteration = 0;
  timeLeft.value = 10; // suponer 10 segundos de operación

  progressInterval.value = setInterval(() => {
    iteration++;
    // Aumentamos en 10% cada medio segundo
    progressValue.value += 10;
    timeLeft.value -= 0.5;

    // Log intermedio (Consejo #7: mensajes descriptivos)
    addLog(`Progreso: ${progressValue.value}%`);

    if (progressValue.value >= 100) {
      clearInterval(progressInterval.value);
      progressInterval.value = null;
      isProcessing.value = false;
      addLog("¡Proceso completado!");
      showSuccess(finalMsg);
    }
  }, 500);
}

/**
 * Ejemplo de polling real (Consejo #6):
 * Si tu backend da info de progreso:
 * 
 * async function startRealProgressCheck() {
 *   progressInterval.value = setInterval(async () => {
 *     try {
 *       const resp = await axios.get("/procesamiento/status");
 *       progressValue.value = resp.data.progress; // 0..100
 *       timeLeft.value = resp.data.eta;          // en seg
 *       if (progressValue.value >= 100) {
 *         clearInterval(progressInterval.value);
 *         progressInterval.value = null;
 *         isProcessing.value = false;
 *         showSuccess("Proceso completado con éxito.");
 *       }
 *     } catch (err) {
 *       console.error("Error poll status", err);
 *     }
 *   }, 1000);
 * }
 */

/**
 * resetState:
 * Consejo #1 y #9: restablece la vista.
 */
function resetState() {
  isProcessing.value = false;
  progressValue.value = 0;
  successMessage.value = "";
  errorMessage.value = "";
  currentProcess.value = "";
  timeLeft.value = 0;
}
</script>

<style scoped>

/* Consejo #10: Envolver contenido en tarjeta */
.process-card {
  max-width: 700px;
  margin: 2rem auto;
  padding: 1rem 2rem;
  background-color: var(--medium-gray);
  color: var(--text-color);
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  transition: transform 0.2s ease;
}
.process-card:hover {
  transform: translateY(-3px);
}

.title {
  text-align: center;
  font-size: 1.6rem;
  margin-bottom: 1rem;
  color: var(--white);
}

/* Botones y contenedor principal */
.buttons-section {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

/* Consejo #1: Spinner con animación */
.spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--white);
  border-radius: 50%;
  border-top-color: var(--accent-color);
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Botones generales */
.btn-process {
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
  border-radius: 4px;
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease, transform 0.2s ease;
}
.btn-process:hover:not(:disabled) {
  background-color: var(--accent-color);
  transform: translateY(-2px);
}
.btn-process:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Botón cancelar */
.btn-cancel {
  background-color: var(--danger-color);
  color: var(--white);
  border: none;
  border-radius: 4px;
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease, transform 0.2s ease;
}
.btn-cancel:hover {
  background-color: #c0392b;
  transform: translateY(-2px);
}

/* Sección de progreso */
.progress-section {
  margin-top: 1rem;
  text-align: center;
  background-color: var(--dark-gray);
  padding: 1rem;
  border-radius: 8px;
}

/* Tiempo estimado */
.time-estimate {
  margin-bottom: 0.5rem;
  color: var(--light-gray);
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

/* Consejo #4: si se completa, animación "pulse" */
.progress-bar-fill.complete {
  animation: pulse 1s infinite alternate;
}
@keyframes pulse {
  from { background-color: #27ae60; }
  to { background-color: #2ecc71; }
}

/* Mensaje de éxito */
.success-message {
  color: #27ae60;
  margin-top: 1rem;
  font-weight: 600;
}

/* Mensaje de error */
.error {
  color: var(--danger-color);
  margin-top: 1rem;
  font-weight: 500;
}

/* Consejo #2: Log / consola de mensajes */
.log-console {
  background-color: var(--dark-gray);
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 8px;
}
.log-console h3 {
  margin-top: 0;
  color: var(--white);
}
.log-console ul {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 200px;
  overflow-y: auto;
}
.log-console li {
  color: var(--light-gray);
  margin-bottom: 0.25rem;
}
</style>
