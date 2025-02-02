<!--frontend/src/views/CameraView.vue -->
<template>
  <TheNavbar />

  <div class="camera-container">
    <!-- Sección de Controles / Acciones -->
    <div class="controls">
      <h2>Captura de Señas con MediaPipe</h2>

      <!-- Botón para activar/desactivar cámara -->
      <button
        class="btn-camera"
        :class="{ active: isCameraActive }"
        @click="toggleCamera"
      >
        {{ isCameraActive ? "Detener Cámara" : "Iniciar Cámara" }}
      </button>

      <!-- Campo para la palabra o seña -->
      <div class="sign-input">
        <label for="sign-label">Palabra/Seña</label>
        <input
          id="sign-label"
          v-model="signLabel"
          type="text"
          placeholder="Ej: Hola"
        />
      </div>

      <!-- Botones de Grabación -->
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

      <!-- Zona de mensajes de estado (cuenta regresiva / grabación) -->
      <div class="status-message">
        <!-- Mostrar cuenta regresiva si isPreparing -->
        <div v-if="isPreparing" class="countdown-message highlight-msg">
          <!-- Mensaje mejorado -->
          <span>¡Preparando en {{ countdown }} segundos!</span>
        </div>

        <!-- Mostrar "Grabando" si isRecording -->
        <div v-else-if="isRecording" class="recording-indicator highlight-msg">
          <span>Grabando...</span>
          <span>Frames: {{ capturedFrames.length }}</span>
        </div>
      </div>

      <!-- Contador de gestos capturados en la sesión -->
      <div
        class="session-count info-message"
        v-if="capturedGesturesCount > 0"
      >
        <p>
          Gestos capturados en esta sesión: 
          <strong>{{ capturedGesturesCount }}</strong>
        </p>
      </div>

      <!-- Mensaje de éxito cuando se envían datos -->
      <div v-if="successMessage" class="success-message highlight-msg">
        {{ successMessage }}
      </div>
    </div>

    <!-- Vista de Cámara / Canvas -->
    <div class="camera-view">
      <!-- Video (oculto por defecto si no deseas mostrarlo) -->
      <video ref="videoRef" class="video-preview" playsinline></video>

      <!-- Canvas con los landmarks dibujados -->
      <canvas ref="canvasRef" class="output-canvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import TheNavbar from "@/components/TheNavbar.vue";
import { onMounted, ref } from "vue";

// Hooks (composables) de MediaPipe y dibujo
import { useHolistic } from "@/utils/mediapipeUtils";
import { useDrawing } from "@/utils/drawingUtils";

// Hook para la lógica de grabación (cuenta regresiva, frames, etc.)
import { useRecording } from "@/utils/recordingUtils";

// Cliente HTTP (Axios)
import axios from "@/services/api";

// Extraemos las funciones de dibujo
const { drawFaceLandmarks, drawPoseLandmarks, drawHandLandmarks } = useDrawing();

// Extraemos la lógica de grabación
const {
  signLabel,
  isRecording,
  isPreparing,
  countdown,
  capturedFrames,
  prepareRecording,
  startRecording,
  stopRecording,
  handleResults,
  capturedGesturesCount
} = useRecording();

// Mensaje de éxito (cuando se envían datos)
const successMessage = ref("");

/**
 * Callback que envía datos al backend una vez completada la grabación.
 */
async function sendDataCallback(bodyData) {
  try {
    const response = await axios.post("/captura", bodyData);
    // Mensaje mejorado
    successMessage.value = "¡Datos enviados con éxito al servidor!";
    // Limpiar el mensaje tras 3s
    setTimeout(() => {
      successMessage.value = "";
    }, 3000);
  } catch (error) {
    console.error("Error al enviar datos:", error);
    alert("Ocurrió un error al enviar los datos al servidor.");
  }
}

/**
 * Detener la grabación y mandar datos al backend con la callback.
 */
async function stopRecordingWithSend() {
  await stopRecording(sendDataCallback);
}

/**
 * Callback de Holistic: se llama cada frame para dibujar landmarks y capturar info.
 */
function onResultsHolistic(results) {
  const canvas = canvasRef.value;
  const ctx = canvas.getContext("2d");
  canvas.width = videoRef.value.videoWidth;
  canvas.height = videoRef.value.videoHeight;

  ctx.save();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

  // Dibujo de landmarks con colores
  drawFaceLandmarks(ctx, results.faceLandmarks);
  drawPoseLandmarks(ctx, results.poseLandmarks);
  drawHandLandmarks(ctx, results.rightHandLandmarks, "#CC0000", "#00FFFF");
  drawHandLandmarks(ctx, results.leftHandLandmarks, "#00CC00", "#FFFF00");

  ctx.restore();

  // Verificar si hay manos detectadas (bool)
  const handDetected = !!(results.rightHandLandmarks || results.leftHandLandmarks);

  // Armar frameData para grabación
  const frameData = {};
  if (results.faceLandmarks) {
    frameData.face = results.faceLandmarks.map(lm => ({ x: lm.x, y: lm.y, z: lm.z }));
  }
  if (results.rightHandLandmarks) {
    frameData.rightHand = results.rightHandLandmarks.map(lm => ({ x: lm.x, y: lm.y, z: lm.z }));
  }
  if (results.leftHandLandmarks) {
    frameData.leftHand = results.leftHandLandmarks.map(lm => ({ x: lm.x, y: lm.y, z: lm.z }));
  }
  if (results.poseLandmarks) {
    frameData.pose = results.poseLandmarks.map(lm => ({ x: lm.x, y: lm.y, z: lm.z }));
  }

  // Pasar a handleResults (composable) para grabar
  handleResults(handDetected, frameData, sendDataCallback);
}

// Inicializar Holistic y cámara
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
    ""
  );
});
</script>

<style scoped>
/* Container principal */
.camera-container {
  display: flex;
  flex-direction: row;
  gap: 2rem;
  margin: 1rem 2rem;
  background-color: var(--dark-gray);
  color: var(--text-color);
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Panel de controles (izquierda) */
.controls {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background-color: var(--medium-gray);
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

/* Título */
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

/* Input de la seña */
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

/* Mensajes de estado (cuenta regresiva, grabando) */
.status-message {
  margin-top: 0.5rem;
}
.countdown-message {
  background-color: #ff5252;
  color: #fff;
  padding: 0.4rem 0.7rem;
  border-radius: 4px;
  font-weight: bold;
  font-size: 1.1rem;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
  margin-bottom: 0.3rem;
}
.recording-indicator {
  background-color: #2ecc71;
  color: #fff;
  padding: 0.4rem 0.7rem;
  border-radius: 4px;
  font-weight: bold;
  font-size: 1.0rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

/* Contador de gestos en la sesión */
.session-count {
  background-color: #3498db;
  color: #fff;
  padding: 0.4rem 0.7rem;
  border-radius: 4px;
  font-size: 1rem;
}

/* Mensaje de éxito */
.success-message {
  background-color: #27ae60;
  color: #fff;
  padding: 0.4rem 0.7rem;
  border-radius: 4px;
  margin-top: 0.5rem;
  font-weight: bold;
  font-size: 1rem;
}

/* Sección de la cámara (derecha) */
.camera-view {
  flex: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* Video */
.video-preview {
  display: none; /* Ocúltalo si no deseas */
  border: 1px solid var(--light-gray);
  width: 600px;
  height: 500px;
  background-color: #000;
  margin-bottom: 1rem;
}

/* Canvas */
.output-canvas {
  border: 1px solid var(--light-gray);
  width: 600px;
  height: 500px;
}
</style>
