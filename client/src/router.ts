import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import { JWDJ_SUBPATH } from "@/config";

const HomeView = () => import("@/views/HomeView.vue");
const NewPollView = () => import(/* webpackChunkName: "new" */ "@/views/NewPollView.vue");
const MyPollsView = () => import(/* webpackChunkName: "my" */ "@/views/MyPollsView.vue");
const PollView = () => import(/* webpackChunkName: "poll" */ "@/views/PollView.vue");
const NotFoundComp = () => import(/* webpackChunkName: "404" */ "@/components/NotFoundComp.vue");
const EditView = () => import(/* webpackChunkName: "edit" */ "@/views/EditView.vue");

const routes: Array<RouteRecordRaw> = [
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

const router = createRouter({
  history: createWebHistory(JWDJ_SUBPATH), // process.env.BASE_URL
  routes,
});

export default router;
