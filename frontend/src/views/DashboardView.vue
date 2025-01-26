<template>
  <div>
    <!-- Navbar -->
    <TheNavbar />

    <!-- Contenedor principal -->
    <div class="dashboard-container">
      <h2 class="title">Panel de Control</h2>

      <!-- Sección de Bienvenida o Info de Usuario -->
      <div class="user-greeting">
        <h3>Hola, {{ username }}!</h3>
        <p>Bienvenido a tu panel de estadísticas.</p>
      </div>

      <!-- Sección de Estadísticas Resumidas -->
      <div class="stats-summary">
        <div class="stats-card" @click="goToCaptures">
          <h4>Capturas Realizadas</h4>
          <p>{{ capturesCount }}</p>
        </div>
        <div class="stats-card" @click="goToTrainings">
          <h4>Entrenamientos</h4>
          <p>{{ trainingsCount }}</p>
        </div>
      </div>

      <!-- Sección de Detalle de Capturas y Entrenamientos -->
      <div class="detailed-section">
        <!-- Detalle de Capturas -->
        <div class="detail-card">
          <h3>Historial de Capturas</h3>
          <table class="detail-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Palabra</th>
                <th>Frames</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="capture in captureLogs" :key="capture.id">
                <td>{{ capture.id }}</td>
                <td>{{ capture.label }}</td>
                <td>{{ capture.frames_count }}</td>
                <td>{{ formatDate(capture.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Detalle de Entrenamientos -->
        <div class="detail-card">
          <h3>Historial de Entrenamientos</h3>
          <table class="detail-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Estado</th>
                <th>Fecha Inicio</th>
                <th>Fecha Fin</th>
                <th>Accuracy</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="training in trainingLogs" :key="training.id">
                <td>{{ training.id }}</td>
                <td>
                  <span
                    class="status-pill"
                    :class="{
                      'completed': training.status === 'completed',
                      'failed': training.status === 'failed',
                      'started': training.status === 'started'
                    }"
                  >
                    {{ training.status }}
                  </span>
                </td>
                <td>{{ formatDate(training.started_at) }}</td>
                <td>{{ formatDate(training.finished_at) }}</td>
                <td>{{ training.accuracy }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "@/store/auth";
import { storeToRefs } from "pinia";

// Importa tu Navbar
import TheNavbar from "@/components/TheNavbar.vue";

// Importa tu instancia de Axios (con interceptores)
import axios from "@/services/api";

const authStore = useAuthStore();
const { username } = storeToRefs(authStore);

// Estados para estadísticas resumidas
const capturesCount = ref(0);
const trainingsCount = ref(0);

// Arrays para detalle
const captureLogs = ref([]);
const trainingLogs = ref([]);

/**
 * Función para formatear fecha/hora
 */
function formatDate(dateString) {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleString(); // Ajusta según tu preferencia
}

/**
 * Cargar datos del dashboard al montar
 */
onMounted(async () => {
  try {
    // 1) Carga stats resumidas
    // Suponiendo que tienes un endpoint /dashboard_data
    const resStats = await axios.get("/dashboard_data");
    capturesCount.value = resStats.data.capture_count || 0;
    trainingsCount.value = resStats.data.training_count || 0;

    // 2) Cargar logs de capturas
    // Suponiendo que tienes un endpoint /captures/logs
    const resCaptures = await axios.get("/captures/logs");
    captureLogs.value = resCaptures.data || [];

    // 3) Cargar logs de entrenamientos
    // Suponiendo que tienes un endpoint /trainings/logs
    const resTrainings = await axios.get("/trainings/logs");
    trainingLogs.value = resTrainings.data || [];
  } catch (error) {
    console.error("Error al cargar datos del Dashboard:", error);
    // Podrías mostrar un mensaje de error en pantalla
  }
});

/**
 * Funciones para navegar a detalles, si deseas
 */
function goToCaptures() {
  // Router push a la vista de Capturas
  // e.g. this.$router.push("/captures")
}

function goToTrainings() {
  // Router push a la vista de Entrenamientos
  // e.g. this.$router.push("/process")
}
</script>

<style scoped>

.dashboard-container {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 1rem;
  background-color: var(--dark-gray);
  color: var(--text-color);
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.title {
  text-align: center;
  font-size: 1.8rem;
  margin-bottom: 1rem;
  color: var(--white);
}

/* Sección de bienvenida */
.user-greeting {
  text-align: center;
  margin-bottom: 2rem;
}

/* Resumen de estadísticas */
.stats-summary {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.stats-card {
  flex: 1;
  background-color: var(--medium-gray);
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.stats-card:hover {
  background-color: var(--accent-color);
}

.stats-card h4 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--white);
}

.stats-card p {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 0.5rem;
}

/* Sección de tablas detalladas */
.detailed-section {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

/* Tarjeta individual para capturas o entrenamientos */
.detail-card {
  flex: 1;
  min-width: 300px;
  background-color: var(--medium-gray);
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* Títulos dentro de la tarjeta */
.detail-card h3 {
  margin: 0 0 1rem;
  font-size: 1.3rem;
  color: var(--white);
  text-align: center;
}

/* Tablas */
.detail-table {
  width: 100%;
  border-collapse: collapse;
}

.detail-table thead {
  background-color: var(--dark-gray);
}

.detail-table th,
.detail-table td {
  padding: 0.5rem;
  text-align: left;
  border-bottom: 1px solid var(--dark-gray);
}

.detail-table th {
  font-weight: 600;
  color: var(--white);
}
.detail-table td {
  color: var(--text-color);
}

/* Estilos para el status */
.status-pill {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  color: var(--white);
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: capitalize;
}

.status-pill.completed {
  background-color: #2ecc71; /* Verde */
}
.status-pill.failed {
  background-color: var(--danger-color);
}
.status-pill.started {
  background-color: var(--accent-color);
}

</style>
