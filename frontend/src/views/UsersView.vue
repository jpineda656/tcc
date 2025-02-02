<!-- frontend/src/views/UsersView.vue -->
<template>
  <TheNavbar />

  <div class="users-container">
    <h2 class="title">Gestión de Usuarios y Roles</h2>

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
          <!-- Si se está editando este usuario -->
          <div v-if="editUserId === user.id" class="edit-form">
            <input v-model="editData.nombre" placeholder="Nombre" />
            <input v-model="editData.apellido" placeholder="Apellido" />
            <input v-model="editData.correo" type="email" placeholder="Correo" />
            <!-- Campo para cambiar contraseña (opcional) -->
            <input v-model="editData.password" type="password" placeholder="Nueva Contraseña (opcional)" />
            <button @click="handleUpdateUser(user.id)">Guardar</button>
            <button @click="cancelEdit">Cancelar</button>
          </div>

          <!-- Vista normal (no editando) -->
          <div v-else class="user-item">
            <span class="user-info">
              {{ user.nombre }} {{ user.apellido }} - {{ user.correo }}
            </span>
            <div class="user-actions">
              <button @click="startEdit(user)">Editar</button>
              <button @click="openRolesModal(user)">Roles</button>
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

  <!-- Modal para asignar roles -->
  <div class="roles-modal" v-if="showRolesModal">
    <div class="roles-modal-content">
      <h3>Gestionar Roles para {{ selectedUser.nombre }}</h3>
      <p>ID de usuario: {{ selectedUser.id }}</p>

      <!-- Listado de roles disponibles -->
      <div class="available-roles">
        <h4>Roles disponibles:</h4>
        <ul>
          <li v-for="role in rolesList" :key="role.nombre_rol">
            <span>{{ role.nombre_rol }}</span>
            <!-- Agregar / Quitar rol segun si el usuario lo tiene -->
            <button v-if="!userHasRole(role.nombre_rol)" @click="assignRole(selectedUser.id, role.nombre_rol)">
              Asignar
            </button>
            <button v-else @click="removeRole(selectedUser.id, role.nombre_rol)">
              Remover
            </button>
          </li>
        </ul>
      </div>

      <!-- Botón para cerrar modal -->
      <button @click="closeRolesModal">Cerrar</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import TheNavbar from "@/components/TheNavbar.vue";
import { showConfirm, showSuccess, showError } from "@/utils/alertUtils"
import {
  getAllUsers,
  createUser,
  updateUser,
  deleteUser,
  getAllRoles,
  assignRoleToUser,
  removeRoleFromUser
} from "@/services/apiUsers";

const users = ref([]);
const newUserData = ref({ nombre: "", apellido: "", correo: "", password: "" });


// Para editar usuario
const editUserId = ref(null);
const editData = ref({ nombre: "", apellido: "", correo: "", password: "" });

// Errores
const errorCreate = ref("");
const errorLoad = ref("");
const isLoadingUsers = ref(false);

// Roles (para modal)
const rolesList = ref([]);     // Lista global de roles
const showRolesModal = ref(false);
const selectedUser = ref({});  // Usuario en edición de roles

////////////////////////////////////////////////////////////
// Cargar usuarios
////////////////////////////////////////////////////////////
async function loadUsers() {
  try {
    errorLoad.value = "";
    isLoadingUsers.value = true;
    users.value = await getAllUsers();
  } catch (error) {
    errorLoad.value = "Error al cargar usuarios.";
  } finally {
    isLoadingUsers.value = false;
  }
}

////////////////////////////////////////////////////////////
// Crear un nuevo usuario
////////////////////////////////////////////////////////////
async function handleCreateUser() {
  try {
    await createUser(newUserData.value);
    showSuccess("Usuario creado exitosamente")
    loadUsers();
    newUserData.value = { nombre: "", apellido: "", correo: "", password: "" };
  } catch (error) {
    errorCreate.value = "Error al crear usuario.";
    showError("Error al crear usuario")
  }
}

////////////////////////////////////////////////////////////
// Editar usuario
////////////////////////////////////////////////////////////
function startEdit(user) {
  editUserId.value = user.id;
  editData.value = {
    nombre: user.nombre,
    apellido: user.apellido,
    correo: user.correo,
    password: ""  // Para cambio opcional
  };
}
function cancelEdit() {
  editUserId.value = null;
}

async function handleUpdateUser(userId) {
  try {
    await updateUser(userId, editData.value);
    showSuccess("Usuario actualizado exitosamente")
    loadUsers();
    cancelEdit();
  } catch (error) {
    showError("Error al actualizar usuario")
    console.error("Error al actualizar usuario:", error);
  }
}

////////////////////////////////////////////////////////////
// Eliminar usuario
////////////////////////////////////////////////////////////
async function handleDeleteUser(userId) {
  const result = await showConfirm({
    title: "¿Estás seguro?",
    text: "Esta acción no se puede deshacer",
    icon: "warning",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar"
  })

  if (result.isConfirmed) {
    try {
      await deleteUser(userId)
      showSuccess("Usuario eliminado exitosamente")
      await loadUsers()
    } catch (error) {
      console.error("Error al eliminar usuario:", error)
      showError("No se pudo eliminar el usuario")
    }
  }
}

////////////////////////////////////////////////////////////
// Roles - Modal
////////////////////////////////////////////////////////////
async function openRolesModal(user) {
  selectedUser.value = user;
  showRolesModal.value = true;

  if (rolesList.value.length === 0) {
    try {
      // Cargar roles globales
      const data = await getAllRoles();
      rolesList.value = data; // array de { name: "admin" }, etc.
    } catch (err) {
      console.error("Error al cargar roles:", err);
    }
  }
}
function closeRolesModal() {
  showRolesModal.value = false;
  selectedUser.value = {};
}

function userHasRole(roleName) {
  if (!selectedUser.value.roles) return false;
  return selectedUser.value.roles.some(r => r.name === roleName);
}

async function assignRole(userId, roleName) {
  try {
    await assignRoleToUser(userId, roleName);
    // Actualizar local
    if (!selectedUser.value.roles) {
      selectedUser.value.roles = [];
    }
    selectedUser.value.roles.push({ name: roleName });
  } catch (err) {
    console.error("Error al asignar rol:", err);
  }
}

async function removeRole(userId, roleName) {
  try {
    await removeRoleFromUser(userId, roleName);
    if (selectedUser.value.roles) {
      selectedUser.value.roles = selectedUser.value.roles.filter(r => r.name !== roleName);
    }
  } catch (err) {
    console.error("Error al remover rol:", err);
  }
}

////////////////////////////////////////////////////////////
// onMounted => cargar usuarios
////////////////////////////////////////////////////////////
loadUsers();
</script>

<style scoped>
.users-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1rem;
  background-color: var(--dark-gray);
  color: var(--text-color);
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
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

/* Modal de Roles */
.roles-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.roles-modal-content {
  background-color: var(--medium-gray);
  padding: 1.5rem;
  border-radius: 8px;
  width: 400px;
  color: var(--white);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.roles-modal-content h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.available-roles {
  margin-top: 1rem;
}

.available-roles ul {
  list-style: none;
  padding: 0;
}

.available-roles li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--dark-gray);
  margin-bottom: 0.3rem;
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
}

.available-roles button {
  background-color: var(--accent-color);
  border: none;
  color: var(--white);
  border-radius: 4px;
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  font-weight: 500;
}

.available-roles button:hover {
  background-color: var(--primary-color);
}
</style>
