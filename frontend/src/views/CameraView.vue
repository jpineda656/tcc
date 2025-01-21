<!-- src/views/cameraView.vue -->
<template>
  <TheNavbar />

  <div class="camera-container">
    <!-- Sección de Configuración / Acciones -->
    <div class="controls">
      <h2>Captura de Señas con MediaPipe</h2>

      <!-- Botón para activar/desactivar la cámara -->
      <button
        class="btn-camera"
        :class="{ active: isCameraActive }"
        @click="toggleCamera"
      >
        {{ isCameraActive ? 'Detener Cámara' : 'Iniciar Cámara' }}
      </button>

      <!-- Input para la palabra/seña -->
      <div class="sign-input">
        <label for="sign-label">Palabra/Seña</label>
        <input
          id="sign-label"
          v-model="signLabel"
          type="text"
          placeholder="Ej: Hola"
        />
      </div>

      <!-- Botones de grabación -->
      <div class="recording-buttons">
        <button
          class="btn-record"
          @click="prepareRecording"
          :disabled="!isCameraActive || isPreparing || isRecording"
        >
          Iniciar Grabación
        </button>
        <button
          class="btn-stop"
          @click="stopRecordingWithSend"
          :disabled="!isCameraActive || (!isPreparing && !isRecording)"
        >
          Detener y Enviar
        </button>
      </div>

      <!-- Cuenta regresiva -->
      <div v-if="isPreparing" class="countdown-message">
        <span>Comenzando en {{ countdown }}...</span>
      </div>

      <!-- Mensaje de éxito -->
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
    </div>

    <!-- Sección de Vista de Cámara / Canvas -->
    <div class="camera-view">
      <!-- Video (oculto si no se quiere mostrar) -->
      <video ref="videoRef" class="video-preview" playsinline></video>

      <!-- Canvas donde se dibujan los landmarks -->
      <canvas ref="canvasRef" class="output-canvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import TheNavbar from "@/components/TheNavbar.vue";
import { onMounted, ref } from "vue";
import { useHolistic } from "@/utils/mediapipeUtils";
import { useDrawing } from "@/utils/drawingUtils";
import { useRecording } from "@/utils/recordingUtils";

const { 
  drawFaceLandmarks, 
  drawPoseLandmarks, 
  drawHandLandmarks 
} = useDrawing();

const {
  signLabel,
  isRecording,
  isPreparing,
  countdown,
  capturedFrames,
  prepareRecording,
  startRecording,
  stopRecording,
  handleResults
} = useRecording();

// Mensaje de éxito
const successMessage = ref("");

/**
 * Callback para enviar datos al backend.
 * Puedes modificar la URL o usar axios.
 */
async function sendDataCallback(bodyData) {
  try {
    const response = await fetch("http://localhost:8000/captura", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bodyData),
    });

    if (!response.ok) {
      throw new Error(`Error en el servidor: ${response.status}`);
    }

    successMessage.value = "Datos enviados correctamente al servidor";
    // Limpiar el mensaje después de 3 segundos
    setTimeout(() => {
      successMessage.value = "";
    }, 3000);
  } catch (error) {
    console.error("Error al enviar datos:", error);
    alert("Ocurrió un error al enviar los datos.");
  }
}

/**
 * stopRecording con callback para envío de datos.
 */
async function stopRecordingWithSend() {
  await stopRecording(sendDataCallback);
}

/* ==========================
   Callback de Holistic
   ========================== */
