<!-- frontend/src/views/RolesView.vue -->
<template>
  <div>
    <TheNavbar />

    <div class="roles-container">
      <h2 class="title">Gestión de Roles</h2>

      <section class="create-section">
        <h3>Crear Nuevo Rol</h3>
        <form @submit.prevent="handleCreateRole">
          <input v-model="newRoleData.nombre_rol" placeholder="Nombre del Rol" />
          <button type="submit">Crear Rol</button>
        </form>
        <p v-if="errorCreate" class="error">{{ errorCreate }}</p>
      </section>

      <section class="list-section">
        <div class="list-header">
          <h3>Lista de Roles ({{ roles.length }})</h3>
          <button :disabled="isLoadingRoles" @click="loadRoles">
            {{ isLoadingRoles ? 'Cargando...' : 'Cargar Roles' }}
          </button>
        </div>
        <p v-if="errorLoad" class="error">{{ errorLoad }}</p>

        <!-- Mostrar lista si hay roles -->
        <ul class="roles-list" v-if="!isLoadingRoles && roles.length > 0">
          <li v-for="role in roles" :key="role.id">
            <div v-if="editRoleId === role.id" class="edit-form">
              <input v-model="editData.nombre_rol" placeholder="Nombre del Rol" />
              <button @click="handleUpdateRole(role.id)">Guardar</button>
              <button @click="cancelEdit">Cancelar</button>
            </div>
            <div v-else class="role-item">
              <span class="role-info">{{ role.nombre_rol }}</span>
              <div class="role-actions">
                <button @click="startEdit(role)">Editar</button>
                <button @click="handleDeleteRole(role.id)">Eliminar</button>
              </div>
            </div>
          </li>
        </ul>

        <!-- Si no hay roles y no está cargando -->
        <p v-else-if="!isLoadingRoles && roles.length === 0" class="no-roles">
          No hay roles registrados.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
import TheNavbar from "@/components/TheNavbar.vue";
import { ref } from "vue";
import { getAllRoles, createRole, updateRole, deleteRole } from "@/services/apiRoles";

const roles = ref([]);
const newRoleData = ref({ nombre_rol: "" });
const editRoleId = ref(null);
const editData = ref({ nombre_rol: "" });

const errorCreate = ref("");
const errorLoad = ref("");
const isLoadingRoles = ref(false); // Nuevo estado para la carga

async function loadRoles() {
  try {
    errorLoad.value = "";
    isLoadingRoles.value = true; // Activar loading
    roles.value = await getAllRoles();
  } catch (error) {
    errorLoad.value = "Error al cargar roles.";
  } finally {
    isLoadingRoles.value = false; // Desactivar loading
  }
}

async function handleCreateRole() {
  try {
    await createRole(newRoleData.value);
    loadRoles();
    newRoleData.value = { nombre_rol: "" };
  } catch (error) {
    errorCreate.value = "Error al crear rol.";
  }
}

function startEdit(role) {
  editRoleId.value = role.id;
  editData.value = { ...role };
}

function cancelEdit() {
  editRoleId.value = null;
}

async function handleUpdateRole(roleId) {
  try {
    await updateRole(roleId, editData.value);
    loadRoles();
    cancelEdit();
  } catch (error) {
    console.error("Error al actualizar rol:", error);
  }
}

async function handleDeleteRole(roleId) {
  try {
    await deleteRole(roleId);
    loadRoles();
  } catch (error) {
    console.error("Error al eliminar rol:", error);
  }
}
loadRoles();

</script>

<style scoped>
.roles-container {
  max-width: 800px;
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
  margin-bottom: 1.5rem;
  color: var(--white);
}

.create-section,
.list-section {
  background-color: var(--medium-gray);
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
}

.create-section h3,
.list-section h3 {
  margin-bottom: 1rem;
  font-size: 1.3rem;
  color: var(--white);
}

/* Header de la lista */
.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.create-section form,
.edit-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.create-section form input,
.edit-form input {
  flex: 1;
  min-width: 150px;
  padding: 0.4rem;
  border-radius: 4px;
  border: 1px solid var(--light-gray);
  background-color: var(--dark-gray);
  color: var(--white);
}

.create-section button,
.list-section button {
  background-color: var(--accent-color);
  color: var(--white);
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.create-section button:hover,
.list-section button:hover {
  background-color: var(--primary-color);
}

.error {
  margin-top: 0.5rem;
  color: var(--danger-color);
  font-weight: 500;
}

/* Lista de roles */
.roles-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.role-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--dark-gray);
  padding: 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.role-info {
  margin-right: 1rem;
}

.role-actions button {
  margin-left: 0.5rem;
}

/* Mensaje cuando no hay roles */
.no-roles {
  font-style: italic;
  color: var(--light-gray);
  text-align: center;
}
</style>
