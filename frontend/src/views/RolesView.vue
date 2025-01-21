<!-- src/views/RolesView.vue -->
<template>
  <div>
    <TheNavbar />
    <div class="roles-container">
      <h2 class="title">Gestión de Roles</h2>
      <section class="create-section">
        <h3>Crear Nuevo Rol</h3>
        <form @submit.prevent="handleCreateRole">
          <input v-model="newRoleData.name" placeholder="Nombre del Rol" />
          <button type="submit">Crear Rol</button>
        </form>
        <p v-if="errorCreate" class="error">{{ errorCreate }}</p>
      </section>
      <section class="list-section">
        <h3>Lista de Roles</h3>
        <button @click="loadRoles">Cargar Roles</button>
        <ul>
          <li v-for="role in roles" :key="role.id">
            <div v-if="editRoleId === role.id">
              <input v-model="editData.name" placeholder="Nombre del Rol" />
              <button @click="handleUpdateRole(role.id)">Guardar</button>
              <button @click="cancelEdit">Cancelar</button>
            </div>
            <div v-else>
              {{ role.name }}
              <button @click="startEdit(role)">Editar</button>
              <button @click="handleDeleteRole(role.id)">Eliminar</button>
            </div>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import TheNavbar from "@/components/TheNavbar.vue";
import { ref } from "vue";
import { getAllRoles, createRole, updateRole, deleteRole } from "@/services/apiRoles";

const roles = ref([]);
const newRoleData = ref({ name: "" });
const editRoleId = ref(null);
const editData = ref({ name: "" });
const errorCreate = ref("");
const errorLoad = ref("");

async function loadRoles() {
  try {
    errorLoad.value = "";
    roles.value = await getAllRoles();
  } catch (error) {
    errorLoad.value = "Error al cargar roles.";
  }
}

async function handleCreateRole() {
  try {
    await createRole(newRoleData.value);
    loadRoles();
    newRoleData.value = { name: "" };
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
</script>

<style scoped>
.roles-container {
  max-width: 800px;
  margin: 2rem auto;
}
.create-section,
.list-section {
  margin-bottom: 1.5rem;
}
.error {
  color: red;
  margin-top: 0.5rem;
}
.title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 1rem;
}
</style>

