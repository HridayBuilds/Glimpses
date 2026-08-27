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

export async function archiveEvent(eventId) {
  const { data } = await api.post(`/events/${eventId}/archive`)
  return data
}

export async function deleteEvent(eventId) {
  const { data } = await api.delete(`/events/${eventId}`)
  return data
}

export async function getEventDetail(eventId) {
  const { data } = await api.get(`/events/${eventId}`)
  return data
}

export async function updateEventDetail(eventId, fields) {
  const { data } = await api.put(`/events/${eventId}`, fields)
  return data
}

export async function getEventStats(eventId) {
  const { data } = await api.get(`/events/${eventId}/stats`)
  return data
}

export async function getQrcodeUrl(eventId) {
  const { data } = await api.get(`/events/${eventId}/qrcode`)
  return data
}
