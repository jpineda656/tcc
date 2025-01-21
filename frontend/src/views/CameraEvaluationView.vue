<!-- views/CameraView.vue -->
<template>
  
  <div class="camera-container">
    <!-- Sección de Configuración / Acciones -->
    <div class="controls">
      <h2>Evaluación del Modelo con MediaPipe</h2>

      <!-- Botón para activar/desactivar la cámara -->
      <button 
        class="btn-camera"
        :class="{ active: isCameraActive }"
        @click="toggleCamera"
      >
        {{ isCameraActive ? 'Detener cámara' : 'Iniciar cámara' }}
      </button>

      <!-- Botones para grabación (sin necesidad de palabra/seña) -->
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

      <!-- Mensaje de éxito -->
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
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
import TheNavbar from "@/components/TheNavbar.vue"
import { onMounted, ref } from 'vue'

// Composable para inicializar Holistic y manejar la cámara
import { useHolistic } from '@/utils/mediapipeUtils'
// Composable para dibujar landmarks
import { useDrawing } from '@/utils/drawingUtils'
// Composable para la lógica de grabación (cuenta regresiva, captura)
import { useRecording } from '@/utils/recordingUtils'
import { log } from "@tensorflow/tfjs"

// Importamos métodos de dibujo
const { 
  drawFaceLandmarks, 
  drawPoseLandmarks, 
  drawHandLandmarks 
} = useDrawing()

// useRecording: controla la lógica de cuenta regresiva y captura
// Eliminamos la lógica de 'signLabel' porque no necesitamos palabra
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

// Variable para mostrar mensaje de éxito en pantalla
const successMessage = ref('')

/**
 * Función para enviar datos al backend cuando termina la grabación
 * (similar a la captura de puntos, pero aquí se usa para evaluación).
 */
async function sendDataCallback(bodyData) {
  try {
    // En este endpoint, el backend realizará la evaluación
    // (p.ej. /realtime_evaluate)
    const response = await fetch('http://localhost:8000/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bodyData) 
    })
    if (!response.ok) {
      throw new Error(`Error en el servidor: ${response.status}`)
    }
    const result = await response.json()

    // Mostramos el resultado de la inferencia
    successMessage.value = `Predicción: ${result.predicted_label} (confianza: ${result.confidence.toFixed(2)})`

    // Limpiar el mensaje después de 3 segundos
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    console.error('Error al enviar datos para evaluación:', error)
    alert('Ocurrió un error al enviar los datos para evaluación.')
  }
}

/**
 * stopRecording con la callback para envío de datos
 */
async function stopRecordingWithSend() {
  await stopRecording(sendDataCallback)
}

/* ==========================
   1) Callback de Holistic
   ========================== */
function onResultsHolistic(results) {
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight

  ctx.save()
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height)

  // Dibujo de rostro
  drawFaceLandmarks(ctx, results.faceLandmarks)
  // Dibujo de pose
  drawPoseLandmarks(ctx, results.poseLandmarks)
  // Dibujo de manos
  drawHandLandmarks(ctx, results.rightHandLandmarks, '#CC0000', '#00FFFF')
  drawHandLandmarks(ctx, results.leftHandLandmarks, '#00CC00', '#FFFF00')

  ctx.restore()

  // Determinar si hay manos
  const handDetected = !!(results.rightHandLandmarks || results.leftHandLandmarks)

  // Puntos de referencia capturados (cara, manos, pose)
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

  // Llamamos al manejador de resultados de grabación
  handleResults(handDetected, frameData, sendDataCallback)
}

/* ==========================
   2) useHolistic
   ========================== */
const {
  videoRef,
  canvasRef,
  initHolistic,
  toggleCamera,
  isCameraActive
} = useHolistic(onResultsHolistic)

/* ==========================
   3) Ciclo de vida
   ========================== */
onMounted(() => {
  // Inicializar Holistic de inmediato en onMounted.
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
    '' // Ruta local para WASM si no deseas usar un CDN
  )
})
</script>

<style scoped>
.camera-container {
  display: flex;
  flex-direction: row;
  gap: 2rem;
  margin: 1rem 2rem;
}

/* Sección de controles / acciones */
.controls {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.controls h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}

/* Botón para iniciar/detener cámara */
.btn-camera {
  background-color: #2c3e50;
  color: #fff;
  padding: 0.5rem 1rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
  font-weight: 500;
  border-radius: 4px;
}

.btn-camera.active {
  background-color: #e74c3c;
}

.btn-camera:hover {
  background-color: #34495e;
}

/* Sección de botones de grabación */
.recording-buttons {
  display: flex;
  gap: 1rem;
}

.btn-record {
  background-color: #27ae60;
  color: #fff;
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
  background-color: #e74c3c;
  color: #fff;
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

/* Mensaje de cuenta regresiva */
.countdown-message {
  color: #e74c3c;
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

/* Sección de la cámara y canvas */
.camera-view {
  flex: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.video-preview {
  display: none; /* Oculta el video si solo quieres mostrar el canvas */
  border: 1px solid #ccc;
  width: 600px;
  height: 500px;
  background-color: #000;
  margin-bottom: 1rem;
}

.output-canvas {
  border: 1px solid #ccc;
  width: 600px;
  height: 500px;
}
</style>
