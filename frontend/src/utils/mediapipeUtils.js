// src/utils/mediapipeUtils.js

import { ref, onBeforeUnmount } from 'vue'
import { Holistic } from '@mediapipe/holistic'
import { Camera } from '@mediapipe/camera_utils'

/**
 * useHolistic
 * Encapsula la lógica de inicialización y control de MediaPipe Holistic.
 *
 * @param {Function} onResults - Callback que se llama cada vez que Holistic genera resultados (p.ej. para dibujar).
 * @returns {Object} - Retorna referencias y métodos para usar en un componente Vue 3.
 */
export function useHolistic(onResults) {
  // Referencias a los elementos de video y canvas
  const videoRef = ref(null)
  const canvasRef = ref(null)

  // Instancias de Holistic y Camera
  let holisticInstance = null
  let cameraInstance = null

  // Estado para saber si la cámara está activa
  const isCameraActive = ref(false)

  /**
   * Inicializa Holistic y la cámara, indicando que preferimos usar WebGL (GPU).
   * @param {Object} options - Configuración de Holistic.
   * @param {string} wasmPath - Ruta local para los archivos WASM (si no quieres usar CDN).
   */
  const initHolistic = (options = {}, wasmPath = '') => {
    holisticInstance = new Holistic({
      locateFile: (file) => {
        // Si wasmPath está vacío, usamos un CDN por defecto
        return wasmPath
          ? `${wasmPath}/${file}`
          : `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`
      },
    })

    // Ajustamos opciones para intentar forzar o priorizar el uso de GPU (WebGL)
    holisticInstance.setOptions({
      modelComplexity: 3,
      smoothLandmarks: true,
      enableSegmentation: true,
      smoothSegmentation: true,
      refineFaceLandmarks: true,

      // Ajustes de GPU / WebGL:
      // MediaPipe debería preferir WebGL con esta config
      useCpuInference: false,  // Indica que no queremos caer en CPU a menos que sea necesario
      webGlVersion: 2,        // Intenta usar WebGL2

      ...options,
    })

    // Cuando haya resultados del modelo, invocamos el callback
    holisticInstance.onResults(onResults)

    // Crear la instancia de cámara
    cameraInstance = new Camera(videoRef.value, {
      onFrame: async () => {
        if (holisticInstance) {
          await holisticInstance.send({ image: videoRef.value })
        }
      },
      width: 640,
      height: 480,
    })

    // Iniciar la cámara
    cameraInstance.start()
    isCameraActive.value = true
  }

  /**
   * Activa o desactiva la cámara.
   */
  const toggleCamera = () => {
    if (!cameraInstance) return
    if (isCameraActive.value) {
      cameraInstance.stop()
      isCameraActive.value = false
    } else {
      cameraInstance.start()
      isCameraActive.value = true
    }
  }

  /**
   * Libera los recursos (cámara y modelo) al desmontar el componente.
   */
  const destroyHolistic = () => {
    if (cameraInstance) {
      cameraInstance.stop()
      cameraInstance = null
    }
    if (holisticInstance) {
      // Holistic no tiene un método destroy oficial, usamos close() si existe
      holisticInstance.close && holisticInstance.close()
      holisticInstance = null
    }
  }

  onBeforeUnmount(() => {
    destroyHolistic()
  })

  // Retornamos todo lo necesario para el componente
  return {
    videoRef,
    canvasRef,
    initHolistic,
    toggleCamera,
    destroyHolistic,
    isCameraActive,
  }
}