function onResultsHolistic(results) {
  const canvas = canvasRef.value;
  const ctx = canvas.getContext("2d");
  canvas.width = videoRef.value.videoWidth;
  canvas.height = videoRef.value.videoHeight;

  ctx.save();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

  // Dibujo
  drawFaceLandmarks(ctx, results.faceLandmarks);
  drawPoseLandmarks(ctx, results.poseLandmarks);
  drawHandLandmarks(ctx, results.rightHandLandmarks, "#CC0000", "#00FFFF");
  drawHandLandmarks(ctx, results.leftHandLandmarks, "#00CC00", "#FFFF00");
  ctx.restore();

  // Determinar si hay manos detectadas
  const handDetected = !!(results.rightHandLandmarks || results.leftHandLandmarks);

  // frameData con cara/pose/manos
  const frameData = {};
  if (results.faceLandmarks) {
    frameData.face = results.faceLandmarks.map(lm => ({
      x: lm.x,
      y: lm.y,
      z: lm.z,
    }));
  }
  if (results.rightHandLandmarks) {
    frameData.rightHand = results.rightHandLandmarks.map(lm => ({
      x: lm.x,
      y: lm.y,
      z: lm.z,
    }));
  }
  if (results.leftHandLandmarks) {
    frameData.leftHand = results.leftHandLandmarks.map(lm => ({
      x: lm.x,
      y: lm.y,
      z: lm.z,
    }));
  }
  if (results.poseLandmarks) {
    frameData.pose = results.poseLandmarks.map(lm => ({
      x: lm.x,
      y: lm.y,
      z: lm.z,
    }));
  }

  // Llamar a la función del composable
  handleResults(handDetected, frameData, sendDataCallback);
}

/* ==========================
   Inicializar Holistic
   ========================== */
const {
  videoRef,
  canvasRef,
  initHolistic,
  toggleCamera,
  isCameraActive
} = useHolistic(onResultsHolistic);

onMounted(() => {
  initHolistic(
    {
      modelComplexity: 2,
      smoothLandmarks: true,
      enableSegmentation: true,
      smoothSegmentation: true,
      refineFaceLandmarks: true,
      selfieMode: true,
      useCpuInference: false,
      webGlVersion: 2,
    },
    "" // Ruta local, ajusta si requieres otra
  );
});
</script>

<style scoped>


/* Contenedor principal */
.camera-container {
  display: flex;
  flex-direction: row;
  gap: 2rem;
  margin: 1rem 2rem;
  background-color: var(--dark-gray);
  color: var(--text-color);
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Sección de controles (lado izquierdo) */
.controls {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background-color: var(--medium-gray);
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
}

.controls h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--white);
}

/* Botón de cámara */
.btn-camera {
  background-color: var(--primary-color);
  color: var(--white);
  padding: 0.5rem 1rem;
  border: none;
  cursor: pointer;
  font-weight: 500;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.btn-camera.active {
  background-color: var(--danger-color);
}

.btn-camera:hover {
  background-color: var(--accent-color);
}

/* Entrada de la seña */
.sign-input {
  display: flex;
  flex-direction: column;
}

.sign-input label {
  font-size: 0.9rem;
  margin-bottom: 0.3rem;
  color: var(--white);
}

.sign-input input {
  border: 1px solid var(--light-gray);
  padding: 0.4rem;
  border-radius: 4px;
  background-color: var(--dark-gray);
  color: var(--white);
}

/* Botones de grabación */
.recording-buttons {
  display: flex;
  gap: 1rem;
}

/* Botón grabar */
.btn-record {
  background-color: #27ae60;
  color: var(--white);
  border: none;
  padding: 0.5rem 1.2rem;
  cursor: pointer;
  border-radius: 4px;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.btn-record:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-record:hover:not(:disabled) {
  background-color: #2ecc71;
}

/* Botón detener */
.btn-stop {
  background-color: var(--danger-color);
  color: var(--white);
  border: none;
  padding: 0.5rem 1.2rem;
  cursor: pointer;
  border-radius: 4px;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.btn-stop:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-stop:hover:not(:disabled) {
  background-color: #c0392b;
}

/* Cuenta regresiva */
.countdown-message {
  color: var(--danger-color);
  font-weight: 600;
  font-size: 1.1rem;
}

/* Mensaje de éxito */
.success-message {
  color: #27ae60;
  font-weight: bold;
  font-size: 1rem;
  margin-top: 1rem;
}

/* Sección de la cámara y canvas (lado derecho) */
.camera-view {
  flex: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* Video de previsualización */
.video-preview {
  display: none; /* Ocúltalo si no deseas mostrarlo */
  border: 1px solid var(--light-gray);
  width: 600px;
  height: 500px;
  background-color: #000;
  margin-bottom: 1rem;
}

/* Canvas donde se dibujan landmarks */
.output-canvas {
  border: 1px solid var(--light-gray);
  width: 600px;
  height: 500px;
}
</style>
