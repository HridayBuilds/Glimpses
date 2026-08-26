import api from './api'

export async function requestDownload(eventId, photoIds) {
  const { data } = await api.post(`/events/${eventId}/photos/download`, photoIds ? { photoIds } : undefined)
  return data
}

export async function getDownloadStatus(eventId, downloadId) {
  const { data } = await api.get(`/events/${eventId}/downloads/${downloadId}/status`)
  return data
}
