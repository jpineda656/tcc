// src/services/apiUsers.js
import axios from "axios";

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
