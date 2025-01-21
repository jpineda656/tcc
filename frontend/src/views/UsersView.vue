// src/views/UsersView.vue
<template>
  <div>
    <TheNavbar />
    <div class="users-container">
      <h2 class="title">Gestión de Usuarios</h2>
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
      <section class="list-section">
        <h3>Lista de Usuarios</h3>
        <button @click="loadUsers">Cargar Usuarios</button>
        <ul>
          <li v-for="user in users" :key="user.id">
            <div v-if="editUserId === user.id">
              <input v-model="editData.nombre" placeholder="Nombre" />
              <input v-model="editData.apellido" placeholder="Apellido" />
              <input v-model="editData.correo" type="email" placeholder="Correo" />
              <button @click="handleUpdateUser(user.id)">Guardar</button>
              <button @click="cancelEdit">Cancelar</button>
            </div>
            <div v-else>
              {{ user.nombre }} {{ user.apellido }} - {{ user.correo }}
              <button @click="startEdit(user)">Editar</button>
              <button @click="handleDeleteUser(user.id)">Eliminar</button>
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
import { getAllUsers, createUser, updateUser, deleteUser } from "@/services/apiUsers";

const users = ref([]);
const newUserData = ref({ nombre: "", apellido: "", correo: "", password: "" });
const editUserId = ref(null);
const editData = ref({ nombre: "", apellido: "", correo: "" });
const errorCreate = ref("");
const errorLoad = ref("");

async function loadUsers() {
  try {
    errorLoad.value = "";
    users.value = await getAllUsers();
  } catch (error) {
    errorLoad.value = "Error al cargar usuarios.";
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
.users-container {
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