// src/utils/alertUtils.js
import Swal from "sweetalert2"

/**
 * Muestra una notificación de éxito.
 * @param {string} message - Mensaje a mostrar.
 * @param {string} [title="Éxito"] - Título de la notificación.
 */
export function showSuccess(message, title = "Éxito") {
  Swal.fire(title, message, "success")
}

/**
 * Muestra una notificación de error.
 * @param {string} message - Mensaje a mostrar.
 * @param {string} [title="Error"] - Título de la notificación.
 */
export function showError(message, title = "Error") {
  Swal.fire(title, message, "error")
}

/**
 * Muestra un diálogo de confirmación.
 * @param {Object} options - Opciones para el diálogo.
 * @param {string} [options.title="¿Estás seguro?"] - Título del diálogo.
 * @param {string} [options.text=""] - Texto descriptivo.
 * @param {string} [options.icon="warning"] - Icono (por ejemplo, "warning").
 * @param {string} [options.confirmButtonText="Sí, confirmar"] - Texto del botón de confirmación.
 * @param {string} [options.cancelButtonText="Cancelar"] - Texto del botón de cancelación.
 * @returns {Promise} - La promesa de SweetAlert2 con la respuesta del usuario.
 */
export async function showConfirm(options = {}) {
  const {
    title = "¿Estás seguro?",
    text = "",
    icon = "warning",
    confirmButtonText = "Sí, confirmar",
    cancelButtonText = "Cancelar"
  } = options

  return Swal.fire({
    title,
    text,
    icon,
    showCancelButton: true,
    confirmButtonText,
    cancelButtonText
  })
}
