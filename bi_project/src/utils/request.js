// src/utils/request.js
import axios from 'axios'
import { useUserStore } from '../store/user'
import router from '../router'
import { ElMessage } from 'element-plus'
import { h } from 'vue'

const service = axios.create({
  baseURL: '/api',
  timeout: 30000
});

// 请求拦截器
service.interceptors.request.use(config => {
  const userStore = useUserStore()
  const token = userStore.access_token || localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config; // 必须返回config
});

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    // 成功响应直接返回
    return response;
  },
  (error) => {
    if (error.response) {
      // 处理HTTP错误状态码
      switch (error.response.status) {
        case 400:
          // 登录失败（用户名或密码错误）
          ElMessage({
            message:h('span', { style: 'font-size: 18px' }, error.response?.data?.message),
            type: 'error',
            duration: 3000
          });
          return Promise.reject(error);
          
        case 401:
          // 未授权（令牌过期或无效）
          ElMessage({
            message:h('span', { style: 'font-size: 18px' }, error.response?.data?.message),
            type: 'error',
            duration: 3000
          });
          const userStore = useUserStore();
          userStore.logout();
          router.push('/');
          return Promise.reject(error);
          
        case 403:
          // 禁止访问
          ElMessage.error('没有权限访问该资源,请联系工程师Mr.周');
          return Promise.reject(error);
          
        case 404:
          // 资源不存在
          ElMessage.error('请求的资源不存在,请联系工程师Mr.周');
          return Promise.reject(error);
        case 422:
          // 令牌过期
          ElMessage.error('登录已过期,请重新登录');
          setTimeout(() => { // 修正：使用setTimeout而不是timeout
            router.push('/');
          }, 2000);
          return Promise.reject(error);
        case 500:
          // 服务器内部错误
          ElMessage.error('数据库太拉了,连不上,再试几次看看,实在不行联系工程师Mr.周');
          return Promise.reject(error);
          
        default:
          // 其他错误
          ElMessage.error(`请求失败，状态码: ${error.response.status},请联系工程师Mr.周`);
          return Promise.reject(error);
      }
    } else if (error.request) {
      // 请求已发送，但没有收到响应
      ElMessage.error('没有收到服务器响应,请联系工程师Mr.周');
      return Promise.reject(error);
    } else {
      // 发送请求时出错
      ElMessage.error(`请求出错: ${error.message},请联系工程师Mr.周`);
      return Promise.reject(error);
    }
  }
);

export default service;