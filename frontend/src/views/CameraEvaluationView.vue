<!-- src/views/CameraEvaluationView.vue -->
<template>
  <div class="camera-container">
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

      <!-- Botón para mostrar configuración adicional -->
      <button class="btn-settings" @click="showSettings = !showSettings">
        Configuraciones Adicionales
      </button>

      <!-- Panel de configuración adicional (toggle con showSettings) -->
      <div class="settings-panel" v-if="showSettings">
        <h3>Configuraciones</h3>

        <!-- 1) Ocultar/mostrar landmarks -->
        <label>
          <input type="checkbox" v-model="showLandmarks" />
          Mostrar Puntos de Referencia
        </label>

        <!-- 2) Cambiar colores de landmarks -->
        <div class="color-pickers">
          <label>Color Manos Derecha:
            <input type="color" v-model="landmarkColors.rightHand" />
          </label>
          <label>Color Manos Izquierda:
            <input type="color" v-model="landmarkColors.leftHand" />
          </label>
          <label>Color Rostro:
            <input type="color" v-model="landmarkColors.face" />
          </label>
          <label>Color Pose:
            <input type="color" v-model="landmarkColors.pose" />
          </label>
        </div>

        <!-- 3) Selección de voces en español -->
        <div class="voice-select">
          <label for="voice">Voz en Español:</label>
          <select id="voice" v-model="selectedVoiceIndex">
            <option
              v-for="(voice, idx) in esVoices"
              :key="idx"
              :value="idx"
            >
              {{ voice.name }} ({{ voice.lang }})
            </option>
          </select>
        </div>
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

      <!-- Mensaje de cuenta regresiva -->
      <div v-if="isPreparing" class="countdown-message">
        <span>Comenzando en {{ countdown }}...</span>
      </div>

      <!-- Palabras detectadas -->
      <div class="recognized-words" v-if="recognizedWords.length">
        <h4>Texto detectado:</h4>
        <ul class="words-list">
          <li v-for="(word, index) in recognizedWords" :key="index">
            {{ word }}
          </li>
        </ul>
      </div>
    </div>

    <!-- Sección de Vista de Cámara / Canvas -->
    <div class="camera-view">
      <video ref="videoRef" class="video-preview" playsinline></video>
      <canvas ref="canvasRef" class="output-canvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from "@/services/api"

// Composable para inicializar Holistic y manejar la cámara
import { useHolistic } from '@/utils/mediapipeUtils'
// Composable para dibujar landmarks
import { useDrawing } from '@/utils/drawingUtils'
// Composable para la lógica de grabación (cuenta regresiva, captura)
import { useRecording } from '@/utils/recordingUtils'

// Importar la función speak
import { speak } from "@/utils/speak.js"

////////////////////////////////////////////////////////////
// DIBUJO
////////////////////////////////////////////////////////////
const { drawFaceLandmarks, drawPoseLandmarks, drawHandLandmarks } = useDrawing()

////////////////////////////////////////////////////////////
// GRABACIÓN
////////////////////////////////////////////////////////////
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

////////////////////////////////////////////////////////////
// ESTADOS
////////////////////////////////////////////////////////////
// Palabras detectadas
const recognizedWords = ref([])

// Control de cámara
const {
  videoRef,
  canvasRef,
  initHolistic,
  toggleCamera,
  isCameraActive
} = useHolistic(onResultsHolistic)

// Mostrar/ocultar panel de configuraciones
const showSettings = ref(false)

// Mostrar/ocultar landmarks
const showLandmarks = ref(true)

// Colores de landmarks
const landmarkColors = ref({
  rightHand: "#CC0000",  // Default color mano derecha
  leftHand: "#00CC00",   // Default color mano izquierda
  face: "#E0E0E0",       // Default color rostro
  pose: "#FF00FF"        // Default color pose, ajusta a tu gusto
})

// Voces en español y selección
const esVoices = ref([])            // Se llenará con getVoices() filtradas
const selectedVoiceIndex = ref(0)   // Índice en esVoices

/**
 * - Llamado cuando se complete la grabación y se envíen datos.
 */
