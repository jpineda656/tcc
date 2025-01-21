<!-- views/cameraView.vue -->
<template>
  <TheNavbar />

  <div class="camera-container">

    <!-- Sección de Configuración / Acciones -->
    <div class="controls">
      <!-- Título o indicador del flujo -->
      <h2>Captura de señas con MediaPipe</h2>

      <!-- Botón para activar/desactivar la cámara -->
      <button 
        class="btn-camera"
        :class="{ active: isCameraActive }"
        @click="toggleCamera"
      >
        {{ isCameraActive ? 'Detener cámara' : 'Iniciar cámara' }}
      </button>

      <!-- Input para la palabra/seña -->
      <div class="sign-input">
        <label for="sign-label">Palabra/Seña:</label>
        <input 
          id="sign-label" 
          v-model="signLabel" 
          type="text" 
          placeholder="Ej: Hola" 
        />
      </div>

      <!-- Botones para grabación -->
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
      <!-- Video (oculto si no lo deseas ver) -->
      <video ref="videoRef" class="video-preview" playsinline></video>
      
      <!-- Canvas donde se dibujan los landmarks -->
      <canvas ref="canvasRef" class="output-canvas"></canvas>
    </div>

  </div>
</template>

<script setup>
import TheNavbar from "@/components/TheNavbar.vue"
import { onMounted, ref } from 'vue'
import { useHolistic } from '@/utils/mediapipeUtils'
import { useDrawing } from '@/utils/drawingUtils'
import { useRecording } from '@/utils/recordingUtils'

const { 
  drawFaceLandmarks, 
  drawPoseLandmarks, 
  drawHandLandmarks 
} = useDrawing()

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
} = useRecording()

// Nueva variable para el mensaje de éxito
const successMessage = ref('')

/**
 * Enviar datos al backend (callback).
 * Puedes modificar la URL o usar axios.
 */
async function sendDataCallback(bodyData) {
  try {
    const response = await fetch('http://localhost:8000/captura', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bodyData)
    })

    if (!response.ok) {
      throw new Error(`Error en el servidor: ${response.status}`)
    }
    // alert('Datos enviados correctamente al backend')
        // Establecer el mensaje de éxito
    successMessage.value = 'Datos enviados correctamente al servidor'
    // Limpiar el mensaje después de 3 segundos
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    console.error('Error al enviar datos:', error)
    alert('Ocurrió un error al enviar los datos.')
  }
}

/**
 * stopRecording pero pasándole la callback de envío.
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

  // Dibujo
  drawFaceLandmarks(ctx, results.faceLandmarks)
  drawPoseLandmarks(ctx, results.poseLandmarks)
  drawHandLandmarks(ctx, results.rightHandLandmarks, '#CC0000', '#00FFFF')
  drawHandLandmarks(ctx, results.leftHandLandmarks, '#00CC00', '#FFFF00')
  ctx.restore()

  // Determinar si hay manos
  const handDetected = !!(results.rightHandLandmarks || results.leftHandLandmarks)

  // frameData con cara/pose/manos
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

  // Llamamos a la función del composable para manejar la lógica
  handleResults(handDetected, frameData, sendDataCallback)
}

/* ==========================
   2) Uso del composable Holistic
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
    '' // Ruta local
  )
})
</script>

<style scoped>
/* Contenedor principal para la vista de la cámara y los controles */
.camera-container {
  display: flex;
  flex-direction: row;
  gap: 2rem;
  margin: 1rem 2rem;
}
.success-message {
  color: #27ae60;
  font-weight: bold;
  font-size: 1rem;
  margin-top: 1rem;
}


/* Sección de controles / acciones */
.controls {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Un título para dar contexto */
.controls h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}

/* Botón general de la cámara */
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

/* Estados en base a clases dinámicas */
.btn-camera.active {
  background-color: #e74c3c;
}

/* Hover */
.btn-camera:hover {
  background-color: #34495e;
}

/* Sección del input de la seña */
.sign-input {
  display: flex;
  flex-direction: column;
}

.sign-input label {
  font-size: 0.9rem;
  margin-bottom: 0.3rem;
}

.sign-input input {
  border: 1px solid #ccc;
  padding: 0.4rem;
  border-radius: 4px;
}

/* Botones de grabación */
.recording-buttons {
  display: flex;
  gap: 1rem;
}

/* Botón grabar */
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

/* Botón detener */
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

/* Zona donde están el video y el canvas */
.camera-view {
  flex: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* Video de previsualización */
.video-preview {
  display: none; /* Oculto si no quieres mostrar el video */
  border: 1px solid #ccc;
  width: 600px;
  height: 500px;
  background-color: #000;
  margin-bottom: 1rem;
}

/* Canvas */
.output-canvas {
  border: 1px solid #ccc;
  width: 600px;
  height: 500px;
}
</style>

