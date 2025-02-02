//frontend/src/services/apiUsers.js
import axios from "@/services/api"; // <-- la instancia con interceptores

export async function getAllUsers() {
  try {
    const response = await axios.get("/users/");
    return response.data;
  } catch (error) {
    throw error;
  }
}

export async function createUser(userData) {
  try {
    const response = await axios.post("/users", userData);
    return response.data;
  } catch (error) {
    throw error;
  }
}

export async function updateUser(userId, updates) {
  try {
    const response = await axios.put(`/users/${userId}`, updates);
    return response.data;
  } catch (error) {
    throw error;
  }
}

export async function deleteUser(userId) {
  try {
    await axios.delete(`/users/${userId}`);
  } catch (error) {
    throw error;
  }
}


// Roles
export async function getAllRoles() {
  try {
    const response = await axios.get("/roles");
    return response.data;
  } catch (error) {
    throw error;
  }
}

export async function assignRoleToUser(userId, roleName) {
  // POST /users/{userId}/roles/{roleName}
  try {
    const response = await axios.post(`/users/${userId}/roles/${roleName}`);
    return response.data;
  } catch (error) {
    throw error;
  }
  
}

export async function removeRoleFromUser(userId, roleName) {
  // DELETE /users/{userId}/roles/{roleName}
  try {
    await axios.delete(`/users/${userId}/roles/${roleName}`);
  } catch (error) {
    throw error;
  }
}