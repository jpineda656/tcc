// frontend/src/utils/speak.js

/**
 * speak(text, voiceObj)
 * Reproduce en voz alta el texto dado.
 * - text: la frase o palabra a pronunciar.
 * - voiceObj: objeto de tipo SpeechSynthesisVoice (opcional). 
 */
export function speak(text, voiceObj) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);

    // Si tenemos un objeto de voz, lo aplicamos
    if (voiceObj) {
      utterance.voice = voiceObj;
      // También podrías aplicar utterance.lang = voiceObj.lang 
      // si deseas forzar el idioma exacto de la voz.
    } else {
      // Fallback en caso de no tener uno. 
      utterance.lang = 'es-ES'; 
    }

    // Ajustar velocidad, pitch, volumen si lo deseas:
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;

    window.speechSynthesis.speak(utterance);
  } else {
    console.warn("Este navegador no soporta speechSynthesis.");
  }
}
