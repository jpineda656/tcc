//frontend/src/services/apiRoles.js
import axios from "@/services/api"; // <-- la instancia con interceptores

export async function getAllRoles() {
  try {
    const response = await axios.get("/roles/");
    return response.data;
  } catch (error) {
    throw error;
  }
}

export async function createRole(roleData) {
  try {
    const response = await axios.post("/roles", roleData);
    return response.data;
  } catch (error) {
    throw error;
  }
}

export async function updateRole(roleId, updates) {
  try {
    const response = await axios.put(`/roles/${roleId}`, updates);
    return response.data;
  } catch (error) {
    throw error;
  }
}

export async function deleteRole(roleId) {
  try {
    await axios.delete(`/roles/${roleId}`);
  } catch (error) {
    throw error;
  }
}
