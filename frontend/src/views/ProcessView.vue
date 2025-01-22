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
          {{ isProcessing && currentProcess === 'normalization'
             ? 'Normalizando...' 
             : 'Iniciar Normalización'
          }}
        </button>
  
        <!-- Botón para Entrenamiento -->
        <button
          class="btn-process"
          :disabled="isProcessing"
          @click="handleTraining"
        >
          {{ isProcessing && currentProcess === 'training'
             ? 'Entrenando...' 
             : 'Iniciar Entrenamiento'
          }}
        </button>
      </div>
  
      <!-- Barra de progreso (se muestra solo si isProcessing es true) -->
      <div class="progress-section" v-if="isProcessing">
        <p><strong>Proceso en curso:</strong> {{ currentProcessLabel }}</p>
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
  import { ref, computed  } from "vue";
  import TheNavbar from "@/components/TheNavbar.vue";
  
  // Estado
  const isProcessing = ref(false);
  const progressValue = ref(0); // Valor numérico del 0 al 100
  const currentProcess = ref(""); // "normalization" o "training" para saber cuál
  const successMessage = ref("");
  const errorMessage = ref("");
  
  // Texto amigable para mostrar en la UI
  function currentProcessLabel() {
    if (currentProcess.value === "normalization") return "Normalización de Datos";
    if (currentProcess.value === "training") return "Entrenamiento del Modelo";
    return "";
  }
  const currentProcessLabelComputed = computed(currentProcessLabel);
  
  /**
   * Simula o llama un endpoint para Normalización.
   */
  async function handleNormalization() {
    try {
      // Reiniciar estado
      resetState();
  
      currentProcess.value = "normalization";
      isProcessing.value = true;
      progressValue.value = 0;
  
      // Llamada al endpoint
      // Por ejemplo: POST /trigger_preprocessing
      const response = await fetch("http://localhost:8000/procesamiento/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
                  "Authorization": `Bearer ${token}`
      });
      if (!response.ok) {
        throw new Error(`Error en el servidor: ${response.status}`);
      }
  
      // Simular barra de progreso (o usar una lógica de polling)
      simulateProgress(() => {
        successMessage.value = "Normalización completada con éxito.";
      });
  
    } catch (error) {
      console.error("Error en la normalización:", error);
      errorMessage.value = "Error al normalizar los datos.";
    }
  }
  
  /**
   * Simula o llama un endpoint para Entrenamiento.
   */
  async function handleTraining() {
    try {
      // Reiniciar estado
      resetState();
  
      currentProcess.value = "training";
      isProcessing.value = true;
      progressValue.value = 0;
  
      // Llamada al endpoint
      // Por ejemplo: POST /train/start
      const response = await fetch("http://localhost:8000/entrenamiento/", {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error(`Error en el servidor: ${response.status}`);
      }
  
      // Simular barra de progreso (o polling real)
      simulateProgress(() => {
        successMessage.value = "Entrenamiento finalizado con éxito.";
      });
  
    } catch (error) {
      console.error("Error en el entrenamiento:", error);
      errorMessage.value = "Error al entrenar el modelo.";
    }
  }
  
  /**
   * Simulación de progreso (0 -> 100%) en 4-5 segundos.
   * Podrías reemplazarlo con un "polling" real a tu backend
   * que indique en qué % va el proceso.
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
   * Reiniciar estado
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
  /* Ajusta tus variables globales, p. ej:
     :root {
       --primary-color: #2c3e50;
       --accent-color: #1abc9c;
       --danger-color: #e74c3c;
       --dark-gray: #37474f;
       --light-gray: #cfd8dc;
       --white: #ffffff;
       --text-color: #eceff1;
     }
  */
  
  .process-container {
    max-width: 600px;
    margin: 2rem auto;
    padding: 1rem;
    background-color: var(--dark-gray);
    color: var(--text-color);
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
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
  