async function sendDataCallback(bodyData) {
  try {
    const response = await axios.post("/", bodyData);
    const result = response.data;

    if (result.predicted_label) {
      recognizedWords.value.push(result.predicted_label);

      // Llamar a speak con la voz seleccionada
      const voiceObj = esVoices.value[selectedVoiceIndex.value]
      speak(result.predicted_label, voiceObj)
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

/**
 * onResultsHolistic: Se llama cada vez que Holistic produce landmarks.
 */
function onResultsHolistic(results) {
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight

  ctx.save()
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height)
  ctx.restore()

  // Si showLandmarks es true, dibujamos
  if (showLandmarks.value) {
    drawAllLandmarks(ctx, results)
  }

  // Determinar si hay manos detectadas
  const handDetected = !!(results.rightHandLandmarks || results.leftHandLandmarks)

  // Armar frameData
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

  // Grabar
  handleResults(handDetected, frameData, sendDataCallback)
}

/**
 * Función refactor para dibujar todos los landmarks con colores personalizables.
 */
function drawAllLandmarks(ctx, results) {
  // Rostro
  if (results.faceLandmarks) {
    drawFaceLandmarks(ctx, results.faceLandmarks, {
      color: landmarkColors.value.face, // <= cambiar if needed
      lineWidth: 1
    })
  }
  // Pose
  if (results.poseLandmarks) {
    drawPoseLandmarks(ctx, results.poseLandmarks, {
      color: landmarkColors.value.pose,
      lineWidth: 2
    })
  }
  // Mano derecha
  if (results.rightHandLandmarks) {
    drawHandLandmarks(ctx, results.rightHandLandmarks, landmarkColors.value.rightHand, "#00FFFF")
  }
  // Mano izquierda
  if (results.leftHandLandmarks) {
    drawHandLandmarks(ctx, results.leftHandLandmarks, landmarkColors.value.leftHand, "#FFFF00")
  }
}

////////////////////////////////////////////////////////////
// Manejo de Voces en Español
////////////////////////////////////////////////////////////
function loadSpanishVoices() {
  const allVoices = window.speechSynthesis.getVoices()
  // Filtrar solo las voces es-*
  const filtered = allVoices.filter(voice => voice.lang.startsWith("es"))
  // Si quieres solo 4, recorta:
  esVoices.value = filtered.slice(0, 4)
  // Ajusta si no hay 4
  if (esVoices.value.length === 0) {
    console.warn("No hay voces en español disponibles en este navegador.")
  }
}

onMounted(() => {
  // Iniciar Holistic
  initHolistic({
    modelComplexity: 2,
    smoothLandmarks: true,
    enableSegmentation: true,
    smoothSegmentation: true,
    refineFaceLandmarks: true,
    selfieMode: true,
    useCpuInference: false,
    webGlVersion: 2,
  }, '')

  // Cargar voces
  if ('speechSynthesis' in window) {
    // speechSynthesis.getVoices() puede estar vacío al primer load
    // Se recomienda un callback
    window.speechSynthesis.onvoiceschanged = loadSpanishVoices
    // Llamar la primera vez
    loadSpanishVoices()
  }
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

/* Botones Principales */
.btn-camera,
.btn-settings {
  background-color: var(--primary-color);
  color: var(--white);
  padding: 0.5rem 1rem;
  border: none;
  cursor: pointer;
  font-weight: 500;
  border-radius: 4px;
  transition: background-color 0.3s ease;
  margin-bottom: 0.5rem;
}
.btn-camera.active {
  background-color: var(--danger-color);
}
.btn-camera:hover,
.btn-settings:hover {
  background-color: var(--accent-color);
}

/* Panel de configuraciones */
.settings-panel {
  background-color: var(--dark-gray);
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  color: var(--white);
}
.settings-panel h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}
.color-pickers,
.voice-select {
  margin: 0.5rem 0;
}
.color-pickers label,
.voice-select label {
  display: block;
  margin-bottom: 0.3rem;
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

/* Countdown resaltado */
.countdown-message {
  color: #ff5252; 
  font-weight: bold;
  font-size: 1.4rem;
  text-shadow: 1px 1px #000;
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
  padding-left: 1.2rem; /* deja algo de espacio para la lista */
}
.recognized-words .words-list li {
  margin-bottom: 0.3rem;
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
  display: none; /* Ocúltalo si deseas */
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
