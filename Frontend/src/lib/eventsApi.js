import api from './api'

export async function createEvent(name, description) {
  const { data } = await api.post('/events', { name, description })
  return data
}

export async function getOrganizedEvents() {
  const { data } = await api.get('/events')
  return data
}

export async function getMyEvents() {
  const { data } = await api.get('/events/my-events')
  return data
}
