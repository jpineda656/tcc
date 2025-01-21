// src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/store/auth";

const LoginView = () => import("@/views/LoginView.vue");
const DashboardView = () => import("@/views/DashboardView.vue");
const UsersView = () => import("@/views/UsersView.vue");
const RolesView = () => import("@/views/RolesView.vue");
const CameraView = () => import("@/views/CameraView.vue");
// const NotFoundView = () => import("@/views/NotFoundView.vue");
const CameraEvaluationView = () => import("@/views/CameraEvaluationView.vue");

const routes = [
  { path: "/login", name: "Login", component: LoginView },
  { path: "/", name: "/", component: CameraEvaluationView },
  { path: "/dashboard", name: "Dashboard", component: DashboardView, meta: { requiresAuth: true } },
  { path: "/users", name: "Users", component: UsersView, meta: { requiresAuth: true } },
  { path: "/roles", name: "Roles", component: RolesView, meta: { requiresAuth: true } },
  { path: "/camera", name: "Camera", component: CameraView, meta: { requiresAuth: true } },
  // { path: "/:catchAll(.*)", name: "NotFound", component: NotFoundView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Guard global de navegación
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.name === "Login" && authStore.isAuthenticated) {
    return next("/dashboard");
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    authStore.setRedirectPath(to.fullPath);
    return next("/login");
  }

  next();
});

export default router;