// frontend/src/utils/recordingUtils.js

import { ref } from 'vue'

export function useRecording() {
  // Bandera para automatizar (entra mano => graba, sale mano => envía)
  const autoFlow = ref(true)

  // Estado principal (máquina de estados)
  // Posibles: 'IDLE' | 'PREPARING' | 'RECORDING' | 'STOPPED'
  const recordState = ref('IDLE')

  // Variables ya existentes
  const signLabel = ref('')
  const isRecording = ref(false)        // seguirá existiendo, aunque lo sincronicemos con 'RECORDING'
  const isPreparing = ref(false)        // sincrónico con 'PREPARING'
  const countdown = ref(0)
  const capturedFrames = ref([])

  const capturedGesturesCount = ref(0);

  // Conteo regresivo
  let countdownInterval = null

  // Detección de “no manos”
  const noHandFramesCount = ref(0)
  const NO_HANDS_THRESHOLD = 10

  /* ========================
   * Métodos de ayuda
   * ======================== */
  function setState(newState) {
    recordState.value = newState
    console.log('recordState =>', newState)
  }

  /**
   * Prepara la grabación (inicia cuenta regresiva de 4s).
   */
  function prepareRecording() {
    // if (!signLabel.value) {
    //   alert('Por favor ingresa la palabra/seña antes de grabar')
    //   return
    // }
    setState('PREPARING')
    isPreparing.value = true
    isRecording.value = false

    countdown.value = 2
    capturedFrames.value = []
    noHandFramesCount.value = 0

    // Iniciamos el temporizador de 4s
    countdownInterval = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(countdownInterval)
        countdownInterval = null
        isPreparing.value = false
        startRecording() // Pasa a RECORDING
      }
    }, 1000)
  }

  /**
   * Comienza la grabación real (tras el conteo).
   */
  function startRecording() {
    setState('RECORDING')
    isRecording.value = true
    isPreparing.value = false
    noHandFramesCount.value = 0
    console.log('Iniciando grabación...')
  }

  /**
   * Detiene la grabación y envía datos.
   * (Podrías separar "stop" de "send" si quisieras.)
   */
  async function stopRecording(sendDataCallback) {
    // Cancelar conteo si seguía
    if (countdownInterval) {
      clearInterval(countdownInterval)
      countdownInterval = null
    }
    isPreparing.value = false
    countdown.value = 0
    isRecording.value = false

    setState('STOPPED')

    if (!capturedFrames.value.length) {
      alert('No se han capturado datos')
      // Regresar a IDLE para esperar la próxima mano
      setState('IDLE')
      return
    }

    //Estructura de datos
    const bodyData = {
      label: signLabel.value,
      //framesCount: capturedFrames.value.length,
      framesData: capturedFrames.value
    }

    console.log('Enviando:', bodyData)
    // console.log(JSON.stringify(bodyData));

    if (capturedFrames.value.length > 0) {
      capturedGesturesCount.value += 1; 
    }

    // Llamamos a la callback
    if (typeof sendDataCallback === 'function') {
      await sendDataCallback(bodyData)
    }

    // Una vez enviado, volvemos a IDLE para permitir nuevas capturas
    setState('IDLE')
  }

  /**
   * handleResults:
   * Lógica que se llama en onResultsHolistic para cada frame:
   * - Si no hay manos => sumamos noHandFramesCount => si pasa umbral => stopRecording
   * - Si hay manos => si estamos IDLE => autoFlow => prepareRecording
   *                => si estamos RECORDING => capturar
   */
  function handleResults(handDetected, frameData, sendDataCallback) {
    // -- Manejo manual, si NO estamos grabando:
    // (Si no estás en autoFlow, se basará en botones.)
    if (!autoFlow.value) {
      if (isRecording.value && !handDetected) {
        noHandFramesCount.value++
        if (noHandFramesCount.value >= NO_HANDS_THRESHOLD) {
          console.log('No se detectan manos (autoFlow off); deteniendo grabación...')
      
          stopRecording(sendDataCallback)
        }
      } else if (isRecording.value && handDetected) {
        noHandFramesCount.value = 0
        if (Object.keys(frameData).length > 0) {
          //frameData.timestamp = performance.now()
          capturedFrames.value.push(frameData)
        }
      }
      return
    }

    // -- Con autoFlow encendido:
    switch (recordState.value) {
      case 'IDLE':
        // Al ver una mano en IDLE => iniciamos prepareRecording
        if (handDetected) {
          prepareRecording()
        }
        break

      case 'PREPARING':
        // Si se estaba preparando y la mano desaparece, podríamos volver a IDLE:
        if (!handDetected) {
          noHandFramesCount.value++
          if (noHandFramesCount.value >= NO_HANDS_THRESHOLD / 2) {
            // Media preferencia. O lo pones en 1 frame si quieres.
            console.log('Mano se fue durante conteo => cancelo grabación, regresa a IDLE')
            resetCountdown()
            setState('IDLE')
          }
        } else {
          noHandFramesCount.value = 0
        }
        break

      case 'RECORDING':
        if (handDetected) {
          // Capturamos
          noHandFramesCount.value = 0
          if (Object.keys(frameData).length > 0) {
            //frameData.timestamp = performance.now()
            capturedFrames.value.push(frameData)
          }
        } else {
          // Sube el contador
          noHandFramesCount.value++
          if (noHandFramesCount.value >= NO_HANDS_THRESHOLD) {
            console.log('No se detectan manos => deteniendo y enviando...')
            stopRecording(sendDataCallback)
          }
        }
        break

      case 'STOPPED':
        // Teóricamente, aquí ya se envió la data y pasamos a IDLE, 
        // pero si el code tarda un micro, cuidado.
        // Lo usual es: en stopRecording => setState('IDLE') al final.
        break
    }
  }

  /**
   * resetCountdown:
   * Pequeña función auxiliar para limpiar intervalos
   */
  function resetCountdown() {
    if (countdownInterval) {
      clearInterval(countdownInterval)
      countdownInterval = null
    }
    countdown.value = 0
    isPreparing.value = false
  }

  return {
    // Estado y banderas:
    autoFlow,
    recordState,
    signLabel,
    isRecording,
    isPreparing,
    countdown,
    capturedFrames,
    capturedGesturesCount,

    // Métodos:
    prepareRecording,
    startRecording,
    stopRecording,
    handleResults,

    // Extras por si los usas en UI o debug
    noHandFramesCount,
    NO_HANDS_THRESHOLD
  }
}
