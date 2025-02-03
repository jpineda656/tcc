<!-- frontend/src/views/DashboardView.vue -->
<template>
  <div>
    <TheNavbar />

    <div class="dashboard-container">
      <h2 class="dashboard-title">Panel de Control</h2>

      <!-- Sección de Resumen (estadísticas) -->
      <section class="summary-section">
        <!-- Tarjeta de capturas -->
        <div class="summary-card">
          <h3>Capturas</h3>
          <p class="summary-count">{{ summaryData.capture_count }}</p>
          <p>Capturas registradas en total</p>
        </div>

        <!-- Tarjeta de entrenamientos -->
        <div class="summary-card">
          <h3>Entrenamientos</h3>
          <p class="summary-count">{{ summaryData.training_count }}</p>
          <p>Entrenamientos realizados</p>
        </div>
      </section>

      <!-- Sección de Capturas (con paginación) -->
      <section class="list-section">
        <div class="section-header">
          <h3>Historial de Capturas</h3>
          <div class="pagination-controls">
            <button
              :disabled="pageCaptures <= 1"
              @click="pageCaptures--"
            >
              Prev
            </button>
            <span>Página {{ pageCaptures }}</span>
            <button
              :disabled="capturesList.length < limitCaptures"
              @click="pageCaptures++"
            >
              Next
            </button>
          </div>
        </div>

        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Palabra</th>
              <th>Fotogramas</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="capture in capturesList" :key="capture.id">
              <td>{{ capture.id }}</td>
              <td>{{ capture.label }}</td>
              <td>{{ capture.frames_count }}</td>
              <td>{{ formatDate(capture.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Sección de Entrenamientos (con paginación) -->
      <section class="list-section">
        <div class="section-header">
          <h3>Historial de Entrenamientos</h3>
          <div class="pagination-controls">
            <button
              :disabled="pageTrainings <= 1"
              @click="pageTrainings--"
            >
              Prev
            </button>
            <span>Página {{ pageTrainings }}</span>
            <button
              :disabled="trainingsList.length < limitTrainings"
              @click="pageTrainings++"
            >
              Next
            </button>
          </div>
        </div>

        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Estado</th>
              <th>Hora Inicio</th>
              <th>Hora Fin</th>
              <th>Exactitud</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="training in trainingsList" :key="training.id">
              <td>{{ training.id }}</td>
              <td>{{ training.status }}</td>
              <td>{{ formatDate(training.started_at) }}</td>
              <td>{{ formatDate(training.finished_at) }}</td>
              <td>{{ training.accuracy || 'N/A' }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Sección de Usuarios (Opcional, con paginación) -->
      <section class="list-section">
        <div class="section-header">
          <h3>Listado de Usuarios</h3>
          <div class="pagination-controls">
            <button
              :disabled="pageUsers <= 1"
              @click="pageUsers--"
            >
              Prev
            </button>
            <span>Página {{ pageUsers }}</span>
            <button
              :disabled="usersList.length < limitUsers"
              @click="pageUsers++"
            >
              Next
            </button>
          </div>
        </div>

        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Correo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="usr in usersList" :key="usr.id">
              <td>{{ usr.id }}</td>
              <td>{{ usr.nombre }} {{ usr.apellido }}</td>
              <td>{{ usr.correo }}</td>
            </tr>
          </tbody>
        </table>
      </section>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import TheNavbar from "@/components/TheNavbar.vue";
import axios from "@/services/api";

// Estado para la información resumida
const summaryData = ref({
  capture_count: 0,
  training_count: 0,
});

// ------------------
// Capturas
// ------------------
const capturesList = ref([]);
const pageCaptures = ref(1);
const limitCaptures = ref(5); // Muestra 5 capturas por página

// ------------------
// Entrenamientos
// ------------------
const trainingsList = ref([]);
const pageTrainings = ref(1);
const limitTrainings = ref(5);

// ------------------
// Usuarios (Opcional)
// ------------------
const usersList = ref([]);
const pageUsers = ref(1);
const limitUsers = ref(5);

/**
 * Formatea fecha a string legible
 */
function formatDate(dateStr) {
  if (!dateStr) return "-";
  const d = new Date(dateStr);
  return d.toLocaleString();
}

/**
 * Cargar datos de Resumen (cantidad de capturas, entrenamientos, etc.)
 */
async function fetchDashboardSummary() {
  try {
    const resp = await axios.get("/dashboard/data");
    summaryData.value = resp.data;
  } catch (error) {
    console.error("Error al cargar datos de resumen:", error);
  }
}

/**
 * Cargar Capturas, usando la paginación actual (pageCaptures, limitCaptures)
 */
async function fetchCaptures() {
  try {
    const resp = await axios.get("/dashboard/captures", {
      params: {
        page: pageCaptures.value,
        limit: limitCaptures.value
      }
    });
    capturesList.value = resp.data;
  } catch (error) {
    console.error("Error al cargar capturas:", error);
  }
}

/**
 * Cargar Entrenamientos, usando la paginación actual (pageTrainings, limitTrainings)
 */
async function fetchTrainings() {
  try {
    const resp = await axios.get("/dashboard/trainings", {
      params: {
        page: pageTrainings.value,
        limit: limitTrainings.value
      }
    });
    trainingsList.value = resp.data;
  } catch (error) {
    console.error("Error al cargar entrenamientos:", error);
  }
}

/**
 * Cargar Usuarios, usando la paginación actual (pageUsers, limitUsers)
 */
async function fetchUsers() {
  try {
    const resp = await axios.get("/users", {
      params: {
        page: pageUsers.value,
        limit: limitUsers.value
      }
    });
    usersList.value = resp.data; 
  } catch (error) {
    console.error("Error al cargar usuarios:", error);
  }
}

/**
 * Al montar, cargamos todo lo necesario:
 * - resumen
 * - lista capturas
 * - lista entrenamientos
 * - lista usuarios
 */
onMounted(async () => {
  await fetchDashboardSummary();
  await fetchCaptures();
  await fetchTrainings();
  await fetchUsers(); // si lo usas
});

/**
 * Observamos los cambios en pageCaptures, limitCaptures
 * y volvemos a cargar la lista de capturas
 */
watch([pageCaptures, limitCaptures], () => {
  fetchCaptures();
});

/**
 * Observamos cambios en pageTrainings, limitTrainings
 */
watch([pageTrainings, limitTrainings], () => {
  fetchTrainings();
});

/**
 * Observamos cambios en pageUsers, limitUsers
 */
watch([pageUsers, limitUsers], () => {
  fetchUsers();
});
</script>

<style scoped>
.dashboard-container {
  max-width: 1100px;
  margin: 2rem auto;
  background-color: var(--dark-gray);
  padding: 1rem 2rem;
  border-radius: 8px;
  color: var(--text-color);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.dashboard-title {
  text-align: center;
  font-size: 1.8rem;
  margin-bottom: 1rem;
  color: var(--white);
}

/* Sección de tarjetas de resumen */
.summary-section {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.summary-card {
  background-color: var(--medium-gray);
  border-radius: 8px;
  padding: 1rem;
  width: 200px;
  text-align: center;
  transition: transform 0.2s ease, background-color 0.2s ease;
}
.summary-card:hover {
  transform: translateY(-3px);
  background-color: var(--accent-color);
}

.summary-card h3 {
  margin: 0;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: var(--white);
}
.summary-count {
  font-size: 2rem;
  font-weight: bold;
  color: var(--white);
  margin: 0.5rem 0;
}

/* Secciones de tablas */
.list-section {
  margin-bottom: 2rem;
  background-color: var(--medium-gray);
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.section-header h3 {
  font-size: 1.2rem;
  color: var(--white);
  margin: 0;
}

/* Paginación */
.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.pagination-controls button {
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.pagination-controls button:hover {
  background-color: var(--accent-color);
}
.pagination-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Tablas */
.data-table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--dark-gray);
  color: var(--text-color);
}

.data-table thead {
  background-color: var(--primary-color);
}
.data-table thead th {
  padding: 0.75rem;
  text-align: left;
  color: var(--white);
}
.data-table tbody tr {
  transition: background-color 0.2s ease;
}
.data-table tbody tr:hover {
  background-color: rgba(255,255,255,0.1);
}
.data-table td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--medium-gray);
}
</style>
