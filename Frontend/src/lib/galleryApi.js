import api from './api'

export async function listPhotos(eventId, { mine, cursor } = {}) {
  const params = mine ? { mine: true } : cursor ? { cursor } : undefined
  const { data } = await api.get(`/events/${eventId}/photos`, { params })
  return data
}
