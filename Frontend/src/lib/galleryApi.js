import api from './api'

export async function listPhotos(eventId, { mine, cursor } = {}) {
  const params = mine ? { mine: true } : cursor ? { cursor } : undefined
  const { data } = await api.get(`/events/${eventId}/photos`, { params })
  return data
}

export async function getDownloadUrls(eventId, photoIDs) {
  const { data } = await api.post(`/events/${eventId}/photos/download-urls`, { photoIDs })
  return data
}

export async function deletePhoto(eventId, photoId) {
  const { data } = await api.delete(`/events/${eventId}/photos/${photoId}`)
  return data
}

export async function bulkDeletePhotos(eventId, photoIDs) {
  const { data } = await api.post(`/events/${eventId}/photos/bulk-delete`, { photoIDs })
  return data
}
