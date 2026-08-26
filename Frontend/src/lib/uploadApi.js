import api from './api'

export async function getUploadUrl(eventId) {
  const { data } = await api.post(`/events/${eventId}/upload-url`)
  return data
}

export async function getJobStatus(eventId, jobId) {
  const { data } = await api.get(`/events/${eventId}/jobs/${jobId}/status`)
  return data
}
