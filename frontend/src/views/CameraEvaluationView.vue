<!-- src/views/CameraEvaluationView.vue -->
<template>

  <div class="camera-container">
    <!-- Panel de Controles -->
    <div class="controls">
      <h2>Evaluación del Modelo con MediaPipe</h2>

      <!-- Botón para activar/desactivar la cámara -->
      <button
        class="btn-camera"
        :class="{ active: isCameraActive }"
        @click="toggleCamera"
      >
        {{ isCameraActive ? "Detener Cámara" : "Iniciar Cámara" }}
      </button>

      <!-- Sección de Botones de grabación -->
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

      <!-- Mensaje de cuenta regresiva -->
      <div v-if="isPreparing" class="countdown-message">
        <span>Comenzando en {{ countdown }}...</span>
      </div>

      <!-- Sección para mostrar texto completo detectado -->
      <div class="recognized-words" v-if="recognizedWords.length">
        <h4>Texto detectado:</h4>
        <p class="words-list">
          {{ recognizedWords.join("") }}
        </p>
      </div>
    </div>

    <!-- Sección de Vista de Cámara / Canvas -->
    <div class="camera-view">
      <!-- Video (oculto si no deseas mostrarlo) -->
      <video ref="videoRef" class="video-preview" playsinline></video>

      <!-- Canvas donde se dibujan los landmarks -->
      <canvas ref="canvasRef" class="output-canvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

// Composable para inicializar Holistic y manejar la cámara
import { useHolistic } from '@/utils/mediapipeUtils'
// Composable para dibujar landmarks
import { useDrawing } from '@/utils/drawingUtils'
// Composable para la lógica de grabación (cuenta regresiva, captura)
import { useRecording } from '@/utils/recordingUtils'
import axios from "@/services/api";

const { 
  drawFaceLandmarks, 
  drawPoseLandmarks, 
  drawHandLandmarks 
} = useDrawing()

const { 
  isRecording,
  isPreparing,
  countdown,
  capturedFrames,
  prepareRecording,
  startRecording,
  stopRecording,
  handleResults
} = useRecording()

// Variable para almacenar las palabras detectadas de forma acumulada
const recognizedWords = ref([])

/**
 * Función para enviar datos al backend cuando termina la grabación
 * (aquí se usa para evaluación en tiempo real, por ej. /realtime_evaluate).
 */
 async function sendDataCallback(bodyData) {
  try {
    const response = await axios.post("/", bodyData);

    // Si la respuesta es 2xx, obtenemos el resultado
    const result = response.data;
    
    // Supongamos que el backend retorna { predicted_label, confidence }
    if (result.predicted_label) {
      recognizedWords.value.push(result.predicted_label);
    }

  } catch (error) {
    console.error("Error al enviar datos para evaluación:", error);
    alert("Ocurrió un error al enviar los datos para evaluación.");
  }
}
/**
 * Detener la grabación con la callback anterior.
 */
async function stopRecordingWithSend() {
  await stopRecording(sendDataCallback)
}

/* ==========================
   Callback de Holistic
   ========================== */
function onResultsHolistic(results) {
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight

  ctx.save()
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height)

  // Dibujar landmarks
  drawFaceLandmarks(ctx, results.faceLandmarks)
  drawPoseLandmarks(ctx, results.poseLandmarks)
  drawHandLandmarks(ctx, results.rightHandLandmarks, '#CC0000', '#00FFFF')
  drawHandLandmarks(ctx, results.leftHandLandmarks, '#00CC00', '#FFFF00')
  ctx.restore()

  // Determinar si hay manos detectadas
  const handDetected = !!(results.rightHandLandmarks || results.leftHandLandmarks)

  // frameData: cara, manos, pose
  const frameData = {}
  if (results.faceLandmarks) {
    frameData.face = results.faceLandmarks.map(lm => ({ x: lm.x, y: lm.y, z: lm.z }))
  }
  if (results.rightHandLandmarks) {
    frameData.rightHand = results.rightHandLandmarks.map(lm => ({ x: lm.x, y: lm.y, z: lm.z }))
  }
  if (results.leftHandLandmarks) {
    frameData.leftHand = results.leftHandLandmarks.map(lm => ({ x: lm.x, y: lm.y, z: lm.z }))
  }
  if (results.poseLandmarks) {
    frameData.pose = results.poseLandmarks.map(lm => ({ x: lm.x, y: lm.y, z: lm.z }))
  }

  // Lógica de grabación
  handleResults(handDetected, frameData, sendDataCallback)
}

/* ==========================
   Inicialización de Holistic
   ========================== */
const {
  videoRef,
  canvasRef,
  initHolistic,
  toggleCamera,
  isCameraActive
} = useHolistic(onResultsHolistic)

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
    '' // Ruta local al WASM o CDN si deseas
  )
})
</script>

<style scoped>


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

.countdown-message {
  color: var(--danger-color);
  font-weight: 600;
  font-size: 1.1rem;
}

/* Palabras detectadas */
.recognized-words {
  margin-top: 1rem;
  background-color: var(--dark-gray);
  padding: 0.5rem;
  border-radius: 4px;
  color: var(--white);
}

.recognized-words .words-list {
  margin: 0;
  font-size: 1rem;
}

/* Sección de cámara y canvas */
.camera-view {
  flex: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.video-preview {
  display: none; /* Oculte el video si desea solo canvas */
  border: 1px solid var(--light-gray);
  width: 600px;
  height: 500px;
  background-color: #000;
  margin-bottom: 1rem;
}

.output-canvas {
  border: 1px solid var(--light-gray);
  width: 600px;
  height: 500px;
}
</style>
