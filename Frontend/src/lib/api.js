import axios from 'axios'
import { getCurrentSession, refreshCurrentSession } from './cognito'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

api.interceptors.request.use(async (config) => {
  const session = await getCurrentSession()
  if (session) {
    config.headers.Authorization = `Bearer ${session.getIdToken().getJwtToken()}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error
    if (response?.status === 401 && !config._retried) {
      config._retried = true
      const session = await refreshCurrentSession()
      if (session) {
        config.headers.Authorization = `Bearer ${session.getIdToken().getJwtToken()}`
        return api(config)
      }
    }
    return Promise.reject(error)
  },
)

export default api
