import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import { useUserStore } from '../store/user' // 引入用户Store（无需引入pinia）

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/home',
    name: 'Home',
    component: HomeView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory('/powerbi/'),
  routes
})

router.beforeEach((to, from, next) => {
  // 直接调用 useUserStore()，无需传递pinia（Pinia会自动获取全局实例）
  const userStore = useUserStore() 
  const isAuthenticated = userStore.access_token || localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' })
  } else {
    next()
  }
})
// 全局错误处理
router.onError((error) => {
  console.error('[路由错误]', error)
  alert(`路由错误: ${error.message}`)
})

export default router