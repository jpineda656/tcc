<!-- src/views/UsersView.vue -->
<template>
  <div>
    <TheNavbar />

    <div class="users-container">
      <h2 class="title">Gestión de Usuarios</h2>

      <!-- Sección para crear usuario -->
      <section class="create-section">
        <h3>Crear Nuevo Usuario</h3>
        <form @submit.prevent="handleCreateUser">
          <input v-model="newUserData.nombre" placeholder="Nombre" />
          <input v-model="newUserData.apellido" placeholder="Apellido" />
          <input v-model="newUserData.correo" type="email" placeholder="Correo" />
          <input v-model="newUserData.password" type="password" placeholder="Contraseña" />
          <button type="submit">Crear Usuario</button>
        </form>
        <p v-if="errorCreate" class="error">{{ errorCreate }}</p>
      </section>

      <!-- Sección para listar usuarios -->
      <section class="list-section">
        <div class="list-header">
          <h3>Lista de Usuarios ({{ users.length }})</h3>
          <button :disabled="isLoadingUsers" @click="loadUsers">
            {{ isLoadingUsers ? 'Cargando...' : 'Cargar Usuarios' }}
          </button>
        </div>
        <p v-if="errorLoad" class="error">{{ errorLoad }}</p>

        <!-- Mostrar lista si hay usuarios -->
        <ul class="users-list" v-if="!isLoadingUsers && users.length > 0">
          <li v-for="user in users" :key="user.id">
            <div v-if="editUserId === user.id" class="edit-form">
              <input v-model="editData.nombre" placeholder="Nombre" />
              <input v-model="editData.apellido" placeholder="Apellido" />
              <input v-model="editData.correo" type="email" placeholder="Correo" />
              <button @click="handleUpdateUser(user.id)">Guardar</button>
              <button @click="cancelEdit">Cancelar</button>
            </div>
            <div v-else class="user-item">
              <span class="user-info">
                {{ user.nombre }} {{ user.apellido }} - {{ user.correo }}
              </span>
              <div class="user-actions">
                <button @click="startEdit(user)">Editar</button>
                <button @click="handleDeleteUser(user.id)">Eliminar</button>
              </div>
            </div>
          </li>
        </ul>

        <!-- Si no hay usuarios y no está cargando -->
        <p v-else-if="!isLoadingUsers && users.length === 0" class="no-users">
          No hay usuarios registrados.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
import TheNavbar from "@/components/TheNavbar.vue";
import { ref } from "vue";
import {
  getAllUsers,
  createUser,
  updateUser,
  deleteUser
} from "@/services/apiUsers";

// Estado
const users = ref([]);
const newUserData = ref({ nombre: "", apellido: "", correo: "", password: "" });

// Editar usuario
const editUserId = ref(null);
const editData = ref({ nombre: "", apellido: "", correo: "" });

// Errores
const errorCreate = ref("");
const errorLoad = ref("");
const isLoadingUsers = ref(false); // Nuevo estado para indicar la carga

async function loadUsers() {
  try {
    errorLoad.value = "";
    isLoadingUsers.value = true; // Activa el loading
    users.value = await getAllUsers();
  } catch (error) {
    errorLoad.value = "Error al cargar usuarios.";
  } finally {
    isLoadingUsers.value = false; // Desactiva el loading
  }
}

async function handleCreateUser() {
  try {
    await createUser(newUserData.value);
    loadUsers();
    newUserData.value = { nombre: "", apellido: "", correo: "", password: "" };
  } catch (error) {
    errorCreate.value = "Error al crear usuario.";
  }
}

function startEdit(user) {
  editUserId.value = user.id;
  editData.value = { ...user };
}

function cancelEdit() {
  editUserId.value = null;
}

async function handleUpdateUser(userId) {
  try {
    await updateUser(userId, editData.value);
    loadUsers();
    cancelEdit();
  } catch (error) {
    console.error("Error al actualizar usuario:", error);
  }
}

async function handleDeleteUser(userId) {
  try {
    await deleteUser(userId);
    loadUsers();
  } catch (error) {
    console.error("Error al eliminar usuario:", error);
  }
}
</script>

<style scoped>
/* Ajusta estos estilos a tu tema global con variables como
   var(--dark-gray), var(--accent-color), etc.
*/

.users-container {
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

/* Cabecera de la lista de usuarios */
.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

/* Form de creación y edición */
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

/* Botones generales */
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

/* Errores */
.error {
  margin-top: 0.5rem;
  color: var(--danger-color);
  font-weight: 500;
}

/* Lista de usuarios */
.users-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.user-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--dark-gray);
  padding: 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.user-info {
  margin-right: 1rem;
}

.user-actions button {
  margin-left: 0.5rem;
}

/* Texto cuando no hay usuarios */
.no-users {
  font-style: italic;
  color: var(--light-gray);
  text-align: center;
}
</style>
