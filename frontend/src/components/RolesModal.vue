<template>
    <div class="roles-modal" v-if="show">
      <div class="roles-modal-content">
        <h3>Gestionar Roles para {{ selectedUser.nombre }}</h3>
        <p>ID de usuario: {{ selectedUser.id }}</p>
  
        <!-- Listado de roles disponibles -->
        <div class="available-roles">
          <h4>Roles disponibles:</h4>
          <ul>
            <li v-for="role in rolesList" :key="role.nombre_rol">
              <span>{{ role.nombre_rol }}</span>
              <!-- Si el usuario no tiene el rol, muestra el botón para asignarlo -->
              <button v-if="!userHasRole(role.nombre_rol)" @click="assignRole(selectedUser.id, role.nombre_rol)">
                Asignar
              </button>
              <!-- Si ya lo tiene, muestra el botón para removerlo -->
              <button v-else @click="removeRole(selectedUser.id, role.nombre_rol)">
                Remover
              </button>
            </li>
          </ul>
        </div>
  
        <!-- Botón para cerrar el modal -->
        <button class="close-modal" @click="handleClose">Cerrar</button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from "vue";
  import { getAllRoles, assignRoleToUser, removeRoleFromUser } from "@/services/apiUsers";
  import { showSuccess, showError } from "@/utils/alertUtils";
  
  // Recibir props del componente padre
  const props = defineProps({
    selectedUser: {
      type: Object,
      required: true
    },
    show: {
      type: Boolean,
      default: false
    }
  });
  const emit = defineEmits(["close"]);
  
  // Lista de roles disponibles obtenida desde la API
  const rolesList = ref([]);
  
  onMounted(async () => {
    try {
      const roles = await getAllRoles();
      rolesList.value = roles; // Se espera que el API devuelva un arreglo de objetos con propiedad "name"
    } catch (error) {
      console.error("Error al cargar roles:", error);
      showError("Error al cargar roles");
    }
  });
  
  // Función auxiliar para verificar si el usuario ya tiene asignado un rol
  function userHasRole(roleName) {
    if (!props.selectedUser.roles) return false;
    return props.selectedUser.roles.some(r => r.nombre_rol === roleName);
  }
  
  // Función para asignar un rol
  async function assignRole(userId, roleName) {
    try {
      await assignRoleToUser(userId, roleName);
      if (!props.selectedUser.roles) {
        props.selectedUser.roles = [];
      }
      if (!userHasRole(roleName)) {
        props.selectedUser.roles.push({ nombre_rol: roleName });
        // Forzamos la actualización asignando una nueva referencia al array
        props.selectedUser.roles = [...props.selectedUser.roles];
      }
      showSuccess("Rol asignado exitosamente");
    } catch (error) {
      console.error("Error al asignar rol:", error);
      showError("No se pudo asignar el rol");
    }
  }
  
  // Función para remover un rol
  async function removeRole(userId, roleName) {
    try {
      await removeRoleFromUser(userId, roleName);
      if (props.selectedUser.roles) {
        props.selectedUser.roles = props.selectedUser.roles.filter(r => r.nombre_rol !== roleName);
        props.selectedUser.roles = [...props.selectedUser.roles];
      }
      showSuccess("Rol removido exitosamente");
    } catch (error) {
      console.error("Error al remover rol:", error);
      showError("No se pudo remover el rol");
    }
  }
  
  function handleClose() {
    emit("close");
  }
  </script>
  
  <style scoped>
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
  
  .close-modal {
    margin-top: 1rem;
    background-color: var(--primary-color);
    color: var(--white);
    border: none;
    border-radius: 4px;
    padding: 0.5rem 1rem;
    cursor: pointer;
  }
  </style>
  