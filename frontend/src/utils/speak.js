export function speak(text) {
    if ('speechSynthesis' in window) {
      // Crear un objeto de mensaje
      const utterance = new SpeechSynthesisUtterance(text);
      // Configurar idioma (ej. español)
      utterance.lang = 'es-ES';
      // Ajustar velocidad, pitch, volumen si quieres
      utterance.rate = 1; // Velocidad (0.1 - 10)
      utterance.pitch = 1; // Tono (0 - 2)
      utterance.volume = 1;  // Puedes escoger entre las voces disponibles en el navegador
      // Lanzar
      window.speechSynthesis.speak(utterance);

      const voices = window.speechSynthesis.getVoices();
      console.log(voices); // Para ver cada voice.name, voice.lang, etc.
    } else {
      console.warn("Este navegador no soporta speechSynthesis.");
    }
  }
  