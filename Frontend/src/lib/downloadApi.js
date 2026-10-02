import api from './api'

export async function requestDownload(eventId, photoIds, scope) {
  const { data } = await api.post(`/events/${eventId}/photos/download`, {
    scope,
    ...(photoIds ? { photoIds } : {}),
  })
  return data
}

export async function getDownloadStatus(eventId, downloadId) {
  const { data } = await api.get(`/events/${eventId}/downloads/${downloadId}/status`)
  return data
}
