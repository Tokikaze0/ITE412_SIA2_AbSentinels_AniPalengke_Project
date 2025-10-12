import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const setToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    localStorage.setItem('token', token)
  } else {
    delete api.defaults.headers.common['Authorization']
    localStorage.removeItem('token')
  }
}

const stored = localStorage.getItem('token')
if (stored) setToken(stored)

export default api
