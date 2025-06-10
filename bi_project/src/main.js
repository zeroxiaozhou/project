import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import Layout from './components/Layout.vue'  // 引入布局组件
import router from './router'
import { createPinia } from 'pinia'
import 'element-plus/dist/index.css'


const app = createApp(Layout)  // 使用布局组件作为根组件
const pinia = createPinia()
app.use(ElementPlus)
app.use(pinia)
app.use(router)
app.mount('#app')


