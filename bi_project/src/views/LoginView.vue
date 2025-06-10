<template>
  <div class="overall">
    <div class="curtain">
      <div class="login">
        <h1 style="font-size: 24px; font-weight: 700; line-height: 32px; color: #000;">账号登录</h1>
        <el-input v-model="username" style="width: 360px; height: 48px;" placeholder="用户名" :suffix-icon="User" @keyup.enter="handleLogin" />
        <el-input v-model="password" style="width: 360px; height: 48px;" type="password" placeholder="密码" show-password @keyup.enter="handleLogin" />
        <el-button 
          type="primary" 
          style="width: 360px; height: 48px;" 
          @click="handleLogin"
          :loading="loading">
          {{ loading? '登录中...' : '登录' }}
        </el-button>
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, h } from 'vue'
import { useRouter } from 'vue-router'
import { User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import CryptoJS from 'crypto-js'; 
import service from '../utils/request'
import { useUserStore } from '../store/user'
const errorMessage = ref('') // 定义响应式变量
const username = ref('')
const password = ref('')
const loading = ref(false)
const router = useRouter()
const userStore = useUserStore() // 直接调用，无需传入pinia
const ENCRYPTION_KEY = import.meta.env.VITE_ENCRYPTION_KEY;
function parseKey(key) {
  const keyBytes = CryptoJS.enc.Base64.parse(key);
  return CryptoJS.lib.WordArray.create(keyBytes.words.slice(0, 32 / 4));
}
const encryptPassword = (plainText) => {
  try {
    const parsedKey = parseKey(ENCRYPTION_KEY);
    // 生成随机初始化向量 (IV) - 16字节
    const iv = CryptoJS.lib.WordArray.random(128 / 8);
    // 使用 CBC 模式加密
    const encrypted = CryptoJS.AES.encrypt(plainText, parsedKey, {
      iv: iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7
    });
    return iv.toString(CryptoJS.enc.Base64) + ':' + encrypted.toString();
  } catch (e) {
    console.error('加密失败:', e);
    return plainText;
  }
};

const handleLogin = async () => {
  // 重置错误信息
  errorMessage.value = '';
  // 防止重复提交
  if (loading.value) return;
  // 表单验证
  if (!username.value.trim()) {
    errorMessage.value = '请输入用户名';
    return;
  }
  if (!password.value) {
    errorMessage.value = '请输入密码';
    return;
  }

  loading.value = true;
  try {
    const encryptedPassword = encryptPassword(password.value);
    const response = await service.post('/login', {
      username: username.value,
      password: encryptedPassword
    });

    if (response.data.success) {
      const { access_token, user } = response.data;
      userStore.setUserInfo(user.username, access_token, user.tablename, user.filter);
      
      // 跳转前延迟，确保动画完成
      await router.push({ name: 'Home' });
      ElMessage.success('登录成功');
    } else {
      errorMessage.value = response.data.message || '认证失败，请检查凭证';
      // 添加登录失败日志
      console.warn('登录失败:', response.data.message);
    }
  } catch (error) {
    errorMessage.value = '网络错误，请稍后重试';
    console.error('登录请求异常:', error);
    
    // 错误类型判断
    if (error.response?.status === 401) {
      errorMessage.value = '用户名或密码错误';
    } else if (error.code === 'ECONNABORTED') {
      errorMessage.value = '请求超时，请检查网络';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 保持原有样式不变 */
.overall {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background-image: url("/bg.jpg");
  background-size: cover;
  background-repeat: no-repeat;
  background-position: left center;
  z-index: -1;
  min-height: 100vh;
  display: flex;
  justify-content: flex-end;
}

.curtain {
  width: 488px;
  min-height: 100vh;
  background: hsla(0, 0%, 96.5%, .7);
  box-shadow: 0 16px 32px 0 rgba(215, 223, 246, .3);
  display: flex;
  justify-content: center;
  align-items: center;
}

.login {
  width: 70%;
  display: flex;
  justify-content: left;
  flex-wrap: wrap;
  gap: 20px;
}

.error-message {
  color: #f56c6c;
  font-size: 14px;
  margin-top: -10px;
}
</style>