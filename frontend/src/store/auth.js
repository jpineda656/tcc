// src/store/auth.js
import { defineStore } from "pinia";
import axios from "axios";

axios.defaults.baseURL = "http://localhost:8000";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: null,
    username: null,
    redirectPath: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(username, password) {
      try {
        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);

        const response = await axios.post("/auth/login", formData);
        const { access_token } = response.data;

        this.token = access_token;
        this.username = username;
        localStorage.setItem("token", access_token);
        localStorage.setItem("username", username);

        axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      } catch (error) {
        throw error;
      }
    },

    logout() {
      this.token = null;
      this.username = null;
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      delete axios.defaults.headers.common["Authorization"];
    },

    initializeStore() {
      const token = localStorage.getItem("token");
      const username = localStorage.getItem("username");

      if (token) {
        this.token = token;
        this.username = username;
        axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      }
    },

    setRedirectPath(path) {
      this.redirectPath = path;
    },

    clearRedirectPath() {
      this.redirectPath = null;
    },
  },
});