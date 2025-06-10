import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({ username: '', access_token: '', tablename: {}, filter: {} }), // 将 tablename 初始化为对象
  actions: {
    setUserInfo(username, access_token, tablename, filter) {
      this.username = username
      this.access_token = access_token
      this.tablename = tablename || {} // 避免传入null时出错
      this.filter = filter || {} // 避免传入null时出错
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('username', username)
      localStorage.setItem('tablename', JSON.stringify(tablename || {})) // 存储为 JSON 字符串
      localStorage.setItem('filter', JSON.stringify(filter || {})) // 防止存储undefined
    },
    logout() {
      this.username = ''
      this.access_token = ''
      this.tablename = {} // 重置为对象
      this.filter = {} // 重置为对象
      localStorage.removeItem('access_token')
      localStorage.removeItem('username')
      localStorage.removeItem('tablename')
      localStorage.removeItem('filter')
    },
    hydrate() {
      const username = localStorage.getItem('username')
      const access_token = localStorage.getItem('access_token')
      const tablenameStr = localStorage.getItem('tablename')
      const filterStr = localStorage.getItem('filter')
      
      let tablename = {}
      let filter = {}
      if (tablenameStr) {
        try {
          tablename = JSON.parse(tablenameStr) // 从 JSON 字符串解析回对象
          filter = JSON.parse(filterStr) // 从 JSON 字符串解析回对象
        } catch (e) {
          console.error('解析 tablename 失败:', e)
        }
      }
      
      if (username && access_token) {
        this.setUserInfo(username, access_token, tablename, filter)
      } else {
        console.log('从 localStorage 恢复用户信息失败')
      }
    }
  }
})