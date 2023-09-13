import axios from 'axios'

// 请求超时时间
const TIMEOUT: number = 3000000
// 创建 axios 实例
export const request = axios.create({
  baseURL: 'http://localhost:8080/api/', // api的base_url
  timeout: TIMEOUT,
  validateStatus: function (status) {
    return status < 500 // response status 不在范围内直接 reject
  }
})