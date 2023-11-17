import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import { JWDJ_SUBPATH, JWDJ_LOGIN_MANAGER } from "@/config";

const HomeView = () => import(/* webpackChunkName: "home" */ "@/views/HomeView.vue");
const NewPollView = () => import(/* webpackChunkName: "new" */ "@/views/NewPollView.vue");
const LoginView = () => import(/* webpackChunkName: "login" */ "@/views/LoginView.vue");
const UserView = () => import(/* webpackChunkName: "user" */ "@/views/UserView.vue");
const MyPollsView = () => import(/* webpackChunkName: "my" */ "@/views/MyPollsView.vue");
const PollView = () => import(/* webpackChunkName: "poll" */ "@/views/PollView.vue");
const NotFoundComp = () => import(/* webpackChunkName: "404" */ "@/components/NotFoundComp.vue");
const EditView = () => import(/* webpackChunkName: "edit" */ "@/views/EditView.vue");

let routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/new",
    name: "new",
    component: NewPollView,
  },
  {
    path: "/my-polls",
    name: "my-polls",
    component: MyPollsView,
  },
  {
    path: "/poll/:id",
    name: "poll",
    component: PollView,
  },
  {
    path: "/edit/:id",
    name: "edit",
    component: EditView,
  },
  {
    path: "/:pathMatch(.*)*",
    name: "404",
    component: NotFoundComp,
  },
];

if (JWDJ_LOGIN_MANAGER) {
  routes = routes.concat([
    {
      path: "/login",
      name: "login",
      component: LoginView,
    },
    {
      path: "/user",
      name: "user",
      component: UserView,
    },
  ]);
}

const router = createRouter({
  history: createWebHistory(JWDJ_SUBPATH), // process.env.BASE_URL
  routes,
});

export default router;
